import json
import os
from unittest.mock import patch

import pytest
from dotenv import load_dotenv

from skipy.chatwork_wrapper import Chatwork


class TestChatwork:
    @pytest.fixture(scope="class")
    def client(self):
        load_dotenv()
        api_key = os.environ["CHATWORK_API_KEY"]
        client = Chatwork(api_key=api_key)
        yield client

    def test_get_contacts(self, client):
        mock_response = {
            "text": json.dumps([{"account_id": 6222482, "name": "自動通知bot"}]),
            "status_code": 200,
        }
        with patch("requests.get") as mock_get:
            mock_get.return_value = type("MockResponse", (object,), mock_response)
            contacts = client.get_contacts()
            assert len(contacts) == 1
            assert contacts[0].get("account_id") == 6222482
            assert contacts[0].get("name") == "自動通知bot"

    def test_get_cw_id(self, client):
        mock_response = {
            "text": json.dumps([{"account_id": 6222482, "name": "自動通知bot"}]),
            "status_code": 200,
        }
        with patch("requests.get") as mock_get:
            mock_get.return_value = type("MockResponse", (object,), mock_response)
            compare = client.get_cw_id("自動通知bot")
            assert compare == 6222482
            # 半角スペースcase
            compare = client.get_cw_id("自動通知 bot")
            assert compare == 6222482
            # 全角スペースcase
            compare = client.get_cw_id("　自動通知bot")
            assert compare == 6222482
