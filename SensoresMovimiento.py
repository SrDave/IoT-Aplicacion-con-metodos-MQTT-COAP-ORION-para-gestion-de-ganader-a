import requests
import time

# URL del broker NGSI (ajusta según tu configuración)
BROKER_URL = "http://127.0.0.1:1026/v2/entities"

# Definir velocidades por tipo de entidad
VELOCIDADES = {
    "Oveja": 10,
    "Vaca": 5,
    "Cabra": 20,
    "Cerdo": 7,
    "Perro": 30
}

# Coordenadas finales (destino)
lat_final = 43.1485969
lon_final = -4.6457931

def obtener_entidades():
    """Realiza una petición GET para obtener las entidades del broker."""
    try:
        response = requests.get(BROKER_URL)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error al obtener entidades: {e}")
        return []

def filtrar_entidades_con_coordenadas(entidades):
    """Filtra las entidades que tienen latitud y longitud directamente en su estructura."""
    return [
        entidad for entidad in entidades
        if "latitud" in entidad and "longitud" in entidad
    ]

def mover_entidad(entidad):
    """Mueve una entidad en función de su tipo y velocidad."""
    tipo = entidad["type"]
    velocidad = VELOCIDADES.get(tipo, 0)  # Velocidad por defecto si el tipo no está definido

    # Coordenadas actuales
    lat = entidad["latitud"]["value"]
    lon = entidad["longitud"]["value"]

    # Calcular diferencias y aplicar movimiento
    delta_lat = lat_final - lat
    delta_lon = lon_final - lon
    new_lat = lat + (delta_lat * velocidad / 3600)
    new_lon = lon + (delta_lon * velocidad / 3600)

    # Actualizar en el broker
    try:
        entidad_id = entidad["id"]
        url = f"{BROKER_URL}/{entidad_id}/attrs"
        payload = {
            "latitud": {"value": new_lat, "type": "Float"},
            "longitud": {"value": new_lon, "type": "Float"}
        }
        headers = {"Content-Type": "application/json"}
        response = requests.patch(url, json=payload, headers=headers)
        if response.status_code == 204:
            print(f"Entidad {entidad_id} movida a nueva posición: ({new_lat:.6f}, {new_lon:.6f})")
        else:
            print(f"Error al actualizar entidad {entidad_id}: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error al mover entidad {entidad['id']}: {e}")

def main():
    """Función principal que simula el movimiento de las entidades."""
    while True:
        entidades = obtener_entidades()
        if not entidades:
            print("No se encontraron entidades.")
            time.sleep(5)
            continue

        entidades_con_coordenadas = filtrar_entidades_con_coordenadas(entidades)
        if not entidades_con_coordenadas:
            print("No hay entidades con coordenadas válidas.")
            time.sleep(5)
            continue

        for entidad in entidades_con_coordenadas:
            mover_entidad(entidad)

        print("Ciclo completo. Moviendo entidades...")
        time.sleep(5)  # Esperar 5 segundos antes de la siguiente actualización

if __name__ == "__main__":
    main()
