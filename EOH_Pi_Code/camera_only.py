from picamera2 import Picamera2
import time

def capture(cam, timestamp):
    filename = "img_{}.jpg".format(timestamp)

    cam.capture_file(filename)
    return filename

def main():
    picam2 = Picamera2()
    config = picam2.create_still_configuration(main={"size": (1280, 720)}) # 720p is as high as we can go under 200 kb
    picam2.configure(config)
    picam2.start()

    timestamp = int(time.time())
    imageName = capture(picam2, timestamp)
    print(imageName)

if __name__ == "__main__":
              main()
