from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import os


def crawl_amazon(search_term, max_pages=3):
    chrome_options = Options()
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)

    driver.get("https://www.amazon.in")
    print("Please solve CAPTCHA manually if prompted...")
    time.sleep(20)  # Manual handling if CAPTCHA appears

    scraped_data = []

    try:
        search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.RETURN)

        for page in range(max_pages):
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot")))
            products = driver.find_elements(By.CSS_SELECTOR, "div.s-main-slot div[data-component-type='s-search-result']")

            print(f"Page {page + 1} - Found {len(products)} product elements.")

            for product in products:
                try:
                    name = product.find_element(By.CSS_SELECTOR, "h2 a span").text

                    price_elem = product.find_elements(By.CSS_SELECTOR, ".a-price-whole")
                    price = price_elem[0].text if price_elem else "N/A"

                    rating_elem = product.find_elements(By.CSS_SELECTOR, "span.a-icon-alt")
                    rating = rating_elem[0].get_attribute("innerHTML") if rating_elem else "No rating"

                    link = product.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")

                    print(f"{name} | ₹{price} | Rating: {rating}")
                    scraped_data.append({
                        "name": name,
                        "price": price,
                        "rating": rating,
                        "link": link
                    })
                except Exception as e:
                    print("Skipped one item due to error:", e)
                    continue

            # Try to click next page button
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "ul.a-pagination li.a-last a")
                if next_button:
                    next_button.click()
                    time.sleep(3)
                else:
                    print("No more pages.")
                    break
            except Exception:
                print("No next page button found. Ending pagination.")
                break

        os.makedirs("output", exist_ok=True)
        filename = f"output/{search_term.lower()}s.csv"
        print(f"Saving {len(scraped_data)} products to {filename}")
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "price", "rating", "link"])
            writer.writeheader()
            writer.writerows(scraped_data)

        print(f"Crawling complete. Data saved to {filename}")

        # NEGATIVE TEST: Search for gibberish product name
        print("Performing negative test: searching for a non-existent product...")
        try:
            search_box = wait.until(EC.presence_of_element_located((By.ID, "twotabsearchtextbox")))
            search_box.clear()
            search_box.send_keys("ajsdhaskdjhasd")
            search_box.send_keys(Keys.RETURN)

            time.sleep(3)
            page_text = driver.page_source

            if "did not match any products" in page_text or "No results for" in page_text:
                print("Negative test passed: No results shown for gibberish search.")
            else:
                print("Negative test failed: Unexpected results found.")
        except Exception as e:
            print("Error during negative test:", e)

        return scraped_data

    except Exception as e:
        print("Failed to crawl:", e)
        return []
    finally:
        driver.quit()