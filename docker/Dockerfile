FROM alpine:3.22
RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    py3-flask \
    py3-requests \
    py3-paho-mqtt \
    libpcap \
    mosquitto \
    mosquitto-clients \
    tcpdump \
    iproute2 \
    iputils \
    nano \
    curl \
    && pip3 install --no-cache-dir --break-system-packages pymodbus==3.6.9 scapy
