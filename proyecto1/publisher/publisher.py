import pika
import os
import json
from elasticsearch import Elasticsearch

if __name__ == '__main__':
    # Parámetros de conexión con RabbitMQ
    RABBIT_MQ = os.getenv('RABBITMQ')
    RABBIT_MQ_PASSWORD = os.getenv('RABBITPASS')
    QUEUE_NAME = os.getenv('RABBITQUEUE')

    # Parámetros de conexión a Elasticsearch
    ESENDPOINT = os.getenv('ESENDPOINT')
    ESPASSWORD = os.getenv('ESPASSWORD')
    GROUPINDEX = os.getenv('GROUPINDEX')
    JOBINDEX = os.getenv('JOBINDEX')

    # Conexión con RabbitMQ
    credentials = pika.PlainCredentials('user', RABBIT_MQ_PASSWORD)
    parameters = pika.ConnectionParameters(host=RABBIT_MQ, credentials=credentials)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME, durable=True)

    # Conexión con Elasticsearch
    client = Elasticsearch("http://" + ESENDPOINT + ":9200", basic_auth=("elastic", ESPASSWORD), verify_certs=False)

    # Loop donde el controller va a revisar el índice por mensajes no procesados.
    while True:
        print("Revisando...")
        try:
            method_frame, header_frame, body = channel.basic_get(queue=QUEUE_NAME)
            if method_frame:
                message = json.loads(body)
                group_id = message["group_id"]
                job_id = message["job_id"]
                print(f"Received message for group_id: {group_id}")

                # Obtiene el documento del grupo desde Elasticsearch
                group_doc = client.get(index=GROUPINDEX, id=group_id)

                # Obtiene el documento del job desde Elasticsearch
                job_doc = client.get(index=JOBINDEX, id=job_id)

                # Procesa cada documento en el campo docs
                for doc in group_doc["_source"]["docs"]:
                    # Publica el documento en el índice destination_data_source
                    client.index(index=group_doc["_source"]["destination_data_source"], body=doc)

                # Remueve el documento del índice de groups en Elasticsearch
                client.delete(index=GROUPINDEX, id=group_id)

                print("Processing complete.")
            else:
                print("No messages in the queue.")
        except Exception as e:
            print("Error:", e)
            continue
        
        
    connection.close()
