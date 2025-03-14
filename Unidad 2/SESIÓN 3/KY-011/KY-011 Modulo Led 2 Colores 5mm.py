import network
from umqtt.simple import MQTTClient
from machine import Pin
import time

# Configuración WiFi
WIFI_SSID = "GUSTAVO"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_BROKER = "192.168.137.217"
MQTT_CLIENT_ID = "ESP32_ACTUADOR"
MQTT_TOPIC = "cm/trabajo/proximidad"
MQTT_PORT = 1883

# Configurar el actuador de 2 colores (único pin, supongamos que es un LED bicolor)
actuador_color = Pin(4, Pin.OUT)  # Pin de salida digital

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

# Bucle infinito para controlar el actuador de color
while True:
    # Supongamos que 'estado' se determina a partir de un valor que cambia
    # Por ejemplo, 0 será un color (rojo) y 1 será otro color (verde)
    estado = actuador_color.value()  # Leer el estado del actuador (inicialmente en 0 o 1)

    if estado == 1:
        mensaje = "Color Rojo encendido"
        actuador_color.value(0)  # Cambiar el actuador a color 1 (veremos si cambia a otro estado)
    else:
        mensaje = "Color Amarillo encendido"
        actuador_color.value(1)  # Cambiar el actuador a color 2 (rojo, por ejemplo)

    print(mensaje)
    
    if client:
        client.publish(MQTT_TOPIC, mensaje)

    time.sleep(3)  # Reducir tiempo de muestreo para mejor respuesta