from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración WiFi
WIFI_SSID = "GUSTAVO"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_BROKER = "192.168.137.217"
MQTT_CLIENT_ID = "ESP32_SR602"
MQTT_TOPIC = "cm/trabajo/proximidad"
MQTT_PORT = 1883

# Configuración del SR602
PIN_SENSOR = 4  # GPIO14 para entrada digital (D5)
TIEMPO_INACTIVIDAD = 10  # Segundos para considerar "sin movimiento"

# Variables de estado
ultimo_estado = False
ultimo_evento = time.time()

def conectar_wifi():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    if not sta_if.isconnected():
        print("Conectando WiFi...")
        sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
        while not sta_if.isconnected():
            time.sleep(0.5)
    print("WiFi OK - IP:", sta_if.ifconfig()[0])

def conectar_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
    try:
        client.connect()
        print("MQTT Conectado")
        return client
    except Exception as e:
        print("Error MQTT:", e)
        return None

# Inicializar hardware
sensor = Pin(PIN_SENSOR, Pin.IN)
client = None
conectar_wifi()
client = conectar_mqtt()

while True:
    try:
        estado_actual = sensor.value()  # 1 = Movimiento detectado
        
        # Detectar cambios de estado
        if estado_actual != ultimo_estado:
            mensaje = "MOVIMIENTO_DETECTADO" if estado_actual else "SIN_MOVIMIENTO"
            print(mensaje)
            if client:
                client.publish(MQTT_TOPIC, mensaje)
            ultimo_estado = estado_actual
            ultimo_evento = time.time()
        
        # Enviar estado periódico si hay movimiento continuo
        elif estado_actual and (time.time() - ultimo_evento) >= TIEMPO_INACTIVIDAD:
            print("MOVIMIENTO_CONTINUO")
            if client:
                client.publish(MQTT_TOPIC, "MOVIMIENTO_CONTINUO")
            ultimo_evento = time.time()
        
        time.sleep(0.1)
        
    except Exception as e:
        print("Error:", e)
        time.sleep(5)