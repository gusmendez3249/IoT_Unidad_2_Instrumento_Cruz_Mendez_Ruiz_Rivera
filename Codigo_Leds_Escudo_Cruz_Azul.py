from machine import Pin
import time

# Definir pines
led1 = Pin(2, Pin.OUT)  # LED conectado al pin 2
led2 = Pin(4, Pin.OUT)  # LED conectado al pin 4

# Función para crear una secuencia bonita
def bonita_secuencia():
    while True:
        # Alternar LEDs rápidamente (efecto de parpadeo alterno)
        for _ in range(5):  # Repetir 5 veces
            led1.value(1)  # Encender LED 1
            led2.value(0)  # Apagar LED 2
            time.sleep(0.1)  # Esperar 100 ms
            led1.value(0)  # Apagar LED 1
            led2.value(1)  # Encender LED 2
            time.sleep(0.1)  # Esperar 100 ms

        # Encender ambos LEDs juntos y luego apagarlos
        led1.value(1)  # Encender LED 1
        led2.value(1)  # Encender LED 2
        time.sleep(0.5)  # Esperar 500 ms
        led1.value(0)  # Apagar LED 1
        led2.value(0)  # Apagar LED 2
        time.sleep(0.5)  # Esperar 500 ms

        # Encender y apagar LEDs en secuencia inversa
        led1.value(1)  # Encender LED 1
        time.sleep(0.3)  # Esperar 300 ms
        led2.value(1)  # Encender LED 2
        time.sleep(0.3)  # Esperar 300 ms
        led1.value(0)  # Apagar LED 1
        time.sleep(0.3)  # Esperar 300 ms
        led2.value(0)  # Apagar LED 2
        time.sleep(0.3)  # Esperar 300 ms

# Ejecutar la secuencia
bonita_secuencia()