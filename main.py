from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import os
import random
import datetime
import glob

OUTPUT_DIR = "output"
MAX_RETRIES = 2
RANDOM_WAIT_RANGE = (1, 3)

def save_screenshot(driver, name):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs("screenshots", exist_ok=True)
    screenshot_path = f"screenshots/{name}_{timestamp}.png"
    driver.save_screenshot(screenshot_path)
    print(f"Screenshot saved: {screenshot_path}")

def clear_old_screenshots():
    if os.path.exists("screenshots"):
        for f in glob.glob("screenshots/*.png"):
            os.remove(f)
        print("Cleared old screenshots.")

def crawl_amazon(search_term):
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)
    scraped_data = []

    try:
        driver.get("https://www.amazon.in")
        print("Please solve CAPTCHA manually if prompted...")
        time.sleep(20)  # Manual CAPTCHA handling

        search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        search_box.clear()
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.RETURN)

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot")))
        product_elements = driver.find_elements(By.CSS_SELECTOR, "div.s-main-slot div[data-component-type='s-search-result']")

        print(f"Found {len(product_elements)} results for '{search_term}'.")

        for idx, product in enumerate(product_elements[:10]):
            time.sleep(random.uniform(*RANDOM_WAIT_RANGE))  # Human-like delay
            retries = 0
            has_error = False

            while retries <= MAX_RETRIES:
                try:
                    name = product.find_element(By.CSS_SELECTOR, "h2 a span").text
                    price_elem = product.find_elements(By.CSS_SELECTOR, ".a-price-whole")
                    price = price_elem[0].text if price_elem else "N/A"
                    link = product.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")

                    scraped_data.append({"name": name, "price": price, "link": link})
                    print(f"{idx + 1}. {name} | ₹{price}")
                    has_error = False
                    break
                except Exception as e:
                    retries += 1
                    has_error = True
                    print(f"Retry {retries}/{MAX_RETRIES} for item {idx + 1} due to error: {e}")
                    time.sleep(1)

            if has_error:
                save_screenshot(driver, f"{search_term}_product_{idx + 1}_failed")
                print(f"Skipped item {idx + 1} after {MAX_RETRIES} retries.")

        # Save to CSV
        output_path = os.path.join(OUTPUT_DIR, search_term.lower())
        os.makedirs(output_path, exist_ok=True)
        csv_path = os.path.join(output_path, f"{search_term.lower()}s.csv")

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "price", "link"])
            writer.writeheader()
            writer.writerows(scraped_data)

        print(f"Data for '{search_term}' saved to: {csv_path}")

        # Negative Test
        print("\nPerforming negative test...")
        search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        search_box.clear()
        search_box.send_keys("ajsdhaskdjhasd")
        search_box.send_keys(Keys.RETURN)

        time.sleep(3)
        page_text = driver.page_source
        if "did not match any products" in page_text or "No results for" in page_text:
            print("Negative test passed: No products found for gibberish term.")
        else:
            print("Negative test failed: Unexpected results for gibberish.")

        return scraped_data

    except Exception as e:
        print("Error during crawling:", e)
        save_screenshot(driver, f"{search_term}_fatal_error")
        return []

    finally:
        driver.quit()

def main():
    clear_old_screenshots()

    search_terms = ["laptop", "smartphone"]

    for term in search_terms:
        print(f"\nStarting crawl for: {term}")
        data = crawl_amazon(term)
        if data:
            print(f"{len(data)} products scraped for '{term}'.")
        else:
            print(f"No data scraped for '{term}'. Check logs and screenshots.")

if __name__ == "__main__":
    main()
