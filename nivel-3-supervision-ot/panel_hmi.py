import time, threading, logging
from flask import Flask, jsonify, render_template_string
from pymodbus.client import ModbusTcpClient

logging.getLogger('werkzeug').setLevel(logging.ERROR)
app = Flask(__name__)

PLC_IP = "10.10.10.10"
PLC_PORT = 502
cliente = ModbusTcpClient(PLC_IP, port=PLC_PORT)

estado_hmi = {
    "nivel": 0.0,
    "bomba_estado": 0,
    "bomba_texto": "INACTIVA [OFF]",
    "alerta_nivel_cod": 0,
    "alerta_nivel_txt": "NORMAL (20% - 90%)",
    "cloro_ppm": 0.0,
    "alerta_cloro_cod": 0,
    "alerta_cloro_txt": "RANGO SEGURO (0.2 - 4.0 ppm)",
    "conectado": False,
    "ultima_lectura": "--:--:--"
}
lock = threading.Lock()

HTML_SCADA = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Panel HMI Local - Planta de Agua Potable OT (Nivel 3)</title>
    <style>
        body { background: #0f172a; color: #f8fafc; font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .header { background: #1e293b; padding: 15px 25px; border-radius: 8px; border-left: 6px solid #38bdf8; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
        .card { background: #1e293b; padding: 20px; border-radius: 8px; border: 1px solid #334155; }
        .title { font-size: 14px; color: #94a3b8; text-transform: uppercase; margin-bottom: 10px; }
        .value { font-size: 38px; font-weight: bold; margin: 10px 0; }
        .bar-bg { background: #334155; height: 28px; border-radius: 14px; overflow: hidden; margin-top: 10px; }
        .bar-fill { background: linear-gradient(90deg, #0284c7, #38bdf8); height: 100%; width: 0%; transition: width 0.5s; }
        .badge { display: inline-block; padding: 8px 14px; border-radius: 6px; font-weight: bold; font-size: 15px; }
        .ok { background: #065f46; color: #34d399; border: 1px solid #10b981; }
        .danger { background: #7f1d1d; color: #fca5a5; border: 1px solid #ef4444; }
        .off { background: #1e3a8a; color: #93c5fd; border: 1px solid #3b82f6; }
        .footer { margin-top: 20px; font-size: 13px; color: #64748b; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <div>
            <h2 style="margin:0;">PANEL HMI LOCAL DE OPERADOR EN PLANTA (NIVEL 3 - ZONA SUPERVISIÓN OT)</h2>
            <small style="color:#94a3b8;">Nodo: panel-hmi-local (10.10.30.10) &longrightarrow; Consulta Directa Modbus TCP (Puerto 502 / FC=03) &longrightarrow; plc-central (10.10.10.10)</small>
        </div>
        <div id="conn" class="badge ok">ONLINE MODBUS TCP</div>
    </div>

    <div class="grid">
        <div class="card">
            <div class="title">1. Nivel Físico del Estanque (Holding Register 0)</div>
            <div class="value" id="nivel">-- %</div>
            <div class="bar-bg"><div class="bar-fill" id="barra"></div></div>
        </div>

        <div class="card">
            <div class="title">2. Concentración Química de Cloro Residual (Holding Register 3)</div>
            <div class="value" id="cloro">-- ppm</div>
            <div id="alerta_cloro" class="badge ok">CARGANDO...</div>
        </div>

        <div class="card">
            <div class="title">3. Estado Operativo Bomba de Impulsión (Holding Register 1)</div>
            <div style="margin-top:15px;"><span id="bomba" class="badge off">CARGANDO...</span></div>
        </div>

        <div class="card">
            <div class="title">4. Alerta Hidráulica Safety (Holding Register 2)</div>
            <div style="margin-top:15px;"><span id="alerta_nivel" class="badge ok">CARGANDO...</span></div>
        </div>
    </div>
    <div class="footer">Última lectura directa al PLC por Modbus TCP (Puerto 502): <span id="hora">--:--:--</span></div>

    <script>
        async function actualizarHMI() {
            try {
                const r = await fetch('/api/estado');
                const d = await r.json();
                document.getElementById('nivel').innerText = d.nivel.toFixed(1) + ' %';
                document.getElementById('barra').style.width = d.nivel + '%';
                document.getElementById('cloro').innerText = d.cloro_ppm.toFixed(2) + ' ppm';
                document.getElementById('hora').innerText = d.ultima_lectura;

                const b = document.getElementById('bomba');
                b.innerText = d.bomba_texto;
                b.className = 'badge ' + (d.bomba_estado === 1 ? 'ok' : 'off');

                const an = document.getElementById('alerta_nivel');
                an.innerText = d.alerta_nivel_txt;
                an.className = 'badge ' + (d.alerta_nivel_cod === 0 ? 'ok' : 'danger');

                const ac = document.getElementById('alerta_cloro');
                ac.innerText = d.alerta_cloro_txt;
                ac.className = 'badge ' + (d.alerta_cloro_cod === 0 ? 'ok' : 'danger');
            } catch (e) {}
        }
        setInterval(actualizarHMI, 1000);
        actualizarHMI();
    </script>
</body>
</html>
"""

def polling_modbus_plc():
    print("=== PANEL HMI LOCAL WEB + CONSOLA ACTIVO EN http://10.10.30.10:8080 ===")
    while True:
        try:
            if not cliente.connected:
                cliente.connect()
            rr = cliente.read_holding_registers(address=0, count=5)
            if not rr.isError():
                with lock:
                    nivel = round(rr.registers[0] / 10.0, 1)
                    bomba = int(rr.registers[1])
                    alerta_n = int(rr.registers[2])
                    cloro = round(rr.registers[3] / 100.0, 2)
                    alerta_c = int(rr.registers[4])

                    estado_hmi["nivel"] = nivel
                    estado_hmi["bomba_estado"] = bomba
                    estado_hmi["bomba_texto"] = "ACTIVA [ON] - Extrayendo Caudal" if bomba == 1 else "INACTIVA [OFF] - Llenando Estanque"
                    estado_hmi["alerta_nivel_cod"] = alerta_n
                    estado_hmi["alerta_nivel_txt"] = "NORMAL (20% - 90%)" if alerta_n == 0 else ("PELIGRO NIVEL ALTO >= 90%" if alerta_n == 1 else "PELIGRO NIVEL BAJO <= 20%")
                    estado_hmi["cloro_ppm"] = cloro
                    estado_hmi["alerta_cloro_cod"] = alerta_c
                    estado_hmi["alerta_cloro_txt"] = "RANGO SEGURO (0.2 - 4.0 ppm)" if alerta_c == 0 else ("PELIGRO QUÍMICO: Cloro > 4.0 ppm" if alerta_c == 1 else "PELIGRO QUÍMICO: Cloro < 0.2 ppm")
                    estado_hmi["conectado"] = True
                    estado_hmi["ultima_lectura"] = time.strftime("%H:%M:%S")

                barra = "#" * int(nivel // 5) + "-" * (20 - int(nivel // 5))
                print(f"[HMI-WEB-8080] Agua: [{barra}] {nivel:5.1f}% | Bomba: {'ON' if bomba else 'OFF'} | Cloro: {cloro:4.2f} ppm")
        except Exception as e:
            print(f"[HMI-LOCAL] Error leyendo PLC: {e}")
        time.sleep(1.5)

@app.route('/')
def index():
    return render_template_string(HTML_SCADA)

@app.route('/api/estado')
def api_estado():
    with lock:
        return jsonify(estado_hmi)

if __name__ == '__main__':
    threading.Thread(target=polling_modbus_plc, daemon=True).start()
    app.run(host='0.0.0.0', port=8080)
