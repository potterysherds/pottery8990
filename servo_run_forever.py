import RPi.GPIO as GPIO
import time

servoPIN = 18
buttonPIN = 14

print("Setting up")
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPIN, GPIO.OUT)
GPIO.setup(buttonPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
p = GPIO.PWM(servoPIN, 50)
spin = False

while True:
    #print("Enter loop")   
    input_state = GPIO.input(buttonPIN)
    try:
        if input_state == False:
            time.sleep(0.2)
            #print("2")
            spin = not spin
        if spin:
            #print("3")
            p.start(0.5)
        else:
            #print("4")
            p.stop()
    except:
        GPIO.cleanup()

