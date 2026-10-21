import json
from pathlib import Path

import pytest

from app.rag.legacy import parse_legacy_text

FIXTURE = Path(__file__).parent / "fixtures" / "notebook_llm_outputs.json"
OUTPUTS = json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.mark.parametrize("item", OUTPUTS, ids=lambda x: f"{x['notebook']}-{x['topic']}")
def test_parses_every_notebook_output(item):
    cards = parse_legacy_text(item["output"])

    assert len(cards) >= 4
    for card in cards:
        assert card["title"] and card["question"] and card["answer"]
        assert "Flashcard" not in card["answer"]


def test_dash_header_used_by_phi():
    text = "Flashcard 1 - Definition\nQ: What is it?\nA: A disease.\n\nFlashcard 2 - Etiology\nQ: Cause?\nA: Genes."
    cards = parse_legacy_text(text)
    assert [c["title"] for c in cards] == ["Definition", "Etiology"]
    assert cards[1]["answer"] == "Genes."


def test_markdown_bold_and_multiline_answers():
    text = "**Flashcard 1: [Diagnosis]**\n**Q:** Which test?\n**A:** HbA1c.\nIt is >= 6.5%."
    assert parse_legacy_text(text) == [
        {"title": "Diagnosis", "question": "Which test?", "answer": "HbA1c. It is >= 6.5%."}
    ]


def test_incomplete_cards_are_dropped():
    text = "Flashcard 1: X\nQ: Question?\nA: Answer.\nFlashcard 2: Y\nQ: Cut off before the answer"
    assert len(parse_legacy_text(text)) == 1


@pytest.mark.parametrize("text", ["", None, "Just some prose without cards."])
def test_no_cards(text):
    assert parse_legacy_text(text) == []
