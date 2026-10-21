import sys
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from config import Settings  # noqa: E402

from helpers import FakeLLM, FakeRetriever, FakeSupport, smart_responder  # noqa: E402


@pytest.fixture
def settings(tmp_path):
    return Settings(
        vectorstore_dir=tmp_path / "vectorstore",
        cache_dir=tmp_path / "cache",
        reranker_model="",
        ollama_model="fake-model",
    )


@pytest.fixture
def retriever():
    return FakeRetriever()


@pytest.fixture
def llm():
    return FakeLLM(smart_responder)


@pytest.fixture
def generator(settings, retriever, llm):
    from app.rag.generator import FlashcardGenerator

    return FlashcardGenerator(settings, retriever, llm, FakeSupport())


@pytest.fixture
def client(settings, generator):
    from app import create_app

    app = create_app(settings, generator=generator)
    app.testing = True
    return app.test_client()
