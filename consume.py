import yaml
import praw
import threading
import json
import os
from kafka import KafkaConsumer
MAX_SUBMITTED=1000
from dotenv import load_dotenv
load_dotenv()

consumer = None
topic = None


if __name__ == "__main__":

    kafka_config = {k: os.environ[k] for k in ['host', 'port', 'topic']}
    print(f'kafka_config: {kafka_config}')

    consumer = KafkaConsumer(bootstrap_servers=f'{kafka_config["host"]}:{kafka_config["port"]}',
                             auto_offset_reset='earliest',
                             enable_auto_commit=False,
                             group_id='my-group',
                             value_deserializer=lambda x: json.loads(x.decode('utf-8')));
    topic = kafka_config["topic"]
    consumer.subscribe(topic)
    for message in consumer:
        print(message)
