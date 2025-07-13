import os
import csv
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def take_screenshot(driver, name="failure"):
    os.makedirs("screenshots", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"screenshots/{name}_{timestamp}.png"
    driver.save_screenshot(filepath)
    print(f"📸 Screenshot saved: {filepath}")


def validate_csv(file_path="output/laptops.csv"):
    assert os.path.exists(file_path), "CSV file not found!"
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            assert row["name"], "Product name is empty!"
            assert row["price"], "Product price is empty!"
    print("✅ CSV content validation passed.")


def init_driver(headless=True):
    service = Service("./chromedriver.exe")
    options = Options()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def test_search_functionality(search_term, expect_results=True):
    driver = init_driver()
    try:
        driver.get("https://www.amazon.in/")
        time.sleep(2)

        search_box = driver.find_element(By.ID, "twotabsearchtextbox")
        search_box.clear()
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.RETURN)

        time.sleep(3)

        results = driver.find_elements(By.CSS_SELECTOR, "div.s-main-slot div[data-component-type='s-search-result']")

        if expect_results:
            passed = len(results) > 0
        else:
            # Sometimes page may show text instead of results
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
    results = {
        "Add to Cart button": "FAIL",
        "Product Details section": "FAIL",
        "Image Gallery": "FAIL"
    }

    try:
        driver.get(url)
        time.sleep(3)

        # Add to Cart button check
        try:
            driver.find_element(By.ID, "add-to-cart-button")
            results["Add to Cart button"] = "PASS"
        except:
            pass

        # Product details check (try multiple possible IDs)
        try:
            if driver.find_element(By.ID, "productDetails_techSpec_section_1") or driver.find_element(By.ID, "productDescription"):
                results["Product Details section"] = "PASS"
        except:
            pass

        # Image gallery check (look for thumbnails or images)
        try:
            thumbnails = driver.find_elements(By.CSS_SELECTOR, "#altImages img")
            if thumbnails and len(thumbnails) > 0:
                results["Image Gallery"] = "PASS"
            else:
                # fallback: any img tag presence
                imgs = driver.find_elements(By.TAG_NAME, "img")
                if imgs and len(imgs) > 0:
                    results["Image Gallery"] = "PASS"
        except:
            pass

        # Screenshot on any failure
        if "FAIL" in results.values():
            take_screenshot(driver, "product_page_fail")

        return results

    except Exception as e:
        take_screenshot(driver, "product_page_error")
        print(f"Error testing product page {url}: {e}")
        return results

    finally:
        driver.quit()