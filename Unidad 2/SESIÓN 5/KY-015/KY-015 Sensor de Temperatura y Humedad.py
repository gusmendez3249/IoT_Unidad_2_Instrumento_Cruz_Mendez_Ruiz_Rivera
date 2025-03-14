import network
from umqtt.simple import MQTTClient
import dht
from machine import Pin
import time

# Configuración WiFi
WIFI_SSID = "GUSTAVO"
WIFI_PASSWORD = "12345678"

# Configuración MQTT
MQTT_BROKER = "192.168.137.217"
MQTT_CLIENT_ID = ""
MQTT_TOPIC_TEMP = "cm/trabajo/proximidad"
MQTT_TOPIC_HUM = "cm/trabajo/"
MQTT_PORT = 1883

# Configurar el sensor de temperatura y humedad KY-015 (DHT22) en GPIO 4
sensor_dht = dht.DHT22(Pin(4))  # Cambia el pin según tu conexión (por ejemplo, GPIO4)

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
        print(f"Conectado a MQTT Broker: {MQTT_BROKER}")
        return client
    except Exception as e:
        print(f"Error al conectar con MQTT: {e}")
        return None

# Iniciar conexiones
conectar_wifi()
client = conectar_broker()

if client:
    while True:
        try:
            # Leer los datos del sensor KY-015 (DHT22)
            sensor_dht.measure()
            temperatura = sensor_dht.temperature()  # Leer la temperatura en °C
            humedad = sensor_dht.humidity()  # Leer la humedad en %

            # Mostrar los valores de temperatura y humedad
            print(f"Temperatura: {temperatura}°C")
            print(f"Humedad: {humedad}%")
            
            # Publicar los valores de temperatura y humedad en los temas MQTT
            client.publish(MQTT_TOPIC_TEMP, str(temperatura))
            client.publish(MQTT_TOPIC_HUM, str(humedad))
            
            time.sleep(3)  # Esperar 3 segundos antes de tomar otra lectura

        except Exception as e:
            print(f"Error en el loop MQTT: {e}")
            time.sleep(5)
