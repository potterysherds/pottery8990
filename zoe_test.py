from picamera import PiCamera

import time
import RPi.GPIO as GPIO
#import os

#copy-pasting stepper motor control from here
#https://medium.com/@Keithweaver_/controlling-stepper-motors-using-python-with-a-raspberry-pi-b3fbd482f886
GPIO.setmode(GPIO.BCM)
In1 = 12
In2 = 13
In3 = 16
In4 = 26
ENA = 22 # Can use PWM on EN pins to control speed?
ENB = 23
# Actual location (GPIO.BOARD)
#In1 = 32
#In2 = 33
#In3 = 36
#In4 = 37
#ENA = 15
#ENB = 16
control_pins = [In1,In2,In3,In4,ENA,ENB]
buttonPIN = 14

STEPS = 25600
DELAY = 0.002 # seconds

#get sherd name from command line?
#or write another script that assigns the sherd name
#create a folder for each sherd

#if not os.path.exists(directory):
#   os.makedirs(directory)
#camera = PiCamera()

for pin in control_pins:
  #GPIO.setup(pin, GPIO.BCM)
  GPIO.setup(pin, GPIO.OUT)
  #GPIO.output(pin, 0)
GPIO.output(ENA, True)
GPIO.output(ENB, True)

# Taken from servo_button_control.py
GPIO.setup(buttonPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


''' # might not match our wiring
halfstep_seq = [
  [1,0,0,0],
  [1,1,0,0],
  [0,1,0,0],
  [0,1,1,0],
  [0,0,1,0],
  [0,0,1,1],
  [0,0,0,1],
  [1,0,0,1]
]
halfstep_seq = [ # Motor doesn't seem to be able to handle half-steps
  [1,0,0,0],
  [1,0,1,0],
  [0,0,1,0],
  [0,1,1,0],
  [0,1,0,0],
  [0,1,0,1],
  [0,0,0,1],
  [1,0,0,1]
]
'''
halfstep_seq = [
  [1,0,1,0], # A high, A\ low, B high, B\ low
  [0,1,1,0], # A low, A\ high, B high, B\low
  [0,1,0,1], # A low, A\ high, B low, B\ high
  [1,0,0,1]  # A high, A\ low, B low, B\ high
]

#When we're ready to take pics, uncomment the camera lines below
#Also uncomment the image_num increment
#not sure how to save as .raw yet

#camera.start_preview()
#image_num = 0
for i in range(STEPS): #replace with while True to spin forever
  for j in range(4): #loop through step seq
    for pin in range(4): #assign output to pin
      GPIO.output(control_pins[pin], halfstep_seq[j][pin])
    print('i = ' + str(i) + '; step = ' + str(j+1))
    time.sleep(DELAY)
  if i % 5 == 0:
    #camera.capture('./image' + str(image_num) + '.png')
    #image_num = image_num + 1
    time.sleep(.5)
    while True:
      if GPIO.input(buttonPIN) == False:
        break
#camera.stop_preview()
GPIO.cleanup()
