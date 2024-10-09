# Proyecto 2 - Plataforma de busquedas de películas 
## Bases de Datos 2

_Integrantes:_
- Fabián Bustos: 2020048344
- Ian Murillo: 2020148871
- Luany Masis: 2022155917
- David Blanco: 2020053806
- Harlen Quirós: 2022035693
- Mario Lara: 2020035341

La plataforma busca funcionar como una especie de buscador, donde el usuario tiene la capacidad de buscar películas por su nombre, nombres de actores y directores, reparto, y otra información relacionada. El usuario puede interactuar con la aplicación mediante un prototipo de Thunkable, el cual fue dirigido a uso en aparatos móviles. 

## Instalación 

Los elementos del proyecto que necesitan instalación son Docker y Ngrok. Se asumirá que Docker ya se encuentra instalado. 

### Instalación Ngrok

1. Instalar ngrok via Chocolatey 
    
    choco install ngrok

2. Agregar Token
    
    ngrok config add-authtoken <your-ngrok-auth-token>
    
3. Correr en el puerto en el que se está ejecutando el proyecto

    ngrok http http://localhost:5000

Para llevar a cabo la instalación de los helm charts necesarios para la aplicación se requiere correr los siguientes comandos: 

    helm install application application 
    helm install monitoring-stack monitoring-stack

## Neo4j 

Una de las fuentes de la información de películas se obtiene de Neo4J. Neo4j es una sistema admninistrador de bases de datos de grafos. Esta almacena nodos, relaciones, y sus respectivos atributos. Esta propiedad la hace sumamente eficiente en representar relaciones y patrones entre los datos que almacena. 

Para esta aplicación en específico se utiliza la base de datos de ejemplo sobre películas. Contiene nodos que representan películas y personas, los cuales tienen relaciones entre si tales como "actuó en" o "dirigió", las cuales son esenciales para el funcionamiento de la aplicación. 

Mediante una representación visual del modelo de grafos que se encuentra en la base de películas, se puede observar como este es sumamente útil para evaluar las relaciones colaborativas que se llevan a cabo en el ambiente de las películas.

![neo4j1](resources/images/neo4j1.png)

Observando con más detalle, se pueden observar los diferentes tipos de relaciones que hay entre cada nodo así como los atributos que tiene cada uno. 

![neo4j2](resources/images/neo4j2.png)

La información que se obtiene de esta base de datos conforma una parte del funcionamiento de la aplicación. Toda esta información se accede mediante un API construida en Flask, la cual será explicada más adelante.

## Mongo Atlas 

Con respecto a Mongo Atlas, se debe crear la base de datos. Para crear la base de datos, se puede realizar mediante internet. Una vez se tenga la base de datos creada, se procede a crear los índices. Se debe ir al apartado de Atlas Search, y se ingresa al botón 'Create Index' donde se mostrará la siguiente pantalla:

![createIndex](resources/images/createIndex.png)

Se utilizará el JSON Editor, donde se configurará el mapping dependiendo del propósito del índice. Una vez realizados los índices, estos están listos para útilizar. Para efectos de este proyecto, se realizaron los índices de Cast, Directors y Plot.


## Flask API 

La aplicación utiliza un API de Python implementada utilizando Flask para comunicarse con las bases de datos necesarias. Ambas implementaciones utilizan librerías de Python para llevar a cabo las conexiones seguras con las bases de datos. Para neo4j se utiliza la librería del mismo nombre, para Mongo Atlas se utiliza la librería denominada "pymongo". Todo esto se encuentra en un contenedor y se puede ejecutar mediante Kubernetes. Este API contiene diversos endpoints con diferentes criterios de busqueda que son utilizados para  Este será accedido mediante la herramienta llamada Ngrok. 

## Grafana 

Grafana es una plataforma de análisis y monitoreo que se utilizará junto con Prometheus para supervisar el API y MongoDB Atlas.

#### Instalación y Configuración:

1. Instalar Grafana en Kubernetes:
Instalar Grafana en Kubernetes.

2. Configurar Prometheus:
Se utiliza y configura Prometheus para recolectar métricas del API y MongoDB Atlas.

3. Importar Dashboards:
Utilizar dashboards para visualizar las métricas de el API, como el número de peticiones y el tiempo de respuesta.


## Ngrok

