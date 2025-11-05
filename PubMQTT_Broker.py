import json
import paho.mqtt.client as mqtt
import requests
import random  # Para simular cambios en el peso
import time

# Configuración de ORION y MQTT
ORION_URL = "http://127.0.0.1:1026/v2/entities"
MQTT_BROKER = "127.0.0.1"
MQTT_PORT = 1883
MQTT_TOPIC = "granja/sensores"

# Función para obtener los animales desde ORION
def obtener_animales():
    try:
        response = requests.get(ORION_URL)
        if response.status_code == 200:
            entidades = response.json()
            return [
                {
                    "id": entidad["id"],
                    "peso": entidad.get("peso", {}).get("value", None)
                }
                for entidad in entidades
                if "peso" in entidad
            ]
        else:
            print(f"Error al obtener entidades de ORION: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error de conexión con ORION: {e}")
        return []

# Función para simular un nuevo peso
def generar_nuevo_peso(peso_actual):
    return round(peso_actual + random.uniform(-5, 5), 2)  # Cambios entre -5 y +5 kg

# Publicación en MQTT
def publicar_pesos(client):
    animales = obtener_animales()
    for animal in animales:
        nuevo_peso = generar_nuevo_peso(animal["peso"])
        
        # Crear el mensaje
        mensaje = {
            "id": animal["id"],
            "peso": nuevo_peso
        }
        
        # Publicar el mensaje en el tema
        client.publish(MQTT_TOPIC, json.dumps(mensaje), qos=1)
        print(f"Publicado: {mensaje}")
        time.sleep(1)


# Configuración del cliente MQTT
def main():
    client = mqtt.Client()
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.loop_start()
    
    try:
        while True:
            publicar_pesos(client)
    except KeyboardInterrupt:
        print("Finalizando...")
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main()
