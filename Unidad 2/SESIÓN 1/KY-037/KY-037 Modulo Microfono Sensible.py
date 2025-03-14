import network

from umqtt.simple import MQTTClient

from machine import Pin, ADC

import time



# Configuración WiFi (ANTONIOBM)

WIFI_SSID = "GUSTAVO"

WIFI_PASSWORD = "12345678"



# Configuración MQTT

MQTT_BROKER = "192.168.137.217"

MQTT_USER = ""

MQTT_PASSWORD = ""

MQTT_CLIENT_ID = "ESP32_KY038"

MQTT_TOPIC = "cm/trabajo/proximidad"

MQTT_PORT = 1883



# Configuración del KY-038 (Lectura Analógica)

SENSOR_PIN = 34  # GPIO para A0 (debe ser un ADC)

sensor = ADC(Pin(SENSOR_PIN))  

sensor.atten(ADC.ATTN_11DB)  # Configuración para leer de 0 a 3.3V (rango 0-4095)



# Función para conectar a WiFi

def conectar_wifi():

    print("Conectando a WiFi…", end="")

    sta_if = network.WLAN(network.STA_IF)

    sta_if.active(True)

    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)

    while not sta_if.isconnected():

        print(".", end="")

        time.sleep(0.3)

    print("\nWiFi Conectada!")



# Función para conectar al bróker MQTT

def conectar_broker():

    try:

        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT, user=MQTT_USER, password=MQTT_PASSWORD)

        client.connect()

        print(f"Conectado a MQTT Bróker: {MQTT_BROKER}, Topic: {MQTT_TOPIC}")

        return client

    except Exception as e:

        print(f"Error al conectar MQTT: {e}")

        return None



# Conectar a WiFi y MQTT

conectar_wifi()

client = conectar_broker()



ultimo_valor = sensor.read()  # Guardar la primera lectura del sensor



# Bucle principal

while True:

    valor_actual = sensor.read()  # Leer la intensidad del sonido (0 - 4095)

    

    # Si la diferencia es mayor a 100 (ajustable), enviamos el dato

    if abs(valor_actual - ultimo_valor) > 100:

        print(f"🎤 Nivel de sonido: {valor_actual}")  # Mostrar en consola

        if client:

            client.publish(MQTT_TOPIC, str(valor_actual))  # Enviar a MQTT

        

        ultimo_valor = valor_actual  # Actualizar última lectura enviada

    

    time.sleep(0.1)  # Pequeña pausa antes de la siguiente lectura
