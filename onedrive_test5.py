import onedrivesdk
import os
from onedrivesdk.helpers import GetAuthCodeServer

#you MUST run authenticate() after you create an instance of this class
#otherwise, nothing will work
#this also assumes all your credentials are entered correctly
class OneDriveHandler:
    def __init__(self, redirect_uri, client_id, client_secret):
        self.redirect_uri = redirect_uri
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = ['wl.signin', 'wl.offline_access', 'onedrive.readwrite']
        self.client = onedrivesdk.get_consumer_client(
            self.client_id, scopes=self.scopes) # get_default_client() is deprecated
        self.common_path='root'
        self.common_folder='root'
        
    def authenticate(self):
        auth_url = self.client.auth_provider.get_auth_url(self.redirect_uri)
        #print(auth_url)
        #this will block until we have the code
        code = GetAuthCodeServer.get_auth_code(auth_url, self.redirect_uri)

        self.client.auth_provider.authenticate(code, self.redirect_uri, self.client_secret)
    
    #upload file to root if not given a parent id
    def upload_file(self, filename, parent='root'):
        cwd = os.getcwd()
        returned_item = self.client.item(drive='me', id=parent).children[filename].upload(cwd +'/'+ filename)
        return returned_item

    #from https://stackoverflow.com/questions/10377998/how-can-i-iterate-over-files-in-a-given-directory
    #upload to root level on a directory, or
    #to a folder given a parent id
    def upload_folder(self, folder_name, parent='root'):
        #directory = os.fsencode(folder_name)
        for file in os.listdir(folder_name):
            #filename = os.fsdecode(file)
            cwd = os.getcwd()
            item = self.client.item(drive='me', id=parent).children[file].upload(cwd + '/' + folder_name + '/' +file)
            continue

    #create to_folder if to_folder does not exist
    #kinda useless since upload_folder will upload to
    #a specified id and create folder returns a folder
    #created
    def upload_to_folder(self, from_folder, to_folder):
        folder = self.get_onedrive_folder(to_folder)
        if folder == 0:
            folder = self.create_folder(to_folder)
        for file in os.listdir(from_folder):
            #if file.endswith('.txt'):
            cwd = os.getcwd()
            item = self.client.item(drive='me', id=folder.id).children[file].upload(cwd + '/' + from_folder + '/' +file)
            continue
        
    #create a root level folder, or given the id of parent folder, create a folder in a folder
    def create_folder(self, new_name, parent='root'):
        f = onedrivesdk.Folder()
        i = onedrivesdk.Item()
        i.name = new_name
        i.folder = f
        fold = self.client.item(drive='me', id=parent).children.add(i)
        return fold

    #five identifiers on sherd - should be expecting five layers
    #N or S
    #four num fields(ints)
    #since this will be used to deposit items in the most nested folder,
    #return most nested folder
    #MAY NEED TO CHANGE TO BACKSLASH
    def create_nested_folder(self, full_identifier, parent='root'):
        folders = full_identifier.split('/')
        #locate first folder
        #creating from root
        if parent == 'root':
            above_level = self.get_onedrive_folder(folders[0])
            if above_level == 0:
                above_level = self.create_folder(folders[0])
        else:
            #creating from specified folder
            above_level = self.get_onedrive_folder(folders[0], parent)
        #we know top folder exists
        index = 1
        while index < len(folders):
            if folders[index] != '':
                #see if folder is in current level
                curr_level = self.get_onedrive_folder(folders[index], parent=above_level.id)
                if curr_level == 0:
                    curr_level = self.create_folder(folders[index], parent=above_level.id)
                above_level = curr_level
            index = index + 1
        return curr_level
    
    #iterate through and find the folder in the folder given
    #or just iterate through root
    def get_onedrive_folder(self, onedrive_folder, parent='root'):
        coll = self.client.item(drive='me',id=parent).children.request().get()
        for item in coll:
            if item.name == onedrive_folder:
                return item
        return 0

    #show ALL contents of the onedrive 
    def dump_onedrive(self):
        coll = self.client.item(drive='me',id='root').children.request().get()
        for item in coll:
            print(item.name)
        return coll
    
    #e.g. hku/research/armenia/vayotsdzor/files/finds/N
    #MAY NEED TO CHANGE TO BACKSLASH
    #assumes that the folders along path exist
    def set_common_directory(self, path):
        onedrive_path = path.split('/')
        above_level = self.get_onedrive_folder(onedrive_path[0])
        index = 1
        while index < len(onedrive_path):
            if onedrive_path[index] != '':
                curr_level = self.get_onedrive_folder(onedrive_path[index], above_level.id)
                above_level = curr_level
            index = index + 1
        self.common_path = path
        self.common_folder = curr_level