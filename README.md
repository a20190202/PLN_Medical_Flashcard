# Automatic Generation of Medical Flashcard Question Using Natural Language Processing


## Integrantes

* Gabriel Omar Durán Ruiz    			- Usuario Github: gabo52 
* Jose Antonio Farah Zapata 			- Usuario Github: Antonio-Farah 
* Sebastian Antonio Martinez Toledo 	- Usuario Github: ezeAst 
* Jose Luis Ángel Flores Gonzales		- Usuario Github: a20190202 
* Alejandro Ríos						- Usuario Github: alez-2210
 
## Folders
La carpeta `apps` contiene el desarrollo de la aplicación web para el uso de flashcards. Es necesario crear y guardar los embeddings según desee el usuario, pues estos no se encuentran en el repositorio de Github. En caso se desee usar otros embeddings, se debe modificar la variable `vectorstore_dir` del archivo `llm_wrapper.py` en el backend. Es necesario instalar y ejecutar Ollama para que el software funcione adecuadamente.

Asimismo, la carpeta `pln_model` contiene los cuadernos de los modelos utilizados para las pruebas, estos incluyen los llms llama y phi.

## Natural Language Processing

Para esta implementación utilizamos un RAG(Retrieval Augmented Generation Model). Para ello se utilizó los libros en inglés del dataset MedQA como fuente de información y se crearon los vectore store con ayuda de embeddings de HuggingFace. El embedding seleccionado fue [BioBert](https://huggingface.co/pritamdeka/BioBERT-mnli-snli-scinli-scitail-mednli-stsb).

Asimismo, se utilizó el modelo llama2 como large language model para generar las salidas como  flashcards. Su implementación fue mediante Ollama de la librería langchain.