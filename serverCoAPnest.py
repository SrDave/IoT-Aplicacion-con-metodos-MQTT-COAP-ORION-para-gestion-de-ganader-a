import logging
import asyncio
from aiocoap import resource, Message, Context
from aiocoap.numbers import Code
import requests
import json
import nest_asyncio

# Aplicar compatibilidad para entornos con bucles activos
nest_asyncio.apply()

# Configuración de Orion
ORION_URL = "http://127.0.0.1:1026/v2/entities"

# Recurso que procesa las solicitudes CoAP
class SaludRecurso(resource.Resource):
    def __init__(self):
        super().__init__()

    async def render_patch(self, request):
        logging.info(f"Solicitud recibida: {request.payload.decode('utf-8')}")
        try:
            payload = json.loads(request.payload.decode('utf-8'))
            entidad_id = payload.get("id")
            nueva_salud = payload.get("salud")
    
            if not entidad_id or not nueva_salud:
                logging.warning("ID o salud no proporcionados")
                return Message(code=Code.BAD_REQUEST, payload=b"ID o salud no proporcionados")
    
            url_orion = f"{ORION_URL}/{entidad_id}/attrs"
            headers = {"Content-Type": "application/json"}
            data = {
                "salud": {
                    "value": nueva_salud,
                    "type": "Text"
                }
            }
            logging.info(f"Enviando actualización a Orion: {data}")
            response = requests.patch(url_orion, headers=headers, data=json.dumps(data))
    
            if response.status_code in (200, 204):
                logging.info("Actualización exitosa en Orion")
                return Message(code=Code.CHANGED, payload=b"Salud actualizada correctamente en Orion")
            else:
                error_message = f"Error al actualizar en Orion: {response.status_code} {response.text}"
                logging.error(error_message)
                return Message(code=Code.BAD_GATEWAY, payload=error_message.encode())
        except Exception as e:
            logging.error(f"Error procesando la solicitud: {e}")
            return Message(code=Code.INTERNAL_SERVER_ERROR, payload=b"Error interno del servidor")


# Crear y ejecutar el servidor CoAP
async def iniciar_servidor():
    logging.basicConfig(level=logging.INFO)

    # Crear el árbol de recursos
    root = resource.Site()
    root.add_resource(('salud',), SaludRecurso())

    # Crear el contexto del servidor CoAP
    await Context.create_server_context(root, bind=("127.0.0.1", 5683))
    print("Servidor CoAP iniciado en el puerto 5683...")
    await asyncio.Future()  # Mantener el servidor activo

def main():
    asyncio.run(iniciar_servidor())

if __name__ == "__main__":
    main()
