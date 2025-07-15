from .model.llm_wrapper import generar_con_llm
from langchain_ollama import OllamaLLM


def generar_preguntas_llm(texto):
    llm = OllamaLLM(model="llama2:latest", temperature=0.05, system="")
    return generar_con_llm(llm, texto)
