"""Errores de dominio. Cada uno sabe con qué código HTTP responder."""


class AppError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message, *, hint=None):
        super().__init__(message)
        self.message = message
        self.hint = hint

    def to_dict(self):
        body = {"error": self.message, "code": self.code}
        if self.hint:
            body["hint"] = self.hint
        return body


class InvalidRequestError(AppError):
    status_code = 400
    code = "invalid_request"


class ServiceUnavailableError(AppError):
    """Una dependencia externa (Ollama, vector store, modelos) no está disponible."""

    status_code = 503
    code = "service_unavailable"


class GenerationError(AppError):
    """El LLM respondió, pero no se pudo obtener ninguna flashcard válida."""

    status_code = 422
    code = "generation_failed"


class InvalidCardError(ValueError):
    """Una tarjeta individual no cumple el formato esperado."""
