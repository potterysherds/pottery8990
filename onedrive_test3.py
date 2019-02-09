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

def upload_file(filename, client):
    cwd = os.getcwd()
    returned_item = client.item(drive='me', id='root').children[filename].upload(cwd+ filename)

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

def create_folder(new_name, client):
    f = onedrivesdk.Folder()
    i = onedrivesdk.Item()
    i.name = new_name
    i.folder = f
    fold = client.item(drive='me', id='root').children.add(i)
    return fold

def get_onedrive_folder(onedrive_folder, client):
    coll = client.item(drive='me',id='root').children.request().get()
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
upload_to_folder('tif photos','tif upload test 2 Feb 2019',c)
