"""Recuperación de fragmentos: densa (Chroma + BioBERT), léxica (BM25) e híbrida.

La búsqueda híbrida combina ambos rankings con Reciprocal Rank Fusion y luego,
si hay un cross-encoder configurado, reordena los candidatos comparando la
consulta con cada fragmento.
"""

import logging
import pickle
import threading
from array import array
from collections import Counter
from dataclasses import dataclass

import numpy as np

from ..errors import ServiceUnavailableError
from .text import tokenize

log = logging.getLogger(__name__)

RETRIEVAL_MODES = ("dense", "bm25", "hybrid")
_BM25_CACHE_VERSION = 1


@dataclass
class Passage:
    text: str
    source: str
    chunk_id: int | None = None
    score: float = 0.0

    @property
    def key(self):
        return f"{self.source}#{self.chunk_id}" if self.chunk_id is not None else self.text[:200]


def reciprocal_rank_fusion(rankings, k=60, limit=None):
    """Fusiona varios rankings de Passage. El score resultante es la suma de 1/(k + rank)."""
    fused = {}
    for ranking in rankings:
        for rank, passage in enumerate(ranking, start=1):
            entry = fused.get(passage.key)
            if entry is None:
                entry = fused[passage.key] = Passage(passage.text, passage.source, passage.chunk_id, 0.0)
            entry.score += 1.0 / (k + rank)
    result = sorted(fused.values(), key=lambda p: p.score, reverse=True)
    return result[:limit] if limit else result


