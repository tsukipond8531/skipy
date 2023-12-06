from __future__ import annotations

import io
import time
from pathlib import Path

import googleapiclient.discovery
import magic
from google.oauth2.service_account import Credentials
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

SCOPES = [
    "https://www.googleapis.com/auth/drive",
]


class DriveService:
    # NOTE:
    # https://googleapis.github.io/google-api-python-client/docs/dyn/drive_v3.files.html
    def __init__(self, service_account_file=None, service_account_info=None):
        if service_account_file:
            creds = Credentials.from_service_account_file(
                service_account_file, scopes=SCOPES
            )
        elif service_account_info:
            creds = Credentials.from_service_account_info(
                service_account_info, scopes=SCOPES
            )
        else:
            raise ValueError(
                "Either service_account_file or service_account_info must be provided."
            )
        self.client = googleapiclient.discovery.build(
            "drive", "v3", credentials=creds, cache_discovery=False
        )

    def create_folder(self, name: str, folder_id: str) -> str:
        file_metadata = {
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [folder_id],
        }
        folder = (
            self.client.files()
            .create(body=file_metadata, supportsAllDrives=True)
            .execute()
        )

        return folder.get("id")

    def get_folders(self, parent_folder_id: str, share_drive_id: str) -> list:
        try:
            list_ = []
            query = (
                "'%s' in parents and mimeType = 'application/vnd.google-apps.folder' \
                and trashed=false"
                % parent_folder_id
            )
            results = (
                self.client.files()
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

    async def get_child_items(self, parent_folder_id: str, share_drive_id: str) -> list:
        try:
            list_ = []
            query = f'"{parent_folder_id}" in parents and trashed=false'
            results = (
                self.client.files()
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

    def download_file(self, path: str, file_id: str):
        try:
            request = self.client.files().get_media(fileId=file_id)
            fh = io.FileIO(path, mode="wb")
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                _, done = downloader.next_chunk()
        except Exception as e:
            raise e

    def upload_file(self, file_path: str, folder_id) -> str:
        try:
            mime_type = magic.from_file(file_path, mime=True)
            file_metadata = {
                "name": Path(file_path).name,
                "mimeType": mime_type,
                "parents": [folder_id],
            }
            media = MediaFileUpload(file_path, mimetype=mime_type)
            file = (
                self.client.files()
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
            self.client.files().delete(fileId=file_id, supportsAllDrives=True).execute()
        except Exception as e:
            raise e

    def rename_file(self, file_id: str, rename: str):
        try:
            file = {"name": rename}
            r = (
                self.client.files()
                .update(fileId=file_id, body=file, supportsAllDrives=True)
                .execute()
            )
            # WARNING:
            # update func is async,
            # It takes time to change the file name.
            for _ in range(10):
                check = (
                    self.client.files()
                    .get(fileId=file_id, fields="name", supportsAllDrives=True)
                    .execute()
                )
                if check["name"] == rename:
                    return r
                time.sleep(0.5)
            raise TimeoutError(f"Failed to rename file {file_id}")
        except Exception as e:
            raise e

    def move_file(self, file_id: str, src_folder_id: str, dst_folder_id: str):
        return (
            self.client.files()
            .update(
                fileId=file_id,
                addParents=dst_folder_id,
                removeParents=src_folder_id,
                supportsAllDrives=True,
            )
            .execute()
        )
