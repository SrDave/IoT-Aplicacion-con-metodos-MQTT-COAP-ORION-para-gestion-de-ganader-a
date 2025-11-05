from PyQt5.QtWebEngineWidgets import QWebEngineView
import paho.mqtt.client as mqtt
import requests
import asyncio
from aiocoap import Message, Context
from aiocoap.numbers import Code
import json
import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QColor
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import  QGraphicsDropShadowEffect, QFileDialog, QMessageBox, QCheckBox
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QUrl, QTimer
from PyQt5 import QtCore, QtWidgets
import folium
from threading import Thread
from qasync import QEventLoop
import numpy as np

# **** APLICACIÓN ****

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi('Proyecto_IoT.ui', self)  # Asegúrate de que esta ruta sea correcta
        self.client = None
        # Encuentra el marcador de posición del mapa (widget vacío)
        placeholder_widget = self.findChild(QtWidgets.QWidget, "widgetMapa")
        
        ''' Aqui defino todos los botones, varables y casillas donde incluiremos texto 
        en la aplicación'''

        # Reemplázalo con QWebEngineView
        self.web_view = QWebEngineView(self)
        layout = placeholder_widget.layout() or QtWidgets.QVBoxLayout(placeholder_widget)
        layout.addWidget(self.web_view)
        
        # Variables
        self.lineIP = self.lineIP
        self.linePUERTO = self.linePUERTO
        self.detener_bucle = False
        # Declarar las listas para almacenar atributos, valores y tipos dinámicos
        self.atributos_inputs = []
        self.valores_inputs = []
        self.tipo_inputs = []
        self.atributos_inputsPUT= []
        self.valores_inputsPUT = []
        self.tipo_inputsPUT = []

        
        # Añadir opciones al comboBox
        self.comboBox.addItem("")
        self.comboBox.addItem("POST")
        self.comboBox.addItem("GET")
        self.comboBox.addItem("PUT")
        self.comboBox.addItem("PATCH")
        self.comboBox.addItem("DELETE")
        self.comboBox.setCurrentIndex(-1)

        
        # Añadir opciones al comboBox

        self.comboBox_2.addItem("Text")
        self.comboBox_2.addItem("Float")
        self.comboBox_2.addItem("Boolean")
        self.comboBox_2.addItem("Number")
        self.comboBox_2.addItem("Integer")
        self.comboBox_2.addItem("Date")
        self.comboBox_2.setCurrentIndex(-1)

        # Añadir opciones al comboBox
        self.comboBox_3.addItem("Text")
        self.comboBox_3.addItem("Float")
        self.comboBox_3.addItem("Boolean")
        self.comboBox_3.addItem("Number")
        self.comboBox_3.addItem("Integer")
        self.comboBox_3.addItem("Date")
        self.comboBox_3.setCurrentIndex(-1)
        
        # Añadir opciones al comboBox
        self.comboBox_4.addItem("Text")
        self.comboBox_4.addItem("Float")
        self.comboBox_4.addItem("Boolean")
        self.comboBox_4.addItem("Number")
        self.comboBox_4.addItem("Integer")
        self.comboBox_4.addItem("Date")
        self.comboBox_4.setCurrentIndex(-1)
        
        self.bt_menu_iz.clicked.connect(self.mover_menu)
        self.bt_menu_dr.clicked.connect(self.mover_menu)
        self.bt_menu_iz_2.clicked.connect(self.mover_menu)
        self.bt_menu_dr_2.clicked.connect(self.mover_menu)

        # Ocultar botones
        self.bt_menu_dr.hide()
        self.bt_menu_dr_2.hide()
        self.bt_minimizar.hide()
        self.BT_menos.hide()
        self.BT_menos_2.hide()
        self.frame_30.hide()
        self.bt_parar_coor.hide()
        self.bt_parar_MQTT.hide()
        self.bt_parar_alarma_3.hide()

        
        # Obtener los paneles desde el archivo .ui
        self.PanelPOST = self.findChild(QtWidgets.QFrame, 'PanelPOST')
        self.PanelGET = self.findChild(QtWidgets.QFrame, 'PanelGET')
        self.PanelPUT = self.findChild(QtWidgets.QFrame, 'PanelPUT')
        self.PanelPATCH = self.findChild(QtWidgets.QFrame, 'PanelPATCH')
        self.PanelDELETE = self.findChild(QtWidgets.QFrame, 'PanelDELETE')


        # Diccionario que mapea opciones a paneles
        self.panels = {
            "POST": self.PanelPOST,
            "GET": self.PanelGET,
            "PUT": self.PanelPUT,
            "PATCH": self.PanelPATCH,
            "DELETE": self.PanelDELETE,
        }
        
        # Inicialmente, ocultar todos los paneles
        self.ocultar_todos_los_paneles()
        
        # Conectar el comboBox a una función
        self.comboBox.currentTextChanged.connect(self.mostrar_panel_correspondiente)
        
        self.frames = []  # Lista para llevar un control de los frames creados


        # Sombra widgets
        self.sombra_frame(self.stackedWidget)
        self.sombra_frame(self.frame_superior)
        self.sombra_frame(self.toolBox)
        self.sombra_frame(self.bt_1)
        self.sombra_frame(self.bt_2)
        self.sombra_frame(self.bt_3)


        self.sombra_frame(self.label_2)

        # Control barra superior
        self.bt_cerrar.clicked.connect(self.control_bt_cerrar)
        self.bt_minimizar.clicked.connect(self.control_bt_normal)
        self.bt_mini.clicked.connect(self.control_bt_minimizar)
        self.bt_maximizar.clicked.connect(self.control_bt_maximizar)

        # Eliminar borde de la ventana
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowOpacity(1)

        # SizeGrip
        self.gripSize = 10
        self.grip = QtWidgets.QSizeGrip(self)
        self.grip.resize(self.gripSize, self.gripSize)

        # Mover ventana
        self.frame_superior.mouseMoveEvent = self.mover_ventana

        # Páginas
        self.bt_1.clicked.connect(self.pagina_1)
        self.bt_2.clicked.connect(self.pagina_2)
        self.bt_3.clicked.connect(self.pagina_3)
        self.bt_4.clicked.connect(self.pagina_4)

        # Conectar los botones a sus funciones correspondientes
        self.bt_busqueda_2.clicked.connect(self.browse_folder_separator)
        self.path_edit = self.lineCargarDatos
        self.BT_mas.clicked.connect(lambda: self.incluir_frame(self.PanelPOST))
        self.BT_menos.clicked.connect(lambda: self.eliminar_atributo(self.PanelPOST))
        self.BT_mas_2.clicked.connect(lambda: self.incluir_frame(self.PanelPUT))
        self.BT_menos_2.clicked.connect(lambda: self.eliminar_atributo(self.PanelPUT))
        self.bt_enviar.clicked.connect(self.enviarEntidad)
        self.comboBox.currentTextChanged.connect(self.actualizar_frame)
        self.bt_enviar_2.clicked.connect(lambda:self.cargarDatos(self.path_edit.text()))
        self.bt_enviarGet.clicked.connect(self.obtenerDatos)
        self.bt_enviarDELETE.clicked.connect(self.borrarDatos)
        self.bt_enviarPATCH.clicked.connect(self.enviarPATCH)
        self.bt_enviarPUT.clicked.connect(self.enviarPUT)
        self.checkBoxDELETE.stateChanged.connect(self.toggle_frame_30)
        self.bt_enviar_Coor.clicked.connect(self.actualizarMapa)
        self.bt_Detectar.clicked.connect(self.detectarYMostrarMapa)
        self.bt_parar_coor.clicked.connect(self.detenerActualizacion)
        self.bt_enviar_MQTT.clicked.connect(self.mainMQTT)
        self.bt_parar_MQTT.clicked.connect(self.detenerMQTT)
        self.bt_enviar_CoAP.clicked.connect(self.modificar_atributo)
        self.bt_parar_alarma_3.clicked.connect(self.detener_verificacion)
        self.bt_enviar_alarma_3.clicked.connect(self.iniciar_verificacion_periodica)
        self.bt_enviar_subscripcion.clicked.connect(self.crear_suscripcion)
        
