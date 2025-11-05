import http.server
import socketserver
from urllib.parse import urlparse
from urllib.parse import parse_qs
import json

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        # Devolvemos 200 porque la petición es exitosa: ha alcanzado el servidor y se genera respuesta.
        self.send_response(200)

        # Se configura la cabecera con el tipo de contenido que vamos a devolver (JSON)
        self.send_header("Content-type", "application/json")

        # Se cierra la cabecera.
        self.end_headers()

        # Se obtiene el tamaño del contenido recibido para poder procesarlo.
        content_length = int(self.headers['Content-Length'])

        # Se obtienen los datos de la petición. El objeto post_data contiene ahora la información del mensaje de notificación enviado por ORION.
        post_data = self.rfile.read(content_length) 

        # Se convierte a un objeto JSON. Con esto ya podría navegarse por los atributos recibidos desde ORION.    
        data_string = post_data.decode('utf8').replace("'", '"')            
        json_data = json.loads(data_string)
       
        
        # Esta es la reacción a la notificación. Esta lógica podría modificarse a elección del programador. Como funcionalidad básica, se imprime por pantalla el contenido recibido.
        
        print(data_string)
        
        print(json.dumps(json_data))
        
        return

# Creación del objeto de la clase anterior.
handler_object = MyHttpRequestHandler

# Configuración del puerto.
PORT = 8181

# Declaración del servidor.
my_server = socketserver.TCPServer(("", PORT), handler_object)

# Inicialización del servidor, que estará siempre ejecutándose.
my_server.serve_forever()