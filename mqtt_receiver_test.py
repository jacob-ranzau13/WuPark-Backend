from paho.mqtt import client as mqtt_client
from cryptography.fernet import Fernet
import base64, json
from prompt_toolkit import Application
import requests as rq
import datetime as dt
from dotenv import load_dotenv
import os

from handler import response
from info import broker, port, topic, topic_sub, client_sub
import db_functions as db_funcs

import queue, threading

work_q = queue.Queue()

class MessageProcessor:
    @staticmethod
    def encrypt_image(image_bytes: bytes) -> str:
        key = os.getenv("encryption_key").encode()
        cipher = Fernet(key)
        encrypted = cipher.encrypt(image_bytes)
        return base64.b64encode(encrypted).decode()
    

    @staticmethod
    def payload_to_json(payload: bytes) -> str:
        lotNum = payload[0]
        timestamp = int.from_bytes(payload[1:5], byteorder='big')
        status = payload[5]
        image_bytes = payload[6:]

        encrypted_image = MessageProcessor.encrypt_image(image_bytes)

        data = {
            "lot_num": lotNum,
            "timestamp_unix": timestamp,
            "timestamp_readable": dt.datetime.fromtimestamp(timestamp).isoformat(),
            "status": status,
            "image": encrypted_image

        }

        return json.dumps(data, indent=4)
    
    @staticmethod
    def handle_message(payload: bytes):
        json_data = MessageProcessor.payload_to_json(payload)
        print("Message received:")
        print(json_data)

        url = os.getenv("aws_url")
        key = os.getenv("aws_api_key")
        headers = {"x-api-key": key}
        response = rq.post(url=url, json=json_data, headers=headers)

        print("Status:", response.status_code)

class WorkerQueue:

    def __init__(self):
        self.queue = queue.Queue()
        self.start_worker()

    def start_worker(self):
        thread = threading.Thread(target=self.worker, daemon=True)
        thread.start()

    def worker(self):
        while True:
            data = self.queue.get()
            MessageProcessor.handle_message(data)
            self.queue.task_done()

    def add_task(self, payload):
        self.queue.put(payload)


class MQTTClient:

    def __init__(self, worker_queue: WorkerQueue):
        self.client_id = client_sub
        self.worker_queue = worker_queue

        self.client = mqtt_client.Client(
            mqtt_client.CallbackAPIVersion.VERSION1,
            self.client_id
        )

        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect(self):
        self.client.connect(broker, port, keepalive=30)
        self.client.reconnect_delay_set(1, 60)

    def subscribe(self):
        self.client.subscribe(topic_sub)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Successfully connected to MQTT broker")
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        self.worker_queue.add_task(msg.payload)

    def start(self):
        self.connect()
        self.subscribe()
        self.client.loop_forever()


class Application:

    def __init__(self):
        load_dotenv("env\\.env")
        db_funcs.table_setup()

        self.worker_queue = WorkerQueue()
        self.mqtt_client = MQTTClient(self.worker_queue)

    def run(self):
        self.mqtt_client.start()


if __name__ == "__main__":
    app = Application()
    app.run()