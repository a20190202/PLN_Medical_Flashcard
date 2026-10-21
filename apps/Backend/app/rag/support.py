"""Verificación de que la respuesta de una tarjeta está respaldada por los fragmentos.

Cada oración de la respuesta se compara (similitud coseno de embeddings) con
todas las oraciones de los fragmentos citados y se queda con la más parecida.
El puntaje de la tarjeta es el de su oración menos respaldada: basta una
afirmación sin respaldo para marcar la tarjeta. Es una heurística para señalar
posibles alucinaciones, no una verificación médica.
"""

import numpy as np

from ..schemas import Support
from .text import split_sentences


class SupportChecker:
    def __init__(self, embed, threshold, max_context_sentences=300):
        """`embed(textos)` debe devolver vectores normalizados (norma 1)."""
        self.embed = embed
        self.threshold = threshold
        self.max_context_sentences = max_context_sentences

    def check(self, statement, passages):
        claims = split_sentences(statement or "")
        context = [s for p in passages for s in split_sentences(p.text)]
        context = context[: self.max_context_sentences]
        if not claims or not context:
            return None
        vectors = np.asarray(self.embed(claims + context), dtype=np.float32)
        similarities = vectors[: len(claims)] @ vectors[len(claims) :].T
        score = float(similarities.max(axis=1).min())
        return Support(score=round(score, 3), supported=score >= self.threshold)
