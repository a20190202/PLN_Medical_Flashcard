# Import Windows fix FIRST - before any other imports
from .windows_fix import setup_windows_chromadb

from transformers import pipeline, T5Tokenizer, T5ForConditionalGeneration
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import json
import re
import os

EMBEDDINGS = "pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb"

template = """
Medical Flashcard Generator Prompt

You will receive the name of a medical condition or disease. Your task is to create 5 comprehensive flashcards that systematically cover the essential aspects of the condition for medical education purposes.

Required Coverage Areas:
1. Definition & Pathophysiology - Core concept and underlying mechanisms
2. Etiology & Risk Factors - Causes and predisposing factors
3. Clinical Presentation - Signs, symptoms, and clinical manifestations
4. Diagnostic Approach - Key tests, criteria, and differential considerations
5. Management & Treatment - Therapeutic interventions and prognosis

Flashcard Requirements:
- Each flashcard must contain one focused question and one comprehensive answer
- Questions should be clinically relevant and test practical knowledge
- Answers should be precise, direct, and medically accurate
- Provide specific details (lab values, medication dosages, timeframes where applicable)
- Use medical terminology appropriately while maintaining clarity
- Give concise, focused responses without bullet points or lists
- Prioritize high-yield information commonly tested in medical examinations

Context Considerations:
{context}

Output Format:
Flashcard 1: [Topic Area]
Q: [Specific, focused question]
A: [Precise, direct answer in paragraph form]

Flashcard 2: [Topic Area]
Q: [Specific, focused question]
A: [Precise, direct answer in paragraph form]

[Continue for all 5 flashcards]

Quality Standards:
- Ensure medical accuracy and evidence-based content
- Use current clinical guidelines and best practices
- Include relevant mnemonics or memory aids where helpful
- Maintain consistency in terminology and formatting
- Focus on clinically actionable information

Medical Condition: {input}
"""


def parse_flashcards_to_json(text):
    """
    Parse flashcard text format and convert to JSON structure
    """
    try:
        flashcards = []

        # Updated regex pattern to match the actual format
        flashcard_pattern = r"Flashcard (\d+): ([^\n]+)\n+Q: ([^\n]+)\nA: ((?:(?!(?:\n+)?Flashcard \d+:)[\s\S])*?)(?=\n+Flashcard \d+:|$)"

        matches = re.findall(flashcard_pattern, text, re.DOTALL)

        if not matches:
            print("Warning: No flashcards found in the text")
            return {"flashcards": []}

        for match in matches:
            try:
                flashcard_id = int(match[0])
                title = match[1].strip()
                question = match[2].strip()
                answer = match[3].strip()

                # Validate that we have all required fields
                if not title or not question or not answer:
                    print(
                        f"Warning: Skipping flashcard {flashcard_id} due to missing fields"
                    )
                    continue

                flashcard = {
                    "title": title,
                    "question": question,
                    "answer": answer,
                }
                flashcards.append(flashcard)
            except (ValueError, IndexError) as e:
                print(f"Error processing flashcard: {e}")
                continue

        return {"flashcards": flashcards}

    except Exception as e:
        print(f"Error parsing flashcards: {e}")
        return {"flashcards": []}


def generar_con_llm(llm, texto):

    vectorstore_dir = os.path.join(
        "app",
        "model",
        "data",
        "pritamdeka_BioBERT-mnli-snli-scinli-scitail-mednli-stsb",
    )
    print(f"Using vector store directory: {vectorstore_dir}")
    print(os.getcwd())

    print(f"Looking for vector store at: {vectorstore_dir}")

    # Check if vectorstore directory exists
    if not os.path.exists(vectorstore_dir):
        # Fallback: create a simple response without RAG
        print(
            f"Warning: Vector store directory {vectorstore_dir} not found. Using fallback mode."
        )
        return create_fallback_flashcards(texto)

    try:
        embeddings_model = HuggingFaceEmbeddings(
            model_name=EMBEDDINGS,
        )
        print(f"Using embeddings model: {EMBEDDINGS}")

        # Load the vector store
        vectorstore = Chroma(
            persist_directory=vectorstore_dir, embedding_function=embeddings_model
        )

        print("Vector store loaded successfully")

        prompt = ChatPromptTemplate.from_template(template)

        print("Creating retriever...")

        retriever = vectorstore.as_retriever(
            search_type="similarity", search_kwargs={"k": 5}
        )
        print("Retriever created successfully")

        # RAG Chain
        combine_docs_chain = create_stuff_documents_chain(llm, prompt)
        print("Combine documents chain created successfully")
        retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)
        print("Retrieval chain created successfully")

        result = retrieval_chain.invoke({"input": texto})
        print("RAG pipeline invoked successfully")
        print(f"Result: {result}")
        flashcards = parse_flashcards_to_json(result["answer"])
        print("Flashcards parsed successfully")
        return flashcards

    except Exception as e:
        print(f"Error in RAG pipeline: {e}")
        return create_fallback_flashcards(texto)


def create_fallback_flashcards(texto):
    """
    Create simple flashcards when RAG is not available
    """
    flashcards = [
        {
            "title": "Definition",
            "question": f"What is {texto}?",
            "answer": f"{texto} is a medical condition that requires further research and study.",
        },
        {
            "title": "Clinical Significance",
            "question": f"Why is understanding {texto} important in medical practice?",
            "answer": f"Understanding {texto} is crucial for proper diagnosis and treatment planning.",
        },
    ]
    return {"flashcards": flashcards}
