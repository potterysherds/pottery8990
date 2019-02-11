from time import sleep
from datetime import datetime
#from sh import gphoto2 as gp
import signal, os, subprocess
import RPi.GPIO as GPIO
import json
import sys
# from os_capture import capture # Importing this script causes one camera to take a shot. I guess Python is built to be like that. 
from download_and_rename import download_and_rename

# two_camera_batch..., but cleaner. 2/9
# Camera control code credit: The Zan Show
# Motor control code credit: https://medium.com/@Keithweaver_/controlling-stepper-motors-using-python-with-a-raspberry-pi-b3fbd482f886

# Set up motor pins and step cycle at the start of the script
GPIO.setmode(GPIO.BCM)
In1 = 12 # Define pins for motor controll output
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
CAMERA_PIC_PATH = "/store_00020001/DCIM/100CANON"
DELETE_FLAG = "-D" # equivalent to "--delete-all-files"
RECURSE_FLAG = "-R"
DOWNLOAD_ALL_FLAG = "-P" # equivalent to "--get-all-files"
clearCommand = ["gphoto2", "--folder", CAMERA_PIC_PATH, \
                DELETE_FLAG, RECURSE_FLAG]
captureAndDownloadCommand = ["--capture-image-and-download"]
downloadCommand = [DOWNLOAD_ALL_FLAG]
autoDetectCommand = ['gphoto2', '--auto-detect']

# Define some directory paths
HOME_PI = "/home/pi/"
CAPTURE_METHOD_FILE= HOME_PI+'Scripts/os_capture.py'
DELETE_METHOD_FILE = HOME_PI+'Scripts/os_delete.py'
DOWNLOAD_AND_RENAME_METHOD_FILE = HOME_PI+'Scripts/download_and_rename.py'
IMAGE_STORAGE_BASE_ADDR = HOME_PI+"Desktop/gphoto/images/"

# These are used to filter printouts from --auto-detect to find the port numbers
CAMERA_MODEL = "Canon EOS 1300D"
CAMERA_MODEL_NO_SPACE = "Canon\ EOS\ 1300D"

# More constants for motor control
NUM_OF_PICS_PER_SHERD = 20.0 # The number of pictures you want to take in a full cycle. 
DELAY = 0.002 # Unit: seconds. The time that the controller code waits before doing the next step.
FULL_STEPPER_CYCLE_STEPS = 200 # Stepper motors use 200 steps for a full cycle.
GEAR_RATIO = 4 # Multiply this number to FULL_STEPPER_CYCLE_STEPS to get the real number of steps our small motor needs to turn in order to make the big table spin one full cycle. See line below.
FULL_CYCLE_STEPS = FULL_STEPPER_CYCLE_STEPS * GEAR_RATIO
AVG_STEPS_PER_SHOT = FULL_CYCLE_STEPS / NUM_OF_PICS_PER_SHERD
SLEEP_TIME_BETWEEN_SHOTS = 0.2 # Unit: seconds. Planned to wait this long for oscillation to vanish before taking the next turn, but it seems the delay that cameras need to capture rendered this useless.

# Read in some file that records previous state
STATE_FILE = open(HOME_PI+'Scripts/vars/parameters.json', 'r+')
STATE_VAR = json.load(STATE_FILE)
SHERD_ID = STATE_VAR["sherd ID"]

# Parameters for debug mode / logging
openproc = False
DEBUG_MODE = False # If True, write debug logfiles
KEEP_OLD_LOG_FILE = False # Change this to True once we know how to chmod newly created files
if DEBUG_MODE:
    from gphoto_log_trim_tool import trim_file

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

# Reset the capture target to card, so we can keep the file
def resetCaptureTarget():
    # Use subprocess because we don't want its garbage output
    p = subprocess.Popen(['gphoto2','--set-config','capturetarget=1'], stdout=subprocess.PIPE)
    p.wait()
    #out,err = p.communicate()
    #os.system('gphoto2 --set-config capturetarget=1')

# Find the right ports of the cameras
def findCameraPorts():
    p = subprocess.Popen(autoDetectCommand, stdout=subprocess.PIPE)
    out, err = p.communicate()
    ports = []
    
    # Search for the outputs
    for line in out.splitlines():
        if CAMERA_MODEL in line:
            ports.append(line.split("usb:")[-1].rstrip())
    
    if len(ports) == 0:
        print("No camera port found!!!")
        sys.exit(0)
    return ports

# Clear all files from camera. ###Might be a source of excessive printout
def clearCameraFiles():
    for i in range(num_of_ports):
        # We used to run this directly from here, but now we call subprocesses to deter excessive printouts
        #p = subprocess.Popen(clearCommand + ["--port", 'usb:'+ports[i]])
        p = subprocess.Popen(['python', DELETE_METHOD_FILE, ports[i]], stdout=subprocess.PIPE)
        out, err = p.communicate() # If we want true parallel, we put this in a second loop, and make p belong to a list of processes. But deletion should be fast, so no...

# Create a new folder to save files to
def createSaveFolder(save_location):
    try:
        os.makedirs(save_location)
    except:
        if (os.path.isdir(save_location) == False):
            print("Failed to create new directory: "+save_location)

