import pytest

from app.errors import ServiceUnavailableError
from app.rag.retrieval import BM25Index, Passage, Retriever, reciprocal_rank_fusion
from app.rag.text import book_name, excerpt, split_sentences, tokenize

DOCS = [
    Passage("Diabetes mellitus causes hyperglycemia due to insulin deficiency.", "a.txt", 0),
    Passage("Asthma presents with wheezing and bronchospasm.", "b.txt", 1),
    Passage("Type 2 diabetes is treated first with metformin.", "c.txt", 2),
]


def test_bm25_ranks_matching_documents():
    index = BM25Index(DOCS)
    results = index.search("diabetes metformin treatment", k=2)
    assert [p.source for p in results] == ["c.txt", "a.txt"]
    assert results[0].score > results[1].score > 0


def test_bm25_unknown_terms_return_nothing():
    assert BM25Index(DOCS).search("zzz qqq", k=3) == []


def test_bm25_rejects_empty_corpus():
    with pytest.raises(ValueError):
        BM25Index([])


def test_bm25_save_and_load(tmp_path):
    path = tmp_path / "bm25.pkl"
    BM25Index(DOCS).save(path)
    assert BM25Index.load(path).search("asthma", 1)[0].source == "b.txt"


def test_reciprocal_rank_fusion_merges_duplicates():
    a, b, c = DOCS
    fused = reciprocal_rank_fusion([[a, b], [b, c]], k=60)
    assert [p.source for p in fused] == ["b.txt", "a.txt", "c.txt"]
    assert len(reciprocal_rank_fusion([[a, b], [b, c]], limit=1)) == 1


def _retriever(settings, monkeypatch, dense, bm25):
    retriever = Retriever(settings)
    monkeypatch.setattr(retriever, "dense", lambda q, k: dense[:k])

    class _BM25:
        def search(self, q, k):
            return bm25[:k]

    retriever._bm25 = _BM25()
    return retriever


def test_search_modes(settings, monkeypatch):
    a, b, c = DOCS
    retriever = _retriever(settings, monkeypatch, dense=[a, b], bm25=[c, b])

    assert retriever.search("q", k=1, mode="dense") == [a]
    assert retriever.search("q", k=1, mode="bm25") == [c]
    assert retriever.search("q", k=1, mode="hybrid")[0].source == "b.txt"


def test_unknown_mode_is_rejected(settings, monkeypatch):
    retriever = _retriever(settings, monkeypatch, dense=[], bm25=[])
    with pytest.raises(ValueError):
        retriever.search("q", mode="magic")


def test_missing_vectorstore_reports_how_to_create_it(settings):
    with pytest.raises(ServiceUnavailableError) as exc:
        Retriever(settings).store
    assert "vectorial_db.py" in exc.value.hint
    assert Retriever(settings).status()["vectorstore_found"] is False


def test_text_helpers():
    assert tokenize("The HbA1c is NOT normal") == ["hba1c", "not", "normal"]
    assert split_sentences("Insulin lowers glucose. Ok. Metformin is first-line.") == [
        "Insulin lowers glucose. Ok.",
        "Metformin is first-line.",
    ]
    assert excerpt("word " * 100, limit=20).endswith("…")
    assert book_name("Pathology_Robbins.txt") == "Pathology Robbins"
