import time
from pymodbus.client import ModbusTcpClient

cliente = ModbusTcpClient("10.10.10.10", port=502)

print("=== PANEL HMI LOCAL DE PLANTA (NIVEL 3) ===")
while True:
    try:
        if not cliente.connected:
            cliente.connect()
        rr = cliente.read_holding_registers(address=0, count=3)
        if not rr.isError():
            nivel = rr.registers[0] / 10.0
            bomba = "ACTIVA [ON]" if rr.registers[1] == 1 else "INACTIVA [OFF]"
            alerta = "NORMAL" if rr.registers[2] == 0 else ("PELIGRO NIVEL ALTO >=90%" if rr.registers[2] == 1 else "PELIGRO NIVEL BAJO <=20%")
            barra = "#" * int(nivel // 5) + "-" * (20 - int(nivel // 5))
            print(f"[HMI-LOCAL] Estanque: [{barra}] {nivel:5.1f}% | Bomba: {bomba} | Safety: {alerta}")
    except Exception as e:
        print(f"[HMI-LOCAL] Error leyendo PLC: {e}")
    time.sleep(2.0)