#   ********************************************************************************
#   * FUNCIONES PARA CREAR Y ELIMINAR LAS CASILLAS ADICIONEALES CON EL METODO POST *
#   ********************************************************************************

    def toggle_frame_30(self):
        if self.checkBoxDELETE.isChecked():
            self.frame_30.show()
        else:
            self.frame_30.hide()



    def actualizar_frame(self):
        if self.comboBox.currentText():
            self.frame_11.hide()
        else:
            self.frame_11.show()
        
        
    def incluir_frame(self, panel):
        """Añade un frame con campos de Atributo y Valor al Pane."""
        frame = QtWidgets.QFrame(panel)
        frame.setLayout(QtWidgets.QHBoxLayout())

        # Crear un solo par de inputs
        self.crear_atributos(frame, panel)

        # Añadir el nuevo frame al layout del PanelPOST
        panel.layout().addWidget(frame)
        self.frames.append(frame)  # Guardar el frame en la lista

        # Verificar si hay más de un frame, y hacer visible el botón "menos"
        if len(self.frames) > 0:
            if panel == self.PanelPOST:
                self.BT_menos.setVisible(True)
            else:
                self.BT_menos_2.setVisible(True)
        
    def eliminar_atributo(self, panel):
        """Elimina el último frame añadido en el panel correspondiente."""
        
        # Dependiendo del panel, obtener la lista de frames adecuada
        if panel == self.PanelPOST:
            frames = self.frames
            boton_menos = self.BT_menos
        elif panel == self.PanelPUT:
            frames = self.frames
            boton_menos = self.BT_menos_2
        else:
            return  # Si no es ni PanelPOST ni PanelPUT, no hacer nada
    
        if frames:
            last_frame = frames.pop()  # Obtener y eliminar el último frame
            last_frame.deleteLater()  # Eliminar el frame de la interfaz
    
            # Si no quedan frames en ese panel, ocultar el botón "menos"
            if len(frames) == 0:
                boton_menos.setVisible(False)


    def crear_atributos(self, parent_frame, panel):
        """Crea un par de QLabel, QLineEdit y QComboBox para atributo, valor y tipo."""

        # Crear los QLabel y QLineEdit para "Atributo" y "Valor"
        atributo_label = QtWidgets.QLabel("Atributo:", parent_frame)
        atributo_input = QtWidgets.QLineEdit(parent_frame)
        valor_label = QtWidgets.QLabel("Valor:", parent_frame)
        valor_input = QtWidgets.QLineEdit(parent_frame)
        
        # Crear el QComboBox para seleccionar el tipo de valor
        tipo_label = QtWidgets.QLabel("Tipo:", parent_frame)
        comboBox = QtWidgets.QComboBox(parent_frame)
        comboBox.addItem("Text")
        comboBox.addItem("Float")
        comboBox.addItem("Boolean")
        comboBox.addItem("Number")
        comboBox.addItem("Integer")
        comboBox.addItem("Date")
        comboBox.setCurrentIndex(-1)  # Inicializar el comboBox con ningún ítem seleccionado
        
        # Añadir los widgets al layout del parent_frame
        parent_frame.layout().addWidget(atributo_label)
        parent_frame.layout().addWidget(atributo_input)
        parent_frame.layout().addWidget(tipo_label)
        parent_frame.layout().addWidget(comboBox)
        parent_frame.layout().addWidget(valor_label)
        parent_frame.layout().addWidget(valor_input)
        # Almacenar los widgets para acceder a ellos más tarde
        if panel == self.PanelPOST:           
            self.atributos_inputs.append(atributo_input)
            self.valores_inputs.append(valor_input)
            self.tipo_inputs.append(comboBox)
        else:
            self.atributos_inputsPUT.append(atributo_input)
            self.valores_inputsPUT.append(valor_input)
            self.tipo_inputsPUT.append(comboBox)
            
    def ocultar_todos_los_paneles(self):
        """
        Oculta todos los paneles.
        """
        for panel in self.panels.values():
            panel.hide()

    def mostrar_panel_correspondiente(self, text):
        """
        Muestra el panel correspondiente a la opción seleccionada.
        """
        self.ocultar_todos_los_paneles()  # Primero, oculta todos los paneles
        if text in self.panels:
            self.panels[text].show()  # Muestra el panel correspondiente

