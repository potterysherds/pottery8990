from time import sleep
from datetime import datetime
from sh import gphoto2 as gp
import signal, os, subprocess
import RPi.GPIO as GPIO

# Created at 1/22 11:00 right before CDR
# Camera control code credit: The Zan Show
# Motor control code credit: https://medium.com/@Keithweaver_/controlling-stepper-motors-using-python-with-a-raspberry-pi-b3fbd482f886

# Define pins for motor controll output
GPIO.setmode(GPIO.BCM)
In1 = 12
In2 = 13
In3 = 16
In4 = 26
control_pins = [In1,In2,In3,In4]

for pin in control_pins:
    GPIO.setup(pin, GPIO.OUT)

step_seq = [
    [1,0,1,0], # A high, A\ low, B high, B\ low
    [0,1,1,0], # A low, A\ high, B high, B\low
    [0,1,0,1], # A low, A\ high, B low, B\ high
    [1,0,0,1]  # A high, A\ low, B low, B\ high
]

# Define constant commands for terimnal window camera control
#picID = "PiShots"
suffix = ''
clearCommand = ["--folder", "/store_00020001/DCIM/100CANON", \
                "--delete-all-files", "-R"] # Might be different in our camera
#triggerCommand = ["--trigger-capture"]
captureCommand = "--capture-image-and-download"
sudo = "sudo "
#downloadCommand = ["--get-all-files"]

# More constants for scanning
NUM_OF_PICS_PER_SHERD = 3.0 # Modify this for the number of pictures you want to take in a full cycle. The motor will stop this amount of times during the cycle to take pictures. Remember to add ".0" to make sure calculation will be precise. 
DELAY = 0.002 # Unit: seconds. The time that the controller code waits before heading to the next step. Should be necessary to control the motor, but should be relatively short.
FULL_CYCLE_STEPS = 400 #??? Usually stepper motors use 200 steps for a full cycle, but this one seems to have its own idea and requires 400 steps.
AVG_STEPS_PER_SHOT = FULL_CYCLE_STEPS / NUM_OF_PICS_PER_SHERD
SLEEP_TIME_BETWEEN_SHOTS = 2 # Unit: seconds. Gives this amount of time for the table to rest and wait for oscillation to vanish before taking the next turn.
SHERD_ID = 10086 # Used when creating folders. Ideally should be read from a data file and modified in that file.

# Kill the gphoto process that starts
# whenever we turn on the camera or reboot the raspberry pi.
# Also kill the gvfsd thing or whatever it's called
def killGphoto2Process():
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()

    # Search for the process we want to kill
    for line in out.splitlines():
        if (b'gvfsd-gphoto2' in line) or (b'gvfs-gphoto2-volume-monitor' in line):
            # Kill that process!
            pid = int(line.split(None,1)[0])
            os.kill(pid, signal.SIGKILL)

##def createSaveFolder(save_location):
##    try:
##        os.makedirs(save_location)
##    except:
##        if (os.path.isdir(save_location) == False):
##            print("Failed to create new directory.")
##    #os.chdir(save_location)

##def captureImages(dir_and_name = ""):
##    if (len(dir_and_name) == 0):
##        os.system(sudo+"gphoto2 "+captureCommand)
##    else:
##        os.system(sudo+"gphoto2 "+captureCommand + ' --filename="'+dir_and_name+'"')

def one_sherd_photo_cycle():
    global SHERD_ID
    step_seq_index = 0
    angle_index = 0
    next_angle_steps = 0
    for i in range(FULL_CYCLE_STEPS):
        if i >= next_angle_steps:
            # Wait for the motor to finish moving
##            sleep(SLEEP_TIME_BETWEEN_SHOTS)
##            # Take picture
##            shot_date = datetime.now().strftime("%Y-%m-%d")
##            folder_name = shot_date + "_sherd" + str(SHERD_ID)
##            save_location = "/home/pi/Desktop/gphoto/images/" + folder_name
##            createSaveFolder(save_location)
##            shot_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
##            file_name = save_location+'/'+shot_time+"_angle"+str(angle_index)+suffix
            #captureImages(file_name)
            # Increment next angle step
            next_angle_steps += AVG_STEPS_PER_SHOT
            angle_index += 1
        # For each iteration, run one step of motor
        for pin in range(4): #assign output to pin
            GPIO.output(control_pins[pin], step_seq[step_seq_index][pin])
            sleep(DELAY)
        # Increment sequence index to get ready for next step
        if (step_seq_index == 3):
            step_seq_index = 0
        else:
            step_seq_index += 1
    SHERD_ID += 1

killGphoto2Process()
#gp(clearCommand)
one_sherd_photo_cycle()

GPIO.cleanup()
#>
