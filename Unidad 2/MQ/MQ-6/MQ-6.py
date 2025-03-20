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
MQTT_CLIENT_ID = "sensor_mq6"
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "cm/trabajo/proximidad"

# Configuración del sensor MQ-6
sensor_gas = ADC(Pin(34))  # Conectar al pin 34
sensor_gas.atten(ADC.ATTN_11DB)  # Rango completo de 3.3V
sensor_gas.width(ADC.WIDTH_12BIT)  # Precisión de 12 bits (0-4095)

# Tiempo de calentamiento del sensor (20 segundos)
print("Calentando sensor MQ-6...")
time.sleep(20)

def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)

    start_time = time.time()
    while not sta_if.isconnected():
        if time.time() - start_time > 15:
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

def leer_concentracion_glp():
    valor = sensor_gas.read()
    voltaje = valor * (3.3 / 4095)  # Convertir a voltaje
    rs_ro = (5.0 - voltaje) / voltaje  # Calcular relación RS/RO
    
    print(f"Lectura: {valor} | Voltaje: {voltaje:.2f}V | RS/RO: {rs_ro:.2f}")
    
    # Umbrales ajustados para GLP (LPG)
    if rs_ro < 1.5:
        return "Aire limpio"
    elif rs_ro > 1.5:
        return "GLP detectado (bajo)"
    elif rs_ro > 2.5:
        return "GLP detectado (moderado)"
    else:
        return "PELIGRO! Alta concentración GLP"

if conectar_wifi():
    client = conectar_broker()

while True:
    estado = leer_concentracion_glp()
    client.publish(MQTT_TOPIC_PUB, estado)
    print(f"Estado: {estado}")
    time.sleep(5)  # Intervalo aumentado para estabilidad