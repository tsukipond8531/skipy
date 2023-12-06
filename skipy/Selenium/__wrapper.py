import os

from selenium import webdriver


def setup_driver(is_lambda=False):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    if is_lambda:
        dl_path = "/tmp/downloads"
    else:
        dl_path = "./downloads"
    os.makedirs(dl_path, exist_ok=True)
    options.add_experimental_option(
        "prefs",
        {"download.default_directory": dl_path, "download.prompt_for_download": False},
    )
    chrome = webdriver.Chrome(options=options)
    chrome.implicitly_wait(15)
    return chrome
