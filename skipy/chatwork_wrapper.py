import json
import re
from pathlib import Path

import requests


class Chatwork:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_contacts(self):
        url = "https://api.chatwork.com/v2/contacts"
        headers = {"accept": "application/json", "x-chatworktoken": self.api_key}
        res = requests.get(url, headers=headers)
        contacts = json.loads(res.text)

        return contacts

    def get_cw_id(self, name: str):
        # Remove space
        name = re.sub("[ 　]", "", name)
        contacts = self.get_contacts()
        for contact in contacts:
            if re.sub("[ 　]", "", contact["name"]) == name:
                return contact["account_id"]
        return None

    def post_message(self, room_id: str, message: str, name: str = ""):
        """
        Post message to Chatwork

        Args:
            room_id(str): Room id which message is sent
            message(str): Posted message
            name(str): Mentioned member
        """
        cw_id = self.get_cw_id(name)

        url = f"https://api.chatwork.com/v2/rooms/{room_id}/messages"
        payload = {
            "body": f"[To:{cw_id}]{name}さん\n{message}" if name != "" else message,
            "self_unread": 1,  # Message sent by myself read setting(0: read, 1: unread)
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "x-chatworktoken": self.api_key,
        }

        _ = requests.post(url, data=payload, headers=headers)

    def post_file(self, room_id: str, message: str, file_path: str, mimetype: str, name: str = ""):
        """
        Post file to Chatwork

        Args:
            room_id(str): Room id which message is sent
            message(str): Posted message
            file_path(str): Posted file path
            mimetype(str): Posted file"s mimetype
            name(str): Mentioned person
        """
        cw_id = self.get_cw_id(name)
        file_name = Path(file_path).name
        with Path(file_path).open("rb") as f:
            file_data = f.read()

        url = f"https://api.chatwork.com/v2/rooms/{room_id}/files"
        files = {"file": (file_name, file_data, mimetype)}
        payload = {"message": f"[To:{cw_id}]{name}さん\n{message}" if name != "" else message}
        headers = {"X-ChatWorkToken": self.api_key}

        _ = requests.post(url, files=files, data=payload, headers=headers)

    def create_task(self, room_id: str, message: str, name: str) -> None:
        """
        Create task of Chatwork

        Args:
            room_id(str): Room id which message is sent
            message(str): Posted message
            name(str): Tasked person
        """
        cw_id = self.get_cw_id(name)

        url = f"https://api.chatwork.com/v2/rooms/{room_id}/tasks"
        payload = {
            "limit_type": "none",
            "body": message,
            "to_ids": cw_id,
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "x-chatworktoken": self.api_key,
        }

        _ = requests.post(url, data=payload, headers=headers)
