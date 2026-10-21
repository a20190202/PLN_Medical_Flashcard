import pytest

from app.errors import GenerationError, InvalidRequestError, ServiceUnavailableError
from app.rag.areas import AREAS
from app.rag.generator import PASSAGE_NUM_CTX, FlashcardGenerator, areas_for
from app.schemas import GenerateRequest, RegenerateRequest
from helpers import FakeLLM, FakeSupport, smart_responder

VALID_QA = {"title": "x", "question": "What is insulin?", "answer": "A hormone.", "source_ids": [1]}


def _generator(settings, retriever, llm, support=None):
    return FlashcardGenerator(settings, retriever, llm, support)


def test_topic_mode_retrieves_once_per_area(generator, retriever, llm):
    result = generator.generate(GenerateRequest(texto="Diabetes"))

    assert retriever.queries == [area.query("Diabetes") for area in AREAS]
    assert [c.area for c in result.flashcards] == [a.key for a in AREAS]
    assert [c.title for c in result.flashcards] == [a.title_en for a in AREAS]
    assert result.query_topic == "Diabetes"
    assert result.warnings == []
    # Cada tarjeta trae su fuente (pasaje 1 de su propia búsqueda) y su verificación.
    first = result.flashcards[0]
    assert first.sources[0].book == "Pathology Robbins"
    assert "definition" in first.sources[0].excerpt
    assert first.support.supported
    # El prompt de cada tarjeta incluye los fragmentos numerados.
    assert "[1] (Pathology Robbins)" in llm.calls[0]["prompt"]


def test_fewer_cards_use_the_first_areas(generator):
    result = generator.generate(GenerateRequest(texto="Asthma", num_cards=3))
    assert [c.area for c in result.flashcards] == ["definition", "etiology", "clinical"]


def test_more_than_five_cards_repeat_areas_without_repeating_questions(generator, llm):
    result = generator.generate(GenerateRequest(texto="Asthma", num_cards=7))

    assert [a.key for a in areas_for(7)] == [c.area for c in result.flashcards]
    sixth_prompt = llm.calls[5]["prompt"]
    assert "Do not repeat these existing questions" in sixth_prompt
    assert result.flashcards[0].question in sixth_prompt


def test_spanish_topic_is_translated_for_retrieval(generator, retriever, llm):
    result = generator.generate(GenerateRequest(texto="Diabetes", language="es", num_cards=2))

    assert "english_term" in llm.calls[0]["schema"]["properties"]
    assert retriever.queries[0] == AREAS[0].query("Diabetes mellitus")
    assert result.query_topic == "Diabetes mellitus"
    assert result.flashcards[0].title == "Definición y fisiopatología"
    assert "Spanish" in llm.calls[1]["system"]
    assert "Diabetes (Diabetes mellitus)" in llm.calls[1]["prompt"]


def test_non_ascii_topic_is_translated_even_in_english(generator, llm):
    generator.generate(GenerateRequest(texto="Hipotiroidismo congénito ñ", num_cards=1))
    assert "english_term" in llm.calls[0]["schema"]["properties"]


def test_bad_translation_falls_back_to_original_topic(settings, retriever):
    llm = FakeLLM(smart_responder, responses=[{"english_term": ""}])
    result = _generator(settings, retriever, llm).generate(
        GenerateRequest(texto="Asma", language="es", num_cards=1)
    )
    assert result.query_topic == "Asma"


def test_invalid_answer_is_retried(settings, retriever):
    llm = FakeLLM(smart_responder, responses=[{"title": "x", "question": "", "answer": ""}, VALID_QA])
    result = _generator(settings, retriever, llm).generate(GenerateRequest(texto="Diabetes", num_cards=1))

    assert len(llm.calls) == 2
    assert result.flashcards[0].question == "What is insulin?"


def test_area_that_always_fails_becomes_a_warning(settings, retriever):
    bad = {"title": "x"}
    llm = FakeLLM(smart_responder, responses=[bad, bad])
    result = _generator(settings, retriever, llm).generate(GenerateRequest(texto="Diabetes", num_cards=3))

    assert [c.area for c in result.flashcards] == ["etiology", "clinical"]
    assert len(result.warnings) == 1
    assert "Definition & Pathophysiology" in result.warnings[0]


def test_no_valid_cards_raises_generation_error(settings, retriever):
    llm = FakeLLM(lambda prompt, schema: {"nothing": True})
    with pytest.raises(GenerationError):
        _generator(settings, retriever, llm).generate(GenerateRequest(texto="Diabetes", num_cards=2))


