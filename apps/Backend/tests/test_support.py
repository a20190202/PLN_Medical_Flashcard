import pytest

from app.rag.retrieval import Passage
from app.rag.support import SupportChecker
from helpers import bag_of_words_embed

CONTEXT = [
    Passage(
        "Metformin is the first-line drug for type 2 diabetes. It reduces hepatic glucose production.",
        "InternalMed_Harrison.txt",
        1,
    )
]


def test_statement_copied_from_context_is_supported():
    checker = SupportChecker(bag_of_words_embed, threshold=0.6)
    support = checker.check("Metformin is the first-line drug for type 2 diabetes.", CONTEXT)
    assert support.score == pytest.approx(1.0)
    assert support.supported


def test_one_unsupported_sentence_marks_the_card():
    checker = SupportChecker(bag_of_words_embed, threshold=0.6)
    statement = (
        "Metformin is the first-line drug for type 2 diabetes. "
        "Surgical gastrectomy cures all patients within weeks."
    )
    support = checker.check(statement, CONTEXT)
    assert support.score < 0.6
    assert not support.supported


@pytest.mark.parametrize("statement, passages", [("", CONTEXT), ("Some claim here.", [])])
def test_nothing_to_compare_returns_none(statement, passages):
    assert SupportChecker(bag_of_words_embed, 0.6).check(statement, passages) is None
