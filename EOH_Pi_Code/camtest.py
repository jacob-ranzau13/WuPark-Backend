from picamera2 import Picamera2, Preview
import paho.mqtt.client as mqtt_client

import struct, time, os

broker = 'broker.hivemq.com'
port = 1883
topic = 'wupark/photos'
client_id = 'wupark-pub'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("connection successful")
        else:
            print("connection failed, return code %d", rc)

    client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION1, client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    print("client ready")
    return client

def capture(cam, timestamp):
    filename = "img_{}.jpg".format(timestamp)

    cam.capture_file(filename)
    return filename

def transmit(image, client, timestamp, x):
    with open(image, 'rb') as file:
        lotNum = 1
        status = x

        header = struct.pack('>BIB', lotNum, timestamp, status)
        filecontent = file.read()
        imageBytes = bytearray(filecontent)
        payload = header + imageBytes

        result = client.publish(topic, payload, 2)

    msg_status = result[0]
    if msg_status != 0:
        print("message failed")

def main():
    picam2 = Picamera2()
    config = picam2.create_still_configuration(main={"size": (1280, 720)}) # 720p is as high as we can go under 200 kb
    picam2.configure(config)
    picam2.start()

    client = connect_mqtt()
    client.loop_start()
    print("connecting to broker")

    for x in range(1):
        timestamp = int(time.time())
        imageName = capture(picam2, timestamp)
        
        transmit(imageName, client, timestamp, x + 10)
        print("message {} transmitted".format(x + 1))

        client.loop_stop()
        if os.path.exists(imageName):
            os.remove(imageName)

        time.sleep(15)
    
if __name__ == "__main__":
    main()
