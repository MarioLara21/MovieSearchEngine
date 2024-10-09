import json
import pika
import os
from elasticsearch import Elasticsearch
from kubernetes import client, config
import re 
from pika import channel 

config.load_kube_config()
kubernetes_client = client.CoreV1Api()

RABBIT_MQ = os.getenv('RABBITMQ')
RABBIT_MQ_PASSWORD = os.getenv('RABBITPASS')
RABBIT_QUEUE = 'root.stages[name=transform].transformation[type=regex_transform].source_queue'

ES_ENDPOINT = os.getenv('ESENDPOINT')
ES_PASSWORD = os.getenv('ESPASSWORD')
GROUP_INDEX = 'root.control_data_source'
JOB_INDEX = 'jobs'

# conn space 
credentials = pika.PlainCredentials('user', RABBIT_MQ_PASSWORD)
param = pika.ConnectionParameters(host=RABBIT_MQ, credentials=credentials)
connection = pika.BlockingConnection(param)
channelRabbit = connection.channel()
channelRabbit.queue_declare(queue=RABBIT_QUEUE, durable=True)

# es
es_client = Elasticsearch("http://" + ES_ENDPOINT + ":9200", basic_auth=("elastic", ES_PASSWORD), verify_certs=False)


def proc_mensaje(ch, method, properties, body):
    try:
        message = json.loads(body.decode('utf-8'))

        group_id = message.get('group_id')
        group_document = es_client.get(index=GROUP_INDEX, id=group_id)['_source']

        job_id = group_document.get('job_id')
        job_document = es_client.get(index=JOB_INDEX, id=job_id)['_source']

        for doc in group_document.get('docs', []):
            regex_expression = job_document['stages']['transform']['transformation']['regex_config']['regex_expression']
            field = job_document['stages']['transform']['transformation']['regex_config']['field']
            group = job_document['stages']['transform']['transformation']['regex_config']['group']

            if regex_expression and field in doc:
                match = re.search(regex_expression, doc[field])
                if match:
                    doc[field] = match.group(group)


    except Exception as e:
        print("error", e)

    ch.basic_ack(delivery_tag=method.delivery_tag)


def proc_regex():
    channel.basic_consume(queue=RABBIT_QUEUE, on_message_callback=proc_mensaje)
    print('aaa')
    channel.start_consuming()


if __name__ == '__main__':
    proc_regex()