class BM25Index:
    """BM25 sobre una matriz dispersa: cabe en memoria con los ~120 mil fragmentos del corpus."""

    def __init__(self, passages, k1=1.5, b=0.75):
        from scipy.sparse import coo_matrix

        self.passages = [Passage(p.text, p.source, p.chunk_id) for p in passages]
        n_docs = len(self.passages)
        if n_docs == 0:
            raise ValueError("No hay documentos para indexar")

        self.vocab = {}
        rows, cols, counts = array("i"), array("i"), array("f")
        lengths = np.zeros(n_docs, dtype=np.float32)
        for i, passage in enumerate(self.passages):
            term_counts = Counter(tokenize(passage.text))
            lengths[i] = sum(term_counts.values())
            for term, count in term_counts.items():
                rows.append(i)
                cols.append(self.vocab.setdefault(term, len(self.vocab)))
                counts.append(count)

        rows = np.frombuffer(rows, dtype=np.int32)
        cols = np.frombuffer(cols, dtype=np.int32)
        tf = np.frombuffer(counts, dtype=np.float32)

        doc_freq = np.bincount(cols, minlength=len(self.vocab)).astype(np.float32)
        idf = np.log((n_docs - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)
        avgdl = float(lengths.mean()) or 1.0
        weights = idf[cols] * tf * (k1 + 1) / (tf + k1 * (1 - b + b * lengths[rows] / avgdl))

        self.matrix = coo_matrix(
            (weights.astype(np.float32), (rows, cols)), shape=(n_docs, len(self.vocab))
        ).tocsc()

    def __len__(self):
        return len(self.passages)

    def search(self, query, k):
        term_ids = sorted({self.vocab[t] for t in tokenize(query) if t in self.vocab})
        if not term_ids:
            return []
        scores = np.asarray(self.matrix[:, term_ids].sum(axis=1)).ravel()
        k = min(k, len(scores))
        top = np.argpartition(-scores, k - 1)[:k]
        top = top[np.argsort(-scores[top])]
        return [
            Passage(self.passages[i].text, self.passages[i].source, self.passages[i].chunk_id, float(scores[i]))
            for i in top
            if scores[i] > 0
        ]

    def save(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".tmp")
        with open(tmp, "wb") as f:
            pickle.dump((_BM25_CACHE_VERSION, self), f, protocol=pickle.HIGHEST_PROTOCOL)
        tmp.replace(path)

    @staticmethod
    def load(path):
        with open(path, "rb") as f:
            version, index = pickle.load(f)
        if version != _BM25_CACHE_VERSION:
            raise ValueError("Versión de caché BM25 incompatible")
        return index


class Retriever:
    """Carga perezosa y única de embeddings, vector store, BM25 y reranker."""

    def __init__(self, settings):
        self.settings = settings
        self._lock = threading.RLock()
        self._embeddings = None
        self._store = None
        self._bm25 = None
        self._reranker = None
        self._reranker_failed = False

    # ---- carga de recursos -------------------------------------------------

    @property
    def embeddings(self):
        with self._lock:
            if self._embeddings is None:
                try:
                    from langchain_huggingface import HuggingFaceEmbeddings
                except ImportError as exc:  # pragma: no cover - depende del entorno
                    raise ServiceUnavailableError(
                        "Faltan dependencias de embeddings.",
                        hint="Instala apps/Backend/requirements.txt",
                    ) from exc
                log.info("Cargando embeddings %s", self.settings.embeddings_model)
                self._embeddings = HuggingFaceEmbeddings(model_name=self.settings.embeddings_model)
            return self._embeddings

    @property
    def store(self):
        with self._lock:
            if self._store is None:
                path = self.settings.vectorstore_dir
                if not (path / "chroma.sqlite3").exists():
                    raise ServiceUnavailableError(
                        f"No se encontró la base vectorial en {path}.",
                        hint="Genérala con: python pln_model/vectorial_db.py "
                        "(o define VECTORSTORE_DIR con la ruta correcta).",
                    )
                from langchain_chroma import Chroma

                store = Chroma(persist_directory=str(path), embedding_function=self.embeddings)
                if store._collection.count() == 0:
                    raise ServiceUnavailableError(
                        f"La base vectorial en {path} está vacía.",
                        hint="Vuelve a generarla con: python pln_model/vectorial_db.py",
                    )
                self._store = store
            return self._store

    @property
    def bm25(self):
        with self._lock:
            if self._bm25 is None:
                store = self.store
                count = store._collection.count()
                cache = self.settings.cache_dir / f"bm25_{self.settings.vectorstore_dir.name}_{count}.pkl"
                if cache.exists():
                    try:
                        self._bm25 = BM25Index.load(cache)
                    except Exception as exc:
                        log.warning("No se pudo leer la caché BM25 (%s); se reconstruye", exc)
                if self._bm25 is None:
                    log.info("Construyendo índice BM25 sobre %d fragmentos…", count)
                    self._bm25 = BM25Index(self._all_passages(store, count))
                    try:
                        self._bm25.save(cache)
                    except OSError as exc:
                        log.warning("No se pudo guardar la caché BM25: %s", exc)
            return self._bm25

    @property
    def reranker(self):
        with self._lock:
            if self._reranker is None and self.settings.reranker_model and not self._reranker_failed:
                try:
                    from sentence_transformers import CrossEncoder

                    log.info("Cargando reranker %s", self.settings.reranker_model)
                    self._reranker = CrossEncoder(self.settings.reranker_model)
                except Exception as exc:
                    self._reranker_failed = True
                    log.warning("Reranker desactivado (%s)", exc)
            return self._reranker

    @staticmethod
    def _all_passages(store, count, page=5000):
        passages = []
        for offset in range(0, count, page):
            batch = store.get(include=["documents", "metadatas"], limit=page, offset=offset)
            for text, meta in zip(batch["documents"], batch["metadatas"]):
                meta = meta or {}
                passages.append(Passage(text, meta.get("source", ""), meta.get("chunk_id")))
        return passages

    def warmup(self, include_bm25=True):
        self.store
        if include_bm25 and self.settings.retrieval_mode in ("bm25", "hybrid"):
            self.bm25
        self.reranker

    def status(self):
        path = self.settings.vectorstore_dir
        return {
            "vectorstore_dir": str(path),
            "vectorstore_found": (path / "chroma.sqlite3").exists(),
            "embeddings_model": self.settings.embeddings_model,
            "retrieval_mode": self.settings.retrieval_mode,
            "reranker_model": self.settings.reranker_model or None,
            "loaded": {
                "embeddings": self._embeddings is not None,
                "vectorstore": self._store is not None,
                "bm25": self._bm25 is not None,
                "reranker": self._reranker is not None,
            },
        }

    # ---- búsqueda ----------------------------------------------------------

    def embed(self, texts):
        vectors = np.asarray(self.embeddings.embed_documents(list(texts)), dtype=np.float32)
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / np.maximum(norms, 1e-12)

    def dense(self, query, k):
        results = self.store.similarity_search_with_score(query, k=k)
        return [
            Passage(doc.page_content, doc.metadata.get("source", ""), doc.metadata.get("chunk_id"), -float(dist))
            for doc, dist in results
        ]

    def rerank(self, query, passages):
        model = self.reranker
        if model is None or len(passages) < 2:
            return passages
        scores = model.predict([(query, p.text) for p in passages])
        for passage, score in zip(passages, scores):
            passage.score = float(score)
        return sorted(passages, key=lambda p: p.score, reverse=True)

    def search(self, query, k=None, mode=None, rerank=True):
        k = k or self.settings.context_k
        mode = mode or self.settings.retrieval_mode
        if mode not in RETRIEVAL_MODES:
            raise ValueError(f"Modo de recuperación desconocido: {mode}")
        n = max(self.settings.candidates_k, k)

        if mode == "dense":
            candidates = self.dense(query, n)
        elif mode == "bm25":
            candidates = self.bm25.search(query, n)
        else:
            candidates = reciprocal_rank_fusion([self.dense(query, n), self.bm25.search(query, n)], limit=n)

        if rerank:
            candidates = self.rerank(query, candidates)
        return candidates[:k]
