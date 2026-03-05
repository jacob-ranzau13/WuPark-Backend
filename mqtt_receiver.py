from paho.mqtt import client as mqtt_client
import struct
import base64, json
import requests as rq
import datetime as dt
from dotenv import load_dotenv
import os

from info import broker, port, topic, topic_sub, client_sub
import db_functions as db_funcs

import queue, threading

work_q = queue.Queue()

def handle_message(payload):
    lotNum, timestamp, status = struct.unpack('>BIB', payload[:6]) # unpack the header
    # datetime = dt.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M') # convert unix time to readable format
    image_bytes = payload[6:] # extract the image
    print("Image received {}".format(timestamp))

    image_b64 = base64.b64encode(image_bytes).decode('ascii') # encode image to base64 string
    data = {
        "lotNum": lotNum,
        "timestamp": timestamp,
        "status": status,
        "image": image_b64
    }

    url = os.getenv("aws_url")
    key = os.getenv("aws_api_key")
    headers = {"x-api-key": key}
    response = rq.post(url=url, json=data, headers=headers)

    print("Status:", response.status_code)

    with open("mqtt\\ReceivedImages\\output.json", "w") as f:
        json.dump(data, f)

def worker():
    while True:
        data = work_q.get()
        handle_message(data)  # send data to handler function
        work_q.task_done()

threading.Thread(target=worker, daemon=True).start()

client_id = client_sub

def connect_mqtt():
    def on_connect(client, userdata, flags, rc): # attempt to connect to MQTT broker
        if rc == 0:
            print("Successfully connected to MQTT broker")
        else:
            print("Failed to connect, return code %d", rc)

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
    client.on_connect = on_connect
    client.connect(broker, port, keepalive=30) # add reconnect functionality
    client.reconnect_delay_set(1, 60)
    return client

def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg): # offload message processing to worker thread
        work_q.put(msg.payload)

    client.subscribe(topic_sub)
    client.on_message = on_message

def main():
    db_funcs.table_setup() # ensure the database table is set up
    load_dotenv()  # load environment variables from .env file
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever() # subscribe to messages indefinitely
    
if __name__ == '__main__':
    main()