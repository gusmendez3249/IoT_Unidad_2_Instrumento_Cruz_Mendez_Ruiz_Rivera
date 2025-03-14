import network
from umqtt.simple import MQTTClient
from machine import Pin
import time

# Configuración WiFi
WIFI_SSID = "GUSTAVO"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_BROKER = "192.168.137.217"
MQTT_CLIENT_ID = ""
MQTT_TOPIC = "cm/trabajo/proximidad"
MQTT_PORT = 1883

# Configurar el sensor KY-002 (vibración) en GPIO 4
sensor_vibracion = Pin(17, Pin.IN)

# Función para conectar a WiFi
def conectar_wifi():
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    
    for _ in range(30):  # Esperar 9 segundos máximo
        if sta_if.isconnected():
            print("✅ WiFi conectada!")
            return
        time.sleep(0.3)
    
    print("⚠️ Error: No se pudo conectar a WiFi")

# Función para conectar al broker MQTT con reintento
def conectar_broker():
    global client
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"✅ Conectado a MQTT Broker: {MQTT_BROKER}, Topic: {MQTT_TOPIC}")
    except Exception as e:
        print(f"⚠️ Error al conectar con MQTT: {e}")
        client = None  # Marcar que la conexión falló

# Conectar a WiFi y MQTT
conectar_wifi()
conectar_broker()

# Bucle principal: Detectar vibraciones y enviar MQTT
while True:
    try:
        if sensor_vibracion.value() == 1:  # Detecta vibración
            print("💥 Vibración detectada!")
            
            if client:  # Verificar si MQTT está conectado
                try:
                    client.publish(MQTT_TOPIC, "Vibración detectada")
                except Exception as e:
                    print(f"⚠️ Error al enviar MQTT: {e}")
                    conectar_broker()  # Intentar reconectar MQTT
            
            time.sleep(0.5)  # Pequeño delay para evitar múltiples detecciones

    except Exception as e:
        print(f"⚠️ Error en bucle principal: {e}")
        time.sleep(3)  # Esperar antes de reintentar