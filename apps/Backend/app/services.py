# Import Windows fix first
from .model.windows_fix import setup_windows_chromadb

try:
    # Try to import the full RAG implementation
    from .model.llm_wrapper import generar_con_llm
    from langchain_ollama import OllamaLLM

    USE_RAG = True
    print("✓ Full RAG implementation loaded")
except ImportError as e:
    # Fall back to simple implementation
    print(f"⚠ RAG implementation failed: {e}")
    print("✓ Using simple LLM implementation")
    from .model.simple_llm import generar_con_llm_simple as generar_con_llm
    from langchain_ollama import OllamaLLM

    USE_RAG = False


def generar_preguntas_llm(texto):
    try:
        llm = OllamaLLM(model="llama2:latest", temperature=0.05, system="")
        return generar_con_llm(llm, texto)
    except Exception as e:
        print(f"Error with Ollama LLM: {e}")
        # Create a final fallback response
        return {
            "flashcards": [
                {
                    "title": "Medical Topic",
                    "question": f"What should be studied about {texto}?",
                    "answer": f"{texto} is a medical topic that requires further research and clinical understanding.",
                }
            ]
        }
