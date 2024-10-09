import requests
import pika
import os
import json
import math
import time
import mariadb
from elasticsearch import Elasticsearch
from elasticsearch import TransportError

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
        valores = {}

        response = es_client.search(index=JOBINDEX, body={"query": {"term": {"job_id": "job606"}}})
        if len(response['hits']['hits']) != 0:
            jsonread = response['hits']['hits']['_source']
            for stage in jsonread["stages"]:
                if stage["name"] == "transform":
                    for transformacion in stage["transformation"]:
                        if transformacion["type"] == "sql_transform":
                            sql_Sentence = transformacion["expression"]                          
                            valores["table"] = transformacion["table"]
                            valores["doc_field"] = transformacion["doc_field"]
                            valores["field_description"] = transformacion["fields_mapping"]["field_description"] 
                            valores["field_owner"] = transformacion["fields_mapping"]["field_owner"] 
                            for placeholder, valor in valores.items():
                                sql_Sentence = sql_Sentence.replace("%{" + placeholder + "}%", str(valor))
                                sentencia_sin_id = sql_Sentence.split("=")
        print("mapeo")
        response = es_client.search(index=GROUPINDEX, body={"query": {"term": {"group_id.keyword": "job606-0"}}})
        if len(response['hits']['hits']) != 0:
            for hit in response['hits']['hits']:
                hit_ult = hit
            jsonread = hit_ult['_source']["docs"]
            datos_nuevo = []
            for datos in jsonread:
                id_estudiante = datos["id"]
                query_final = sentencia_sin_id[0] + "=" + str(id_estudiante)
                resultados = ejecutarQuery(query_final)
                agregacion = valores["field_description"]
                datos[agregacion] = resultados[0][0]
                datos_nuevo.append(datos)
            es_client.update(index=GROUPINDEX, id=hit['_id'], doc= {'docs': datos}, refresh = True)


            # Enviar mensaje a la cola de destino sin el campo 'docs'
            channel.basic_publish(exchange='', routing_key=RABBIT_DEST, body=json.dumps(jsond))
            print(f"Procesado y enviado a {RABBIT_DEST}")

        else:
            print("No se pudo obtener datos de MySQL")

    except Exception as e:
        print("Error:", e)


# Configuración de conexiones
if __name__ == '__main__':
    # Parámetros de conexión con RabbitMQ
    RABBIT_MQ=os.getenv('RABBITMQ')
    RABBIT_MQ_PASSWORD=os.getenv('RABBITPASS')
    RABBIT_QUEUE=os.getenv('RABBITQUEUE')
    RABBIT_DEST = os.getenv('RABBITQUEUEDEST')

    # Parámetros de conexión a Elasticsearch
    ESENDPOINT=os.getenv('ESENDPOINT')
    ESPASSWORD=os.getenv('ESPASSWORD')
    JOBINDEX=os.getenv('JOBINDEX')
    GROUPINDEX=os.getenv('GROUPINDEX')

    # # Conexión a RabbitMQ
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

