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
MQTT_CLIENT_ID = "ky032_obstaculo"
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "cm/trabajo/proximidad"

# Configuración KY-032
sensor = Pin(4, Pin.IN)  # Pin de entrada para el sensor
DEBOUNCE_TIME = 0.1  # Tiempo para evitar rebotes

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

# Inicialización
if conectar_wifi():
    client = conectar_broker()

# Bucle principal de detección
try:
    estado_anterior = None
    while True:
        # Leer estado del sensor (0 = obstáculo detectado, 1 = libre)
        estado_actual = sensor.value()
        
        # Solo publicar si hay cambio de estado
        if estado_actual != estado_anterior:
            if estado_actual == 0:
                mensaje = "Obstaculo detectado"
            else:
                mensaje = "Camino libre"
            
            client.publish(MQTT_TOPIC_PUB, mensaje)
            print(f"Estado: {mensaje}")
            estado_anterior = estado_actual
        
        time.sleep(5)

except Exception as e:
    print("Error:", e)
    client.disconnect()