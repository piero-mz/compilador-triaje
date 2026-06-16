from flask import Flask, render_template, request, jsonify, Response
from compiler import compilar

app = Flask(__name__)

EJEMPLO_CODIGO = """PACIENTE Garcia {
    SIGNOS VITALES {
        frecuencia_cardiaca = 110;
        presion_sistolica = 85;
        saturacion = 92;
        temperatura = 38.5;
    }
    SINTOMA = "Dolor toracico agudo";
    PRIORIDAD = NIVEL II;
}

PACIENTE Lopez {
    SIGNOS VITALES {
        frecuencia_cardiaca = 72;
        presion_sistolica = 120;
        saturacion = 98;
        temperatura = 36.8;
    }
    SINTOMA = "Corte superficial en mano derecha";
    PRIORIDAD = NIVEL IV;
}"""

@app.route("/")
def index():
    return render_template("index.html", ejemplo=EJEMPLO_CODIGO)

@app.route("/compilar", methods=["POST"])
def compilar_codigo():
    data = request.get_json()
    codigo = data.get("codigo", "")
    if not codigo.strip():
        return jsonify({"error": "vacio"}), 400
    return jsonify(compilar(codigo))

@app.route("/ejemplo")
def obtener_ejemplo():
    return jsonify({"codigo": EJEMPLO_CODIGO})

@app.route("/descargar", methods=["POST"])
def descargar():
    data = request.get_json()
    codigo_py = data.get("codigo_generado", "")
    return Response(
        codigo_py,
        mimetype="text/x-python",
        headers={"Content-Disposition": "attachment; filename=vitalcheck_output.py"}
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
