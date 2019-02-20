from onedrive_test5 import OneDriveHandler
import json

HOME_PI = "/home/pi/"
cred_file = open(HOME_PI+'Scripts/vars/auth.json', 'r+')
cred= json.load(cred_file)

redirect_uri = cred['redirect_uri']
client_id = cred['client_id']
client_secret = cred['client_secret']

scopes=['wl.signin', 'wl.offline_access', 'onedrive.readwrite']

odh = OneDriveHandler(redirect_uri, client_id, client_secret)
odh.authenticate()
folder = odh.create_nested_folder('nested_upload_test/trying/once/more')