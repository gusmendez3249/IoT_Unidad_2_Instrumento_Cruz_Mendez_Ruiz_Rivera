import network
from umqtt.simple import MQTTClient
from machine import Pin, ADC
import time

# Configuración WiFi
WIFI_SSID = "GUSTAVO"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_BROKER = "192.168.137.217"
MQTT_CLIENT_ID = ""
MQTT_TOPIC = "cm/trabajo/proximidad"
MQTT_PORT = 1883

# Configurar el sensor de fotorresistencia (KY-018) en un pin analógico (por ejemplo, GPIO34)
sensor_luz = ADC(Pin(34))  # GPIO donde está conectada la fotorresistencia
sensor_luz.atten(ADC.ATTN_6DB)  # Rango de 0 a 2V

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

if client:
    while True:
        try:
            # Leer el valor de la fotorresistencia (0-4095)
            valor_luz = sensor_luz.read()
            
            # Mostrar el valor de la luz en el monitor serial
            print(f"Valor de luz: {valor_luz}")
            
            # Publicar el valor de la luz en el topic MQTT
            client.publish(MQTT_TOPIC, str(valor_luz))
            
            time.sleep(2)  # Esperar 2 segundos antes de tomar otra lectura

        except Exception as e:
            print(f"Error en el loop MQTT: {e}")
            time.sleep(5)
