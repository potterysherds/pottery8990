import onedrivesdk
import os
from onedrivesdk.helpers import GetAuthCodeServer

def authenticate():
    redirect_uri = 'http://localhost:8080/' #'https://login.live.com/oauth20_desktop.srf' # or should it be the provided 'http://localhost:8080/'?
    client_id = '2b97db18-39d9-4242-8c79-5eeb7160dac3' # or is this 'thayerpotterysherd8990@outlook.com'?
    client_secret = 'wJD4[!bemlixWVSUE8686::' #or is this the application ID?
    # Application ID: 2b97db18-39d9-4242-8c79-5eeb7160dac3
    scopes=['wl.signin', 'wl.offline_access', 'onedrive.readwrite']

    client = onedrivesdk.get_consumer_client(
        client_id, scopes=scopes) # get_default_client() is deprecated

    auth_url = client.auth_provider.get_auth_url(redirect_uri)
    #print(auth_url)
    #this will block until we have the code
    code = GetAuthCodeServer.get_auth_code(auth_url, redirect_uri)

    client.auth_provider.authenticate(code, redirect_uri, client_secret)
    return client

def upload_file(filename, client, parent='root'):
    cwd = os.getcwd()
    returned_item = client.item(drive='me', id=parent).children[filename].upload(cwd +'/'+ filename)
    return returned_item

#from https://stackoverflow.com/questions/10377998/how-can-i-iterate-over-files-in-a-given-directory
def upload_folder(folder_name, client):
    #directory = os.fsencode(folder_name)
    for file in os.listdir(folder_name):
        #filename = os.fsdecode(file)
        if file.endswith('.txt'):
        #if filename.endswith('.txt'):
            cwd = os.getcwd()
            item = client.item(drive='me', id='root').children[file].upload(cwd + '/' + folder_name + '/' +file)
        continue

#create to_folder if to_folder doen
def upload_to_folder(from_folder, to_folder, client):
    folder = get_onedrive_folder(to_folder, client)
    if folder == 0:
        folder = create_folder(to_folder, client)
    for file in os.listdir(from_folder):
        if file.endswith('.txt'):
            cwd = os.getcwd()
            item = client.item(drive='me', id=folder.id).children[file].upload(cwd + '/' + from_folder + '/' +file)
        continue

#create a root level folder, or given the id of parent folder, create a folder in a folder
def create_folder(new_name, client, parent='root'):
    f = onedrivesdk.Folder()
    i = onedrivesdk.Item()
    i.name = new_name
    i.folder = f
    fold = client.item(drive='me', id=parent).children.add(i)
    return fold

#five identifiers on sherd - should be expecting five layers
#N or S
#four num fields(ints)
def create_nested_folder(full_identifier, client):
    folders = full_identifier.split('/')
    #locate first folder
    above_level = get_onedrive_folder(folders[0], client)
    if above_level == 0:
        above_level = create_folder(folders[0], client)
    #we know top folder exists
    index = 1
    while index < len(folders):
        if folders[index] != '':
            #see if folder is in current level
            curr_level = get_onedrive_folder(folders[index], client, parent=above_level.id)
            if curr_level == 0:
                curr_level = create_folder(folders[index], client, parent=above_level.id)
            above_level = curr_level
            index = index + 1
            
def get_onedrive_folder(onedrive_folder, client, parent='root'):
    coll = client.item(drive='me',id=parent).children.request().get()
    index = 0
    for item in coll:
        if coll[index].name == onedrive_folder:
            return coll[index]
        index = index + 1
    return 0

#show ALL contents of the onedrive 
def dump_onedrive(client):
    coll = client.item(drive='me',id='root').children.request().get()
    index = 0
    for item in coll:
        print(coll[index].name)
        index = index + 1
    return coll
    
c = authenticate()
#upload_file('onedrive_test_folder/yeetus1.txt', c)
#upload_folder('onedrive_test_folder', c)
#g = get_onedrive_folder('swamp_thing', c)
#g2 = get_onedrive_folder('porkchop express', c, parent=g.id)
#g3 = get_onedrive_folder('valkyrie', c, parent=g2.id)
#returned_item = upload_file('yeetus.txt', c, parent=g3.id)