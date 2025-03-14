import network
from umqtt.simple import MQTTClient
from machine import Pin, PWM
import time

# Configuración WiFi
WIFI_SSID = "GUSTAVO"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_BROKER = "192.168.137.217"
MQTT_CLIENT_ID = "ESP32_BUZZER"
MQTT_TOPIC = "cm/trabajo/proximidad"
MQTT_PORT = 1883

# Configurar el buzzer pasivo (KY-006) usando PWM
buzzer = PWM(Pin(4))  # Buzzer conectado al pin 4

# Notas musicales (frecuencias en Hz)
NOTAS = {
    "C4": 262, "D4": 294, "E4": 330, "F4": 349, "G4": 392,
    "A4": 440, "B4": 494, "C5": 523
}

# Melodía (Twinkle Twinkle Little Star)
MELODIA = [
    ("C4", 0.5), ("C4", 0.5), ("G4", 0.5), ("G4", 0.5),
    ("A4", 0.5), ("A4", 0.5), ("G4", 1),
    ("F4", 0.5), ("F4", 0.5), ("E4", 0.5), ("E4", 0.5),
    ("D4", 0.5), ("D4", 0.5), ("C4", 1)
]

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

# Función para reproducir una melodía
def reproducir_melodia():
    for nota, duracion in MELODIA:
        buzzer.freq(NOTAS[nota])  # Establecer la frecuencia
        buzzer.duty(512)  # Activar buzzer
        time.sleep(duracion)  # Mantener la nota
        buzzer.duty(0)  # Apagar buzzer entre notas
        time.sleep(0.1)  # Pequeña pausa

# Iniciar conexiones
conectar_wifi()
client = conectar_broker()

# Reproducir la melodía en bucle
while True:
    print("Reproduciendo melodía")
    reproducir_melodia()
    if client:
        client.publish(MQTT_TOPIC, "Melodía reproducida")
    time.sleep(2)  # Pausa antes de repetir la melodía
