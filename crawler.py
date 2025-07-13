from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import os

MAX_PAGES = 3  # Change if you want to scrape more pages

def crawl_amazon(search_term):
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)

    driver.get("https://www.amazon.in")
    print("🔒 Please solve CAPTCHA manually if prompted...")
    time.sleep(20)  # Give user time to solve CAPTCHA if needed

    scraped_data = []
    seen_titles = set()

    try:
        search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.RETURN)

        for page in range(MAX_PAGES):
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot")))

            products = driver.find_elements(By.CSS_SELECTOR, "div.s-main-slot div[data-component-type='s-search-result']")
            print(f"🔍 Page {page + 1}: Found {len(products)} product elements.")

            for product in products:
                try:
                    name = product.find_element(By.CSS_SELECTOR, "h2 a span").text.strip()
                    if name in seen_titles:
                        continue
                    seen_titles.add(name)

                    price_elem = product.find_elements(By.CSS_SELECTOR, ".a-price-whole")
                    price = price_elem[0].text.strip() if price_elem else "N/A"
                    link = product.find_element(By.CSS_SELECTOR, "h2 a").getAttribute("href")
                    print(f"✅ {name} | ₹{price}")
                    scraped_data.append({"name": name, "price": price, "link": link})
                except Exception as e:
                    print("⚠️ Skipped one item due to error:", e)
                    continue

            # Check if next page exists
            try:
                next_btn = driver.find_element(By.CSS_SELECTOR, "a.s-pagination-next")
                if 'disabled' in next_btn.get_attribute("class"):
                    break
                next_btn.click()
                time.sleep(2)
            except Exception:
                print("ℹ️ No further pages or next button not found.")
                break

        # Save results
        os.makedirs("output", exist_ok=True)
        filename = f"output/{search_term.lower()}s.csv"
        print(f"💾 Saving {len(scraped_data)} products to {filename}")
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "price", "link"])
            writer.writeheader()
            writer.writerows(scraped_data)

        print(f"✅ Crawling complete. Data saved to {filename}")

        # NEGATIVE TEST
        print("🔎 Performing negative test: searching for a non-existent product...")
        try:
            search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
            search_box.clear()
            search_box.send_keys("ajsdhaskdjhasd")
            search_box.send_keys(Keys.RETURN)

            time.sleep(3)
            page_text = driver.page_source

            if "did not match any products" in page_text or "No results for" in page_text:
                print("✅ Negative test passed: No results shown for gibberish search.")
            else:
                print("❌ Negative test failed: Unexpected results found.")
        except Exception as e:
            print("⚠️ Error during negative test:", e)

        return scraped_data

    except Exception as e:
        print("❌ Failed to crawl:", e)
        return []
    finally:
        driver.quit()