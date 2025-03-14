from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient

# Configuración WiFi
WIFI_SSID = "GUSTAVO"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_BROKER = "192.168.137.217"
MQTT_CLIENT_ID = "ESP32_M-A"
MQTT_TOPIC = "cm/trabajo/proximidad"
MQTT_PORT = 1883

# Configuración del Joystick
pin_x = ADC(Pin(34))  # Conectar el eje X del joystick al GPIO34
pin_y = ADC(Pin(35))  # Conectar el eje Y del joystick al GPIO35
pin_x.atten(ADC.ATTN_11DB)  # Configurar el rango de lectura (0-3.3V)
pin_y.atten(ADC.ATTN_11DB)

# Variable para almacenar la última dirección
ultima_direccion = "Centro"

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
    
    print("⚠ Error: No se pudo conectar a WiFi")
    raise Exception("No se pudo conectar a WiFi")

# Función para conectar al broker MQTT
def conectar_broker():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"✅ Conectado a MQTT Broker: {MQTT_BROKER}, Topic: {MQTT_TOPIC}")
        return client
    except Exception as e:
        print(f"⚠ Error al conectar con MQTT: {e}")
        return None

# Función para leer la dirección del joystick
def leer_direccion():
    x = pin_x.read()  # Leer el valor del eje X (0-4095)
    y = pin_y.read()  # Leer el valor del eje Y (0-4095)
    
    # Determinar la dirección basada en los valores leídos
    if x < 1000:
        return "Izquierda"
    elif x > 3000:
        return "Derecha"
    elif y < 1000:
        return "Arriba"
    elif y > 3000:
        return "Abajo"
    else:
        return "Centro"

# Conectar a WiFi
conectar_wifi()

# Conectar al broker MQTT
client = conectar_broker()

# Bucle principal
while True:
    try:
        direccion_actual = leer_direccion()  # Obtener la dirección actual
        
        # Solo enviar un mensaje si la dirección ha cambiado
        if direccion_actual != ultima_direccion:
            print(f"Dirección: {direccion_actual}")
            
            if client:  # Si hay conexión MQTT
                try:
                    client.publish(MQTT_TOPIC, direccion_actual)  # Enviar dirección al broker MQTT
                    print(f"✅ Mensaje enviado a MQTT: {direccion_actual}")
                except Exception as e:
                    print(f"⚠ Error al enviar MQTT: {e}")
                    client = conectar_broker()  # Intentar reconectar
        
            ultima_direccion = direccion_actual  # Actualizar la última dirección
        
        time.sleep(0.1)  # Esperar 0.1 segundos entre lecturas
        
    except Exception as e:
        print(f"⚠ Error en bucle principal: {e}")
        time.sleep(3)