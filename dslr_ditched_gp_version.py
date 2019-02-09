from time import sleep
from datetime import datetime
from sh import gphoto2 as gp
import signal, os, subprocess

# Kill the gphoto process that starts
# whenever we turn on the camera or
# reboot the raspberry pi

def killGphoto2Process():
    p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
    out, err = p.communicate()

    # Search for the process we want to kill
    for line in out.splitlines():
        if b'gvfsd-gphoto2' in line:
            # Kill that process!
            pid = int(line.split(None,1)[0])
            os.kill(pid, signal.SIGKILL)

# shot_date = datetime.now().strftime("%Y-%m-%d") # This has been written to the while True loop.
# shot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # This has been written to the while True loop.
picID = "PiShots"
suffix = ''
clearCommand = ["--folder", "/store_00020001/DCIM/100CANON", \
                "--delete-all-files", "-R"]
triggerCommand = ["--trigger-capture"]
captureCommand = ["--capture-image-and-download"]
downloadCommand = ["--get-all-files"]

def createSaveFolder():
    try:
        os.makedirs(save_location)
    except:
        print("Failed to create new directory.")
    os.chdir(save_location)

def captureImages(dir_and_name = ""):
    #gp(triggerCommand)
    if (len(dir_and_name) == 0):
        #gp(captureCommand)
        os.system("gphoto2 "+captureCommand)
    else:
        os.system("sudo gphoto2 "+captureCommand[0] + ' --filename="'+dir_and_name+'"')
    sleep(1)
    #gp(downloadCommand)
    #gp(clearCommand)

def renameFiles(ID):
    for filename in os.listdir("."):
        if len(filename) < 13:
            if filename.endswith(".JPG"):
                os.rename(filename, (shot_time + ID + ".JPG"))
                print("Renamed the JPG")
            elif filename.endswith(".CR2"):
                os.rename(filename, (shot_time + ID + ".CR2"))
                print("Renamed the CR2")


killGphoto2Process()
gp(clearCommand)

for i in range(1):
	shot_date = datetime.now().strftime("%Y-%m-%d")
	shot_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	folder_name = shot_date + picID
	save_location = "/home/pi/Desktop/gphoto/images/" + folder_name
	createSaveFolder()
	captureImages(save_location+'/'+shot_time+suffix)
	#renameFiles(picID)
	#print("saved file in: "+save_location)

#>