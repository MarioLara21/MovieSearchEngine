# Documentación Proyecto 1 
### Integrantes: 
- Fabián Bustos: 2020048344
- Ian Murillo: 2020148871
- Luany Masis: 2022155917
- David Blanco: 2020053806
- Harlen Quirós: 2022035693


##  Instalación
Para la instalación del proyecto se debe de contar con las siguientes carpetas: ‘charts’, ‘orchestrator’, ‘conector’, ‘processor’, ‘regex’ y ‘publisher’. Aparte de estas carpetas, se necesita de los archivos: ‘BaseEstudiantesTEC.py’, ‘ejemplo01.json’ e ‘instrucciones para publicar.txt’. Con esto presente se puede comenzar la instalación de los helm charts y la creación de la base de datos. Cabe recalcar que se debe de tener instalado ‘Docker’ y ‘LENS’.

### Creación para la base de datos
La base de datos se crea de manera local, por lo que se debe tener mariadb instalado en la computadora en la cual se desea correr el proyecto. Para descargar la base de datos se puede utilizar el siguiente link: https://mariadb.org/download/?t=mariadb&p=mariadb&r=11.3.2&os=windows&cpu=x86_64&pkg=msi&mirror=starburst_stlouis una vez se realiza la descarga, se debe cambiar los ajustes del puerto, por default se encuentra en el puerto 3306, dado que este puerto se encuentra ocupado se debe de cambiar al puerto 3307. Con esto hecho, se corre el archivo ‘BaseEstudiantesTEC.py’. Este debe de crear la base de datos con sus respectivas tablas con información predeterminada.

### Charts
Se debe comenzar por abrir la terminal desde la carpeta donde queremos incluir los helm charts y correr los comandos indicados en el ejemplo. Se debe dar un tiempo de inicialización para los `PODS` por lo que una vez se fijen en `LENS` que los `PODS` estén inicializados, se puede seguir corriendo los siguientes comandos.

ej.:
    helm install bootstrap bootstrap

    helm install monitoring-stack monitoring-stack

    helm install databases databases

    helm install grafana-config grafana-config

    helm install application application




### Generar imágenes

Una vez se terminen de instalar los helm charts, se debe de crear las imágenes para poder continuar con el proyecto. Para cada imágen se necesita hacer el docker login y proceder a correr los comandos brindados en el ejemplo. Para correr los comandos, se debe de estar en la ubicación donde se encuentran los ‘Dockerfiles’. Estos se encuentran dentro de las carpetas ‘orchestrator’, ‘conector’, ‘processor’, ‘regex’ y ‘publisher’, el nombre de sus imágenes son las de las carpetas respectivamente. 

ej.:
docker build -t **usuariodocker**/**nombreimagen** .
docker push **usuariodocker**/**nombreimagen**
 

### Elasticsearch Publisher

El "Elasticsearch Publisher" es un componente que se encarga de consumir mensajes de una cola de RabbitMQ y publicar los datos correspondientes en un clúster de Elasticsearch. Tiene las siguientes funciones:

Está diseñado para conectarse a una cola de RabbitMQ, que se identifica como root.stages[name=load].source_queue. De esta cola se dedica a consumir mensajes que llegan.
El "Elasticsearch Publisher" extrae la información relevante del mensaje cuando es recibido, en particular los identificadores group_id y job_id.
Una vez que los documentos fueron obtenidos, el Elasticsearch Publisher publica cada documento en un índice en Elasticsearch, el cual es definido en ‘root.stages[name=load].destination_data_source’.
Los documentos son eliminados luego de ser publicados con éxito, con el fin de que los datos no sean procesados nuevamente.


###MySQL Connector
Se encarga de actuar como intermediario entre MariaDB y RabbitMQ. Su tarea es básicamente  procesar mensajes recibidos desde una cola de RabbitMQ y realizar operaciones de consulta en ‘MariaDB’. Sus funciones son las siguientes:

Consumo de mensajes: Se conecta a ‘root.stages[extract].source_queue’, y consume mensajes que llegan a dicha cola.

Ejecución: La consulta se ejecuta en el datasource, el cual es representado por ‘root.source.data_source’.

Transformación a documentos JSON: Cuando la consulta se termina de ejecutar y se obtienen los resultados, se transforman los resultados a JSON y se guardan en el campo de ‘docs’.

