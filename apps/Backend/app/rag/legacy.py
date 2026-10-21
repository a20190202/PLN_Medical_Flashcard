"""Lectura del formato de texto de los notebooks ("Flashcard N: ... / Q: ... / A: ...").

Se usa solo como respaldo cuando el modelo ignora el JSON Schema. Acepta las
variantes que aparecen en las salidas de Llama 2 y Phi: "Flashcard 1:" o
"Flashcard 1 -", negritas de Markdown y respuestas de varias líneas.
"""

import re

_HEADER_RE = re.compile(r"^flashcard\s+(\d+)\s*[:\-–—.)]?\s*(.*)$", re.IGNORECASE)
_FIELD_RE = re.compile(r"^(q|question|a|answer)\s*[:.]\s*(.*)$", re.IGNORECASE)


def _clean_title(title, number):
    title = title.strip().strip("[]").strip().rstrip(":").strip()
    return title or f"Flashcard {number}"


def parse_legacy_text(text):
    """Devuelve una lista de dicts {title, question, answer} con las tarjetas completas."""
    cards, current, field = [], None, None
    for line in (text or "").splitlines():
        line = line.replace("**", "").strip().lstrip("#").strip()
        header = _HEADER_RE.match(line)
        if header:
            current = {"title": _clean_title(header.group(2), header.group(1)), "question": [], "answer": []}
            cards.append(current)
            field = None
            continue
        if current is None:
            continue
        labeled = _FIELD_RE.match(line)
        if labeled:
            field = "question" if labeled.group(1).lower().startswith("q") else "answer"
            line = labeled.group(2).strip()
        if field and line:
            current[field].append(line)

    result = []
    for card in cards:
        question = " ".join(card["question"]).strip()
        answer = " ".join(card["answer"]).strip()
        if question and answer:
            result.append({"title": card["title"], "question": question, "answer": answer})
    return result
