# Python file that takes on the task of deleting photos, so the printouts in that process won't show up in Terminal.
# 2/10
import os, sys

CAMERA_PIC_PATH = "/store_00020001/DCIM/100CANON"
clearCommand = "gphoto2 --folder " + CAMERA_PIC_PATH + " -D -R"

def delete_all(argv):
    # Expected input: [<camera port in the style of "0xx,0yy">]
    if len(argv) < 1:
        os.system('gphoto2 -D -R')
    else:
        os.system(clearCommand + " --port usb:"+argv[0])

delete_all(sys.argv[1:])