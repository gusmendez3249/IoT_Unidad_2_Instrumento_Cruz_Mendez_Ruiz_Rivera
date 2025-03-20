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
MQTT_CLIENT_ID = "ky036_metal"
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "cm/trabajo/proximidad"

# Configuración KY-036
SENSOR_PIN = 4  # GPIO para la salida digital del sensor
DEBOUNCE_TIME = 0.1  # Tiempo para estabilizar lecturas

# Inicializar sensor
sensor = Pin(SENSOR_PIN, Pin.IN)

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

# Bucle principal
try:
    estado_anterior = sensor.value()
    while True:
        estado_actual = sensor.value()
        
        # Solo publicar si hay cambio de estado
        if estado_actual != estado_anterior:
            if estado_actual == 0:  # 0 = metal detectado
                client.publish(MQTT_TOPIC_PUB, "Metal detectado")
                print("Metal detectado!")
            else:
                client.publish(MQTT_TOPIC_PUB, "Sin metal")
                print("Sin metal")
            estado_anterior = estado_actual
        
        time.sleep(DEBOUNCE_TIME)

except Exception as e:
    print("Error:", e)
    client.disconnect()