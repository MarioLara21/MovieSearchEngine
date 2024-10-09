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

if __name__ == '__main__':
    # Parámetros de conexión con RabbitMQ
    RABBIT_MQ=os.getenv('RABBITMQ')
    RABBIT_MQ_PASSWORD=os.getenv('RABBITPASS')
    QUEUE_NAME=os.getenv('RABBITQUEUE')

    # Parámetros de conexión a Elasticsearch
    ESENDPOINT=os.getenv('ESENDPOINT')
    ESPASSWORD=os.getenv('ESPASSWORD')
    JOBINDEX=os.getenv('JOBINDEX')
    GROUPINDEX=os.getenv('GROUPINDEX')

    # Conexión con RabbitMQ
    # Código de referencia: https://www.rabbitmq.com/tutorials/tutorial-two-python.html
    credentials = pika.PlainCredentials('user', RABBIT_MQ_PASSWORD)
    parameters = pika.ConnectionParameters(host=RABBIT_MQ, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable = True) # Cola por la cual se mandan mensajes al RABBIT

    
    # Conexión con elasticsearch
    client = Elasticsearch("http://"+ESENDPOINT+":9200", basic_auth=("elastic", ESPASSWORD), verify_certs=False)

    try:
        client.indices.create(index=JOBINDEX)
        print(f"Index '{JOBINDEX}' created successfully.")
    except Exception as e:
        print(f"Index '{JOBINDEX}' already exists.")

    # Código de referencia: https://kb.objectrocket.com/elasticsearch/how-to-create-and-delete-elasticsearch-indexes-using-the-python-client-library

    try:
        client.indices.create(index=GROUPINDEX)
        print(f"Index '{GROUPINDEX}' created successfully.")
    except Exception as e:
        print(f"Index '{GROUPINDEX}' already exists.")
    # loop donde el controller va a revisar el índice por mensajes no procesados.
    while True:
        print("Revisando...")
        # Revisa hasta que recibe el request del kibana service.
        try:
            # busca las entradas que no estén procesadas.
            response = client.search(index=JOBINDEX, query = {"term": {
                "status": "new"
            }})
        except Exception as e:
            print("Error:", e)
            time.sleep(5)
            continue
        
        
        # si encontró algún documento

        if len(response['hits']['hits']) != 0:
            print("Found...")
            
            for hit in response['hits']['hits']:
                jsonread = hit['_source']
                job_id = jsonread['job_id']
                tabla_con = jsonread['source']['data_source']
                registros_base = ejecutarQuery(f"SELECT COUNT(1) FROM {tabla_con}")
                print(registros_base) 
                total_registros = registros_base[0][0] # extrae el total de mariadb
                group_size = int(jsonread['source']['grp_size']) # extrae el group size
                cant_groups = math.ceil(total_registros/group_size)
                print(total_registros)
                print(jsonread)

                # Se procesan los splits para publicarlos en la cola de RabbitMQ
                for split in range(cant_groups):
                    offset = split * group_size
                    json_publish = {"job_id": job_id,
                                    "group_id": job_id +"-"+str(offset)
                                    }
                    json_message = json.dumps(json_publish)
                    #Aqui publica los documentos en el indice groups
                    client.index(index=GROUPINDEX, body=json_message)
                    #subir los json al groups
                    client.update(index=JOBINDEX, id=hit['_id'], doc= {'status': "In-Progress"}, refresh = True)
                    channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=json_message)
                # Se actualiza el documento como procesado,
                

        time.sleep(5)
    #connection.close()