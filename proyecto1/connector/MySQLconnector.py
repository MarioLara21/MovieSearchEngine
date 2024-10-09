import pika
import mariadb 
import os
import json
import hashlib
import time

from elasticsearch import Elasticsearch

def ejecutarQuery(query):
    conn = mariadb.connect( 
            user= os.environ.get("MDB_USERNAME"), 
            password= os.environ.get("MDB_PASSWORD"), 
            host= os.environ.get("MDB_HOST"), 
            database= os.environ.get("MDB_DATABASE"),
            port= 3307
    ) 
    cursor = conn.cursor()
    cursor.execute(query)
    resultados = cursor.fetchall()
    cursor.close()
    conn.close()
    return resultados

def lista_a_diccionario(lista):
    columnas = ['id', 'nombre', 'apellido', 'carnet', 'carrera', 'edad', 'correo']
    lista_diccionarios = []
    for tupla in lista:
        diccionario = {}
        for i, columna in enumerate(columnas):
            diccionario[columna] = tupla[i]
        lista_diccionarios.append(diccionario)
    return lista_diccionarios


# Basado en: https://rabbitmq.com/tutorials/tutorial-two-python

def callback(ch, method, properties, body):
    try:
        jsond = json.loads(body)
        es_client = Elasticsearch("http://"+ESENDPOINT+":9200", basic_auth=("elastic", ESPASSWORD), verify_certs=False)
        print(f"Recibido: {jsond}")
        jobId = jsond["job_id"]
        groupId = jsond["group_id"]
        divisionGrp = groupId.split("-")
        offset = str(divisionGrp[1])
        tabla = "estudiantes"
        

        response = es_client.search(index=ESINDEX, body={"query": {"term": {"job_id": "job606"}}})
        print("hola"+ str(len(response['hits']['hits'])))
        if len(response['hits']['hits']) != 0:
            for hit in response['hits']['hits']:
                jsonread = hit['_source']
                group_size = int(jsonread['source']['grp_size'])          # extrae el group size
                    
 
            query = f"SELECT * FROM {tabla} ORDER BY id LIMIT {offset}, {group_size}"
            resultados = ejecutarQuery(query)

            if resultados is not None:
                docs = lista_a_diccionario(resultados)
                print(docs)
                # Actualizar el documento en Elasticsearch

                es_client.index(index=ESGROUPINDEX, body={"job_id": jobId, "group_id": groupId, "docs": docs})

                # Enviar mensaje a la cola de destino sin el campo 'docs'
                
                channel.basic_publish(exchange='', routing_key=RABBIT_DEST, body=json.dumps(jsond))
                print(f"Procesado y enviado a {RABBIT_DEST}")

            else:
                print("No se pudo obtener los datos de MySQL")

    except Exception as e:
        print("Error:", e)


if __name__ == '__main__':
    # Configuración de RabbitMQ
    RABBIT_MQ=os.getenv('RABBITMQ')
    RABBIT_MQ_PASSWORD=os.getenv('RABBITPASS')
    RABBIT_QUEUE=os.getenv('RABBITQUEUE')
    RABBIT_DEST = os.getenv('RABBITQUEUEDEST')
   
    # Configuración de Elasticsearch
    ESENDPOINT=os.getenv('ESENDPOINT')
    ESPASSWORD=os.getenv('ESPASSWORD')
    ESINDEX=os.getenv('JOBINDEX')
    ESGROUPINDEX=os.getenv('GROUPINDEX')

    # Conexión con RabbitMQ
    credentials = pika.PlainCredentials('user', RABBIT_MQ_PASSWORD)
    parameters = pika.ConnectionParameters(host=RABBIT_MQ, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=RABBIT_DEST, durable = True)
    while True:
        print("ColaReady...")
        channel.basic_consume(queue=RABBIT_QUEUE, on_message_callback=callback, auto_ack=True) # Llama a callback cuando recibe un mensaje
        channel.start_consuming()
        time.sleep(5)