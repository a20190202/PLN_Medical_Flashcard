from pathlib import Path

import pytest
from pydantic import ValidationError

from config import Settings
from app.schemas import GenerateRequest, MAX_PASSAGE_CHARS, RegenerateRequest


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "qwen2.5:7b")
    monkeypatch.setenv("CORS_ORIGINS", "http://a.test, http://b.test,")
    monkeypatch.setenv("FLASK_DEBUG", "true")
    monkeypatch.setenv("RERANKER_MODEL", "")
    monkeypatch.setenv("VECTORSTORE_DIR", "/data/store")
    monkeypatch.setenv("RETRIEVAL_CONTEXT_K", "5")
    monkeypatch.setenv("PORT", " ")

    settings = Settings.from_env()

    assert settings.ollama_model == "qwen2.5:7b"
    assert settings.cors_origins == ("http://a.test", "http://b.test")
    assert settings.debug is True
    assert settings.reranker_model == ""
    assert settings.vectorstore_dir == Path("/data/store")
    assert settings.context_k == 5
    assert settings.port == 8000


def test_request_defaults_and_strip():
    req = GenerateRequest(texto="  Asthma  ")
    assert req.texto == "Asthma"
    assert (req.mode, req.card_type, req.difficulty, req.language, req.num_cards) == (
        "topic", "qa", "intermediate", "en", 5,
    )


def test_passage_mode_allows_long_text():
    assert GenerateRequest(texto="x" * 5000, mode="passage")
    with pytest.raises(ValidationError):
        GenerateRequest(texto="x" * (MAX_PASSAGE_CHARS + 1), mode="passage")


def test_regenerate_limits_avoid_list():
    with pytest.raises(ValidationError):
        RegenerateRequest(texto="Asma", avoid_questions=["q"] * 21)