#   *********************************************************************************
#   * FUNCIONES PARA MANEJO DEL MOVIMIENTO de la APLICAcIÓN Y DE DISEÑO EN GENERAL  *
#   *********************************************************************************

    # Mover el menú
    def mover_menu(self):
        width = self.frame_2.width()
        normal = 0
        if width == 0:
            extender = 300
            self.bt_menu_dr.hide()
            self.bt_menu_iz.show()
            self.bt_menu_dr_2.hide()
            self.bt_menu_iz_2.show()
        else:
            self.bt_menu_dr.show()
            self.bt_menu_iz.hide()
            self.bt_menu_dr_2.show()
            self.bt_menu_iz_2.hide()
            extender = normal
        self.animacion = QPropertyAnimation(self.frame_2, b"maximumWidth")
        self.animacion.setStartValue(width)
        self.animacion.setEndValue(extender)
        self.animacion.setDuration(500)
        self.animacion.setEasingCurve(QEasingCurve().OutInBack)
        self.animacion.start()

    def sombra_frame(self, frame):
        sombra = QGraphicsDropShadowEffect(self)
        sombra.setBlurRadius(30)
        sombra.setXOffset(8)
        sombra.setYOffset(8)
        sombra.setColor(QColor(20, 200, 220, 255))
        frame.setGraphicsEffect(sombra)
        
            
    def control_bt_minimizar(self):
        self.showMinimized()

    def control_bt_normal(self):
        self.showNormal()
        self.bt_minimizar.hide()
        self.bt_maximizar.show()

    def control_bt_maximizar(self):
        self.showMaximized()
        self.bt_minimizar.show()
        self.bt_maximizar.hide()

    def resizeEvent(self, event):
        rect = self.rect()
        self.grip.move(rect.right() - self.gripSize, rect.bottom() - self.gripSize)

    # Mover Ventana
    def mousePressEvent(self, event):
        self.clickPosition = event.globalPos()

    def mover_ventana(self, event):
        if not self.isMaximized():
            if event.buttons() == QtCore.Qt.LeftButton:
                self.move(self.pos() + event.globalPos() - self.clickPosition)
                self.clickPosition = event.globalPos()
                event.accept()
        if event.globalPos().y() <= 10:
            self.showMaximized()
            self.bt_maximizar.hide()
            self.bt_mini.show()
        else:
            self.showNormal()
            self.bt_maximizar.show()

    def pagina_1(self):
        self.stackedWidget.setCurrentWidget(self.page_1)

    def pagina_2(self):
        self.stackedWidget.setCurrentWidget(self.page_2)

    def pagina_3(self):
        self.stackedWidget.setCurrentWidget(self.page_3)
        
    def pagina_4(self):
        self.stackedWidget.setCurrentWidget(self.page_4)


    def control_bt_cerrar(self):
        self.close()
            

    def browse_folder_separator(self):
        folder_path,_ = QFileDialog.getOpenFileName(self, "Select Text o CSV File", "", "Files (*.txt *.csv)")
        if folder_path:
            self.lineCargarDatos.setText(folder_path)
 
            
