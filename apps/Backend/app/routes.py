from flask import Blueprint, request, jsonify
from .services import generar_preguntas_llm

main = Blueprint("main", __name__)

@main.route("/generar_preguntas", methods=["POST"])
def generar_preguntas():
    data = request.get_json()
    texto = data.get("texto", "")

    if not texto:
        return jsonify({"error": "Falta el texto académico"}), 400

    try:
        preguntas = generar_preguntas_llm(texto)
        return jsonify({"preguntas": preguntas}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500