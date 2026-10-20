import time
import threading
import logging
from flask import Flask, jsonify, request

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app = Flask(__name__)

estado = {
    "nivel": 25.0,
    "bomba_activa": False,
    "tasa_llenado": 2.0,
    "tasa_vaciado": 2.2,
    "ultimo_tiempo": time.time()
}
lock = threading.Lock()

def motor_fisico_delta_time():
    while True:
        time.sleep(1.0)
        with lock:
            ahora = time.time()
            dt = ahora - estado["ultimo_tiempo"]
            estado["ultimo_tiempo"] = ahora
            if estado["bomba_activa"]:
                estado["nivel"] = max(0.0, estado["nivel"] - (estado["tasa_vaciado"] * dt))
            else:
                estado["nivel"] = min(100.0, estado["nivel"] + (estado["tasa_llenado"] * dt))
            print(f"[ESTANQUE-AGUA] Nivel: {estado['nivel']:.1f}% | Bomba: {'ACTIVA (Vaciando)' if estado['bomba_activa'] else 'INACTIVA (Llenando)'}")

@app.route('/nivel', methods=['GET'])
def obtener_nivel():
    with lock:
        return jsonify({"nivel": round(estado["nivel"], 2), "bomba_activa": estado["bomba_activa"]})

@app.route('/bomba', methods=['POST'])
def controlar_bomba():
    datos = request.get_json(silent=True) or {}
    if "activar" in datos:
        with lock:
            estado["bomba_activa"] = bool(datos["activar"])
        return jsonify({"status": "ok", "bomba_activa": estado["bomba_activa"]})
    return jsonify({"error": "Falta parametro activar"}), 400

if __name__ == '__main__':
    threading.Thread(target=motor_fisico_delta_time, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
