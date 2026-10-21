from types import SimpleNamespace

import ollama
import pytest

from app.errors import ServiceUnavailableError
from app.rag.llm import OllamaClient, normalize_model_name, parse_json_lenient


@pytest.mark.parametrize(
    "content, expected",
    [
        ('{"a": 1}', {"a": 1}),
        ('Sure! Here it is: {"a": 1} Hope it helps', {"a": 1}),
        ("no json here", None),
        (None, None),
    ],
)
def test_parse_json_lenient(content, expected):
    assert parse_json_lenient(content) == expected


def test_normalize_model_name():
    assert normalize_model_name("llama2") == "llama2:latest"
    assert normalize_model_name("llama3.1:8b") == "llama3.1:8b"


class FakeOllama:
    def __init__(self, content='{"ok": true}', error=None, models=("llama3.1:8b",)):
        self.content = content
        self.error = error
        self.models = models
        self.kwargs = None

    def chat(self, **kwargs):
        self.kwargs = kwargs
        if self.error:
            raise self.error
        return SimpleNamespace(message=SimpleNamespace(content=self.content))

    def list(self):
        if self.error:
            raise self.error
        return SimpleNamespace(models=[SimpleNamespace(model=m) for m in self.models])


def _client(settings, **kwargs):
    fake = FakeOllama(**kwargs)
    return OllamaClient(settings.with_overrides(ollama_model="llama3.1:8b"), client=fake), fake


def test_generate_json_sends_schema_and_options(settings):
    client, fake = _client(settings)
    obj, raw = client.generate_json("prompt", {"type": "object"}, system="sys", num_ctx=8192)

    assert obj == {"ok": True}
    assert raw == '{"ok": true}'
    assert fake.kwargs["format"] == {"type": "object"}
    assert fake.kwargs["messages"][0] == {"role": "system", "content": "sys"}
    assert fake.kwargs["options"]["num_ctx"] == 8192
    assert fake.kwargs["options"]["temperature"] == settings.temperature


def test_default_context_window(settings):
    client, fake = _client(settings)
    client.generate_json("prompt", {})
    assert fake.kwargs["options"]["num_ctx"] == settings.ollama_num_ctx
    assert len(fake.kwargs["messages"]) == 1


def test_missing_model_suggests_pull(settings):
    client, _ = _client(settings, error=ollama.ResponseError("model not found", 404))
    with pytest.raises(ServiceUnavailableError) as exc:
        client.generate_json("p", {})
    assert exc.value.hint == "Ejecuta: ollama pull llama3.1:8b"


def test_connection_error_is_service_unavailable(settings):
    client, _ = _client(settings, error=ConnectionError("refused"))
    with pytest.raises(ServiceUnavailableError) as exc:
        client.generate_json("p", {})
    assert "ollama serve" in exc.value.hint


def test_health(settings):
    client, _ = _client(settings)
    assert client.health()["model_available"] is True

    client, _ = _client(settings, models=("llama2:latest",))
    health = client.health()
    assert health["reachable"] is True and health["model_available"] is False

    client, _ = _client(settings, error=ConnectionError("refused"))
    assert client.health()["reachable"] is False
