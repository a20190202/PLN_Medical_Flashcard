"""Genera la base vectorial (Chroma) con los libros de MedQA en data/textbooks.

Uso, desde la raíz del repositorio:
    python pln_model/vectorial_db.py
    python pln_model/vectorial_db.py --embeddings pritamdeka/S-Biomed-Roberta-snli-multinli-stsb

Por defecto guarda la base donde la busca el backend:
    apps/Backend/app/model/data/<embedding con "/" reemplazado por "_">
"""

import argparse
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
DEFAULT_EMBEDDINGS = "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"


def default_output(embeddings):
    return REPO / "apps" / "Backend" / "app" / "model" / "data" / embeddings.replace("/", "_")


def load_documents(folder, chunk_size=1000, chunk_overlap=100):
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len
    )
    documents = []
    for path in sorted(Path(folder).glob("*.txt")):
        chunks = splitter.split_text(path.read_text(encoding="utf-8"))
        for i, chunk in enumerate(chunks):
            documents.append(
                Document(
                    page_content=chunk,
                    metadata={"source": path.name, "chunk_id": i, "total_chunks": len(chunks)},
                )
            )
    return documents


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--embeddings", default=DEFAULT_EMBEDDINGS, help="Modelo de HuggingFace")
    parser.add_argument("--textbooks", type=Path, default=HERE / "data" / "textbooks")
    parser.add_argument("--out", type=Path, default=None, help="Carpeta de salida")
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-overlap", type=int, default=100)
    parser.add_argument("--force", action="store_true", help="Borra la base existente y la vuelve a crear")
    args = parser.parse_args(argv)

    out = args.out or default_output(args.embeddings)
    if (out / "chroma.sqlite3").exists():
        if not args.force:
            print(f"Ya existe una base en {out}. Usa --force para regenerarla.", file=sys.stderr)
            return 1
        shutil.rmtree(out)

    documents = load_documents(args.textbooks, args.chunk_size, args.chunk_overlap)
    if not documents:
        print(f"No se encontraron archivos .txt en {args.textbooks}", file=sys.stderr)
        return 1
    print(f"{len(documents)} fragmentos de {args.textbooks}. Calculando embeddings con {args.embeddings}…")

    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings

    out.mkdir(parents=True, exist_ok=True)
    Chroma.from_documents(
        documents=documents,
        embedding=HuggingFaceEmbeddings(model_name=args.embeddings),
        persist_directory=str(out),
    )
    print(f"Base vectorial guardada en {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
