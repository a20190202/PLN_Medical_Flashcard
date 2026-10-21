"""Utilidades de texto sin dependencias pesadas."""

import re

_TOKEN_RE = re.compile(r"[a-z0-9]+(?:[-'][a-z0-9]+)*")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9(\"'])")

# Lista corta a propósito: en BM25 las palabras vacías solo agregan ruido, pero
# no queremos perder negaciones ni términos clínicos.
STOPWORDS = frozenset(
    """a an and are as at be been being by for from has have had he her his i in into
    is it its of on or our she so than that the their them then there these they this
    those to was we were what which who whom why will with you your""".split()
)


def tokenize(text):
    """Tokens en minúsculas para BM25 (sin palabras vacías)."""
    return [t for t in _TOKEN_RE.findall(text.lower()) if t not in STOPWORDS]


def split_sentences(text, min_chars=20):
    """División en oraciones suficiente para textos médicos en inglés o español."""
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []
    sentences = [s.strip() for s in _SENTENCE_RE.split(text)]
    merged = []
    for sentence in sentences:
        if merged and len(sentence) < min_chars:
            merged[-1] = f"{merged[-1]} {sentence}"
        else:
            merged.append(sentence)
    return merged


def excerpt(text, limit=280):
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return f"{cut}…"


def book_name(source):
    """'Pathology_Robbins.txt' -> 'Pathology Robbins'."""
    name = re.sub(r"\.txt$", "", source or "", flags=re.I)
    return name.replace("_", " ").strip() or "Desconocido"
