import io
import time
from pathlib import Path

import googleapiclient.discovery
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

SCOPES = [
    "https://www.googleapis.com/auth/drive",
]


class DriveService:
    def __init__(self, service_account_file=None, service_account_info=None):
        if service_account_file:
            creds = Credentials.from_service_account_file(service_account_file, scope=SCOPES)
        elif service_account_info:
            creds = Credentials.from_service_account_info(service_account_info, scopes=SCOPES)
        else:
            raise ValueError("Please specify service_account_file or service_account_info")
        self.drive_service = googleapiclient.discovery.build("drive", "v3", credentials=creds, cache_discovery=False)

    def create_folder(self, name: str, folder_id: str) -> str:
        file_metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [folder_id],
        }
        folder = self.drive_service.files().create(body=file_metadata, supportsAllDrives=True).execute()

        return folder.get("id")

    def get_folders(self, parent_folder_id: str, share_drive_id: str) -> list:
        try:
            list_ = []
            query = "'%s' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed=false" % parent_folder_id
            results = (
                self.drive_service.files()
                .list(
                    q=query,
                    driveId=share_drive_id,
                    corpora="drive",
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                    pageSize=1000,
                    fields="nextPageToken, files(name,id)",
                )
                .execute()
            )
            items = results.get("files", [])
            for item in items:
                item_name = item["name"]
                list_.append({"name": item_name, "id": item["id"]})
        except Exception as e:
            raise e
        return list_

    def get_child_items(self, parent_folder_id: str, share_drive_id: str) -> list:
        try:
            list_ = []
            query = f'"{parent_folder_id}" in parents and trashed=false'
            results = (
                self.drive_service.files()
                .list(
                    q=query,
                    driveId=share_drive_id,
                    corpora="drive",
                    includeItemsFromAllDrives=True,
                    supportsAllDrives=True,
                    pageSize=1000,
                    fields="nextPageToken, files(name,id)",
                )
                .execute()
            )
            items = results.get("files", [])
            for item in items:
                list_.append({"name": item["name"], "id": item["id"]})
        except Exception as e:
            raise e
        return list_

    def download_file(self, path: str, _id: str):
        try:
            request = self.drive_service.files().get_media(fileId=_id)
            fh = io.FileIO(path, mode="wb")
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                _, done = downloader.next_chunk()
        except Exception as e:
            raise e

    def upload_file(self, file_path: str, folder_id) -> str:
        try:
            extension = Path(file_path).suffix.lower()
            if extension == ".jpg" or extension == ".jpeg" or extension == ".png":
                mime_type = "image/jpeg"
            elif extension == ".heic":
                mime_type = "image/heif"
            elif extension == ".pdf":
                mime_type = "application/pdf"
            elif extension == "xml" or extension == "xsl":
                mime_type = "application/xml"
            elif extension == "txt":
                mime_type = "text/plain"
            else:
                raise Exception

            file_metadata = {
                "name": Path(file_path).name,
                "mimeType": mime_type,
                "parents": [folder_id],
            }
            media = MediaFileUpload(file_path, mimetype=mime_type)
            file = (
                self.drive_service.files()
                .create(
                    body=file_metadata,
                    media_body=media,
                    fields="id",
                    supportsAllDrives=True,
                )
                .execute()
            )
            file_id = file.get("id")
        except Exception as e:
            raise e
        return file_id

    def delete_file(self, file_id: str):
        try:
            self.drive_service.files().delete(fileId=file_id, supportsAllDrives=True).execute()
        except Exception as e:
            raise e

    def rename_file(self, file_id: str, rename: str):
        try:
            file = {"name": rename}
            self.drive_service.files().update(fileId=file_id, body=file, supportsAllDrives=True).execute()
            for _ in range(10):
                res = self.drive_service.files().get(fileId=file_id, fields="name", supportsAllDrives=True).execute()
                if res["name"] == rename:
                    return
                time.sleep(0.1)

            raise ValueError(f"Failed to rename file {file_id}")

        except Exception as e:
            raise e

    def move_file(self, file_id: str, src_folder_id: str, dst_folder_id: str):
        self.drive_service.files().update(
            fileId=file_id,
            addParents=dst_folder_id,
            removeParents=src_folder_id,
            supportsAllDrives=True,
        ).execute()
