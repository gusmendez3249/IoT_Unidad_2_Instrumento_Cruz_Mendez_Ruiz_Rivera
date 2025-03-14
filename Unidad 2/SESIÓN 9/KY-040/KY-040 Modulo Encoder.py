from umqtt.simple import MQTTClient
from machine import Pin
import network
import time

# Configuración WiFi
WIFI_SSID = "GUSTAVO"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_BROKER = "192.168.137.217"
MQTT_USER = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "ky040_rotary"
MQTT_PORT = 1883
MQTT_TOPIC_PUB = "cm/trabajo/proximidad"

# Configuración KY-040
CLK_PIN = 4  # Pin CLK del encoder
DT_PIN = 5   # Pin DT del encoder
SW_PIN = 16   # Pin del botón
DEBOUNCE_TIME = 0.02  # 20ms para eliminar rebotes

# Inicializar pines
clk = Pin(CLK_PIN, Pin.IN)
dt = Pin(DT_PIN, Pin.IN)
sw = Pin(SW_PIN, Pin.IN, Pin.PULL_UP)

# Variables de estado
ultimo_estado_clk = clk.value()
ultimo_estado_boton = 1
ultimo_giro = 0

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

def publicar_giro(direccion):
    mensaje = "Derecha" if direccion else "Izquierda"
    client.publish(MQTT_TOPIC_PUB, mensaje)
    print(f"Giro: {mensaje}")

def publicar_boton():
    client.publish(MQTT_TOPIC_PUB, "Boton presionado")
    print("Botón presionado")

# Inicialización
if conectar_wifi():
    client = conectar_broker()

# Bucle principal
try:
    while True:
        # Lectura del encoder
        estado_clk = clk.value()
        if estado_clk != ultimo_estado_clk:
            if dt.value() != estado_clk:
                publicar_giro(1)  # Giro derecha
            else:
                publicar_giro(0)  # Giro izquierda
            ultimo_estado_clk = estado_clk
        
        # Lectura del botón
        estado_boton = sw.value()
        if estado_boton != ultimo_estado_boton:
            if estado_boton == 0:
                publicar_boton()
            ultimo_estado_boton = estado_boton
        
        time.sleep(DEBOUNCE_TIME)

except Exception as e:
    print("Error:", e)
    client.disconnect()