import json

import requests


class Slack:
    def __init__(self, web_hook_url):
        self.web_hook_url = web_hook_url

    def post(self, msg, username="Notification-Bot"):
        requests.post(
            self.web_hook_url,
            data=json.dumps(
                {
                    "text": msg,
                    "username": username,
                    "icon_emoji": ":smile_cat:",
                    "link_names": 1,
                }
            ),
        )
