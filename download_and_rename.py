# Created 2/4
# Batch downloads photos from camera, and batch renames them.
import glob, os, subprocess, sys, time
from datetime import datetime

def download_and_rename(argv):
    # Expected input: [<port>, <path to destination folder>, <camera number in str type>]
    if len(argv) < 3:
        print("Not enough arguments to download and rename.")
        quit()
    shot_time = datetime.now().strftime("%Y-%m-%d_%H%M%S") # Eventhough it's actually rename_time
    
    # cd to destination folder
    original_pwd = os.getcwd()
    storage_pwd = argv[1]
    os.chdir(storage_pwd)
    
    # Download pictures (which might take a while, which requires subprocess so we can wait)
    CANONICAL_CANON_FOLDER = '/store_00020001/DCIM/100CANON'
    '''
    proc = subprocess.Popen(['sudo', 'gphoto2', '--port', 'usb:'+argv[0], '-P', '--new'], stdout=subprocess.PIPE)
    out, err = proc.communicate() # also waits for it to finish
    print("Download_and_rename wants to say this:")
    print(out)
    print(err)'''
    os.system('sudo gphoto2 --port usb:'+argv[0]+' -P --new') # Why use a subprocess when you can use os.system???
    time.sleep(2)
    # add error handling code here if you know any
    
    # Analyze file names
    # Here we assume that only one of the two cases below would happen:
    # 1. File number crosses from 9xxx to 0yyy without any 8zzz appearing
    # 2. File number order corresponds to picture order
    # (but it actually doesn't matter, does it?)
    # I'm just trying to make sure the angle order is correct.
    filenames = glob.glob('IMG_*')
    filenames_9 = glob.glob('IMG_9*')
    filenames_0 = glob.glob('IMG_0*')
    #print(filenames, filenames_9, filenames_0)
    filenames_9.sort()
    filenames_0.sort()
    if (len(filenames_9) > 0 and len(filenames_0) > 0):
        filenames = filenames_9 + filenames_0
    else:
        filenames.sort()
    #print(filenames)
    # Start renaming. Assume that the sorted filenames reflects exactly the angle order
    angle_index = 0
    filename_base = shot_time+'_Camera'+argv[2]+'_angle'
    for filename in filenames:
        os.rename(filename, filename_base+('%02d'%angle_index))
        angle_index += 1
    
    # After renaming, if successful, switch back to original directory and clear file from camera
    os.chdir(original_pwd)
    proc = subprocess.Popen(['sudo', 'gphoto2', '--port', 'usb:'+argv[0], '-D', '-R'], stdout=subprocess.PIPE)
    out, err = proc.communicate()
    print('Moved photos to '+argv[1])

if __name__ == '__main__':
    download_and_rename(sys.argv[1:])