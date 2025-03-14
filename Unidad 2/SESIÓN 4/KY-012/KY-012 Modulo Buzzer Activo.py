import network
from umqtt.simple import MQTTClient
from machine import Pin
import time

# Configuración WiFi
WIFI_SSID = "GUSTAVO"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_BROKER = "192.168.137.217"
MQTT_CLIENT_ID = "ESP32_RELAY"
MQTT_TOPIC = "cm/trabajo/proximidad"
MQTT_PORT = 1883

# Configurar el pin del relay (KY-012)
relay_pin = Pin(4, Pin.OUT)  # Conectado al pin 4 del ESP32

# Conectar a WiFi
def conectar_wifi():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(30):  # Esperar hasta 9 segundos
        if sta_if.isconnected():
            print("WiFi conectada!")
            return
        time.sleep(0.3)
    print("Error: No se pudo conectar a WiFi")
    return

# Conectar a MQTT
def conectar_broker():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"Conectado a MQTT Broker: {MQTT_BROKER}, Topic: {MQTT_TOPIC}")
        return client
    except Exception as e:
        print(f"Error al conectar con MQTT: {e}")
        return None

# Iniciar conexiones
conectar_wifi()
client = conectar_broker()

# Bucle infinito para controlar el relay
while True:
    relay_pin.on()  # Activar el relay (enciende el dispositivo conectado)
    print("Relay Activado (ON)")
    if client:
        client.publish(MQTT_TOPIC, "Relay ON")
    time.sleep(2)  # Mantener encendido por 5 segundos

    relay_pin.off()  # Desactivar el relay (apaga el dispositivo conectado)
    print("Relay Desactivado (OFF)")
    if client:
        client.publish(MQTT_TOPIC, "Relay OFF")
    time.sleep(2)  # Mantener apagado por 5 segundos
