import io
import logging
import re

from flask import Blueprint, current_app, jsonify, request, send_file
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from .errors import AppError, InvalidRequestError
from .export import build_apkg
from .rag.areas import AREAS
from .schemas import ExportRequest, GenerateRequest, RegenerateRequest

log = logging.getLogger(__name__)

main = Blueprint("main", __name__)


def _services():
    return current_app.extensions["medcards"]


def _parse(model):
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise InvalidRequestError("El cuerpo de la solicitud debe ser un objeto JSON.")
    return model.model_validate(body)


def _result_payload(result, req):
    settings = _services().settings
    return {
        "flashcards": [card.model_dump(mode="json") for card in result.flashcards],
        "topic": req.texto if req.mode == "topic" else None,
        "query_topic": result.query_topic,
        "mode": req.mode,
        "card_type": req.card_type,
        "difficulty": req.difficulty,
        "language": req.language,
        "model": settings.ollama_model,
        "retrieval_mode": settings.retrieval_mode if req.mode == "topic" else None,
        "warnings": result.warnings,
        "elapsed_seconds": result.elapsed_seconds,
    }


@main.post("/generar_preguntas")
def generar_preguntas():
    req = _parse(GenerateRequest)
    result = _services().generator.generate(req)
    return jsonify(_result_payload(result, req))


@main.post("/regenerar_pregunta")
def regenerar_pregunta():
    req = _parse(RegenerateRequest)
    result = _services().generator.regenerate(req)
    return jsonify(_result_payload(result, req))


@main.post("/exportar_anki")
def exportar_anki():
    req = _parse(ExportRequest)
    data = build_apkg(req.deck_name, req.cards)
    filename = re.sub(r"[^A-Za-z0-9_-]+", "_", req.deck_name).strip("_") or "flashcards"
    return send_file(
        io.BytesIO(data),
        mimetype="application/apkg",
        as_attachment=True,
        download_name=f"{filename}.apkg",
    )


@main.get("/areas")
def areas():
    return jsonify(
        [{"key": a.key, "title_en": a.title_en, "title_es": a.title_es} for a in AREAS]
    )


@main.get("/health")
def health():
    generator = _services().generator
    ollama = generator.llm.health()
    retrieval = generator.retriever.status()
    ok = ollama.get("reachable") and ollama.get("model_available") and retrieval.get("vectorstore_found")
    body = {"status": "ok" if ok else "degraded", "ollama": ollama, "retrieval": retrieval}
    return jsonify(body), 200 if ok else 503


def _validation_details(exc):
    details = []
    for err in exc.errors(include_url=False):
        field = ".".join(str(part) for part in err["loc"]) or None
        details.append({"field": field, "message": err["msg"].removeprefix("Value error, ")})
    return details


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def _app_error(exc):
        return jsonify(exc.to_dict()), exc.status_code

    @app.errorhandler(ValidationError)
    def _validation_error(exc):
        details = _validation_details(exc)
        message = details[0]["message"] if len(details) == 1 else "La solicitud tiene campos inválidos."
        body = {"error": message, "code": InvalidRequestError.code, "details": details}
        return jsonify(body), 400

    @app.errorhandler(HTTPException)
    def _http_error(exc):
        return jsonify({"error": exc.description, "code": exc.name.lower().replace(" ", "_")}), exc.code

    @app.errorhandler(Exception)
    def _unexpected(exc):
        log.exception("Error no controlado")
        return jsonify({"error": "Error interno del servidor.", "code": "internal_error"}), 500
