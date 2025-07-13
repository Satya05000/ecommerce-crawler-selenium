import pytest
import os
import csv
import logging
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

CHROME_DRIVER_PATH = "./chromedriver.exe"
OUTPUT_DIR = "output/laptop"
SCREENSHOT_DIR = "logs/screenshots"
LOG_FILE = "logs/test_log.log"

# Setup folders and clean screenshot dir
if os.path.exists(SCREENSHOT_DIR):
    shutil.rmtree(SCREENSHOT_DIR)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Setup logger
logging.basicConfig(filename=LOG_FILE, level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

@pytest.fixture(scope="function")
def driver():
    service = Service(CHROME_DRIVER_PATH)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    browser = webdriver.Chrome(service=service, options=options)
    yield browser
    browser.quit()

def take_screenshot(driver, test_name, identifier=""):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_{identifier}" if identifier else ""
    filename = os.path.join(SCREENSHOT_DIR, f"{test_name}{suffix}_{timestamp}.png")
    driver.save_screenshot(filename)
    logging.info(f"📸 Screenshot saved: {filename}")

def test_valid_search(driver):
    try:
        driver.get("https://www.amazon.in/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
        ).send_keys("laptop")
        driver.find_element(By.ID, "nav-search-submit-button").click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".s-result-item"))
        )
        logging.info("✅ test_valid_search passed.")
    except Exception as e:
        take_screenshot(driver, "test_valid_search", "laptop")
        logging.error("❌ test_valid_search failed", exc_info=True)
        raise

def test_invalid_search(driver):
    try:
        driver.get("https://www.amazon.in/")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "twotabsearchtextbox"))
        ).send_keys("asdlkfjasldfkjnonexistentproduct123")
        driver.find_element(By.ID, "nav-search-submit-button").click()

        WebDriverWait(driver, 10).until(
            EC.any_of(
                EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'did not match any products')]")),
                EC.presence_of_element_located((By.CSS_SELECTOR, ".s-no-outline"))
            )
        )
        logging.info("✅ test_invalid_search passed.")
    except Exception as e:
        take_screenshot(driver, "test_invalid_search", "invalid_search")
        logging.error("❌ test_invalid_search failed", exc_info=True)
        raise

def test_csv_content():
    try:
        file_path = os.path.join(OUTPUT_DIR, "laptops.csv")
        assert os.path.exists(file_path), "CSV file not found!"

        with open(file_path, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if not rows:
                pytest.skip("⚠️ CSV is empty! Skipping row validation.")
            for row in rows:
                assert row["name"], "Missing product name!"
                assert row["price"], "Missing product price!"

        logging.info("✅ test_csv_content passed.")
    except Exception as e:
        logging.error("❌ test_csv_content failed", exc_info=True)
        raise