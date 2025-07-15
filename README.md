# Ecommerce Product Crawler & QA Tester

This project is a Python-based automation tool for crawling product data from [Amazon.in](https://www.amazon.in) using **Selenium WebDriver**. It includes built-in testing using **Pytest**, auto-screenshot capture, structured logs, and generates HTML test reports.

---

## Features

- Crawls product title, price, rating, and URL
- Supports pagination (first page only, extendable)
- Screenshot capture on failure
- Headless browser mode support
- Logs every event to `logs/crawler.log`
- Generates `CSV` output for each search term
- HTML test report via `pytest-html`
- Fully modular architecture

---

## Folder Structure

ecommerce-crawler/
├── crawler.py # Scrapes Amazon products
├── main.py # Entry point: runs multiple searches
├── test_functions.py # Functional tests using pytest
├── tester.py # CLI test runner
├── tester_utils.py # Reusable test utilities
├── output/ # Stores generated CSV files
├── logs/ # Logs and screenshots
├── screenshots/ # Failure screenshots
├── report.html # Test execution report
├── chromedriver.exe # Required ChromeDriver (downloaded manually)

---

## Setup Instructions

## 1. Clone the Repository


git clone https://github.com/Satya05000/ecommerce-crawler.git
cd ecommerce-crawler

## 2. Install Dependencies

pip install -r requirements.txt
If requirements.txt is not present, manually install:

pip install selenium pytest pytest-html

## 3. Ensure chromedriver.exe is in the project root

Download from: https://chromedriver.chromium.org/downloads
Ensure the version matches your installed Chrome.

## Run the Crawler

Run the main crawler script for specific keywords:

python main.py

## Output CSVs will be saved under /output as:

- laptops.csv
- smartphones.csv

## Run Tests with Pytest

Run functional tests and generate HTML report:

pytest test_functions.py --html=report.html --self-contained-html
If scraping fails, test will be skipped

Screenshots on failure are saved in /logs/screenshots

Logs are written to logs/test_log.log

## Sample Output

- output/laptops.csv
- logs/crawler.log
- report.html
- screenshots/

## Test Coverage

test_valid_search	Checks search results appear for "laptop, Smartphone"
test_invalid_search	Validates Amazon handles gibberish input
test_csv_content	Validates structure and content of CSV

The negative test intentionally uses special characters (!@#$...) for robustness.

Product links may occasionally fail due to DOM changes — retry logic included.

## Author

Satya Venkata Gangadhar Samanthula
https://github.com/Satya05000
