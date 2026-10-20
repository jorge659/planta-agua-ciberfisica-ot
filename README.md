# Planta de Tratamiento de Agua Potable Virtual (Sistemas Ciberfísicos - PTSC08)
**Institución:** INACAP Sede Temuco  
**Asignatura:** Sistemas Ciberfísicos (PTSC08)  
**Docente:** Felipe Andrés Henríquez Vilugrón  
**Autor:** Jorge Luis Contreras Gutiérrez  

## Descripción de la Arquitectura
Gemelo Digital de una Planta de Tratamiento de Agua Potable desplegado sobre **GNS3**, **Docker (Alpine Linux)**, switches **Cisco IOSvL2**, firewall perimetral **FortiGate VM** bajo el **Modelo Purdue (ISA-95 / IEC 62443)** y analítica en la nube en **AWS Academy (Amazon EC2 con InfluxDB y Grafana)**.

## Nomenclatura Oficial de los 9 Contenedores
1. `estanque-agua` (`10.10.10.20`): Simulación física con tasas Delta Time (30-60s) y API REST (Puerto 5000).
2. `plc-central` (`10.10.10.10`): Servidor Modbus TCP (Puerto 502) y lógica de control por umbrales (20% y 90%).
3. `sensor-nivel-estanque` (`10.10.10.30`): Sonda hidrostática (GET API REST -> Escritura Modbus FC=06).
4. `actuador-bomba-agua` (`10.10.10.40`): Bomba de impulsión (Lectura Modbus FC=03 -> POST API REST).
5. `panel-hmi-local` (`10.10.30.10`): Supervisión local en tiempo real para el operador en planta (Nivel 3).
6. `gateway-borde` (`10.10.30.20`): Sondeo Modbus controlado y publicación hacia MQTT.
7. `broker-mqtt` (`10.10.30.30`): Servidor Eclipse Mosquitto (Puerto 1883) para desacoplamiento IT/OT.
8. `sonda-ids` (`10.10.30.40`): Sonda pasiva IDS con Scapy conectada a puerto espejo (SPAN `Gi1/0`).
9. `puente-aws` (`10.10.35.10`): Suscriptor MQTT en DMZ y exportador seguro por HTTPS/TLS (Puerto 443) hacia AWS EC2 (`184.192.209.40`).
