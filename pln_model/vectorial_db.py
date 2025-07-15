from importlib import metadata
import os
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

import os
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


def read_txt_files(folder_path):
    all_docs = []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
    )

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            chunks = splitter.split_text(text)

            for i, chunk in enumerate(chunks):
                doc = Document(
                    page_content=chunk,
                    metadata={
                        "source": filename,
                        "chunk_id": i,
                        "total_chunks": len(chunks),
                    },
                )
                all_docs.append(doc)

    return all_docs


all_documents = read_txt_files("data/textbooks")


# %%
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from tqdm import tqdm

# embeddings = ['all-MiniLM-L6-v2', "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb", "pritamdeka/S-Biomed-Roberta-snli-multinli-stsb"]
embeddings = ["pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"]


for embedding in tqdm(embeddings):

    embeddings_model_1 = HuggingFaceEmbeddings(
        model_name=embedding,  # 384 dimensiones
    )

    # Crear vectorstores (ejecutar solo una vez)
    vectorstore_1 = Chroma.from_documents(
        documents=all_documents,
        embedding=embeddings_model_1,
        persist_directory=f"./{embedding.replace('/','_')}",
    )
