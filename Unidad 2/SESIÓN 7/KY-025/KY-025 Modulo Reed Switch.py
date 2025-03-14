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
MQTT_CLIENT_ID = "sensor_reed"
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "cm/trabajo/proximidad"

# Configuración del sensor Reed Switch (KY-025)
sensor_reed = Pin(34, Pin.IN, Pin.PULL_UP)  # Usamos entrada digital con pull-up interno

# Función para conectar a WiFi
def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)

    start_time = time.time()
    while not sta_if.isconnected():
        if time.time() - start_time > 10:
            print("\nError al conectar a WiFi: Tiempo de espera agotado")
            return False
        print(".", end="")
        time.sleep(0.3)

    print("\nWiFi Conectada!")
    print("IP:", sta_if.ifconfig()[0])
    return True

# Función para conectar al broker MQTT
def conectar_broker():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD)
    client.connect()
    print(f"Conectado a MQTT Broker: {MQTT_BROKER}")
    return client

# Función para leer el estado del reed switch
def leer_estado_reed():
    estado = sensor_reed.value()  # Leer el valor digital (0 o 1)
    
    # La lógica inversa porque usamos PULL_UP:
    # 0 = campo magnético detectado (contacto cerrado)
    # 1 = sin detección (contacto abierto)
    if estado == 0:
        return "Activo (Campo magnético detectado)"
    else:
        return "Inactivo (Sin detección)"

# Conectar a WiFi y MQTT
if conectar_wifi():
    client = conectar_broker()

# Bucle principal
while True:
    # Leer el estado del sensor
    estado = leer_estado_reed()
    print(f"Estado del sensor: {estado}")

    # Publicar el estado en MQTT
    client.publish(MQTT_TOPIC_PUB, estado)

    time.sleep(3)  # Esperar 1 segundo para mayor capacidad de respuesta