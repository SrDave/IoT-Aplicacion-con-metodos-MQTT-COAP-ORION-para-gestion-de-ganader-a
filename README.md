# ÍNDICE

1. Introducción

2. Caso de uso

3. Modelo de datos de las entidades

4. Programa en Python para la creación de entidades

5. Programa en Python para eliminar entidades

6. Programa en Python que permita actualizar los atributos

7. Programa en Python que modifique automáticamente la posición de las entidades

8. Aplicación en Python que permita mostrar gráficamente las diferentes entidades

9. Programa en Python que ejerza de agente IoT MQTT

10. Programa en Python que ejerza de agente IoT CoAP

11. Implementar una notificación

12. Conclusiones

---
## Introducción

El desarrollo y uso de esta aplicación requieren tener en cuenta varios aspectos técnicos. La aplicación cuenta con una interfaz gráfica de usuario (GUI) creada utilizando la biblioteca PyQt5, por lo que es imprescindible instalar esta biblioteca para garantizar su correcto funcionamiento y visualización.

Si bien Anaconda incluye PyQt5 en su entorno de desarrollo integrado Spyder, permitiendo que la aplicación funcione de manera adecuada dentro de este entorno, será necesario instalar la biblioteca de forma manual si se desea ejecutar la aplicación fuera de Anaconda.

Además, para habilitar la funcionalidad de visualización en tiempo real de los localizadores, es necesario instalar el módulo adicional PyQt5.QtWebEngineWidgets. Este módulo permite la representación de mapas o gráficos que facilitan el monitoreo de las entidades geolocalizadas.

Ya existe una empresa española en Madrid que ofrece estos servicios con sus sensores GPS para ganado digitanimal.com.

Caso de uso

Este proyecto consiste en el desarrollo de una aplicación dirigida a un cliente ganadero con necesidades específicas relacionadas con la gestión y el monitoreo de sus animales. El cliente enfrenta problemas recurrentes con animales que se alejan del grupo durante el pastoreo, lo que dificulta su localización. Por tanto, requiere una solución que permita geolocalizar a los animales en tiempo real y establecer un perímetro seguro para evitar que se pierdan. Además, el cliente necesita un sistema que facilite el control e identificación de cada animal, almacenando información relevante como peso, fecha de nacimiento y estado de salud.

---

## Requerimientos funcionales

RF1: Sistema de geofencing
El sistema debe definir un perímetro geográfico basado en coordenadas que pueda ajustarse dinámicamente. Esto es esencial para delimitar el área de interés y detectar cuándo un animal se encuentra fuera del área establecida.

RF2: Detección en tiempo real
El sistema debe procesar actualizaciones de posición en tiempo real para identificar salidas del perímetro con una latencia máxima de 2 segundos. Este requisito es crucial para garantizar una respuesta inmediata ante posibles incidencias.

RF3: Notificaciones automáticas
Cuando un animal salga del perímetro, el sistema debe enviar notificaciones automáticas a un puerto específico (en este caso, el puerto 8181). Las notificaciones deben incluir datos como el ID del animal, la posición actual y la hora en la que ocurrió el evento.

---

## Requerimientos no funcionales

#### RNF1: Escalabilidad
El sistema debe ser capaz de manejar un gran número de entidades simultáneamente (animales) sin afectar negativamente al rendimiento.

#### RNF2: Seguridad de los datos
La comunicación entre el sistema y las notificaciones debe emplear protocolos seguros, como HTTPS, para proteger los datos sensibles y evitar manipulaciones o intercepciones. Adicionalmente, se evaluarán y utilizarán modelos de comunicación ligeros como MQTT y CoAP, según las necesidades específicas del proyecto.

---

## Modelo de datos de las entidades

El sistema incluye cinco tipos de entidades principales, con un total de 15 instancias individuales, cada una representando un animal o dispositivo. Todas las entidades móviles son geolocalizables y tienen atributos de latitud y longitud, además de otros tres atributos: fecha de nacimiento, peso (enviado a través de MQTT) y estado de salud (reportado manualmente mediante CoAP).

El sistema está diseñado para ser totalmente escalable, permitiendo agregar más entidades, tipos de entidades o incluso más atributos sin afectar el rendimiento general.

Programa en Python para la creación de entidades

La aplicación permite crear entidades de manera manual mediante el uso del método POST, lo que ofrece facilidad para incluir entidades, especificar su clase y añadir tantos atributos como se desee.

Además, la aplicación incorpora la funcionalidad de creación masiva de entidades a partir de un archivo en formato JSON. Este archivo debe contener la información necesaria de las entidades, como sus clases y atributos, para que puedan ser procesadas y creadas de forma automatizada en el sistema.

