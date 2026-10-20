from scapy.all import sniff, TCP, IP, Raw

IPS_AUTORIZADAS_ESCRITURA = ["10.10.10.30"]

print("[SONDA-IDS] Escuchando puerto SPAN (eth0) en busca de anomalias Modbus TCP (Puerto 502)...")

def analizar_paquete(pkt):
    if pkt.haslayer(TCP) and pkt.haslayer(Raw) and pkt.haslayer(IP):
        if pkt[TCP].dport == 502:
            payload = bytes(pkt[Raw].load)
            if len(payload) >= 8:
                func_code = payload[7]
                src_ip = pkt[IP].src
                dst_ip = pkt[IP].dst
                if func_code in [6, 16] and src_ip not in IPS_AUTORIZADAS_ESCRITURA:
                    print(f"\n[!!! ALERTA CRITICA IDS !!!] Escritura Modbus NO AUTORIZADA (FC={func_code}) desde {src_ip} hacia PLC {dst_ip}!\n")
                elif func_code == 3:
                    print(f"[SONDA-IDS] Trama Modbus legitima (Lectura FC=03): {src_ip} -> {dst_ip}")

sniff(iface="eth0", filter="tcp port 502", prn=analizar_paquete, store=0)
