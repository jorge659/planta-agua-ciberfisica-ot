import time
import threading
from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext

store = ModbusSlaveContext(
    hr=ModbusSequentialDataBlock(0, [250, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    zero_mode=True
)
context = ModbusServerContext(slaves=store, single=True)

def logica_control_plc():
    print("[PLC-CENTRAL] Servidor Modbus TCP (Puerto 502) activo...")
    while True:
        time.sleep(1.0)
        registros = context[0x00].getValues(3, 0, count=3)
        nivel = registros[0] / 10.0
        bomba = registros[1]
        alerta = 0

        if nivel >= 90.0:
            bomba = 1
            alerta = 1
        elif nivel <= 20.0:
            bomba = 0
            alerta = 2

        context[0x00].setValues(3, 1, [bomba, alerta])
        est_b = "ACTIVA" if bomba == 1 else "INACTIVA"
        est_a = "NORMAL" if alerta == 0 else ("CRITICA ALTA (>=90%)" if alerta == 1 else "CRITICA BAJA (<=20%)")
        print(f"[PLC-CENTRAL] Nivel: {nivel:.1f}% | Bomba: {est_b} | Safety Alarm: {est_a}")

if __name__ == '__main__':
    threading.Thread(target=logica_control_plc, daemon=True).start()
    StartTcpServer(context=context, address=("0.0.0.0", 502))
