# Python file that only executes the capture command via os.system()
# Created on 2/3 for testing purposes
# Modified on 2/4 to test capture-and-then-batch-download method
import sys, os # , datetime, subprocess

def capture(argv):
    # Expected input: [<port>(, <debug logfile name>)]
    # (because we can't specify filename if we store it in the camera)
    #print("Capture is called with arguments ", argv)
    if len(argv) < 1:
        os.system('gphoto2 --capture-image')
    elif len(argv) == 1:
        # Not debug mode
        os.system('gphoto2 --capture-image' +\
                  ' --port ' + "usb:" + argv[0])
    else:
        # Debug mode
        os.system('sudo gphoto2 --capture-image' +\
                  ' --port ' + "usb:" + argv[0] +\
                  ' --debug --debug-logfile=' + argv[1])
    #print('One image is captured') # won't be seen by the subprocess anyway...

def capture_and_download(argv):
    # Expected input: [<port>, <filename> (, <debug logfile name>)]
    if len(argv) < 2:
        os.system('sudo gphoto2 --capture-image-and-download')
        print('File saved')
        return
    elif len(argv) == 2:
        # Not debug mode
        os.system('sudo gphoto2 --capture-image-and-download' +\
                  ' --port ' + "usb:" + argv[0] +\
                  ' --filename ' + argv[1])
    else:
        # Debug mode
        os.system('sudo gphoto2 --capture-image-and-download' +\
                  ' --port ' + "usb:" + argv[0] +\
                  ' --debug --debug-logfile=' + argv[2] +\
                  ' --filename ' + argv[1])
    print('File "'+argv[1]+'" is saved') # subprocess won't print this in terminal anyway...

if __name__ == "__main__":
    capture(sys.argv[1:])
else:
    print("===WARNING: Capture command not run as main program===")
    capture(sys.argv[1:])