import time
import datetime as dt
import struct
from paho.mqtt import client as mqtt_client
from info import broker, port, topic, client_pub

client_id = client_pub

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Successfully connected to MQTT broker")
        else:
            print("Failed to connect, return code %d", rc)
    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client):
    with open('mqtt\\testimage.jpg','rb') as file: # open the image
        lotNum = 1
        timestamp = int(time.time())
        status = 1

        header = struct.pack('>BIB', lotNum, timestamp, status)

        filecontent = file.read()
        image_bytes = bytearray(filecontent) # convert the image to byte array

        payload = header + image_bytes
        result = client.publish(topic,payload,2) # publish the byte array to the MQTT topic
        
    msg_status = result[0]
    if msg_status == 0:
        print(f"message sent to topic {topic}")
    else:
        print(f"Failed to send message to topic {topic}")

def main():
    client = connect_mqtt()
    client.loop_start()
    publish(client)
    time.sleep(5)
    client.loop_stop()
    
if __name__ == '__main__':
    main()