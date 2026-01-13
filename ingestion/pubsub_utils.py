import os
from google.cloud import pubsub_v1
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

project_id = os.environ['PROJECT__ID']

topic_name = os.environ['PUBSUB__TOPIC']

def publish_message():

    try:
    
        publisher = pubsub_v1.PublisherClient()
        
        topic_path = publisher.topic_path(project_id, topic_name)

        data = 'Ingestion logic completed'.encode('utf-8')
        
        future = publisher.publish(topic_path, data)

        message_id = future.result()

        logging.info(f'Message published successfully ID: {message_id}')
    
        return message_id

    except Exception:
        logging.exception('failed to publish message')