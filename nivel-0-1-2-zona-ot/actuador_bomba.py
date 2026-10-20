import time
import requests
from pymodbus.client import ModbusTcpClient

URL_BOMBA = "http://10.10.10.20:5000/bomba"
cliente = ModbusTcpClient("10.10.10.10", port=502)

while True:
    try:
        if not cliente.connected:
            cliente.connect()
        rr = cliente.read_holding_registers(address=1, count=1)
        if not rr.isError():
            activar = (rr.registers[0] == 1)
            requests.post(URL_BOMBA, json={"activar": activar}, timeout=2)
            print(f"[ACTUADOR-BOMBA] Modbus Read PLC Reg[1]={rr.registers[0]} -> POST Estanque Bomba={'ACTIVA' if activar else 'INACTIVA'}")
    except Exception as e:
        print(f"[ACTUADOR-BOMBA] Esperando conexion: {e}")
    time.sleep(1.0)
