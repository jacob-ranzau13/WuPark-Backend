from picamera2 import Picamera2
import paho.mqtt.client as mqtt_client
import struct, time, os
import keyboard as kb

class CameraError(Exception):
    """Custom exception for camera-related errors."""
    pass

class CameraModule:
    """Handles image capture using the Raspberry Pi camera module."""
 
    DEFAULT_RESOLUTION = (1280, 720)
 
    def __init__(self, resolution: tuple = DEFAULT_RESOLUTION):
        self.resolution = resolution
        self.cam = Picamera2()
        self._configure()
 
    def _configure(self):
        config = self.cam.create_still_configuration(
            main={"size": self.resolution}
        )
        self.cam.configure(config)
 
    def start(self):
        self.cam.start()
 
    def capture(self, timestamp: int) -> str:
        """Capture an image and return the saved filename."""
        try:
            filename = f"img_{timestamp}.jpg"
            self.cam.capture_file(filename)
            return filename
        except Exception as e:
            error = CameraError(f"Camera capture failed: {e}")
            return error

    def cleanup(self, filename: str):
        """Remove a captured image file from disk."""
        if os.path.exists(filename):
            os.remove(filename)

class MQTTPublisher:
    """Manages MQTT connection and image payload publishing."""
 
    def __init__(self, broker: str, port: int, topic: str, client_id: str):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client_id = client_id
        self.client = self._build_client()
 
    def _build_client(self) -> mqtt_client.Client:
        client = mqtt_client.Client(
            mqtt_client.CallbackAPIVersion.VERSION1, self.client_id
        )
        client.on_connect = self._on_connect
        return client
 
    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connection successful")
        else:
            print(f"Connection failed, return code {rc}")
 
    def connect(self):
        self.client.connect(self.broker, self.port)
        self.client.loop_start()
        print("Connecting to broker...")
 
    def disconnect(self):
        self.client.loop_stop()
 
    def publish_image(self, image_path: str, timestamp: int, lot_num: int = 1, status: int = 1):
        """Pack image with a binary header and publish to the MQTT topic."""
        with open(image_path, 'rb') as f:
            header = struct.pack('>BIB', lot_num, timestamp, status)
            payload = header + bytearray(f.read())
 
        result = self.client.publish(self.topic, payload, qos=2)
        if result[0] != 0:
            print("Failed to transmit message")
        else:
            print("Message transmitted successfully")

class ParkingPublisher:
    """
    Orchestrates the camera and MQTT publisher.
    Listens for keyboard input and triggers capture + publish on spacebar.
    """
 
    CAPTURE_COOLDOWN = 5  # seconds between captures to prevent spam
 
    def __init__(self, camera: CameraModule, publisher: MQTTPublisher):
        self.camera = camera
        self.publisher = publisher
 
    def start(self):
        self.camera.start()
        self.publisher.connect()
        print("Ready — press SPACE to capture, Q to quit")
        self._listen()
 
    def capture_and_publish(self):
        timestamp = int(time.time())
        image_path = self.camera.capture(timestamp)
        if isinstance(image_path, CameraError):
            self.publisher.publish_image("error.jpg", timestamp, status=0)  # Publish error status
        else:
            try:
                self.publisher.publish_image(image_path, timestamp, status=1)
            finally:
                self.camera.cleanup(image_path)
        time.sleep(self.CAPTURE_COOLDOWN)
        print("Ready")
 
    def listen(self):
        while True:
            key = kb.read_key()
            if key == 'q':
                print("Exiting")
                self.publisher.disconnect()
                break
            elif key == 'space':
                self.capture_and_publish()

def main():
    camera = CameraModule()
    publisher = MQTTPublisher(
        broker='broker.hivemq.com',
        port=1883,
        topic='wupark/photos',
        client_id='wupark-pub'
    )
    app = ParkingPublisher(camera, publisher)
    app.start()

if __name__ == "__main__":
    main()