#   ********************************************************************************
#   * FUNCIONES DE MANEJO DE LOS DIFERENTES METODOS POST, GET, DELETE, PATCH, PUT  *
#   ********************************************************************************
    
    def enviarEntidad(self):       

        # Configuración del Orion Context Broker
        ORION_URL = "http://" + self.lineIP.text() + ":" + self.linePUERTO.text() + "/v2/entities"
        
        
        if self.checkBoxPOST.isChecked():
            # Actualizar atributos de una entidad existente
            ORION_URL =  "http://" + self.lineIP.text() + ":" + self.linePUERTO.text() + "/v2/entities/" + self.textID.toPlainText() + "/attrs"
            entities = [{
                self.textAtributo.toPlainText(): {"value": self.textValor.toPlainText(), "type": self.comboBox_2.currentText()},
                }]
        else:
        # Crear una lista de entidades con los atributos y valores dinámicos
            entities = [{
                "id": self.textID.toPlainText(),
                "type": self.textTipoEnt.toPlainText(),
                self.textAtributo.toPlainText(): {"value": self.textValor.toPlainText(), "type": self.comboBox_2.currentText()},
            }]
            
        # Añadir los atributos dinámicos a la entidad
        for i in range(len(self.atributos_inputs)):
            atributo = self.atributos_inputs[i].text()  # Obtener texto del QLineEdit
            valor = self.valores_inputs[i].text()      # Obtener texto del QLineEdit
            tipo = self.tipo_inputs[i].currentText()           # Obtener texto seleccionado del QComboBox
            # Validar datos
            if not atributo or not valor:
                continue  # Saltar atributos inválidos
                    # Asegurarse de que el atributo no esté vacío antes de añadirlo
            if atributo and valor:
                # Añadir el atributo a la entidad
                entities[0][atributo] = {"value": valor, "type": tipo}
                
        # Crear entidades en Orion
        for entity in entities:
            response = requests.post(ORION_URL, data=json.dumps(entity), headers={"Content-Type": "application/json"})
            if response.status_code in [201,204]:
                if "id" in entity:
                    # Solo mostrar el ID si existe
                    QMessageBox.information(
                        self, "Éxito", f"Entidad {entity['id']} creada correctamente."
                    )
                else:
                    QMessageBox.information(
                        self, "Éxito", "Atributos actualizados correctamente."
                    )
            else:
                # Manejar errores sin asumir que el ID está presente
                error_message = (
                    "Error al procesar la entidad."
                    + (f" ID: {entity.get('id', 'N/A')}.\n" if "id" in entity else "\n")
                    + response.text
                )
                QMessageBox.warning(self, "Error", error_message)
            
    def cargarDatos(self, file_path): 
        # Configuración del Orion Context Broker
        ORION_URL = "http://" + self.lineIP.text() + ":" + self.linePUERTO.text() + "/v2/entities"
        
        # Cargar datos desde el archivo JSON
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)  # Cargar los datos del archivo JSON
        except FileNotFoundError:
            QMessageBox.critical(self, "Error", f"El archivo {file_path} no se encuentra.")
            return
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "Error al leer el archivo JSON.")
            return
    
        # Crear las entidades a partir de los datos cargados
        entities = []
        for entity_data in data["entities"]:
            # Asegurarse de que 'id' y 'type' no estén vacíos
            entity = {
                "id": entity_data.get("id", "").strip(),  # Obtener id y asegurarse de que no sea vacío
                "type": entity_data.get("type", "").strip(),  # Obtener type y asegurarse de que no sea vacío
            }
    
            # Comprobar si el id y el tipo son válidos
            if not entity["id"] or not entity["type"]:
                QMessageBox.warning(self, "Advertencia", "Error: id o type vacío. Esta entidad será omitida.")
                continue  # Saltar esta entidad si el id o type son inválidos
    
            # Añadir atributos dinámicos si los hay
            for atributo, valor in entity_data.get("attributes", {}).items():
                entity[atributo] = {"value": valor["value"], "type": valor["type"]}
    
            entities.append(entity)
        num_entidades = 0
        # Enviar las entidades a Orion
        for entity in entities:
            response = requests.post(ORION_URL, data=json.dumps(entity), headers={"Content-Type": "application/json"})
            if response.status_code == 201:
               num_entidades += 1
            else:
                QMessageBox.warning(self, "Error", f"Error al crear la entidad {entity['id']}:\n{response.text}")
    
        # Imprimir la URL y las entidades para verificar los datos
        QMessageBox.information(self, "Información", f"Datos cargados y enviados a:\n{ORION_URL}\nNumero de entidades creadas: {num_entidades}")

    def obtenerDatos(self):
        # Configuración de la URL del Orion Context Broker
        ORION_URL = "http://" + self.lineIP.text() + ":" + self.linePUERTO.text() + "/v2/entities"
    
        # Obtener los valores de los QTextEdit
        entidad = self.textGetEnt.toPlainText().strip()  # Nombre de la entidad
        tipo = self.textGetTipo.toPlainText().strip()    # Tipo de la entidad
        
        # Construir la URL dependiendo de los valores de entidad o tipo
        if entidad:
            # Buscar por nombre de entidad (id)
            url = f"{ORION_URL}/{entidad}"
        elif tipo:
            # Buscar por tipo de entidad
            url = f"{ORION_URL}?type={tipo}"
        else:
            url = ORION_URL
            
    
        # Realizar la petición GET a la URL de Orion
        try:
            response = requests.get(url, headers={"Accept": "application/json"})
            if response.status_code == 200:
                QMessageBox.information(self, "Información", "Datos cargados y enviados para visualizacion")
                # Si la petición es exitosa, obtener y mostrar los datos
                datos = response.json()
                self.mostrarDatos(datos)
            else:
               QMessageBox.warning(self, "Error", f"Error al obtener datos:\n{response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Error en la conexión:\n{e}")
    
    def mostrarDatos(self, datos):
        # Limpiar el contenido previo del QTextEdit
        self.textMostrarGet.clear()
        
        if isinstance(datos, list):
            # Si los datos son una lista, ordenamos por el tipo de entidad
            datos = sorted(datos, key=lambda x: x.get('type', ''))  # Asegúrate de usar el nombre correcto del campo
            
        # Convertir los datos a formato JSON legible
        datos_str = json.dumps(datos, indent=4)
    
        # Asignar los datos al QTextEdit para mostrar los resultados
        self.textMostrarGet.setPlainText(datos_str)
    
        # Limpiar el contenido previo del segundo QTextEdit
        self.textMostarGet2.clear()
    
        # Función para convertir el JSON en un formato jerárquico legible
        def parse_json(data, indent=0):
            result = ""
            if isinstance(data, dict):  # Si es un diccionario
                for key, value in data.items():
                    # Si el valor es un diccionario, lo procesamos recursivamente
                    if isinstance(value, dict):
                        result += "  " * indent + f"{key} :\n"
                        result += parse_json(value, indent + 1)
                    # Si el valor es una lista, la recorremos
                    elif isinstance(value, list):
                        result += "  " * indent + f"{key} :\n"
                        for item in value:
                            if isinstance(item, dict):
                                result += parse_json(item, indent + 1)
                            else:
                                result += "  " * (indent + 1) + f"{item}\n"
                    else:
                        # Si es un valor simple, lo mostramos
                        result += "  " * indent + f"{key} : {value}\n"
            elif isinstance(data, list):  # Si es una lista
                for item in data:
                    result += parse_json(item, indent)  # Procesamos cada item como si fuera un diccionario
            else:
                result += "  " * indent + str(data) + "\n"
            return result
    
        # Convertir los datos JSON en el formato jerárquico
        datos_str = parse_json(datos)

        # Mostrar el resultado en el segundo QTextEdit
        self.textMostarGet2.setPlainText(datos_str)
        
    def borrarDatos(self):
        # Configuración de la URL del Orion Context Broker
        ORION_URL = "http://" + self.lineIP.text() + ":" + self.linePUERTO.text() + "/v2/entities"
    
        # Obtener los valores del formulario
        entidad = self.textDELETEent.toPlainText().strip()  # ID de la entidad
        atributo = self.textDELETEAtr.toPlainText().strip()  # Nombre del atributo a borrar
    
        # Verificar si se elimina un atributo específico
        if self.checkBoxDELETE.isChecked() and entidad and atributo:
            # Construir la URL para eliminar el atributo de una entidad específica
            url = f"{ORION_URL}/{entidad}/attrs/{atributo}"
            mensaje_confirmacion = f"¿Estás seguro de que deseas eliminar el atributo '{atributo}' de la entidad '{entidad}'?"
        elif entidad:
            # Si se especifica solo una entidad (sin atributo)
            url = f"{ORION_URL}/{entidad}"
            mensaje_confirmacion = f"¿Estás seguro de que deseas eliminar la entidad '{entidad}'?"
        else:
            # Si no se especifica nada, eliminar todas las entidades una a una
            mensaje_confirmacion = "¿Estás seguro de que deseas eliminar todas las entidades una a una?"
            confirmar = QMessageBox.question(
                self,
                "Confirmar eliminación",
                mensaje_confirmacion,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if confirmar != QMessageBox.Yes:
                return
    
            # Obtener todas las entidades
            try:
                response = requests.get(ORION_URL, headers={"Accept": "application/json"})
                if response.status_code == 200:
                    entidades = response.json()
                    if not entidades:
                        QMessageBox.information(self, "Sin datos", "No existen entidades para eliminar.")
                        return
                    entidades_borradas = 0
                    # Borrar entidades una a una
                    for entidad in entidades:
                        entidad_id = entidad["id"]
                        delete_url = f"{ORION_URL}/{entidad_id}"
                        delete_response = requests.delete(delete_url, headers={"Accept": "application/json"})
                        
                        if delete_response.status_code in [200, 204]:
                            entidades_borradas += 1
                        else:
                            print(f"Error al eliminar la entidad '{entidad_id}': {delete_response.text}")
    
                    QMessageBox.information(
                        self, "Eliminación completa", f"Un total de {entidades_borradas} entidades han sido eliminadas correctamente."
                    )
                else:
                    QMessageBox.warning(
                        self, "Error al obtener entidades", f"No se pudieron obtener las entidades:\n{response.text}"
                    )
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(
                    self, "Error en la conexión", f"No se pudo conectar con el servidor:\n{e}"
                )
            return
    
        # Confirmar la operación antes de proceder para atributos o entidades específicas
        confirmar = QMessageBox.question(
            self,
            "Confirmar eliminación",
            mensaje_confirmacion,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if confirmar != QMessageBox.Yes:
            return
    
        # Realizar la petición DELETE a la URL configurada
        try:
            response = requests.delete(url, headers={"Accept": "application/json"})
            if response.status_code in [200, 204]:
                QMessageBox.information(
                    self, "Eliminación exitosa", "Los datos han sido eliminados correctamente."
                )
            else:
                QMessageBox.warning(
                    self, "Error al eliminar", f"No se pudieron eliminar los datos:\n{response.text}"
                )
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(
                self, "Error en la conexión", f"No se pudo conectar con el servidor:\n{e}"
            )

            
    def enviarPATCH(self):
        # Configuración del Orion Context Broker
        ORION_URL = "http://" + self.lineIP.text() + ":" + self.linePUERTO.text() + "/v2/entities"
        
        # Obtener los valores necesarios de los QTextEdit
        entidad_id = self.textPATCHent.toPlainText().strip()  # ID de la entidad a actualizar
        
        # Asegurarse de que el ID no esté vacío
        if not entidad_id:
            QMessageBox.warning(self, "Error", "El ID de la entidad es obligatorio para realizar el PATCH.")
            return
    
        # Construir la URL de la entidad a actualizar
        url = f"{ORION_URL}/{entidad_id}/attrs"
    
        # Crear el objeto de actualización
        atributos = {}
        atributos[self.textPATCHAtr.toPlainText()] = {
            "value": self.textPATCHvalor.toPlainText(),
            "type": self.comboBox_4.currentText(),
        }
    
    
        # Realizar la solicitud PATCH a Orion
        try:
            response = requests.patch(url, data=json.dumps(atributos), headers={"Content-Type": "application/json"})
            if response.status_code == 204:
                # Éxito en la actualización
                QMessageBox.information(self, "Actualización exitosa", f"Entidad {entidad_id} actualizada correctamente.")
            else:
                # Error en la actualización
                QMessageBox.warning(self, "Error al actualizar", f"No se pudo actualizar la entidad:\n{response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error en la conexión", f"No se pudo conectar con el servidor:\n{e}")


    def enviarPUT(self):
        
        print(self.atributos_inputsPUT)
        # Configuración del Orion Context Broker
        ORION_URL = "http://" + self.lineIP.text() + ":" + self.linePUERTO.text() + "/v2/entities"
        
        # Obtener los valores necesarios de los QTextEdit
        entidad_id = self.textPUTent.toPlainText().strip()  # ID de la entidad a actualizar
       
        
        # Asegurarse de que el ID de la entidad no esté vacío
        if not entidad_id:
            QMessageBox.warning(self, "Error", "El ID de la entidad es obligatorio para realizar el PUT.")
            return
    
        # Construir la URL de la entidad a actualizar
        url = f"{ORION_URL}/{entidad_id}/attrs"
        
        # Crear el objeto de atributos de la entidad
        entidad = {
            self.textPUTatr.toPlainText(): {
                "value": self.textPUTvalor.toPlainText(),
                "type": self.comboBox_3.currentText(),
            }
        }
        
        # Añadir los atributos dinámicos a la entidad
        for i in range(len(self.atributos_inputsPUT)):
            atributo = self.atributos_inputsPUT[i].text()  # Obtener texto del QLineEdit
            valor = self.valores_inputsPUT[i].text()      # Obtener texto del QLineEdit
            tipo = self.tipo_inputsPUT[i].currentText()           # Obtener texto seleccionado del QComboBox
            
            # Asegurarse de que el atributo no esté vacío antes de añadirlo
            if atributo and valor:
                # Añadir el atributo a la entidad
                entidad[atributo] = {"value": valor, "type": tipo}
        
        # Realizar la solicitud PUT a Orion
        try:
            response = requests.put(url, data=json.dumps(entidad), headers={"Content-Type": "application/json"})
            if response.status_code in [201, 204]:
                # Éxito en la actualización
                QMessageBox.information(self, "Operación exitosa", f"Atributos de la entidad {entidad_id} actualizados correctamente.")
            else:
                # Error en la operación
                QMessageBox.warning(self, "Error en la operación", f"No se pudo realizar la operación:\n{response.text}")
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error en la conexión", f"No se pudo conectar con el servidor:\n{e}")

#   *******************************************************************
#   * FUNCIONES PARA DETECTAR Y GEOLOCALIZAR EN EL MAPA LAS ENTIDADES *
#   *******************************************************************

    def detectarYMostrarMapa(self):
        self.bt_parar_coor.hide()
        self.bt_enviar_Coor.show()
        # Configuración inicial del Orion Context Broker
        self.ORION_URL = "http://" + self.lineIP.text() + ":" + self.linePUERTO.text() + "/v2/entities"
        
        try:
            # Petición GET para obtener todas las entidades
            response = requests.get(self.ORION_URL, headers={"Accept": "application/json"})
            if response.status_code != 200:
                QMessageBox.warning(self, "Error", "No se pudieron obtener las entidades.")
                return
            
            entidades = response.json()
            if not entidades:
                QMessageBox.information(self, "Sin datos", "No hay entidades disponibles en el servidor.")
                return
            
            # Filtrar entidades con latitud y longitud
            entidades_con_coordenadas = [
                entidad for entidad in entidades
                if "latitud" in entidad and "longitud" in entidad
            ]
            
            if not entidades_con_coordenadas:
                QMessageBox.information(self, "Sin coordenadas", "No hay entidades con atributos de latitud y longitud.")
                return
            
            # Clasificar por tipo (clase)
            self.clases_entidades = {}
            for entidad in entidades_con_coordenadas:
                clase = entidad.get("type", "Desconocido")
                if clase not in self.clases_entidades:
                    self.clases_entidades[clase] = []
                self.clases_entidades[clase].append(entidad)
            
            # Configurar colores para las clases
            colores_predefinidos = [
                'pink', 'darkred', 'blue', 'lightgreen', 'darkpurple', 'gray',
                'cadetblue', 'beige', 'purple', 'lightgray', 'orange', 'green',
                'darkgreen', 'darkblue', 'lightred', 'black', 'white', 'lightblue', 'red'
            ]
            self.colores_por_clase = {}
            
            # Eliminar checkboxes previos
            for child in self.frame_31.findChildren(QCheckBox):
                child.deleteLater()
            
            # Crear checkboxes para clases
            self.check_buttons = []
            for idx, clase in enumerate(self.clases_entidades.keys()):
                color = colores_predefinidos[idx % len(colores_predefinidos)]
                self.colores_por_clase[clase] = color
                
                check_button = QCheckBox(clase, self.frame_31)
                check_button.setStyleSheet(f"""
                    QCheckBox {{
                        background-color: {color};
                        color: white;
                        padding: 5px;
                        border-radius: 5px;
                    }}
                    QCheckBox::indicator {{
                        width: 16px;
                        height: 16px;
                    }}
                """)
                check_button.setChecked(True)
                self.frame_31.layout().addWidget(check_button)
                self.check_buttons.append(check_button)
            
            QMessageBox.information(self, "Éxito", "¡Clases detectadas y cargadas en el frame!")
            
            # Obtener coordenadas para el mapa
            try:
                self.latitud = float(self.lineLatitud.text())
                self.longitud = float(self.lineLongitud.text())
            except ValueError:
                self.web_view.setHtml("<h2>Coordenadas inválidas</h2>")
                return
            
            # Verificar clases seleccionadas
            self.clases_seleccionadas = [
                cb.text() for cb in self.check_buttons if cb.isChecked()
            ]
            
            # Crear mapa con Folium
            mapa = folium.Map(location=[self.latitud, self.longitud], zoom_start=self.barraZOOM_3.value())
            for clase, entidades in self.clases_entidades.items():
                if clase in self.clases_seleccionadas:
                    color = self.colores_por_clase.get(clase, "gray")
                    for entidad in entidades:
                        lat = entidad["latitud"]["value"]
                        lon = entidad["longitud"]["value"]
                        nombre = entidad.get("id", "Sin ID")
                        folium.Marker(
                            location=[lat, lon],
                            popup=f"{nombre} ({clase})",
                            icon=folium.Icon(color=color, icon_color=color)
                        ).add_to(mapa)
            
            # Guardar y mostrar el mapa
            mapa.save('mapa.html')
            self.web_view.setUrl(QUrl.fromLocalFile(os.path.abspath("mapa.html")))
            
            QMessageBox.information(self, "Éxito", "¡Mapa generado con éxito!")
        
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error en la conexión", f"No se pudo conectar al servidor:\n{e}")

    def actualizarMapa(self):
        self.bt_parar_coor.show()
        self.bt_enviar_Coor.hide()
        self.timer = QTimer()
        
        self.timer.timeout.connect(self.generarMapa)  # Vincula el método para generar el mapa
        self.timer.start(1000)  # Actualiza cada 1000 ms (1 segundo)
                    
    def detenerActualizacion(self):        
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        self.bt_parar_coor.hide()
        self.bt_enviar_Coor.show()
        
            
    def generarMapa(self):
        response = requests.get(self.ORION_URL, headers={"Accept": "application/json"})
        if response.status_code != 200:
            QMessageBox.warning(self, "Error", "No se pudieron obtener las entidades.")
            return
        
        entidades = response.json()
        if not entidades:
            QMessageBox.information(self, "Sin datos", "No hay entidades disponibles en el servidor.")
            return
        
        # Filtrar entidades con latitud y longitud
        entidades_con_coordenadas = [
            entidad for entidad in entidades
            if "latitud" in entidad and "longitud" in entidad
        ]
        
        if not entidades_con_coordenadas:
            QMessageBox.information(self, "Sin coordenadas", "No hay entidades con atributos de latitud y longitud.")
            return
        
        # Clasificar por tipo (clase)
        self.clases_entidades = {}
        for entidad in entidades_con_coordenadas:
            clase = entidad.get("type", "Desconocido")
            if clase not in self.clases_entidades:
                self.clases_entidades[clase] = []
            self.clases_entidades[clase].append(entidad)
        
        # Verificar clases seleccionadas
        self.clases_seleccionadas = [
            cb.text() for cb in self.check_buttons if cb.isChecked()
        ]
        # Crear y actualizar el mapa
        mapa = folium.Map(location=[self.latitud, self.longitud], zoom_start=self.barraZOOM_3.value())
        for clase, entidades in self.clases_entidades.items():
            if clase in self.clases_seleccionadas:
                color = self.colores_por_clase.get(clase, "gray")
                for entidad in entidades:
                    lat = entidad["latitud"]["value"]
                    lon = entidad["longitud"]["value"]
                    nombre = entidad.get("id", "Sin ID")
                    folium.Marker(
                        location=[lat, lon],
                        popup=f"{nombre} ({clase})",
                        icon=folium.Icon(color=color, icon_color=color)
                    ).add_to(mapa)
    
        # Guardar y mostrar el mapa
        mapa.save('mapa.html')
        self.web_view.setUrl(QUrl.fromLocalFile(os.path.abspath("mapa.html")))
        self.web_view.update()  # Forzar actualización visual
        
 #   ***************************************************************************************
 #   * FUNCIONES QUE MANEJAN PROTOCOLOS MQTT, CoAP, SUBSCRPICION Y ALARMA DE LA APLICACIÓN *
 #   ***************************************************************************************   

    def mainMQTT(self):
        self.bt_enviar_MQTT.hide()
        self.bt_parar_MQTT.show()
        # Configuración
        MQTT_BROKER = self.lineIP.text()
        MQTT_PORT = int(self.puertoMQTT.text())  # Convertir a entero
        MQTT_TOPIC = self.topicMQTT.text()
        self.ORION_URL = "http://" + self.lineIP.text() + ":" + self.linePUERTO.text() + "/v2/entities"
    
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        
        try:
            self.client.connect(MQTT_BROKER, MQTT_PORT)
            self.client.subscribe(MQTT_TOPIC, qos=1)
            
            # Reflejar conexión en QTextEdit
            self.textMQTT.append(f"Conectado a MQTT Broker en {MQTT_BROKER}:{MQTT_PORT}")
        except Exception as e:
            self.textMQTT.append(f"Error al conectar con el MQTT Broker: {e}")
            return
    
        # Ejecutar el cliente MQTT en un hilo separado
        def mqtt_loop():
            print("Escuchando mensajes MQTT en un hilo...")
            self.client.loop_forever()
    
        mqtt_thread = Thread(target=mqtt_loop, daemon=True)
        mqtt_thread.start()

        
    # Función para enviar datos a ORION
    def enviar_a_orion(self,entity_id, atributo, valor):
        url = f"{self.ORION_URL}/{entity_id}/attrs"
        headers = {"Content-Type": "application/json"}
        payload = {
            atributo: {
                "value": valor,
                "type": "Float"
            }
        }

        try:
            response = requests.patch(url, data=json.dumps(payload), headers=headers)
            if response.status_code == 204:
                print(f"Datos enviados a ORION: {entity_id} -> {atributo}: {valor}")
            else:
                print(f"Error al enviar datos a ORION: {response.status_code}")
        except Exception as e:
            print(f"Error de conexión con ORION: {e}")

    # Callback para recibir mensajes de MQTT
    def on_message(self, client, userdata, msg):
        try:
            mensaje = msg.payload.decode()
            print(f"Mensaje recibido en {msg.topic}: {mensaje}")
            
            # Reflejar mensaje en textMQTT
            QtCore.QMetaObject.invokeMethod(
                self.textMQTT,
                "append",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, f"Mensaje recibido en {msg.topic}: {mensaje}")
            )
            
            # Procesar mensaje (ejemplo: enviar a Orion)
            data = json.loads(mensaje)
            entity_id = data["id"]
            atributo = "peso"
            valor = data["peso"]
            self.enviar_a_orion(entity_id, atributo, valor)
        except Exception as e:
            error_msg = f"Error procesando el mensaje MQTT: {e}"
            print(error_msg)
            QtCore.QMetaObject.invokeMethod(
                self.textMQTT,
                "append",
                QtCore.Qt.QueuedConnection,
                QtCore.Q_ARG(str, error_msg)
                )
                
    def detenerMQTT(self):
        self.bt_enviar_MQTT.show()
        self.bt_parar_MQTT.hide()
        try:
            if self.client:
                # Detener el loop y desconectar el cliente MQTT
                self.client.loop_stop()  # Detener el loop del hilo
                self.client.disconnect()  # Desconectar del broker
                self.client = None  # Liberar la referencia al cliente
                
                # Actualizar el QTextEdit para reflejar el estado
                self.textMQTT.append("Conexión con el broker MQTT detenida.")
            else:
                self.textMQTT.append("No hay conexión activa para detener.")
        except Exception as e:
            self.textMQTT.append(f"Error al detener la conexión: {e}")
            
    async def enviar_peticion_coap(self, entidad_id, nuevo_valor):
        # Obtener el puerto desde un atributo de la interfaz
        puerto = self.puertoCoAP.text().strip()
        ip = self.lineIP.text()
        if not puerto.isdigit():
            print("Error: El puerto debe ser un número.")
            return
        
        # Construir la URL del recurso en el servidor CoAP
        url = f"coap://{ip}:{puerto}/salud"
        payload = {
            "id": entidad_id,
            "salud": nuevo_valor
        }
        
        # Crear la solicitud PATCH para enviar los datos
        request = Message(code=Code.PATCH, uri=url, payload=json.dumps(payload).encode('utf-8'))
        request.opt.content_format = 50  # Indicar que el payload está en formato JSON
        
        context = await Context.create_client_context()
        try:
            response = await context.request(request).response
            QMessageBox.information(None, "Respuesta del servidor",
                                 f"Código: {response.code}\nMensaje: {response.payload.decode('utf-8')}")
        except Exception as e:
            QMessageBox.critical(None, "Error", f"No se pudo enviar la solicitud:\n{e}")
            
    def modificar_atributo(self):
        entidad_id = self.entidadCoAP.text().strip()
        nuevo_valor = self.valorCoAP.text().strip()
    
        if not entidad_id or not nuevo_valor:
            QMessageBox.warning(None, "Error", "Completa todos los campos antes de continuar.")
            return
    
        # Ejecutar la función asíncrona
        asyncio.create_task(self.enviar_peticion_coap(entidad_id, nuevo_valor))
        
    def closeEvent(self, event):
        """Manejar el cierre de la ventana."""
        if loop.is_running():
            loop.stop()  # Detener el bucle de asyncio si está en ejecución
        event.accept()  # Aceptar el evento de cierre
        
    def punto_dentro_del_poligono(self,lat, lon, coordenadas):
        """
        Verifica si un punto (lat, lon) está dentro de un polígono definido por sus coordenadas.
        Utiliza el algoritmo de ray-casting.
        """
        n = len(coordenadas)
        dentro = False
        x_interseccion = lon
        y_interseccion = lat
        x1, y1 = coordenadas[0]
    
        for i in range(n + 1):
            x2, y2 = coordenadas[i % n]
            if y_interseccion > min(y1, y2):
                if y_interseccion <= max(y1, y2):
                    if x_interseccion <= max(x1, x2):
                        if y1 != y2:
                            x_cruce = (y_interseccion - y1) * (x2 - x1) / (y2 - y1) + x1
                        if x1 == x2 or x_interseccion <= x_cruce:
                            dentro = not dentro
            x1, y1 = x2, y2
    
        return dentro
    
    
    def verificar_fuera_del_perimetro(self, entidad):
        """
        Verifica si la entidad está fuera del perímetro definido por el polígono.
        """
        lat = float(entidad["latitud"]["value"])
        lon = float(entidad["longitud"]["value"])
        centro_latitud = float(self.lineLatitud.text())
        centro_longitud = float(self.lineLongitud.text())
        perimetro = float(self.linePERIMETRO_3.text())
        lado = perimetro / 4
    
        # Delta en latitud (constante: 111,320 metros por grado)
        delta_lat = lado / 111320
        delta_lon = lado / (111320 * np.cos(np.radians(centro_latitud)))
    
        # Definir los vértices del polígono
        coordenadas = [
            [centro_longitud - delta_lon, centro_latitud - delta_lat],
            [centro_longitud + delta_lon, centro_latitud - delta_lat],
            [centro_longitud + delta_lon, centro_latitud + delta_lat],
            [centro_longitud - delta_lon, centro_latitud + delta_lat],
            [centro_longitud - delta_lon, centro_latitud - delta_lat]
        ]
        
        # Verificar si el punto (lat, lon) está dentro del polígono
        if not self.punto_dentro_del_poligono(lat, lon, coordenadas):
            return True  # La entidad está fuera del perímetro
        return False

    
    def generarAlertaSiFueraDelPerimetro(self):
        """
        Función que obtiene las entidades y verifica si alguna está fuera del perímetro.
        Si alguna entidad está fuera del perímetro, se activa la alerta.
        """
        
        try:
            response = requests.get(self.ORION_URL, headers={"Accept": "application/json"})
            if response.status_code != 200:
                QMessageBox.warning(self, "Error", "No se pudieron obtener las entidades.")
                return
            
            entidades = response.json()
            if not entidades:
                QMessageBox.information(self, "Sin datos", "No hay entidades disponibles en el servidor.")
                return
            
            # Filtrar entidades con coordenadas
            entidades_con_coordenadas = [
                entidad for entidad in entidades
                if "latitud" in entidad and "longitud" in entidad
            ]
            
            # Verificar si algún animal está fuera del perímetro
            for entidad in entidades_con_coordenadas:
                if self.verificar_fuera_del_perimetro(entidad):
                    nombre = entidad.get("id", "Sin ID")
                    QMessageBox.warning(self, "Alerta", f"¡Alerta! El animal {nombre} ha salido del perímetro.")
                    # Aquí podrías agregar código para hacer sonar una alarma, o mostrar un mensaje en pantalla
    
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error en la conexión", f"No se pudo conectar al servidor:\n{e}")
        
    def iniciar_verificacion_periodica(self):
        self.bt_parar_alarma_3.show()
        self.bt_enviar_alarma_3.hide()
        self.timerA = QTimer()
        self.timerA.timeout.connect(self.generarAlertaSiFueraDelPerimetro)
        self.timerA.start(5000)  # Verificar cada 2 segundos
        
    def detener_verificacion(self):
        self.bt_parar_alarma_3.hide()
        self.bt_enviar_alarma_3.show()
        if self.timerA:
            self.timerA.stop()  # Detener el timer
        print("Verificación detenida")
        
    def crear_suscripcion(self):
        """
        Crea una suscripción en Orion para notificar cambios en las coordenadas de las entidades fuera del perímetro.
        """
        self.ORION_URL_Sub = "http://" + self.lineIP.text() + ":" + self.linePUERTO.text() + "/v2/subscriptions"
        headers = {"Content-Type": "application/json"}
        
        # Obtener el perímetro y las coordenadas del centro
        perimetro = float(self.linePERIMETRO_3.text())
        centro_latitud = float(self.lineLatitud.text())
        centro_longitud = float(self.lineLongitud.text())
        
        # Definir los márgenes del rectángulo
        delta_lat = perimetro / 111320  # Aproximación en grados de latitud por metro
        delta_lon = perimetro / (111320 * np.cos(np.radians(centro_latitud)))
        
        # Definir los vértices del polígono
        coordenadas = [
            [centro_longitud - delta_lon, centro_latitud - delta_lat],
            [centro_longitud + delta_lon, centro_latitud - delta_lat],
            [centro_longitud + delta_lon, centro_latitud + delta_lat],
            [centro_longitud - delta_lon, centro_latitud + delta_lat],
            [centro_longitud - delta_lon, centro_latitud - delta_lat]
        ]
        
        # Definir las entidades para las suscripciones
        entidades = [{"idPattern": ".*", "type": clase} for clase in self.clases_entidades]
        
        # Crear la suscripción con la condición georel
        data = {
            "description": "Notificación de cambios en la posición de las entidades fuera del perímetro",
            "subject": {
                "entities": entidades,  # Para todas las entidades de tipo especificado
                "condition": {
                    "attrs": ["latitud", "longitud"],
                    "expression": {
                        "type": "geo:json",
                        "value": {
                            "type": "Polygon",
                            "coordinates": [coordenadas]
                        },
                        "op": "disjoint"  # Notificar cuando la entidad esté fuera del polígono
                    }
                }
            },
            "notification": {
                "http": {"url": f"http://{self.subscripcionIP.text()}:{self.subscripcionPuerto.text()}"},
                "attrs": ["latitud", "longitud"],  # Enviar solo los atributos relevantes
                "throttling": 10  # Limitar la frecuencia de notificaciones a una cada 10 segundos
            }
        }
    
        try:
            # Realizamos la solicitud POST para crear la suscripción
            response = requests.post(self.ORION_URL_Sub, json=data, headers=headers)
            
            if response.status_code == 201:
                QMessageBox.information(None, "Suscripción", "Suscripción enviada al servidor con éxito")
            else:
                print(f"Error al crear la suscripción: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error en la conexión al crear la suscripción: {e}")



                
if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    try:
        with loop:  # Ejecutar el bucle de eventos de asyncio y Qt juntos
            loop.run_forever()
    except KeyboardInterrupt:
        print("Interrupción manual detectada, cerrando...")
    finally:
        loop.stop()
        loop.close()  # Cerrar el bucle de eventos
        sys.exit(app.exec_())