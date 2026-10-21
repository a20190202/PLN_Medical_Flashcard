"""Cliente de Ollama con salida estructurada (JSON Schema)."""

import json
import logging
import re
import threading

from ..errors import ServiceUnavailableError

log = logging.getLogger(__name__)

_JSON_OBJECT_RE = re.compile(r"\{.*\}", re.DOTALL)


def normalize_model_name(name):
    return name if ":" in name else f"{name}:latest"


def parse_json_lenient(content):
    """JSON del LLM. Si el servidor ignoró el schema, intenta rescatar el primer objeto."""
    try:
        return json.loads(content)
    except (json.JSONDecodeError, TypeError):
        pass
    match = _JSON_OBJECT_RE.search(content or "")
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return None


class OllamaClient:
    def __init__(self, settings, client=None):
        self.settings = settings
        self._client = client
        self._lock = threading.Lock()

    @property
    def client(self):
        with self._lock:
            if self._client is None:
                import ollama

                self._client = ollama.Client(
                    host=self.settings.ollama_base_url, timeout=self.settings.ollama_timeout
                )
            return self._client

    @property
    def model(self):
        return self.settings.ollama_model

    def _unavailable(self, exc):
        import ollama

        if isinstance(exc, ollama.ResponseError):
            if exc.status_code == 404:
                return ServiceUnavailableError(
                    f"El modelo '{self.model}' no está descargado en Ollama.",
                    hint=f"Ejecuta: ollama pull {self.model}",
                )
            return ServiceUnavailableError(f"Ollama respondió con un error: {exc.error}")
        return ServiceUnavailableError(
            f"No se pudo conectar con Ollama en {self.settings.ollama_base_url}.",
            hint="Verifica que Ollama esté instalado y corriendo (ollama serve).",
        )

    def generate_json(self, prompt, schema, system=None, num_ctx=None):
        """Devuelve (objeto JSON o None, texto crudo)."""
        import httpx
        import ollama

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        try:
            response = self.client.chat(
                model=self.model,
                messages=messages,
                format=schema,
                options={
                    "temperature": self.settings.temperature,
                    "num_ctx": num_ctx or self.settings.ollama_num_ctx,
                },
            )
        except (ollama.ResponseError, ConnectionError, httpx.HTTPError) as exc:
            log.warning("Fallo al llamar a Ollama: %s", exc)
            raise self._unavailable(exc) from exc

        content = response.message.content or ""
        return parse_json_lenient(content), content

    def health(self):
        import httpx
        import ollama

        status = {"base_url": self.settings.ollama_base_url, "model": self.model}
        try:
            models = self.client.list().models
        except (ollama.ResponseError, ConnectionError, httpx.HTTPError) as exc:
            error = self._unavailable(exc)
            return {**status, "reachable": False, "model_available": False, "error": error.message, "hint": error.hint}

        names = {normalize_model_name(m.model) for m in models if m.model}
        available = normalize_model_name(self.model) in names
        result = {**status, "reachable": True, "model_available": available}
        if not available:
            result["hint"] = f"Ejecuta: ollama pull {self.model}"
        return result
