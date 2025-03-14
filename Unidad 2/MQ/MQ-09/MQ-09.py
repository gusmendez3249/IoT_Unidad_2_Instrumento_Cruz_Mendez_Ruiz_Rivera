from umqtt.simple import MQTTClient
from machine import Pin, ADC
import network
import time

# Configuración WiFi
WIFI_SSID = "GUSTAVO"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_BROKER = "192.168.137.217"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "mq9_gas"
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "cm/trabajo/proximidad"

# Configuración MQ-9
SENSOR_PIN = 34  # GPIO34 (ADC1 CH6)
CALIBRACION_AIRE_LIMPO = 1500  # Valor en aire limpio
UMBRAL_PELIGRO = 2500          # Valor para considerar peligro
INTERVALO_LECTURA = 2          # Segundos entre lecturas

# Inicializar ADC
sensor_gas = ADC(Pin(SENSOR_PIN))
sensor_gas.atten(ADC.ATTN_11DB)  # Rango completo 0-3.3V

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

def nivel_gas(valor):
    if valor < CALIBRACION_AIRE_LIMPO + 500:
        return "Aire Limpio"
    elif valor < UMBRAL_PELIGRO:
        return "Advertencia"
    else:
        return "PELIGRO!"

# Inicialización
if conectar_wifi():
    client = conectar_broker()

# Bucle principal
try:
    estado_anterior = ""
    while True:
        # Leer valor analógico (0-4095)
        valor = sensor_gas.read()
        
        # Determinar nivel
        estado_actual = nivel_gas(valor)
        
        # Publicar solo si cambia el estado
        if estado_actual != estado_anterior:
            client.publish(MQTT_TOPIC_PUB, estado_actual)
            print(f"Valor: {valor} - Estado: {estado_actual}")
            estado_anterior = estado_actual
        
        time.sleep(2)

except Exception as e:
    print("Error:", e)
    client.disconnect()