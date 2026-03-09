from paho.mqtt import client as mqtt_client
import base64, json
import requests as rq
import datetime as dt
from dotenv import load_dotenv
import os

from info import broker, port, topic, topic_sub, client_sub
import db_functions as db_funcs

import queue, threading

work_q = queue.Queue()

class MessageProcessor:
    @staticmethod
    def payload_to_json(payload: bytes) -> str:
        lotNum = payload[0]
        timestamp = int.from_bytes(payload[1:5], byteorder='big')
        status = payload[5]
        image_bytes = payload[6:]

        data = {
            "lot_num": lotNum,
            "timestamp_unix": timestamp,
            "timestamp_readable": dt.datetime.fromtimestamp(timestamp).isoformat(),
            "status": status,
            "image": len(image_bytes)

        }

        return json.dumps(data, indent=4)
    
    @staticmethod
    def handle_message(payload: bytes):
        json_data = MessageProcessor.payload_to_json(payload)
        print("Message received:")
        print(json_data)