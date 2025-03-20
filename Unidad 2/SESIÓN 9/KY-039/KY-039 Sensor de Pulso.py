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
MQTT_CLIENT_ID = "ky039_corazon"
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "cm/trabajo/proximidad"

# Configuración KY-039
sensor_pulso = ADC(Pin(34))  # Usar pin ADC (GPIO34)
sensor_pulso.atten(ADC.ATTN_11DB)  # Rango completo 0-3.3V

# Parámetros de detección
UMBRAL = 2500  # Ajustar según condiciones de luz
INTERVALO_MUESTREO = 0.5  # 20ms (50 muestras/segundo)
HISTORIAL_MUESTRAS = 150  # 3 segundos de datos
MINIMO_LATIDOS = 30  # BPM mínimo válido
MAXIMO_LATIDOS = 200  # BPM máximo válido

# Variables de estado
muestras = []
ultimo_pico = 0
bpm = 0

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

def detectar_pulso(valor):
    global ultimo_pico, bpm
    
    # Agregar muestra al historial
    muestras.append(valor)
    if len(muestras) > HISTORIAL_MUESTRAS:
        muestras.pop(0)
    
    # Detectar picos (flancos ascendentes)
    if len(muestras) > 2 and valor > UMBRAL and muestras[-2] < UMBRAL:
        ahora = time.time()
        
        if ultimo_pico > 0:
            intervalo = ahora - ultimo_pico
            if intervalo > 0:
                bpm_calculado = 60 / intervalo
                if MINIMO_LATIDOS <= bpm_calculado <= MAXIMO_LATIDOS:
                    bpm = int((bpm * 0.7) + (bpm_calculado * 0.3))  # Suavizado
        
        ultimo_pico = ahora
        return True
    return False

# Inicialización
if conectar_wifi():
    client = conectar_broker()

# Bucle principal
try:
    while True:
        valor = sensor_pulso.read()
        
        if detectar_pulso(valor):
            client.publish(MQTT_TOPIC_PUB, str(bpm))
            print(f"Pulso detectado: {bpm} BPM")
        
        time.sleep(INTERVALO_MUESTREO)

except Exception as e:
    print("Error:", e)
    client.disconnect()