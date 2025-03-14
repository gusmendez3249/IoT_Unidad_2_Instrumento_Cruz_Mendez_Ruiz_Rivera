import network
from umqtt.simple import MQTTClient
from machine import Pin
import time

# Configuración WiFi
WIFI_SSID = "GUSTAVO"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_BROKER = "192.168.137.217"
MQTT_CLIENT_ID = ""
MQTT_TOPIC = "cm/trabajo/proximidad"
MQTT_PORT = 1883

# Configurar pines del módulo RGB
led_rojo = Pin(18, Pin.OUT)
led_verde = Pin(17, Pin.OUT)
led_azul = Pin(16, Pin.OUT)

# Conectar a WiFi
def conectar_wifi():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    for _ in range(30):  # Esperar 9 segundos máximo
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

# Lista de colores y sus configuraciones
colores = [
    ("Rojo", (1, 0, 0)),
    ("Verde", (0, 1, 0)),
    ("Azul", (0, 0, 1))
]

# Bucle infinito para alternar colores
while True:
    for color, (r, g, b) in colores:
        led_rojo.value(r)
        led_verde.value(g)
        led_azul.value(b)
        print(f"Color actual: {color}")
        if client:
            client.publish(MQTT_TOPIC, color)
        time.sleep(3)