# tester_utils.py

import os
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

CHROME_DRIVER_PATH = "./chromedriver.exe"
SCREENSHOT_DIR = "screenshots"

def init_driver(headless=True):
    """
    Initializes a Chrome WebDriver instance.
    :param headless: Whether to run in headless mode.
    :return: WebDriver object
    """
    options = Options()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")

    try:
        service = Service(CHROME_DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        print(f"Failed to initialize WebDriver: {e}")
        raise

def take_screenshot(driver, name="screenshot", folder=SCREENSHOT_DIR):
    """
    Takes a screenshot and saves it with a timestamped filename.
    :param driver: The Selenium WebDriver instance.
    :param name: Base name for the screenshot file.
    :param folder: Directory where the screenshot should be saved.
    """
    try:
        os.makedirs(folder, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(folder, f"{name}_{timestamp}.png")
        driver.save_screenshot(filepath)
        print(f"Screenshot saved: {filepath}")
    except Exception as e:
        print(f"Failed to save screenshot '{name}': {e}")
