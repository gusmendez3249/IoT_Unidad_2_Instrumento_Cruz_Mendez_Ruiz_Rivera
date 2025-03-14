from umqtt.simple import MQTTClient
from machine import ADC, Pin
import network
import time

# Configuración WiFi
WIFI_SSID = "GUSTAVO"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_BROKER = "192.168.137.217"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "sensor_flama"
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "cm/trabajo/proximidad"

# Configuración del sensor de flama KY-026
sensor_flama = ADC(Pin(34))  # Conectar al pin analógico 34
sensor_flama.atten(ADC.ATTN_11DB)  # Rango completo de 0-3.3V

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

# Función para leer intensidad de flama
def leer_flama():
    valor = sensor_flama.read()  # Lectura analógica (0-4095)
    print(f"Valor del sensor: {valor}")
    
    # Valores más bajos = mayor intensidad de flama detectada
    # (ajustar estos valores según calibración)
    if valor < 1000:
        return "No se detecta flama"
    elif valor < 2000:
        return "Flama detectada (baja intensidad)"
    elif valor < 3000:
        return "Flama detectada (media intensidad)"
    else:
        return "FLAMA DETECTADA! (alta intensidad)"

# Conectar a WiFi y MQTT
if conectar_wifi():
    client = conectar_broker()

# Bucle principal
while True:
    # Leer estado del sensor
    estado = leer_flama()
    print(f"Estado del sensor: {estado}")

    # Publicar el estado en MQTT
    client.publish(MQTT_TOPIC_PUB, estado)

    time.sleep(3)  # Lectura más rápida para detección rápida