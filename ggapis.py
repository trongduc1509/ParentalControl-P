from __future__ import print_function

import os.path
from typing import Any, Final
from io import BytesIO

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']

# The ID of a sample document.
OS_FOLDER: Final = '1l3KSP-TeqopJF8fLMk-dckR59sSeDqTw'
APP_DATA_ID: Final = '1A53_C7k4NFkHQG6DgYKm-ap2Qwx4V1sm'
ACCOUNT_DATA_ID: Final = '1XCk7aCsvyvJiHx3z64n-u9wmT5eHpKca'
TIME_CONFIG_ID: Final = '1QY4ZG9-1KhEC0YYFeJf6VPt097ihhyu7'
SCREENSHOTS_FOLDER_ID: Final = '124QdmAC49sPVlJVklxZqomoL47upQWiD'


def start_ggapi(service_func, args=()) -> Any:
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)

        # Retrieve the documents contents from the Docs service.
        #document = service.files().list(q="'1l3KSP-TeqopJF8fLMk-dckR59sSeDqTw' in parents").execute()

        return service_func(service, *args)

    except HttpError as err:
        print(f'An error occurred: {err}')

def list_folders_inside_screenshotfolder(service) -> list[tuple]:
    query = f"parents='{SCREENSHOTS_FOLDER_ID}' and mimeType='application/vnd.google-apps.folder'"
    document = service.files().list(q=query).execute()['files']
    return [(f['id'],f['name']) for f in document]

def create_folder_screenshots_by_date(service, filename):
    file_metadata = {
        'name': filename,
        'parents': [SCREENSHOTS_FOLDER_ID],
        'mimeType': 'application/vnd.google-apps.folder'
    }
    return service.files().create(body=file_metadata, fields='id').execute()

def create_cloud_subfolder(filename):
    return start_ggapi(create_folder_screenshots_by_date, (filename,))

def read_data_file(fileid):
    return start_ggapi(lambda service: service.files().get_media(fileId=fileid).execute().decode())

def upload_screenshots(service, foldername, filename, localFilePath):
    #check if today screenshots folder 
    folders = start_ggapi(list_folders_inside_screenshotfolder)
    targetFolderId = next((item for item in folders if item[1] == foldername), (None, foldername))[0]#id in tuple result (id,name)

    #if not exist then create
    if targetFolderId == None:
        targetFolderId = create_cloud_subfolder(foldername)['id']
    
    screenshot_metadata = {
        'name': filename,
        'parents': [targetFolderId]
    }
    media = MediaFileUpload(localFilePath, mimetype='image/png')
    return service.files().create(body=screenshot_metadata, media_body=media, fields='id').execute()

def update_txt_file(service, file_id, content):
    _mimeType = 'text/plain'
    _textStream = BytesIO(bytes(content,'ascii')) 
    _media = MediaIoBaseUpload(_textStream, mimetype=_mimeType,
        chunksize=1024*1024, resumable=True)
    return service.files().update(fileId=file_id,
        media_body=_media).execute()

def overwrite_cloud_file(file_id,content):
    return start_ggapi(update_txt_file, (file_id, content))

def upload_cloud_imagefile(foldername, filename, path):
    return start_ggapi(upload_screenshots,(foldername,filename,path))

if __name__ == '__main__':
    start_ggapi(update_txt_file, (APP_DATA_ID, ''))