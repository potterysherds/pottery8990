from picamera import PiCamera

import time
import RPi.GPIO as GPIO

#for push button input
GPIO.setmode(GPIO.BCM)

camera = PiCamera()
#FOR 5MP
'''
camera.resolution = (2592,1944)
camera.framerate = 15
camera.start_preview()
'''

#FOR 8MP

camera.resolution = (3280,2464)
camera.start_preview(resolution=(1440,1080))


buttonPIN = 14
GPIO.setup(buttonPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

images = 0

while True:
  input_state = GPIO.input(buttonPIN)
  try:
    if input_state == False:
      time.sleep(0.2)
      camera.capture('8mpmodel' + str(images) + '.raw', format='rgb')
      images = images + 1
      #camera.capture('./image' + str(images) + '.raw', format='rgb')
  except Exception as e:
    print(e)
camera.stop_preview()
camera.close()
GPIO.cleanup()
