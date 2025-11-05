import logging
from aiocoap import resource, Message, Context
from aiocoap.numbers import Code
import requests
import json

# Configuración de Orion
ORION_URL = "http://127.0.0.1:1026/v2/entities"

# Recurso que procesa las solicitudes CoAP
class SaludRecurso(resource.Resource):
    def __init__(self):
        super().__init__()

    async def render_put(self, request):
        try:
            # Parsear el payload recibido
            payload = json.loads(request.payload.decode('utf-8'))
            entidad_id = payload.get("id")
            nueva_salud = payload.get("salud")

            if not entidad_id or not nueva_salud:
                return Message(code=Code.BAD_REQUEST, payload=b"ID o salud no proporcionados")

            # Enviar la actualización a Orion
            url_orion = f"{ORION_URL}/{entidad_id}/attrs"
            headers = {"Content-Type": "application/json"}
            data = {
                "salud": {
                    "value": nueva_salud,
                    "type": "Text"
                }
            }
            response = requests.patch(url_orion, headers=headers, data=json.dumps(data))

            if response.status_code in (200, 204):
                return Message(code=Code.CHANGED, payload=b"Salud actualizada correctamente en Orion")
            else:
                error_message = f"Error al actualizar en Orion: {response.status_code} {response.text}"
                return Message(code=Code.BAD_GATEWAY, payload=error_message.encode())

        except Exception as e:
            logging.error(f"Error procesando la solicitud: {e}")
            return Message(code=Code.INTERNAL_SERVER_ERROR, payload=b"Error interno del servidor")

# Crear y ejecutar el servidor CoAP
def main():
    logging.basicConfig(level=logging.INFO)

    # Crear el árbol de recursos
    root = resource.Site()
    root.add_resource(('salud',), SaludRecurso())

    # Iniciar el servidor
    asyncio.run(Context.create_server_context(root, bind=("127.0.0.1", 5683)))
    print("Servidor CoAP iniciado en el puerto 5683...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

if __name__ == "__main__":
    import asyncio
    main()
