import time
import requests
from pymodbus.client import ModbusTcpClient

URL_ESTANQUE = "http://10.10.10.20:5000/nivel"
cliente = ModbusTcpClient("10.10.10.10", port=502)

while True:
    try:
        r = requests.get(URL_ESTANQUE, timeout=2).json()
        nivel = float(r["nivel"])
        val_reg = int(round(nivel * 10))
        if not cliente.connected:
            cliente.connect()
        cliente.write_register(address=0, value=val_reg)
        print(f"[SENSOR-NIVEL] GET Estanque: {nivel:.1f}% -> Modbus Write PLC Reg[0]={val_reg}")
    except Exception as e:
        print(f"[SENSOR-NIVEL] Esperando conexion: {e}")
    time.sleep(1.0)
