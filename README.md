# Automatic Generation of Medical Flashcard Question Using Natural Language Processing


## Integrantes

* Gabriel Omar Durán Ruiz    			- Usuario Github: gabo52 
* Jose Antonio Farah Zapata 			- Usuario Github: Antonio-Farah 
* Sebastian Antonio Martinez Toledo 	- Usuario Github: ezeAst 
* Jose Luis Ángel Flores Gonzales		- Usuario Github: a20190202 
* Alejandro Ríos						- Usuario Github: alez-2210
 
## Folders
La carpeta `apps` contiene el desarrollo de la aplicación web para el uso de flashcards. Es necesario instalar y ejecutar Ollama para que el software funcione adecuadamente.

### Backend

1. Generar la base vectorial (no está en el repositorio):
   ```bash
   python pln_model/vectorial_db.py
   ```
   Para otros embeddings: `--embeddings pritamdeka/S-Biomed-Roberta-snli-multinli-stsb` y definir `EMBEDDINGS_MODEL` y `VECTORSTORE_DIR` en `apps/Backend/.env`.
2. Descargar el modelo: `ollama pull llama3.1:8b` (se cambia con `OLLAMA_MODEL`).
3. Configuración opcional: copiar `apps/Backend/.env.example` como `.env`.
4. Ejecutar: `pnpm dev` desde la raíz, o `python run.py` dentro de `apps/Backend`.

Endpoints:

| Método | Ruta | Uso |
| --- | --- | --- |
| POST | `/generar_preguntas` | `{"texto": "Asthma", "mode": "topic", "card_type": "qa", "difficulty": "intermediate", "language": "en", "num_cards": 5}` |
| POST | `/regenerar_pregunta` | Igual que el anterior más `area` y `avoid_questions`; devuelve una tarjeta |
| POST | `/exportar_anki` | `{"deck_name": "...", "cards": [...]}`; devuelve un `.apkg` |
| GET | `/areas` | Áreas clínicas disponibles |
| GET | `/health` | Estado de Ollama y de la base vectorial |

`mode`: `topic` (un tema, se buscan fragmentos en los libros por cada área clínica) o `passage` (las tarjetas salen de los apuntes enviados). `card_type`: `qa`, `cloze` o `mcq`. Cada tarjeta incluye sus fuentes (libro y fragmento) y `support`, un puntaje que indica si la respuesta está respaldada por esos fragmentos.

Tests (no requieren Ollama ni la base vectorial):
```bash
cd apps/Backend
pip install -r requirements-dev.txt
pytest
```

Asimismo, la carpeta `pln_model` contiene los cuadernos de los modelos utilizados para las pruebas, estos incluyen los llms llama y phi.

## Natural Language Processing

Para esta implementación utilizamos un RAG(Retrieval Augmented Generation Model). Para ello se utilizó los libros en inglés del dataset MedQA como fuente de información y se crearon los vectore store con ayuda de embeddings de HuggingFace. El embedding seleccionado fue [BioBert](https://huggingface.co/pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb).

Asimismo, se utilizó el modelo llama2 como large language model para generar las salidas como  flashcards. Su implementación fue mediante Ollama de la librería langchain.