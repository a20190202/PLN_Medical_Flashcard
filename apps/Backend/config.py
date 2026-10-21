"""Configuración del backend, leída de variables de entorno (y de un .env opcional)."""

import os
from dataclasses import dataclass, replace
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent

DEFAULT_EMBEDDINGS = "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"
DEFAULT_VECTORSTORE_DIR = (
    BACKEND_DIR / "app" / "model" / "data" / DEFAULT_EMBEDDINGS.replace("/", "_")
)


def _env(name, default):
    value = os.environ.get(name)
    return default if value is None or value.strip() == "" else value.strip()


def _env_bool(name, default):
    return _env(name, str(default)).lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    # Servidor
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    cors_origins: tuple = ("http://localhost:3000",)

    # LLM (Ollama)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"
    ollama_num_ctx: int = 4096
    ollama_timeout: float = 300.0
    temperature: float = 0.1

    # Recuperación
    embeddings_model: str = DEFAULT_EMBEDDINGS
    vectorstore_dir: Path = DEFAULT_VECTORSTORE_DIR
    cache_dir: Path = BACKEND_DIR / ".cache"
    retrieval_mode: str = "hybrid"  # dense | bm25 | hybrid
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"  # "" lo desactiva
    candidates_k: int = 20
    context_k: int = 3

    # Verificación de soporte de las respuestas en el contexto recuperado
    support_threshold: float = 0.6

    @classmethod
    def from_env(cls):
        try:
            from dotenv import load_dotenv

            load_dotenv(BACKEND_DIR / ".env")
        except ImportError:
            pass

        d = cls()
        return cls(
            host=_env("HOST", d.host),
            port=int(_env("PORT", d.port)),
            debug=_env_bool("FLASK_DEBUG", d.debug),
            cors_origins=tuple(
                o.strip()
                for o in _env("CORS_ORIGINS", ",".join(d.cors_origins)).split(",")
                if o.strip()
            ),
            ollama_base_url=_env("OLLAMA_BASE_URL", d.ollama_base_url),
            ollama_model=_env("OLLAMA_MODEL", d.ollama_model),
            ollama_num_ctx=int(_env("OLLAMA_NUM_CTX", d.ollama_num_ctx)),
            ollama_timeout=float(_env("OLLAMA_TIMEOUT", d.ollama_timeout)),
            temperature=float(_env("LLM_TEMPERATURE", d.temperature)),
            embeddings_model=_env("EMBEDDINGS_MODEL", d.embeddings_model),
            vectorstore_dir=Path(_env("VECTORSTORE_DIR", d.vectorstore_dir)),
            cache_dir=Path(_env("CACHE_DIR", d.cache_dir)),
            retrieval_mode=_env("RETRIEVAL_MODE", d.retrieval_mode),
            reranker_model=os.environ.get("RERANKER_MODEL", d.reranker_model).strip(),
            candidates_k=int(_env("RETRIEVAL_CANDIDATES_K", d.candidates_k)),
            context_k=int(_env("RETRIEVAL_CONTEXT_K", d.context_k)),
            support_threshold=float(_env("SUPPORT_THRESHOLD", d.support_threshold)),
        )

    def with_overrides(self, **kwargs):
        return replace(self, **kwargs)
