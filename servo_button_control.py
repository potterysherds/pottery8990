import RPi.GPIO as GPIO
import time

servoPIN = 18
buttonPIN = 14
spinTime = 0.1
stopTime = 3

print("Setting up")
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
GPIO.setup(buttonPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
p = GPIO.PWM(servoPIN, 50)
spin = False
print("Ready")

while True:
    #print("Enter loop")   
    input_state = GPIO.input(buttonPIN)
    try:
        if input_state == False:
            time.sleep(0.2)
            spin = not spin
        if spin:
            time.sleep(spinTime)
            p.stop()
            time.sleep(stopTime)
            #start the servo with duty cycle 50%
            p.start(0.25)
        else:
            p.stop()
    except:
        GPIO.cleanup()


