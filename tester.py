# tester.py

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tester_utils import init_driver, take_screenshot
import time


def test_search_functionality(search_term, expect_results=True):
    """
    Tests Amazon's search functionality for valid or invalid queries.
    Captures screenshots on failure.
    """
    driver = init_driver()
    wait = WebDriverWait(driver, 10)

    try:
        driver.get("https://www.amazon.in/")
        search_box = wait.until(EC.element_to_be_clickable((By.ID, "twotabsearchtextbox")))
        search_box.clear()
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.RETURN)

        wait.until(EC.presence_of_element_located((By.ID, "search")))
        time.sleep(2)

        results = driver.find_elements(By.CSS_SELECTOR, "div.s-main-slot div[data-component-type='s-search-result']")
        page_text = driver.page_source.lower()

        if expect_results:
            passed = len(results) > 0
        else:
            passed = (
                len(results) == 0 or
                "did not match any products" in page_text or
                "no results for" in page_text
            )

        if not passed:
            take_screenshot(driver, f"search_{search_term}_fail")

        return passed

    except Exception as e:
        take_screenshot(driver, f"search_{search_term}_error")
        print(f"[ERROR] Search test for '{search_term}' failed: {e}")
        return False

    finally:
        driver.quit()


def test_product_page(url):
    """
    Tests individual Amazon product page for presence of:
    - Add to Cart button
    - Product description/specs
    - Image gallery
    Captures screenshot if any validation fails.
    """
    driver = init_driver()
    wait = WebDriverWait(driver, 10)

    results = {
        "Add to Cart button": "FAIL",
        "Product Details section": "FAIL",
        "Image Gallery": "FAIL"
    }

    try:
        driver.get(url)
        wait.until(EC.presence_of_element_located((By.ID, "productTitle")))

        # Check: Add to Cart button
        try:
            if driver.find_element(By.ID, "add-to-cart-button"):
                results["Add to Cart button"] = "PASS"
        except:
            pass

        # Check: Product details/description/specs
        try:
            if (
                driver.find_elements(By.ID, "productDetails_techSpec_section_1") or
                driver.find_elements(By.ID, "productDescription") or
                driver.find_elements(By.ID, "feature-bullets")
            ):
                results["Product Details section"] = "PASS"
        except:
            pass

        # Check: Image gallery
        try:
            thumbnails = driver.find_elements(By.CSS_SELECTOR, "#altImages img")
            if thumbnails:
                results["Image Gallery"] = "PASS"
            elif driver.find_elements(By.TAG_NAME, "img"):
                results["Image Gallery"] = "PASS"
        except:
            pass

        if "FAIL" in results.values():
            take_screenshot(driver, "product_page_fail")

        return results

    except Exception as e:
        take_screenshot(driver, "product_page_error")
        print(f"[ERROR] Product page test failed for {url}: {e}")
        return results

    finally:
        driver.quit()
