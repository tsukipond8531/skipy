from __future__ import annotations

import re
from pathlib import Path

import magic
import requests


class Chatwork:
    BASE_URL = "https://api.chatwork.com/v2/"

    def __init__(self, token: str):
        """Set ChatWork's API token.

        Args:
            token: ChatWork API token.
        """
        self._token = token

    def set_token(self, token: str):
        """Set another ChatWork's API token.

        Args:
            token: ChatWork API token.
        """
        self._token = token

    def post_messages(self, message: str, room_id: int) -> dict | None:
        """Add new message to the chat.

        Args:
            message: message body.
            room_id: ChatWork room id.

        Returns:
            JSON Format response as a dict.

        Raises:
            Raises stored :class:`HTTPError`, if one occurred.
        """
        res = requests.post(
            self._make_url("rooms/{}/messages".format(room_id)),
            headers=self._make_headers(),
            params=self._make_body(message=message),
        )
        return self._check_res(res, dict)

    def post_file(self, message: str, room_id: int, file_path: str) -> dict | None:
        """Add new message to the chat.

        Args:
            message: message body.
            room_id: ChatWork room id.
            file_path: File path to be uploaded.

        Returns:
            JSON Format response as a dict.

        Raises:
            Raises stored :class:`HTTPError`, if one occurred.
        """
        res = requests.post(
            self._make_url("rooms/{}/files".format(room_id)),
            headers=self._make_headers(),
            params=self._make_body(message=message),
            files=self._make_files(file_path),
        )
        return self._check_res(res, dict)

    def post_task(
        self,
        message: str,
        room_id: int,
        to_ids: str,
    ) -> dict | None:
        """Add new message to the chat.

        Args:
            message: message body.
            room_id: ChatWork room id.
            to_ids: assingned user ids, separated by comma.

        Returns:
            JSON Format response as a dict.

        Raises:
            Raises stored :class:`HTTPError`, if one occurred.
        """
        res = requests.post(
            self._make_url("rooms/{}/tasks".format(room_id)),
            headers=self._make_headers(),
            params=self._make_body(message=message, to_ids=to_ids),
        )
        return self._check_res(res, dict)

    def get_contacts(self) -> list | None:
        """Get contacts.

        Args:
            No arguments.

        Returns:
            JSON Format response as a list.

        Raises:
            Raises stored :class:`HTTPError`, if one occurred.
        """
        res = requests.get(
            self._make_url("contacts"),
            headers=self._make_headers(),
        )
        return self._check_res(res, list)

    def get_messages(self, room_id: int, force: bool = False) -> list | None:
        """Get new messages from a room.

        If you set force=True, you can get older messages.

        Args:
            room_id: ChatWork room id.
            force (optional): Flag which forces to get 100 newest entries
                regardless of previous calls.

        Returns:
            JSON Format response as a list.

        Raises:
            Raises stored :class:`HTTPError`, if one occurred.
        """
        forceflg = "?force=1" if force else "?force=0"
        res = requests.get(
            self._make_url("rooms/{}/messages".format(room_id) + forceflg),
            headers=self._make_headers(),
        )
        return self._check_res(res, list)

    def _make_url(self, endpoint: str) -> str:
        return self.BASE_URL + endpoint

    def _make_headers(self):
        return {"X-ChatWorkToken": self._token}

    def _make_body(
        self,
        message: str,
        to_ids: str | None = None,
    ):
        payload = {}
        if message:
            payload["body"] = message
        if to_ids:
            payload["to_ids"] = to_ids
        return payload

    def _make_files(self, file_path: str) -> dict:
        file = Path(file_path)
        mimetype = magic.from_file(file, mime=True)
        with file.open("rb") as f:
            data = f.read()
        return {"file": (file.name, data, mimetype)}

    def _check_res(self, res, deftype):
        if res.ok:
            return self._check_status_code(res, deftype)
        else:
            message = res.json()
            raise Exception(message["errors"])

    def _check_status_code(self, res, deftype):
        if res.status_code == 200:
            return res.json()
        elif res.status_code == 204:
            return deftype()
        else:
            res.raise_for_status()

    def _make_firstline(self, to_names: list[str] | None):
        regex = "[ 　]"
        first_line = ""
        if to_names:
            contacts = self.get_contacts()
            if contacts:
                for to_name in to_names:
                    for contact in contacts:
                        if re.sub(regex, "", contact["name"]) == re.sub(
                            regex, "", to_name
                        ):
                            first_line += f"[To:{contact['account_id']}]{to_name}さん"
                            break
        return first_line

    def format_message(
        self,
        message: str,
        title: str = "From Python",
        to_names: list[str] | None = None,
    ):
        format_message = f"""
        {self._make_firstline(to_names)}
        [info][title]{title}[/title]{message}[/info]
        """
        return format_message
