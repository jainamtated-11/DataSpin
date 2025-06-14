# scripts/upload_to_drive.py
import os, pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def upload_to_drive(file_path, drive_filename):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)

    # Check if file exists in Drive
    result = service.files().list(q=f"name='{drive_filename}'", spaces='drive').execute()
    items = result.get('files', [])

    media = MediaFileUpload(file_path, resumable=True)
    if items:
        file_id = items[0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
        print(f"[↑] Updated existing file on Drive: {drive_filename}")
    else:
        service.files().create(body={'name': drive_filename}, media_body=media, fields='id').execute()
        print(f"[↑] Uploaded new file to Drive: {drive_filename}")
