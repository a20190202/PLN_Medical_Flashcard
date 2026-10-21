"""Exportación de flashcards a un mazo de Anki (.apkg)."""

import hashlib
import html
import os
import tempfile

import genanki

# IDs fijos: Anki reconoce el mismo tipo de nota y el mismo mazo entre exportaciones.
MODEL_ID = 1607392319

_CSS = """
.card { font-family: Arial, sans-serif; font-size: 18px; text-align: left; color: #1f2933; background: #fff; }
.area { font-size: 12px; text-transform: uppercase; letter-spacing: .05em; color: #7b8794; margin-bottom: 8px; }
.sources { font-size: 12px; color: #7b8794; margin-top: 16px; }
"""

MODEL = genanki.Model(
    MODEL_ID,
    "MedCards",
    fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Area"}, {"name": "Sources"}],
    templates=[
        {
            "name": "Card 1",
            "qfmt": "<div class='area'>{{Area}}</div>{{Front}}",
            "afmt": "{{FrontSide}}<hr id=answer>{{Back}}<div class='sources'>{{Sources}}</div>",
        }
    ],
    css=_CSS,
)

_LETTERS = "ABCD"


def deck_id(name):
    return int(hashlib.sha1(name.encode("utf-8")).hexdigest()[:8], 16)


def card_fields(card):
    """(frente, reverso) en HTML para cada tipo de tarjeta."""
    e = html.escape
    if card.card_type == "mcq" and card.options:
        options = "".join(f"<li>{e(o)}</li>" for o in card.options)
        front = f"{e(card.question)}<ol type='A'>{options}</ol>"
        back = f"<b>{_LETTERS[card.correct_option]}. {e(card.answer)}</b>"
        if card.explanation:
            back += f"<br>{e(card.explanation)}"
        return front, back
    if card.card_type == "cloze" and card.cloze_sentence and card.cloze:
        sentence, cloze = e(card.cloze_sentence), e(card.cloze)
        return e(card.question), sentence.replace(cloze, f"<b>{cloze}</b>", 1)
    return e(card.question), e(card.answer)


def build_apkg(deck_name, cards):
    deck = genanki.Deck(deck_id(deck_name), deck_name)
    for card in cards:
        front, back = card_fields(card)
        books = list(dict.fromkeys(s.book for s in card.sources))
        sources = "Fuentes: " + "; ".join(html.escape(b) for b in books) if books else ""
        deck.add_note(
            genanki.Note(
                model=MODEL,
                fields=[front, back, html.escape(card.title), sources],
                guid=genanki.guid_for(card.id),
            )
        )
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "deck.apkg")
        genanki.Package(deck).write_to_file(path)
        with open(path, "rb") as f:
            return f.read()
