"""
Simple fallback LLM wrapper without ChromaDB
"""

import os
import json


def generar_con_llm_simple(llm, texto):
    """
    Simple LLM generation without RAG/ChromaDB
    """
    try:
        # Simple prompt without RAG
        simple_prompt = f"""
        Create 3 medical flashcards about {texto}.
        
        Format each flashcard as:
        Flashcard X: [Topic]
        Q: [Question]
        A: [Answer]
        
        Focus on key medical concepts, symptoms, and treatments.
        """

        # Use the LLM directly
        result = llm.invoke(simple_prompt)

        # Parse the result
        flashcards = parse_simple_flashcards(result)
        return {"flashcards": flashcards}

    except Exception as e:
        print(f"Error in simple LLM generation: {e}")
        return create_basic_flashcards(texto)


def parse_simple_flashcards(text):
    """
    Parse simple flashcard format
    """
    flashcards = []
    import re

    # Look for flashcard patterns
    pattern = r"Flashcard\s+(\d+):\s*([^\n]+)\s*\n\s*Q:\s*([^\n]+)\s*\n\s*A:\s*([^(?:Flashcard|\Z)]+)"
    matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)

    for match in matches:
        flashcard = {
            "title": match[1].strip(),
            "question": match[2].strip(),
            "answer": match[3].strip(),
        }
        flashcards.append(flashcard)

    # If no matches found, create basic ones
    if not flashcards:
        return create_basic_flashcards_list(text)

    return flashcards


def create_basic_flashcards_list(texto):
    """Create basic flashcards from text"""
    return [
        {
            "title": "Definition",
            "question": f"What is {texto}?",
            "answer": f"{texto} is a medical condition that requires study and understanding.",
        },
        {
            "title": "Clinical Importance",
            "question": f"Why is {texto} clinically significant?",
            "answer": f"{texto} is important for medical diagnosis and treatment planning.",
        },
    ]


def create_basic_flashcards(texto):
    """
    Create basic fallback flashcards
    """
    flashcards = create_basic_flashcards_list(texto)
    return {"flashcards": flashcards}
