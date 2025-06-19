from transformers import pipeline, T5Tokenizer, T5ForConditionalGeneration


MODEL_NAME = "valhalla/t5-small-qg-hl"

tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME, use_fast=False)
model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)
generator = pipeline("text2text-generation", model=model, tokenizer=tokenizer)


def generar_con_llm(texto):
    prompt = f"generate questions: {texto.strip()}"
    results = generator(prompt, max_length=128, num_return_sequences=3)
    return [r["generated_text"] for r in results]
