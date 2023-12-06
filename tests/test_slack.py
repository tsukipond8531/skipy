from skipy.Slack import Slack


class TestSlack:
    def test_init(self):
        Slack(web_hook_url="dummy_url")
