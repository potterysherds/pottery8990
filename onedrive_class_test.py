from onedrive_test5 import OneDriveHandler

redirect_uri = 'http://localhost:8080/' #'https://login.live.com/oauth20_desktop.srf' # or should it be the provided 'http://localhost:8080/'?
client_id = '2b97db18-39d9-4242-8c79-5eeb7160dac3' # or is this 'thayerpotterysherd8990@outlook.com'?
client_secret = 'wJD4[!bemlixWVSUE8686::' #or is this the application ID?
# Application ID: 2b97db18-39d9-4242-8c79-5eeb7160dac3
scopes=['wl.signin', 'wl.offline_access', 'onedrive.readwrite']

odh = OneDriveHandler(redirect_uri, client_id, client_secret)
odh.authenticate()
folder = odh.create_nested_folder('nested_upload_test/three/two/one/DROP')
odh.upload_folder('onedrive_test_folder', folder.id)
