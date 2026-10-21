"""Validación y normalización de las tarjetas que devuelve el LLM."""

import re

from ..errors import InvalidCardError
from ..schemas import Flashcard, Source
from .text import book_name, excerpt

CLOZE_GAP = "[...]"
MCQ_OPTIONS = 4


def _text(obj, key, required=True):
    value = obj.get(key)
    value = " ".join(value.split()) if isinstance(value, str) else ""
    if required and not value:
        raise InvalidCardError(f"falta el campo '{key}'")
    return value


def _as_int(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def cited_passages(source_ids, passages):
    """Pasajes citados por el modelo (números desde 1). Si no citó ninguno válido, se usan todos."""
    cited, seen = [], set()
    for raw in source_ids if isinstance(source_ids, list) else []:
        sid = _as_int(raw)
        if sid is not None and 1 <= sid <= len(passages) and sid not in seen:
            seen.add(sid)
            cited.append(passages[sid - 1])
    return cited or list(passages)


def _qa_fields(obj):
    return _text(obj, "question"), _text(obj, "answer"), {}


def _cloze_fields(obj):
    sentence = _text(obj, "sentence")
    cloze = _text(obj, "cloze")
    pattern = re.compile(re.escape(cloze), re.IGNORECASE)
    match = pattern.search(sentence)
    if not match:
        raise InvalidCardError("el texto a ocultar (cloze) no aparece en la oración")
    if cloze.lower() == sentence.lower():
        raise InvalidCardError("el cloze no puede ser la oración completa")
    question = f"{sentence[: match.start()]}{CLOZE_GAP}{sentence[match.end():]}"
    return question, match.group(0), {"cloze_sentence": sentence, "cloze": match.group(0)}


def _mcq_fields(obj):
    question = _text(obj, "question")
    options = obj.get("options")
    if not isinstance(options, list) or len(options) != MCQ_OPTIONS:
        raise InvalidCardError(f"se esperaban exactamente {MCQ_OPTIONS} opciones")
    options = [" ".join(o.split()) if isinstance(o, str) else "" for o in options]
    if not all(options):
        raise InvalidCardError("hay opciones vacías")
    if len({o.lower() for o in options}) != MCQ_OPTIONS:
        raise InvalidCardError("hay opciones repetidas")
    correct = _as_int(obj.get("correct_option"))
    if correct is None or not 0 <= correct < MCQ_OPTIONS:
        raise InvalidCardError("correct_option debe ser un índice entre 0 y 3")
    explanation = _text(obj, "explanation", required=False) or None
    fields = {"options": options, "correct_option": correct, "explanation": explanation}
    return question, options[correct], fields


_BUILDERS = {"qa": _qa_fields, "cloze": _cloze_fields, "mcq": _mcq_fields}


def build_card(obj, card_type, passages, area=None, title=None):
    """Convierte el JSON del LLM en una Flashcard. Devuelve (tarjeta, pasajes citados).

    Lanza InvalidCardError si el JSON no cumple el formato del tipo de tarjeta.
    """
    if not isinstance(obj, dict):
        raise InvalidCardError("la respuesta no es un objeto JSON")
    question, answer, fields = _BUILDERS[card_type](obj)
    title = title or _text(obj, "title")
    cited = cited_passages(obj.get("source_ids"), passages)
    card = Flashcard(
        card_type=card_type,
        area=area.key if area else None,
        title=title,
        question=question,
        answer=answer,
        sources=[
            Source(book=book_name(p.source), chunk_id=p.chunk_id, excerpt=excerpt(p.text))
            for p in cited
        ],
        **fields,
    )
    return card, cited


def support_statement(card):
    """Texto de la tarjeta que debe estar respaldado por los fragmentos."""
    if card.card_type == "cloze":
        return card.cloze_sentence
    if card.card_type == "mcq":
        return " ".join(filter(None, [f"{card.answer}.", card.explanation]))
    return card.answer
