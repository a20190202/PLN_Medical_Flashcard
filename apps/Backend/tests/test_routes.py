import io
import sqlite3
import zipfile

from app import create_app
from app.errors import ServiceUnavailableError
from app.rag.generator import FlashcardGenerator
from helpers import FakeLLM, FakeRetriever


def test_generate(client):
    response = client.post("/generar_preguntas", json={"texto": "Diabetes"})

    assert response.status_code == 200
    body = response.get_json()
    assert len(body["flashcards"]) == 5
    card = body["flashcards"][0]
    # Campos que usa el frontend actual, más los nuevos.
    assert {"title", "question", "answer", "sources", "support", "area", "id"} <= set(card)
    assert body["model"] == "fake-model"
    assert body["mode"] == "topic"
    assert body["warnings"] == []


def test_generate_validation_errors(client):
    empty = client.post("/generar_preguntas", json={"texto": "   "})
    assert empty.status_code == 400
    assert empty.get_json()["details"][0]["field"] == "texto"

    too_long = client.post("/generar_preguntas", json={"texto": "x" * 201})
    assert too_long.status_code == 400
    assert "passage" in too_long.get_json()["error"]

    assert client.post("/generar_preguntas", json={"texto": "Asma", "num_cards": 11}).status_code == 400
    assert client.post("/generar_preguntas", json={"texto": "Asma", "card_type": "essay"}).status_code == 400


def test_body_must_be_json(client):
    response = client.post("/generar_preguntas", data="texto=Asma")
    assert response.status_code == 400
    assert response.get_json()["code"] == "invalid_request"


def _client_with(settings, llm):
    app = create_app(settings, generator=FlashcardGenerator(settings, FakeRetriever(), llm))
    return app.test_client()


def test_ollama_unavailable_is_503_with_hint(settings):
    llm = FakeLLM(responses=[ServiceUnavailableError("Sin Ollama", hint="ollama serve")])
    response = _client_with(settings, llm).post("/generar_preguntas", json={"texto": "Asma"})

    assert response.status_code == 503
    assert response.get_json() == {"error": "Sin Ollama", "code": "service_unavailable", "hint": "ollama serve"}


def test_no_valid_cards_is_422(settings):
    llm = FakeLLM(lambda prompt, schema: {})
    response = _client_with(settings, llm).post("/generar_preguntas", json={"texto": "Asma", "num_cards": 1})
    assert response.status_code == 422
    assert response.get_json()["code"] == "generation_failed"


def test_unexpected_error_is_500_without_details(settings):
    llm = FakeLLM(responses=[RuntimeError("secret stack trace")])
    response = _client_with(settings, llm).post("/generar_preguntas", json={"texto": "Asma"})
    assert response.status_code == 500
    assert "secret" not in response.get_data(as_text=True)


def test_regenerate(client):
    response = client.post(
        "/regenerar_pregunta",
        json={"texto": "Diabetes", "area": "treatment", "avoid_questions": ["Old question?"]},
    )
    assert response.status_code == 200
    assert [c["area"] for c in response.get_json()["flashcards"]] == ["treatment"]


def test_export_anki(client):
    cards = client.post("/generar_preguntas", json={"texto": "Diabetes", "num_cards": 2}).get_json()["flashcards"]
    response = client.post("/exportar_anki", json={"deck_name": "Diabetes / USMLE", "cards": cards})

    assert response.status_code == 200
    assert response.mimetype == "application/apkg"
    assert "Diabetes_USMLE.apkg" in response.headers["Content-Disposition"]
    with zipfile.ZipFile(io.BytesIO(response.data)) as apkg:
        assert "collection.anki2" in apkg.namelist()


def test_export_requires_cards(client):
    assert client.post("/exportar_anki", json={"cards": []}).status_code == 400


def test_health_and_areas(client):
    health = client.get("/health")
    assert health.status_code == 200
    assert health.get_json()["status"] == "ok"

    areas = client.get("/areas").get_json()
    assert [a["key"] for a in areas] == ["definition", "etiology", "clinical", "diagnosis", "treatment"]


def test_unknown_route_returns_json(client):
    response = client.get("/nope")
    assert response.status_code == 404
    assert response.get_json()["code"] == "not_found"


def test_cors_allows_frontend_origin(client):
    response = client.post(
        "/generar_preguntas", json={"texto": "Asma", "num_cards": 1}, headers={"Origin": "http://localhost:3000"}
    )
    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:3000"

    other = client.get("/areas", headers={"Origin": "http://evil.example"})
    assert "Access-Control-Allow-Origin" not in other.headers


def test_exported_notes_by_card_type(tmp_path):
    from app.export import build_apkg
    from app.schemas import Flashcard

    cards = [
        Flashcard(title="QA", question="Q <b>?", answer="A"),
        Flashcard(card_type="cloze", title="C", question="X is [...].", answer="Y", cloze_sentence="X is Y.", cloze="Y"),
        Flashcard(
            card_type="mcq", title="M", question="Pick", answer="Two",
            options=["One", "Two", "Three", "Four"], correct_option=1, explanation="Because.",
        ),
    ]
    with zipfile.ZipFile(io.BytesIO(build_apkg("Deck", cards))) as apkg:
        apkg.extract("collection.anki2", tmp_path)
    con = sqlite3.connect(tmp_path / "collection.anki2")
    fields = [row[0].split("\x1f") for row in con.execute("select flds from notes order by id")]
    con.close()

    assert len(fields) == 3
    assert fields[0][0] == "Q &lt;b&gt;?"  # el HTML del modelo se escapa
    assert fields[1][1] == "X is <b>Y</b>."
    assert "<li>Three</li>" in fields[2][0]
    assert fields[2][1].startswith("<b>B. Two</b>")
