import pytest

from app.errors import InvalidCardError
from app.rag.areas import AREAS_BY_KEY
from app.rag.cards import build_card, cited_passages, support_statement
from app.rag.retrieval import Passage

PASSAGES = [
    Passage("Insulin lowers blood glucose.", "Pathology_Robbins.txt", 7),
    Passage("Metformin is first-line therapy.", "InternalMed_Harrison.txt", 9),
]


def test_qa_card_keeps_only_cited_sources():
    obj = {"title": "T", "question": " What  lowers glucose? ", "answer": "Insulin.", "source_ids": [2]}
    card, cited = build_card(obj, "qa", PASSAGES, area=AREAS_BY_KEY["treatment"], title="Manejo")

    assert card.question == "What lowers glucose?"
    assert card.title == "Manejo"
    assert card.area == "treatment"
    assert cited == [PASSAGES[1]]
    assert card.sources[0].book == "InternalMed Harrison"
    assert card.sources[0].chunk_id == 9
    assert card.sources[0].excerpt == "Metformin is first-line therapy."


@pytest.mark.parametrize("source_ids", [[], [0, 5, "x"], None, "1"])
def test_invalid_citations_fall_back_to_all_passages(source_ids):
    assert cited_passages(source_ids, PASSAGES) == PASSAGES


def test_citations_accept_numeric_strings_and_ignore_duplicates():
    assert cited_passages(["1", 1, True], PASSAGES) == [PASSAGES[0]]


@pytest.mark.parametrize("missing", ["question", "answer"])
def test_qa_card_requires_question_and_answer(missing):
    obj = {"title": "T", "question": "Q?", "answer": "A."}
    obj[missing] = "   "
    with pytest.raises(InvalidCardError):
        build_card(obj, "qa", PASSAGES)


def test_title_comes_from_model_when_not_forced():
    card, _ = build_card({"title": "Insulin", "question": "Q?", "answer": "A."}, "qa", PASSAGES)
    assert card.title == "Insulin"


def test_non_dict_is_rejected():
    with pytest.raises(InvalidCardError):
        build_card(None, "qa", PASSAGES)


def test_cloze_card_hides_term_case_insensitively():
    obj = {"title": "T", "sentence": "Metformin is the First-line drug.", "cloze": "first-line"}
    card, _ = build_card(obj, "cloze", PASSAGES)

    assert card.question == "Metformin is the [...] drug."
    assert card.answer == "First-line"
    assert card.cloze_sentence == "Metformin is the First-line drug."
    assert support_statement(card) == "Metformin is the First-line drug."


@pytest.mark.parametrize(
    "sentence, cloze",
    [("Metformin is first-line.", "insulin"), ("Metformin.", "Metformin.")],
)
def test_invalid_cloze_is_rejected(sentence, cloze):
    with pytest.raises(InvalidCardError):
        build_card({"title": "T", "sentence": sentence, "cloze": cloze}, "cloze", PASSAGES)


def _mcq(**overrides):
    obj = {
        "title": "T",
        "question": "First-line drug?",
        "options": ["Metformin", "Insulin", "Glipizide", "Pioglitazone"],
        "correct_option": 0,
        "explanation": "Lowers hepatic glucose output.",
    }
    obj.update(overrides)
    return obj


def test_mcq_card_answer_is_correct_option():
    card, _ = build_card(_mcq(correct_option=2), "mcq", PASSAGES)
    assert card.answer == "Glipizide"
    assert card.correct_option == 2
    assert support_statement(card) == "Glipizide. Lowers hepatic glucose output."


@pytest.mark.parametrize(
    "overrides",
    [
        {"correct_option": 4},
        {"correct_option": -1},
        {"correct_option": True},
        {"correct_option": None},
        {"options": ["A", "B", "C"]},
        {"options": ["A", "B", "C", "a"]},
        {"options": ["A", "B", "C", ""]},
    ],
)
def test_invalid_mcq_is_rejected(overrides):
    with pytest.raises(InvalidCardError):
        build_card(_mcq(**overrides), "mcq", PASSAGES)