Ngrok es una herramienta que permite realizar un port-forwarding de la computadora local y publicarlo en Internet. Ngrok juega un papel vital en este proyecto al facilitar la comunicación entre Thunkable y el API.

Uso: Ngrok funcionará como intermediario entre la aplicación móvil (Thunkable) y el API que se ejecuta localmente. Esto sirve para que la app pueda acceder al API local sin tener que desplegar el API en una nube.Ngrok proporciona una URL pública segura que redirige las solicitudes a la API local.

#### Instalación: 

1. Instalar ngrok via Chocolatey 
    
    choco install ngrok
2. Agregar Token
    
    ngrok config add-authtoken <your-ngrok-auth-token>
    
3. Correr en puerto 

    ngrok http http://localhost:8080

Se obtiene lo siguiente:

![ngrok_connection](resources/images/ngrok_connection.png)

## Thunkable 

Thunkable es una plataforma de desarrollo de aplicaciones móviles que permite crear aplicaciones de manera visual sin necesidad de escribir código.

#### Link al proyecto:

 [https://x.thunkable.com/copy/2127285eed2109ec7f5ec3adcf2da0f6]()

#### Implementación:

1. Crear Proyecto en Thunkable:
Se crea un nuevo proyecto en Thunkable y se configuran las pantallas y componentes necesarios para la aplicación, se debe elaborar la parte de diseño de pantalla y la codificación se realiza con bloques.

![thunkable0](resources/images/thunkable0.png)
![thunkable1](resources/images/thunkable1.png)

2. Configurar Conexión al API:
Usa las URLs proporcionadas por Ngrok para conectar la aplicación móvil al API.

![thunkable_api](resources/images/thunkable_api.png)

3. Autenticación y Autorización:
Implementar la autenticación y autorización de usuarios utilizando Firebase dentro de Thunkable.


## Firebase 

La base de datos de Firebase se utiliza en nuestro programa con el fin de autenticar usuarios. En caso de que el usuario que intente ingresar a la aplicacion no sea valido, devuelve un error.

Para crear la base de datos de Firebase, simplemente en la pagina principal del perfil: Agregar app -> Web -> Agregar nombre -> Registrar.

Firebase es llamado desde Thunkable utilizando "Realtime DB".

![firebase1](resources/images/firebase1.png)

En el proyecto de Thunkable se agregan los "Firebase Settings" los cuales son necesarios para el funcionamiento de la base de datos.

![firebase_settings](resources/images/firebase_settings.png)

El API key y el "Database URL" son encontrados dentro del perfil de Firebase, especificamente en: nombre_de_proyecto/Configuración de proyecto.

![firebase_config](firebase_config.png)

En la pestaña de autenticacion dentro de Firebase, se pueden observar los usuarios y métodos de acceso (en nuestro caso se utiliza correo electrónico y contraseña)

En la pestaña de "Realtime Database" se pueden observar los datos que hay dentro de la base de datos. Por ejemplo se muestran los datos de un correo de prueba:

![firebase_data](firebase_data.png)

## Pruebas Unitarias
Para las pruebas unitarias se va a utilizar una extensión de visual studio code llamda Thunder Client, la misma hace request a un URL deseado, en este se puede editar tanto el body, como el header del request.
Pruebas a cada endpoint de la api:

![titulo](resources/images/titulo.png)

![elenco](resources/images/elenco.png)

![trama](resources/images/trama.png)

![movies](resources/images/movies.png)

![actor](resources/images/actor.png)

![directores](resources/images/directores.png)

![producer](resources/images/producer.png)

![plot](resources/images/plot.png)

![cast1](resources/images/cast1.png)

![cast2](resources/images/cast2.png)

## Métricas del API
Estas son las métricas resultantes de distintos request hechos a cada endpoint de la API, estos se pueden ver en el puerto 8000 de la computadora. En estas se ve reflejado la cantidad de request hechas al endpoint y el tiempo de duración de los request.

![metricasAPI1](resources/images/MetricaApi1.png)

![metricasAPI2](resources/images/MetricaApi2.png)

![metricasAPI3](resources/images/MetricaApi3.png)

![metricasAPI4](resources/images/MetricaApi4.png)

![metricasAPI5](resources/images/MetricaApi5.png)

![metricasAPI6](resources/images/MetricaApi6.png)

![metricasAPI7](resources/images/MetricaApi7.png)

## Recomendaciones 

- Utilizar los comandos de Docker con sumo cuidado. Partes pequeñas del comando por correr pueden tener un gran impacto en qué contenedores o imágenes se crean. Algunos componentes del proyecto cuentan con imagenes oficiales de Docker, por lo que si no se es cuidadoso se puede llegar a crear o correr una imagen que no corresponde a la del proyecto si no a esta imagen oficial. Siempre utilizar los comandos de docker incluyendo su usuario propio para evitar confusiones. 

- Utilizar índices de busqueda para trabajar con Mongo Atlas. Estos incrementan el rendimiento de las consultas. 

- Estudiar bien la documentación de ambas bases de datos. Al ser de modelos que pueden ser relativamente poco conocidos, como el modelo de documentos y de grafos, puede conllevar cierta curva de aprendizaje.

- Familiarizarse con el lenguaje de query de Neo4J. Este implementa su propio lenguaje para realizar consultas, el cual está sumamente orientado a las relaciones por lo que se utiliza de forma muy distinta al SQL conocido. Estas funcione   s se vuelven importantes para la implementación del API para Neo4J. 

- Se recomienda probar los índices de Mongo Atlas, para asegurarse que el mapping sea el adecuado para la búsqueda.

- En caso de utilizar el método gratuito de Mongo Atlas, es iportante tener en cuenta que solo se pueden crear 3 índices. Es por esto que elegir la búsqueda que se hará sin índices antes de comenzar ahorra tiempo y trabajo.

- Monitorear el sistema utilizando Grafana y Prometheus, con el fin de obtener metricas para ver el rendimiento del sistema bajo un flujo de datos.

- Tomar en cuenta medidas de seguridad, para que los usuarios que utilicen la aplicación sean autenticados y verificados para un retorno de datos. Esto puede evitar problemas con las conexiones a bases de datos.

- Optimizar las consultas de Neo4j y Mongo Atlas mediante el uso de índices puede ser conveniente para el rendimiento de la aplicación.

- Es importante tener Python instalado, y sabes ubicar la ubicación del interprete para lograr instalar las librerias y dependencias mediante "PIP" sin problema alguno.

- El uso de Github es necesario para la implementacion de un proyecto con tantas partes. Su uso simplifica el trabajo en equipo para un resultado mas ordenado y fácil. Mediante la herramienta de GitHub Desktop se pueden realizar todo tipo de modificaciones al repositorio del proyecto.

## Conclusiones 

- El uso de bases de datos de grafos como Neo4j están muy bien diseñadas para la representación de datos con gran cantidad de relaciones. Esta forma de representarlos se aproxima de manera más acertada a la forma humana de visualizar relaciones entre datos que el modelo relacional de bases de datos. 

- El uso de Ngrok es una manera relativamente fácil de permitir conexiones remotas a un API. Esto facilitó mucho la implementación y el testeo del API. 

- Neo4j es una herramienta muy útil para manejar datos con muchas relaciones. Ekl hecho de que las consultas sean mediante grafos facilita la comprensión y análisis de relaciones complejas.

- MongoDB Atlas es muy flexible a la hora de manejar grandes volumenes de datos no estructurados. También es muy bueno a la hora de realizar busquedas y almacenar información.

- El uso de Thunkable junto a Firebase facilita la creación de aplicaciones funcionales sin necesidad de desarrollar código extenso y complicado.

- La importancia de monitorear datos para medir el rendimiento de la base de datos y el API permite observar que el sistema si funcione sin interrupciuones ni problemas. De igual manera nos ha ayudado con la resolución de problemas.

- La utilización de tecnologías tan nuevas es muy beneficioso para una aplicación, ya que es más escalable y más eficiente que el uso de tecnologías desactualizadas.

- El uso de archivos JSON para enviar datos entre la base de datos y la aplicacion Thunkable es fundamental para facilitar el manejo de datos.

- El uso de CORS al implementar FLASK-Cors fue muy importante en nuestra aplicación de búsqueda de películas para facilitar la interacción entre el frontend y el backend. 

- El desarrollo de la aplicacion fue fundamental para el aprendizaje acerca de conectar multiples tecnologias a la vez. De la misma manera para controlarlas por medio de comandos de consola.
