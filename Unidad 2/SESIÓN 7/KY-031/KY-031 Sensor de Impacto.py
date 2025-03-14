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
MQTT_CLIENT_ID = "sensor_impacto"
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "cm/trabajo/proximidad"

# Configuración del sensor KY-031
sensor_impacto = Pin(34, Pin.IN, Pin.PULL_UP)  # Usar pull-up interno
estado_anterior = 1  # Estado inicial (sin detección)
debounce_time = 0  # Tiempo del último impacto

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

# Función para detectar impactos con debounce
def detectar_impacto():
    global estado_anterior, debounce_time
    estado_actual = sensor_impacto.value()
    
    # Detectar flanco descendente (impacto detectado)
    if estado_actual == 0 and estado_anterior == 1:
        if time.ticks_ms() - debounce_time > 300:  # Debounce de 300ms
            debounce_time = time.ticks_ms()
            estado_anterior = estado_actual
            return True
    estado_anterior = estado_actual
    return False

# Conectar a WiFi y MQTT
if conectar_wifi():
    client = conectar_broker()

# Bucle principal
while True:
    if detectar_impacto():
        mensaje = "Impacto detectado: " + str(time.ticks_ms())
        print(mensaje)
        client.publish(MQTT_TOPIC_PUB, mensaje)
    
    time.sleep(1)  # Revisar cada 50ms para mejor capacidad de respuesta