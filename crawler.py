import os
import csv
import time
import datetime
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/crawler.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def take_screenshot(driver, name="failure"):
    os.makedirs("screenshots", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"screenshots/{name}_{timestamp}.png"
    driver.save_screenshot(filepath)
    logging.info(f"Screenshot saved: {filepath}")

def crawl_amazon(search_term, max_pages=1, headless=False):
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--start-maximized")
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 15)
    scraped_data = []

    try:
        driver.get("https://www.amazon.in")
        time.sleep(3)

        # Click "Continue shopping" if shown
        try:
            continue_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Continue shopping']"))
            )
            continue_button.click()
            logging.info("Clicked 'Continue shopping' button.")
            time.sleep(2)
        except:
            logging.info("'Continue shopping' button not found.")

        # Begin search
        search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        search_box.clear()
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.RETURN)

        for page in range(max_pages):
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot")))
            products = driver.find_elements(By.CSS_SELECTOR, "div.s-main-slot div[data-component-type='s-search-result']")
            logging.info(f"Page {page+1}: Found {len(products)} products.")

            for idx, product in enumerate(products[:10]):
                try:
                    title_elem = product.find_element(By.XPATH, ".//h2/span")
                    title = title_elem.text.strip()

                    # Try finding link, retry if not found
                    try:
                        link_elem = product.find_element(By.XPATH, ".//h2/a")
                        link = link_elem.get_attribute("href")
                    except:
                        logging.warning(f"Product {idx+1}: Link not found on first attempt. Retrying...")
                        time.sleep(1)
                        try:
                            link_elem = product.find_element(By.XPATH, ".//h2/a")
                            link = link_elem.get_attribute("href")
                        except:
                            link = ""
                            logging.error(f"Product {idx+1}: Link not found after retry.")

                    price_elem = product.find_elements(By.CSS_SELECTOR, ".a-price .a-offscreen")
                    price = price_elem[0].text.strip() if price_elem else "N/A"

                    rating_elem = product.find_elements(By.CSS_SELECTOR, "span.a-icon-alt")
                    rating = rating_elem[0].text.strip() if rating_elem else "No rating"

                    scraped_data.append({
                        "name": title,
                        "price": price,
                        "rating": rating,
                        "link": link
                    })

                    logging.info(f"{idx+1}. {title} | {price} | {rating}")

                except Exception as e:
                    logging.error(f"Skipped item {idx+1} due to error: {e}")
                    take_screenshot(driver, f"{search_term}_product_{idx+1}_failed")

            # Pagination
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "ul.a-pagination li.a-last a")
                if next_btn.is_displayed():
                    next_btn.click()
                    time.sleep(3)
                else:
                    logging.info("No more pages to navigate.")
                    break
            except:
                logging.info("Pagination ended or next button not found.")
                break

        # Save results
        if scraped_data:
            os.makedirs("output", exist_ok=True)
            filepath = f"output/{search_term.lower()}s.csv"
            with open(filepath, "w", newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["name", "price", "rating", "link"])
                writer.writeheader()
                writer.writerows(scraped_data)
            logging.info(f"Saved {len(scraped_data)} items to: {filepath}")
        else:
            logging.warning("No items scraped. CSV not created.")

        # Negative test (can fail safely)
        try:
            logging.info("Performing negative search test...")
            search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
            search_box.clear()
            search_box.send_keys("!@#$%^&*()_+=-[]{}|;:',.<>?/~`")
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)

            if "did not match any products" in driver.page_source.lower() or "no results for" in driver.page_source.lower():
                logging.info("Negative test passed.")
            else:
                logging.warning("Negative test failed. Unexpected content.")
                take_screenshot(driver, "negative_test_failed")
        except Exception as e:
            logging.error(f"Negative test exception: {e}")
            take_screenshot(driver, "negative_test_error")

        return scraped_data

    except Exception as e:
        logging.critical(f"Fatal error during crawl: {e}", exc_info=True)
        take_screenshot(driver, f"{search_term}_fatal")
        return []

    finally:
        driver.quit()
