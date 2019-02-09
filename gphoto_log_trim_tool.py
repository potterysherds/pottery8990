# Short python file to strip away (probably) unwanted information from the log file
# ZZ

# Store all the commands that we don't care here
unwanted_name_list = ['gp_port_library_list', 'foreach_func', 'print_debug_deviceinfo', 'ptp', 'camera_prepare_canon_eos_capture(2):', 'camera_canon_eos_capture']

def trim_file(filename, clearOld = True):
    f1 = open(filename, 'r')
    f2name = filename.strip('.txt')
    f2name = f2name+'_trimmed.txt'
    f2 = open(f2name, 'w')
    
    # Start checking every line
    for line in f1:
        words = line.split(' ')
        # The first "word" should be a timestamp like "12.345678"
        if len(words[0]) < 8:
                continue
        if words[1] in unwanted_name_list:
                continue
        f2.write(line)
        
    f1.close()
    f2.close()
    print("Trimmed log file can be found at: "+f2name)
    
    if clearOld:
        f1 = open(filename, 'w+')
        f1.close()

