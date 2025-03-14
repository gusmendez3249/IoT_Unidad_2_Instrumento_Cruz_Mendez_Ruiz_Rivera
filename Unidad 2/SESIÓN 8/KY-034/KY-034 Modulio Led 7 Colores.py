from umqtt.simple import MQTTClient
from machine import Pin
import network
import time

# Configuración WiFi
WIFI_SSID = "GUSTAVO"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_BROKER = "192.168.137.217"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "ky034_auto"
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "cm/trabajo/proximidad"

# Configuración KY-034
led_signal = Pin(12, Pin.OUT)
color_actual = 0
intervalo_cambio = 4  # Segundos entre cambios
colores = [
    "Apagado",
    "Rojo",
    "Verde",
    "Azul",
    "Amarillo",
    "Cian",
    "Magenta",
    "Blanco"
]

def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)

    start_time = time.time()
    while not sta_if.isconnected():
        if time.time() - start_time > 10:
            print("\nError al conectar a WiFi")
            return False
        print(".", end="")
        time.sleep(0.3)

    print("\nWiFi Conectada!")
    print("IP:", sta_if.ifconfig()[0])
    return True

def conectar_broker():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD)
    client.connect()
    print(f"Conectado a MQTT Broker: {MQTT_BROKER}")
    return client

def cambiar_color():
    global color_actual
    # Generar pulso para cambio de color
    led_signal.value(1)
    time.sleep(1)
    led_signal.value(0)
    
    # Actualizar índice y publicar estado
    color_actual = (color_actual + 1) % 8
    color_nombre = colores[color_actual]
    client.publish(MQTT_TOPIC_PUB, color_nombre)
    
    return color_nombre

# Inicialización
if conectar_wifi():
    client = conectar_broker()
    led_signal.value(0)  # Estado inicial

# Bucle principal de cambio automático
try:
    while True:1
        estado = cambiar_color()
        print(f"Color actual: {estado}")
        time.sleep(intervalo_cambio)

except Exception as e:
    print("Error:", e)
    led_signal.value(0)
    client.disconnect()