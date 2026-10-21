"""Generación de flashcards.

Modo "topic": una búsqueda en los libros y una llamada al LLM por cada área
(definición, etiología, clínica, diagnóstico, tratamiento), así cada tarjeta se
apoya en fragmentos específicos de su área.
Modo "passage": las tarjetas salen de los apuntes que envía el estudiante.
"""

import logging
import re
import time
from dataclasses import dataclass, field

from ..errors import GenerationError, InvalidCardError, InvalidRequestError
from ..schemas import MAX_TOPIC_CHARS
from .areas import AREAS, AREAS_BY_KEY
from .cards import build_card, support_statement
from .legacy import parse_legacy_text
from .prompts import (
    CARD_SCHEMAS,
    TRANSLATE_SCHEMA,
    deck_schema,
    passage_deck_prompt,
    system_prompt,
    topic_card_prompt,
    translate_prompt,
)
from .retrieval import Passage

log = logging.getLogger(__name__)

MAX_ATTEMPTS = 2
PASSAGE_NUM_CTX = 8192
NOTES_SOURCE = "Student notes"


@dataclass
class GenerationResult:
    flashcards: list
    query_topic: str | None = None
    warnings: list = field(default_factory=list)
    elapsed_seconds: float = 0.0


def areas_for(n):
    """Áreas para n tarjetas: se recorren en orden y se repiten si n > 5."""
    return [AREAS[i % len(AREAS)] for i in range(n)]


def _normalize_question(question):
    return re.sub(r"[^a-z0-9áéíóúñü]+", " ", question.lower()).strip()


def _is_repeated(question, previous):
    key = _normalize_question(question)
    return any(key == _normalize_question(p) for p in previous)


