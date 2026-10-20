import time
import json
import paho.mqtt.client as mqtt
from pymodbus.client import ModbusTcpClient

PLC_IP = "10.10.10.10"
BROKER_IP = "10.10.30.30"
TOPICO = "planta/agua/telemetria"

modbus_cli = ModbusTcpClient(PLC_IP, port=502)
mqtt_cli = mqtt.Client()
mqtt_cli.connect(BROKER_IP, 1883, 60)
mqtt_cli.loop_start()

while True:
    try:
        if not modbus_cli.connected:
            modbus_cli.connect()
        rr = modbus_cli.read_holding_registers(address=0, count=3)
        if not rr.isError():
            nivel = round(rr.registers[0] / 10.0, 1)
            bomba = int(rr.registers[1])
            alerta_cod = int(rr.registers[2])
            alerta_msg = "NORMAL" if alerta_cod == 0 else ("ALERTA CRITICA: Nivel >= 90%" if alerta_cod == 1 else "ALERTA CRITICA: Nivel <= 20%")
            payload = {
                "nivel": nivel,
                "bomba_estado": bomba,
                "bomba_texto": "ACTIVA" if bomba == 1 else "INACTIVA",
                "alerta_codigo": alerta_cod,
                "alerta_mensaje": alerta_msg,
                "timestamp": int(time.time())
            }
            mqtt_cli.publish(TOPICO, json.dumps(payload))
            print(f"[GATEWAY-BORDE] Publicado en MQTT -> {payload}")
    except Exception as e:
        print(f"[GATEWAY-BORDE] Error: {e}")
    time.sleep(2.0)