def test_no_passages_found_skips_the_llm(settings):
    from helpers import FakeRetriever

    llm = FakeLLM(smart_responder)
    with pytest.raises(GenerationError):
        _generator(settings, FakeRetriever(passages=[]), llm).generate(GenerateRequest(texto="Xyz", num_cards=1))
    assert llm.calls == []


def test_ollama_down_aborts_the_request(settings, retriever):
    llm = FakeLLM(responses=[ServiceUnavailableError("Ollama caído")])
    with pytest.raises(ServiceUnavailableError):
        _generator(settings, retriever, llm).generate(GenerateRequest(texto="Diabetes"))
    assert len(llm.calls) == 1


def test_plain_text_answer_is_parsed_as_legacy_format(settings, retriever):
    text = "Flashcard 1: Definition\nQ: What is diabetes?\nA: A metabolic disease."
    llm = FakeLLM(responses=[text])
    result = _generator(settings, retriever, llm).generate(GenerateRequest(texto="Diabetes", num_cards=1))
    assert result.flashcards[0].answer == "A metabolic disease."


@pytest.mark.parametrize("card_type", ["cloze", "mcq"])
def test_other_card_types(generator, llm, card_type):
    result = generator.generate(GenerateRequest(texto="Diabetes", card_type=card_type, num_cards=2))

    assert all(c.card_type == card_type for c in result.flashcards)
    assert set(llm.calls[0]["schema"]["properties"]) >= {"source_ids"}
    if card_type == "mcq":
        assert result.flashcards[0].answer == "Metformin"
    else:
        assert "[...]" in result.flashcards[0].question


def test_passage_mode_uses_the_notes_not_the_books(generator, retriever, llm):
    notes = "Asthma is chronic airway inflammation. " * 20
    result = generator.generate(GenerateRequest(texto=notes, mode="passage", num_cards=4))

    assert retriever.queries == []
    assert len(result.flashcards) == 4
    assert result.query_topic is None
    assert llm.calls[0]["num_ctx"] >= PASSAGE_NUM_CTX
    assert llm.calls[0]["schema"]["properties"]["flashcards"]["minItems"] == 4
    assert {s.book for c in result.flashcards for s in c.sources} == {"Student notes"}
    assert all(c.area is None for c in result.flashcards)


def test_passage_mode_drops_invalid_and_repeated_cards(settings, retriever):
    deck = {
        "flashcards": [
            VALID_QA,
            {**VALID_QA, "question": "what is INSULIN?"},
            {"title": "x", "question": "Q2?"},
            {**VALID_QA, "question": "Where is insulin made?"},
        ]
    }
    llm = FakeLLM(responses=[deck])
    result = _generator(settings, retriever, llm).generate(
        GenerateRequest(texto="notes", mode="passage", num_cards=4)
    )
    assert [c.question for c in result.flashcards] == ["What is insulin?", "Where is insulin made?"]
    assert len(result.warnings) == 2


def test_regenerate_topic_card_avoids_existing_questions(generator, retriever, llm):
    req = RegenerateRequest(texto="Diabetes", area="diagnosis", avoid_questions=["How is diabetes diagnosed?"])
    result = generator.regenerate(req)

    assert len(result.flashcards) == 1
    assert result.flashcards[0].area == "diagnosis"
    assert retriever.queries == [AREAS[3].query("Diabetes")]
    assert "How is diabetes diagnosed?" in llm.calls[0]["prompt"]


def test_regenerate_rejects_repeated_question(settings, retriever):
    llm = FakeLLM(responses=[VALID_QA, VALID_QA])
    req = RegenerateRequest(texto="Diabetes", area="definition", avoid_questions=["What is insulin?"])
    with pytest.raises(GenerationError):
        _generator(settings, retriever, llm).regenerate(req)


def test_regenerate_unknown_area(generator):
    with pytest.raises(InvalidRequestError):
        generator.regenerate(RegenerateRequest(texto="Diabetes", area="prevention"))


def test_regenerate_passage_card(generator):
    result = generator.regenerate(RegenerateRequest(texto="Some notes.", mode="passage"))
    assert len(result.flashcards) == 1


def test_support_failure_does_not_break_generation(settings, retriever, llm):
    gen = _generator(settings, retriever, llm, FakeSupport(error=RuntimeError("no embeddings")))
    result = gen.generate(GenerateRequest(texto="Diabetes", num_cards=1))
    assert result.flashcards[0].support is None


def test_support_receives_answer_and_cited_passages(settings, retriever, llm):
    support = FakeSupport(score=0.3)
    result = _generator(settings, retriever, llm, support).generate(GenerateRequest(texto="Diabetes", num_cards=1))

    statement, passages = support.calls[0]
    assert statement == result.flashcards[0].answer
    assert len(passages) == 1  # el modelo citó solo el pasaje 1
    assert result.flashcards[0].support.supported is False