---

## Programa en Python para eliminar entidades

La aplicación permite eliminar todas las entidades almacenadas en el sistema, ya sea de forma individual, por clase o en su totalidad. Esto lo realizará con el método DELETE. Si no se especifica nada en los campos, realizará una petición GET, recorrerá todas las entidades y las borrará. Antes de esto mandará un mensaje de advertencia y de confirmación.

Programa en Python que permita actualizar los atributos

La aplicación permite actualizar los valores de cualquier entidad desde la línea de comandos, seleccionando el identificador, el atributo y el nuevo valor. Los cambios en los atributos se realizan utilizando los métodos POST, PATCH y PUT:

POST: Si el atributo ya existe en la entidad, se actualiza con el nuevo valor; si no existe, se crea un nuevo atributo con el valor proporcionado.

PATCH: Solo actualiza el atributo si ya existe en la entidad, dejando los demás atributos intactos.

PUT: Reemplaza todos los atributos de la entidad con los nuevos valores proporcionados, sobrescribiendo completamente los atributos anteriores.

---

## Programa en Python que modifique automáticamente la posición de las entidades

La aplicación permite modificar automáticamente las posiciones de todas las entidades con atributos de latitud y longitud. Esto se logra mediante un script llamado Sensores Movimiento, que simula el movimiento de los animales.

El proceso funciona de la siguiente manera:

1. Petición GET: Se realiza una solicitud GET a la base de datos de entidades, seleccionando aquellas que tengan los atributos de latitud y longitud.

2. Simulación del Movimiento: El script simula el desplazamiento de los animales.

3. Petición PATCH: Con los nuevos valores de latitud y longitud generados, se actualizan las entidades en tiempo real.

---

## Aplicación en Python que permita mostrar gráficamente las diferentes entidades

La aplicación, desarrollada en Python, utiliza las bibliotecas Folium y PyQt5.QtWebEngineWidgets para representar gráficamente, en un mapa y en tiempo real, la localización georreferenciada de las entidades.

El usuario puede seleccionar las entidades a visualizar, definir un punto central y ajustar el zoom. Las posiciones se actualizan dinámicamente, permitiendo el seguimiento de los movimientos en tiempo real.

Implementar un programa en Python que ejerza de agente IoT que permita que un atributo de una entidad se modifique de forma periódica o bajo demanda mediante MQTT

Se implementa un programa en Python que actúa como agente IoT MQTT. Este agente permite modificar periódicamente o bajo demanda un atributo de una entidad, utilizando un broker MQTT.

En el caso de uso, el peso de los animales se envía mediante MQTT, y la aplicación se suscribe a un topic para recibir la información y actualizar el sistema en tiempo real.

---

## Implementar un programa en Python que ejerza de agente IoT que permita modificar el atributo de una entidad mediante el uso de CoAP

La aplicación incluye un servidor CoAP que escucha en el puerto 5683 y permite actualizar atributos de las entidades, como el estado de salud. Las peticiones se procesan y los cambios se reflejan automáticamente en Orion.

---

## Implementar una notificación

El sistema permite definir un área de geofencing mediante coordenadas calculadas en función de un punto central y un perímetro. Si un animal sale del perímetro, se genera una notificación automática con los datos del evento y se envía a Orion y al puerto configurado por el usuario.

---

## Conclusiones del Proyecto IoT

El proyecto implementa una solución integral y escalable para la gestión y monitoreo de entidades geolocalizadas en un entorno ganadero.

#### Aspectos destacados:

1. Diseño y usabilidad: Interfaz gráfica intuitiva con PyQt5 y visualización en tiempo real con Folium.

2. Gestión dinámica de entidades: Creación, actualización y eliminación flexible y masiva.

3. Integración IoT: Protocolos MQTT y CoAP implementados para comunicación eficiente.

4. Simulación y supervisión: Movimiento en tiempo real y control mediante geofencing.

5. Alertas automatizadas: Notificaciones en tiempo real con Orion y puertos configurables.

6. Escalabilidad y aplicabilidad: Preparado para escenarios de mayor escala e integración futura.

---

## Reflexión final

Este proyecto IoT ha mostrado cómo las nuevas tecnologías pueden usarse para resolver problemas prácticos, como gestionar el ganado de forma más eficiente. Al combinar protocolos IoT, herramientas de visualización en tiempo real y sistemas de notificación, hemos creado una solución sólida y fácil de ampliar, que puede servir de base para mejoras y avances futuros en agricultura inteligente y gestión de recursos.
