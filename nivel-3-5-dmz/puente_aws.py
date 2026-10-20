import json
import urllib3
import requests
import paho.mqtt.client as mqtt

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BROKER_IP = "10.10.30.30"
TOPICO = "planta/agua/telemetria"
AWS_IP = "184.192.209.40"
URL_AWS_HTTPS = f"https://{AWS_IP}/api/telemetria"

def on_connect(client, userdata, flags, rc):
    print(f"[PUENTE-AWS] Conectado a Broker MQTT ({BROKER_IP}). Suscrito a {TOPICO}")
    client.subscribe(TOPICO)

def on_message(client, userdata, msg):
    try:
        datos = json.loads(msg.payload.decode())
        r = requests.post(URL_AWS_HTTPS, json=datos, verify=False, timeout=4)
        print(f"[PUENTE-AWS] Telemetria enviada por HTTPS/TLS a AWS ({AWS_IP}) -> Status {r.status_code}: Nivel={datos['nivel']}% | Bomba={datos['bomba_texto']}")
    except Exception as e:
        print(f"[PUENTE-AWS] Esperando receptor HTTPS en AWS ({AWS_IP}): {e}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_IP, 1883, 60)
client.loop_forever()