Envío de mensaje a la cola: Cuando el documento de un grupo es actualizado, se almacena un mensaje en la cola de RabbitMQ (‘root.stages[name=extract].destination_queue’) sin el campo de ‘docs’.

Solicitud de nuevos mensajes: Cuando se termina de procesar un grupo, se solicita otro mensaje a la cola ‘root.stages[name=extract].source_queue’.

###SQL Processor


El componente SQL Processor revisa una cola de RabbitMQ y asocia los valores que ya posee de una tabla de MariaDB que consiguió en el Connector, en el caso del proyecto la cola cuenta con los datos de los estudiantes, entre ellos sus ID y con eso, busca en la tabla carro, la descripción de los autos asociados al id y sobre el documento de grupo, lo edita para agregar la información del auto asociada a cada estudiante.

Esto lo hace siguiendo una serie de pasos:

Primero, obtiene el índice groups del servidor de ElasticSearch representado por "root.control_data_source", el documento del grupo identificado por el group_id y desde
el índice jobs, obtiene el documento del job representado por job_id.

Se obtiene la
"root.stages[name=transform].transformation[type=sql_transform]".expression y se
realizan los reemplazos de variables, aquí es donde se edita con la nueva información.

Esto lo realiza paea cada uno de los documentos que se encuentran en el campo docs, del documento del grupo, esto mediante la expresión "root.stages[name=transform].transformation[type=sql_transform].source_data_source".


### REGEX Processor

El componente de Regex Processor se encarga de leer mensajes que lleguen mediante la cola de RabbitMQ. Cuando recibe un mensaje este lo asigna a uno de sus pods: 

Obtiene un índice del servidor de Elastic, un documento de un grupo identificado con su debido id y un job. identificado de igual manera. 
A cada documento se le ejecuta una transformación según el dato recibido. En este caso específico, se reciben el número de carnet de estudiante y su correo y se genera una identificación única. 







### Recomendaciones:

Uso de Docker: Utilizar contenedores de Docker es esencial para manejar eficientemente todas las bases de datos, dependencias, configuraciones y otros aspectos del desarrollo.
Visualización y monitoreo con Lens: Supervisar la base de datos de MariaDB con Lens es una herramienta muy importante, con la cual se puede tener rastro de que todo esté funcionando bien.
Developer tools Elastic: Utilizar el puerto de elasticsearch y digitar código en la sección de desarrollador es importante para realizar funciones de debug y encontrar errores e inconsistencias.
Uso de línea de comandos: El uso de línea de comandos para la instalación de helm charts y ejecución de aplicaciones, es una manera más sencilla de correr todas las funciones necesarias del proyecto.
Revisar documentación de Elasticsearch: Leer documentación para entender cómo funcionan las conexiones de Elasticsearch y tener un avance más fluido a la hora de construir el programa.
Verificar la ocupación actual de los puertos de la máquina por usarse, si un puerto ya se encuentra en uso puede que se le asigne al proyecto puertos diferentes.
Asegurarse de que la opción de Kubernetes esté activada, esta se puede verificar desde los ajustes del Docker Desktop y es requerido para la correcta ejecución del proyecto.
Para crear imágenes de Docker de manera adecuada, se recomienda asegurar un login correcto a la cuenta adecuada de Docker.
Leer comunidades y foros, en donde se puedan encontrar explicaciones junto a su código.
Ver tutoriales detallados, así como los vistos en clase, como otros por medios como YouTube.


### Conclusiones:

	El proceso de aprendizaje para pasar datos de una base de datos a otra fue muy importante ya que es funcional para el mundo laboral. De la misma forma se conocieron algunos otros metodos para el traspaso de datos entre bases de datos en el proceso de desarrollos. Un ejemplo de ellos es Logstach que se asocia mas facilmente con ElasticSearch. 
	El DMP (Data Migration Platform) es un sistema complejo con varios componentes requeridos para su funcionamiento. Este busca facilitar la migración de datos entre las plataformas de MariaDB y Elasticsearch, utilizando pipelines ETL. Este destaca por el uso de tecnologías modernas que son usadas en casos cotidianos del área de bases de datos. Esta elección conllevó una formación activa en herramientas reales y que siguen siendo utilizadas por la industria. Además, la limitación del alcance del proyecto a una única ruta de migración y a un conjunto específico de transformaciones posiblemente simplifica el desarrollo y la implementación, ofreciendo un enfoque pragmático y centrado en resultados.
