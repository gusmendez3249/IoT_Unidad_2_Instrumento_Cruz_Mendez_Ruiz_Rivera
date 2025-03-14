from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient

# Configuración WiFi
WIFI_SSID = "GUSTAVO"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_BROKER = "192.168.137.217"
MQTT_CLIENT_ID = "ESP32_KY024"
MQTT_TOPIC = "cm/trabajo/proximidad"
MQTT_PORT = 1883

# Configuración del KY-024
PIN_SENSOR = 34  # GPIO34 para señal analógica
UMBRAL_DETECCION = 2000  # Ajustar según sensibilidad requerida

# Inicializar hardware
sensor = ADC(Pin(PIN_SENSOR))
sensor.atten(ADC.ATTN_11DB)  # Rango completo 0-3.3V

# Variable para almacenar el último estado
ultimo_estado = False

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

# Función para leer el sensor
def leer_sensor():
    valor = sensor.read()  # Leer valor analógico (0-4095)
    return valor > UMBRAL_DETECCION  # True si detecta campo magnético

# Conectar a WiFi
conectar_wifi()

# Conectar al broker MQTT
client = conectar_broker()

# Bucle principal
while True:
    try:
        estado_actual = leer_sensor()
        
        # Solo enviar mensaje si cambia el estado
        if estado_actual != ultimo_estado:
            mensaje = "DETECTADO" if estado_actual else "NO_DETECTADO"
            print(f"Estado: {mensaje} - Valor: {sensor.read()}")
            
            if client:
                try:
                    client.publish(MQTT_TOPIC, mensaje)
                    print(f"✅ Mensaje enviado: {mensaje}")
                except Exception as e:
                    print(f"⚠ Error MQTT: {e}")
                    client = conectar_broker()
            
            ultimo_estado = estado_actual
        
        time.sleep(1)  # Tiempo entre lecturas
        
    except Exception as e:
        print(f"⚠ Error en bucle principal: {e}")
        time.sleep(3)