import requests
from flask import Flask, request, jsonify

app = Flask(__name__)
INFLUX_URL = "http://localhost:8086/write?db=planta_agua"

@app.route("/api/telemetria", methods=["POST"])
def recibir_telemetria():
    d = request.get_json(silent=True) or {}
    nivel = float(d.get("nivel", 0.0))
    bomba_est = int(d.get("bomba_estado", 0))
    bomba_txt = str(d.get("bomba_texto", "INACTIVA")).replace("\"", "")
    alerta_cod = int(d.get("alerta_codigo", 0))
    alerta_msg = str(d.get("alerta_mensaje", "NORMAL")).replace("\"", "")

    linea = f"telemetria nivel={nivel},bomba_estado={bomba_est}i,bomba_texto=\"{bomba_txt}\",alerta_codigo={alerta_cod}i,alerta_mensaje=\"{alerta_msg}\""
    requests.post(INFLUX_URL, data=linea.encode("utf-8"), timeout=2)
    print(f"[AWS-HTTPS] Recibido OK -> Nivel: {nivel}% | Bomba: {bomba_txt} | Alerta: {alerta_msg}")
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=443, ssl_context=("/opt/receptor_ot/cert.pem", "/opt/receptor_ot/key.pem"))