class FlashcardGenerator:
    def __init__(self, settings, retriever, llm, support=None):
        self.settings = settings
        self.retriever = retriever
        self.llm = llm
        self.support = support

    # ---- API pública -------------------------------------------------------

    def generate(self, req):
        start = time.perf_counter()
        if req.mode == "passage":
            query_topic = None
            cards, warnings = self._passage_cards(req, req.num_cards, avoid=[])
        else:
            query_topic = self.retrieval_topic(req.texto, req.language)
            cards, warnings, asked = [], [], {}
            for area in areas_for(req.num_cards):
                try:
                    card = self._topic_card(req, query_topic, area, asked.get(area.key, []))
                except InvalidCardError as exc:
                    warnings.append(f"No se pudo generar la tarjeta de «{area.title(req.language)}»: {exc}")
                    continue
                asked.setdefault(area.key, []).append(card.question)
                cards.append(card)

        if not cards:
            raise GenerationError(
                "El modelo no devolvió ninguna flashcard válida.",
                hint="Intenta de nuevo o prueba con otro modelo (variable OLLAMA_MODEL).",
            )
        return GenerationResult(cards, query_topic, warnings, round(time.perf_counter() - start, 2))

    def regenerate(self, req):
        """Genera una sola tarjeta nueva, distinta de `req.avoid_questions`."""
        start = time.perf_counter()
        if req.mode == "passage":
            query_topic = None
            cards, warnings = self._passage_cards(req, 1, avoid=req.avoid_questions)
        else:
            area = AREAS_BY_KEY.get(req.area or AREAS[0].key)
            if area is None:
                raise InvalidRequestError(
                    f"Área desconocida: '{req.area}'.",
                    hint="Áreas válidas: " + ", ".join(AREAS_BY_KEY),
                )
            query_topic = self.retrieval_topic(req.texto, req.language)
            try:
                cards = [self._topic_card(req, query_topic, area, req.avoid_questions)]
            except InvalidCardError as exc:
                raise GenerationError(f"No se pudo regenerar la tarjeta: {exc}") from exc
            warnings = []
        return GenerationResult(cards[:1], query_topic, warnings, round(time.perf_counter() - start, 2))

    def retrieval_topic(self, topic, language):
        """Los libros están en inglés: si el tema puede no estarlo, se traduce para buscar."""
        if language != "es" and topic.isascii():
            return topic
        obj, _ = self.llm.generate_json(translate_prompt(topic), TRANSLATE_SCHEMA)
        term = obj.get("english_term") if isinstance(obj, dict) else None
        term = " ".join(term.split()) if isinstance(term, str) else ""
        if not term or len(term) > MAX_TOPIC_CHARS:
            log.warning("No se pudo traducir el tema %r; se busca tal cual", topic)
            return topic
        return term

    # ---- detalle -----------------------------------------------------------

    def _topic_card(self, req, query_topic, area, avoid):
        passages = self.retriever.search(area.query(query_topic))
        if not passages:
            raise InvalidCardError("no se encontraron fragmentos relevantes en los libros")

        subject = req.texto if query_topic.lower() == req.texto.lower() else f"{req.texto} ({query_topic})"
        prompt = topic_card_prompt(
            subject, area, req.language, req.difficulty, req.card_type, passages, avoid
        )
        title = area.title(req.language)

        def build(obj, raw):
            if obj is None and req.card_type == "qa":
                legacy = parse_legacy_text(raw)
                obj = legacy[0] if legacy else None
            card, cited = build_card(obj, req.card_type, passages, area=area, title=title)
            if _is_repeated(card.question, avoid):
                raise InvalidCardError("repitió una pregunta que ya existe")
            return card, cited

        card, cited = self._call_with_retries(prompt, CARD_SCHEMAS[req.card_type], req.language, build)
        card.support = self._check_support(card, cited)
        return card

    def _passage_cards(self, req, n, avoid):
        notes = Passage(req.texto, NOTES_SOURCE)
        prompt = passage_deck_prompt(req.texto, n, req.difficulty, req.card_type, avoid)
        num_ctx = max(self.settings.ollama_num_ctx, PASSAGE_NUM_CTX)

        def build(obj, raw):
            items = obj.get("flashcards") if isinstance(obj, dict) else None
            if items is None and req.card_type == "qa":
                items = parse_legacy_text(raw)
            if not isinstance(items, list) or not items:
                raise InvalidCardError("la respuesta no contiene flashcards")
            cards, warnings, seen = [], [], list(avoid)
            for i, item in enumerate(items[:n], start=1):
                try:
                    card, _ = build_card(item, req.card_type, [notes])
                except InvalidCardError as exc:
                    warnings.append(f"Se descartó la tarjeta {i}: {exc}")
                    continue
                if _is_repeated(card.question, seen):
                    warnings.append(f"Se descartó la tarjeta {i}: pregunta repetida")
                    continue
                seen.append(card.question)
                cards.append(card)
            if not cards:
                raise InvalidCardError("ninguna tarjeta tuvo el formato esperado")
            return cards, warnings

        cards, warnings = self._call_with_retries(
            prompt, deck_schema(req.card_type, n), req.language, build, num_ctx=num_ctx
        )
        for card in cards:
            card.support = self._check_support(card, [notes])
        return cards, warnings

    def _call_with_retries(self, prompt, schema, language, build, num_ctx=None):
        last_error = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            obj, raw = self.llm.generate_json(
                prompt, schema, system=system_prompt(language), num_ctx=num_ctx
            )
            try:
                return build(obj, raw)
            except InvalidCardError as exc:
                last_error = exc
                log.info("Respuesta inválida del LLM (intento %d/%d): %s", attempt, MAX_ATTEMPTS, exc)
        raise last_error

    def _check_support(self, card, passages):
        if self.support is None:
            return None
        try:
            return self.support.check(support_statement(card), passages)
        except Exception as exc:  # la verificación es opcional: no debe impedir la generación
            log.warning("No se pudo verificar el soporte de la tarjeta: %s", exc)
            return None


def build_generator(settings):
    """Arma el generador real. Los modelos se cargan recién en la primera solicitud."""
    from .llm import OllamaClient
    from .retrieval import Retriever
    from .support import SupportChecker

    retriever = Retriever(settings)
    support = (
        SupportChecker(retriever.embed, settings.support_threshold)
        if settings.support_threshold > 0
        else None
    )
    return FlashcardGenerator(settings, retriever, OllamaClient(settings), support)
