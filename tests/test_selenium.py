from skipy.Selenium import setup_driver


class TestSelenium:
    def test_init(self):
        setup_driver(is_lambda=True)
