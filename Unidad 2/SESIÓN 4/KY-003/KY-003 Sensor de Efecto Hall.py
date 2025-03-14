import network
from umqtt.simple import MQTTClient
from machine import Pin
import time

# Configuración WiFi
WIFI_SSID = "GUSTAVO"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_BROKER = "192.168.137.217"
MQTT_CLIENT_ID = ""
MQTT_TOPIC = "cm/trabajo/proximidad"
MQTT_PORT = 1883

# Configurar el pin del sensor de efecto Hall (HY-003) con pull-up interno
hall_sensor = Pin(4, Pin.IN, Pin.PULL_UP)  # Usar PULL_UP para evitar flotación del pin

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

# Bucle infinito para leer el sensor de efecto Hall
while True:
    estado = hall_sensor.value()  # Leer estado del sensor
    if estado == 0:  # Invertir la lógica si el sensor es activo bajo
        print("Campo magnético detectado")
        if client:
            client.publish(MQTT_TOPIC, "Campo magnético detectado")
    else:
        print("Sin campo magnético")
        if client:
            client.publish(MQTT_TOPIC, "Sin campo magnético")
    time.sleep(5)  # Leer cada segundo

