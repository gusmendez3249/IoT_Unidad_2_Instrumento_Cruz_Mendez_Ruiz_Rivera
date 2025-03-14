from machine import Pin
import time
import network
from umqtt.simple import MQTTClient

# Configuración WiFi
WIFI_SSID = "GUSTAVO"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_BROKER = "192.168.137.217"
MQTT_CLIENT_ID = "ESP32_KY021"
MQTT_TOPIC = "cm/trabajo/proximidad"
MQTT_PORT = 1883

# Configuración del KY-021
PIN_SENSOR = 34  # GPIO34 para entrada digital
DEBOUNCE_TIME = 50  # Tiempo antirrebote en ms

# Inicializar hardware
sensor = Pin(PIN_SENSOR, Pin.IN, Pin.PULL_UP)  # Usar resistencia pull-up interna

# Variables de estado
ultimo_estado = sensor.value()
ultimo_tiempo = time.ticks_ms()

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
    raise Exception("Error de conexión WiFi")

# Función para conectar al broker MQTT
def conectar_broker():
    try:
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"✅ Conectado a MQTT Broker: {MQTT_BROKER}")
        return client
    except Exception as e:
        print(f"⚠ Error al conectar con MQTT: {e}")
        return None

# Función antirrebote
def estado_estable():
    global ultimo_tiempo, ultimo_estado
    estado_actual = sensor.value()
    
    if estado_actual != ultimo_estado:
        if time.ticks_diff(time.ticks_ms(), ultimo_tiempo) > DEBOUNCE_TIME:
            ultimo_estado = estado_actual
            ultimo_tiempo = time.ticks_ms()
            return estado_actual
    return None

# Conectar a WiFi
conectar_wifi()

# Conectar al broker MQTT
client = conectar_broker()

# Bucle principal
while True:
    try:
        estado = estado_estable()
        
        if estado is not None:
            mensaje = "CERRADO" if estado == 0 else "ABIERTO"  # 0 = contacto cerrado (campo magnético detectado)
            print(f"Estado: {mensaje}")
            
            if client:
                try:
                    client.publish(MQTT_TOPIC, mensaje)
                    print(f"✅ Mensaje enviado: {mensaje}")
                except Exception as e:
                    print(f"⚠ Error MQTT: {e}")
                    client = conectar_broker()
        
        time.sleep(0.1)  # Ciclo rápido para mejor respuesta
        
    except Exception as e:
        print(f"⚠ Error en bucle principal: {e}")
        time.sleep(3)