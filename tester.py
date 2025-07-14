import os
import csv
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def take_screenshot(driver, name="failure"):
    os.makedirs("screenshots", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"screenshots/{name}_{timestamp}.png"
    driver.save_screenshot(filepath)
    print(f"Screenshot saved: {filepath}")


def validate_csv(file_path="output/laptops.csv"):
    assert os.path.exists(file_path), "CSV file not found!"
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            assert row["name"], "Product name is empty!"
            assert row["price"], "Product price is empty!"
    print("CSV content validation passed.")


def init_driver(headless=True):
    service = Service("./chromedriver.exe")
    options = Options()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    # Optional: to avoid detection as a bot
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def test_search_functionality(search_term, expect_results=True):
    driver = init_driver()
    wait = WebDriverWait(driver, 10)
    try:
        driver.get("https://www.amazon.in/")
        # Wait for search box to be clickable
        search_box = wait.until(EC.element_to_be_clickable((By.ID, "twotabsearchtextbox")))
        search_box.clear()
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.RETURN)

        # Wait for search results container or 'no results' message
        wait.until(
            EC.any_of(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot div[data-component-type='s-search-result']")),
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.a-section.a-spacing-base"))
            )
        )

        results = driver.find_elements(By.CSS_SELECTOR, "div.s-main-slot div[data-component-type='s-search-result']")

        if expect_results:
            passed = len(results) > 0
        else:
            page_text = driver.page_source.lower()
            passed = (len(results) == 0) or ("did not match any products" in page_text or "no results for" in page_text)

        if not passed:
            take_screenshot(driver, f"search_{search_term}_fail")

        return passed

    except Exception as e:
        take_screenshot(driver, f"search_{search_term}_error")
        print(f"Error during search test for '{search_term}': {e}")
        return False

    finally:
        driver.quit()


def test_product_page(url):
    driver = init_driver()
    wait = WebDriverWait(driver, 10)

    results = {
        "Add to Cart button": "FAIL",
        "Product Details section": "FAIL",
        "Image Gallery": "FAIL"
    }

    try:
        driver.get(url)
        # Wait for the page to load product title or add to cart button as a sign of readiness
        wait.until(EC.presence_of_element_located((By.ID, "productTitle")))

        # Check Add to Cart button
        try:
            wait.until(EC.presence_of_element_located((By.ID, "add-to-cart-button")))
            results["Add to Cart button"] = "PASS"
        except:
            pass

        # Check Product Details section (try multiple possible IDs)
        try:
            if (
                len(driver.find_elements(By.ID, "productDetails_techSpec_section_1")) > 0 or
                len(driver.find_elements(By.ID, "productDescription")) > 0 or
                len(driver.find_elements(By.ID, "feature-bullets")) > 0
            ):
                results["Product Details section"] = "PASS"
        except:
            pass

        # Check Image Gallery
        try:
            thumbnails = driver.find_elements(By.CSS_SELECTOR, "#altImages img")
            if thumbnails and len(thumbnails) > 0:
                results["Image Gallery"] = "PASS"
            else:
                imgs = driver.find_elements(By.TAG_NAME, "img")
                if imgs and len(imgs) > 0:
                    results["Image Gallery"] = "PASS"
        except:
            pass

        # Take screenshot if any check failed
        if "FAIL" in results.values():
            take_screenshot(driver, "product_page_fail")

        return results

    except Exception as e:
        take_screenshot(driver, "product_page_error")
        print(f"Error testing product page {url}: {e}")
        return results

    finally:
        driver.quit()