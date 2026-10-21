"""Dobles de prueba: reemplazan a Ollama, la base vectorial y los embeddings."""

import json
import re

from app.rag.llm import parse_json_lenient
from app.rag.retrieval import Passage
from app.schemas import Support


class FakeLLM:
    """Responde con `responder(prompt, schema)` o con una lista de respuestas en orden.

    Una respuesta puede ser un dict (se devuelve como JSON), un str (texto crudo)
    o una excepción (se lanza).
    """

    def __init__(self, responder=None, responses=None):
        self.responder = responder
        self.responses = list(responses or [])
        self.calls = []
        self.model = "fake-model"

    def generate_json(self, prompt, schema, system=None, num_ctx=None):
        self.calls.append({"prompt": prompt, "schema": schema, "system": system, "num_ctx": num_ctx})
        response = self.responses.pop(0) if self.responses else self.responder(prompt, schema)
        if isinstance(response, Exception):
            raise response
        if isinstance(response, str):
            return parse_json_lenient(response), response
        return response, json.dumps(response)

    def health(self):
        return {"reachable": True, "model_available": True, "model": self.model}


def _card_for(schema, n):
    props = schema["properties"]
    source_ids = [1]
    if "sentence" in props:
        return {
            "title": "Key fact",
            "sentence": f"Insulin deficiency causes hyperglycemia number {n}.",
            "cloze": "hyperglycemia",
            "source_ids": source_ids,
        }
    if "options" in props:
        return {
            "title": "Treatment",
            "question": f"First-line drug for type 2 diabetes? ({n})",
            "options": ["Metformin", "Insulin glargine", "Glipizide", "Pioglitazone"],
            "correct_option": 0,
            "explanation": "Metformin lowers hepatic glucose output.",
            "source_ids": source_ids,
        }
    return {
        "title": "Ignored title",
        "question": f"Question number {n}?",
        "answer": f"Insulin lowers blood glucose. Detail {n}.",
        "source_ids": source_ids,
    }


def smart_responder(prompt, schema):
    """Respuesta válida según el schema pedido; cada pregunta es distinta."""
    smart_responder.counter += 1
    n = smart_responder.counter
    props = schema["properties"]
    if "english_term" in props:
        return {"english_term": "Diabetes mellitus"}
    if "flashcards" in props:
        count = props["flashcards"]["minItems"]
        return {"flashcards": [_card_for(props["flashcards"]["items"], f"{n}.{i}") for i in range(count)]}
    return _card_for(schema, n)


smart_responder.counter = 0


class FakeRetriever:
    def __init__(self, passages=None):
        self.queries = []
        self.passages = passages

    def search(self, query, k=None, mode=None, rerank=True):
        self.queries.append(query)
        if self.passages is not None:
            return list(self.passages)
        i = len(self.queries)
        return [
            Passage(f"Fragment about {query}. Insulin lowers blood glucose.", "Pathology_Robbins.txt", i),
            Passage("Metformin is first-line therapy.", "InternalMed_Harrison.txt", 100 + i),
        ]

    def status(self):
        return {"vectorstore_found": True, "retrieval_mode": "hybrid"}


class FakeSupport:
    def __init__(self, score=0.9, threshold=0.6, error=None):
        self.score = score
        self.threshold = threshold
        self.error = error
        self.calls = []

    def check(self, statement, passages):
        self.calls.append((statement, passages))
        if self.error:
            raise self.error
        return Support(score=self.score, supported=self.score >= self.threshold)


def bag_of_words_embed(texts):
    """Embedding de juguete: bolsa de palabras normalizada (para probar SupportChecker)."""
    import numpy as np

    tokens = [re.findall(r"[a-z]+", t.lower()) for t in texts]
    vocab = sorted({w for ts in tokens for w in ts})
    index = {w: i for i, w in enumerate(vocab)}
    vectors = np.zeros((len(texts), max(len(vocab), 1)), dtype=np.float32)
    for row, ts in enumerate(tokens):
        for w in ts:
            vectors[row, index[w]] += 1
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / np.maximum(norms, 1e-12)