# Captures images on camera (without downloading) by running the script os_capture.py
def captureImages(dir = '', name = ''):
    # Create a list of subprocesses
    procs = range(num_of_ports)
    resetCaptureTarget() # Moved this here
    if ((DEBUG_MODE == False) or (len(dir) == 0 or len(name) == 0)):
        # If not in debug mode, or if arguments not enough for debug mode, we only capture the image 
        for i in range(num_of_ports):
            # Each subprocess calls the capture python script with port as argument to specify which camera to use
            procs[i] = subprocess.Popen(['python', CAPTURE_METHOD_FILE, ports[i]], stdout=subprocess.PIPE)
    else:
        # In legitimate debug mode, pass in the path for the debug file as well. 
        for i in range(num_of_ports):
            procs[i] = subprocess.Popen(['python', CAPTURE_METHOD_FILE, ports[i], \
                                         dir+'/camera'+str(i)+'/'+name+str(i+1)+'.txt'], \
                                         stdout=subprocess.PIPE)
        '''if DEBUG_MODE:
        for i in range(len(ports)):
            print("Waiting for camera %d to finish" % i)
            procs[i].wait()
            print("Trimming logfile for camera %d", i)
            trim_file(dir_and_name+str(i+1)+".txt", KEEP_OLD_LOG_FILE)'''
    # Wait for capturing to finish
    for i in range(num_of_ports):
        #procs[i].wait()
        out,err = procs[i].communicate()
        print("Camera #%d: "%i + out)
        print("Camera #%d is supposed to finish, but if it's actually not, whatcha gonna do with it?" % i)
    #print("Capture method for the image called '"+name+"' is finished.")

# Gets images from each camera, and then rename them
def download_and_rename_files(dir_name_base = ''):
    d_procs = range(num_of_ports)
    for j in range(num_of_ports):
        d_procs[j] = subprocess.Popen(['python', DOWNLOAD_AND_RENAME_METHOD_FILE, \
                                       ports[j], dir_name_base+str(j), str(j)], \
                                       stdout=subprocess.PIPE)
    # ***find a way to wait for them but still remain parallel here
    # or we should just halt the loop and wait for user input to continue.
    for j in range(num_of_ports):
        d_procs[j].wait()
        #out,err = d_procs[j].communicate() # ??? the right way ???
        #print(out)
    print("Sherd %d finished" % SHERD_ID)

# The full cycle for one sherd, including motor control, camera control, and file processing
# (No need to auto-focus because we want to fix the parameters, since the sherd position is fixed)
def one_sherd_photo_cycle():
    # Update the current sherd ID and save that value to the json file storing all the parameters
    global SHERD_ID
    SHERD_ID += 1
    STATE_VAR["sherd ID"] = SHERD_ID
    STATE_FILE.seek(0)
    STATE_FILE.truncate()
    json.dump(STATE_VAR,STATE_FILE,indent=4,sort_keys=True)

    # Create a main folder for this sherd, and subfolders for all the cameras.
    # The naming convention would change once we figure out how our client wants it to be.
    # main folder
    shot_date = datetime.now().strftime("%Y-%m-%d")
    folder_name = shot_date + "_sherd" + str(SHERD_ID)
    save_location = IMAGE_STORAGE_BASE_ADDR + folder_name
    createSaveFolder(save_location)
    # subfolders
    save_location_subfolder_name_base = save_location+'/camera'
    for j in range(num_of_ports):
        createSaveFolder(save_location_subfolder_name_base+str(j))
    
    step_seq_index = 0 # for keeping track of the signal sent to motor
    angle_index = 0 # for naming the picture with the correct order (but not useful if not using --capture-image-and-download)
    next_angle_steps = 0 # for keeping track of how many steps are needed to reach the next capture time

    # Each iteration of this loop runs a step of the stepper motor.
    for i in range(FULL_CYCLE_STEPS):
        # If we have taken enough steps since the previous capture, then stop and take a picture.
        if (i >= next_angle_steps):
            # Wait a little while for vibration stabilization
            sleep(SLEEP_TIME_BETWEEN_SHOTS)
            
            # Take pictures from all cameras
            shot_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S") # keep in mind that this naming scheme could change
            file_name = shot_time+"_angle"+str(angle_index)+"_camera"
            #resetCaptureTarget() # Just to make sure it doesn't randomly switch to RAM again # Actually I'm moving this to the capture method directly
            captureImages(save_location, file_name)
            #print("Image on sherd #%d finished -- from the main loop" % angle_index)

            # Increment next angle step
            next_angle_steps += AVG_STEPS_PER_SHOT
            angle_index += 1
        
        # For each iteration, run one step of motor
        for pin in range(4): #assign output to pin
            GPIO.output(control_pins[pin], step_seq[step_seq_index][pin])
            sleep(DELAY) # Wait a little while before taking the next step

        # Increment sequence index to give the correct signal for next step
        if (step_seq_index == 3):
            step_seq_index = 0
        else:
            step_seq_index += 1

    # After a full cycle, start downloading files
    print("Downloading...")
    download_and_rename_files(save_location_subfolder_name_base)

killGphoto2Process()
#resetCaptureTarget() # But it seems like the code randomly switches to RAM in the middle, so I moved it into the main loop
ports = findCameraPorts()
num_of_ports = len(ports)
print("Removing all previous files from cameras...")
clearCameraFiles()
while True:
    one_sherd_photo_cycle()
    cont = raw_input("You want to halt before photos are removed? (y/n)")
    if cont == 'n':
        sleep(0.1)
    else:
        break
    print("Removing all recent pictures from camera...")
    clearCameraFiles()
    cont = raw_input("Continue? (y/n)")
    if cont == 'y':
        sleep(0.1)
    else:
        break
    

GPIO.cleanup()
#>