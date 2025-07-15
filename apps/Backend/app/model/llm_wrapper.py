from transformers import pipeline, T5Tokenizer, T5ForConditionalGeneration
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import json
import re

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
    flashcards = []

    # Split text into individual flashcards using regex
    flashcard_pattern = (
        r"Flashcard (\d+): ([^\n]+)\n\nQ: ([^\n]+)\nA: ([^(?:Flashcard|\Z)]+)"
    )

    matches = re.findall(flashcard_pattern, text, re.DOTALL)

    for match in matches:
        flashcard_id = int(match[0])
        title = match[1].strip()
        question = match[2].strip()
        answer = match[3].strip()

        flashcard = {
            "id": flashcard_id,
            "title": title,
            "question": question,
            "answer": answer,
        }
        flashcards.append(flashcard)

    return {"flashcards": flashcards}


def generar_con_llm(llm, texto):
    vectorstore_dir = "data/pritamdeka_BioBERT-mnli-snli-scinli-scitail-mednli-stsb"

    embeddings_model = HuggingFaceEmbeddings(
        model_name=EMBEDDINGS,
    )

    # Load the vector store
    vectorstore = Chroma(
        persist_directory=vectorstore_dir, embedding_function=embeddings_model
    )

    prompt = ChatPromptTemplate.from_template(template)

    retriever = vectorstore.as_retriever(
        search_type="similarity", search_kwargs={"k": 5}
    )

    # RAG Chain
    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    retrieval_chain = create_retrieval_chain(retriever, combine_docs_chain)

    result = retrieval_chain.invoke({"input": texto})
    flashcards = parse_flashcards_to_json(result["answer"])
    return flashcards
