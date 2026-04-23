from picamera2 import Picamera2, Preview
import time

def capture(cam, timestamp):
    filename = "img_{}.jpg".format(timestamp)

    cam.capture_file(filename)
    return filename

def main():
    picam2 = Picamera2()
    camera_config = picam2.create_preview_configuration()
    picam2.configure(camera_config)
    picam2.start_preview(Preview.QTGL)
    picam2.start()
    #time.sleep(300)
    timestamp = int(time.time())
    imageName = capture(picam2, timestamp)
    print(imageName)

if __name__ == "__main__":
              main()
