# Ecommerce Crawler & Automated Testing

Automated crawling and functional testing of an e-commerce website (Amazon India) using Selenium and Python.

---

## Objective

- Crawl product listings for a given search term (e.g., laptops).
- Extract product details: name, price, ratings, and URL.
- Validate product page functionalities: Add to Cart button, product details, image gallery.
- Test search functionality with valid and invalid inputs.
- Store crawled data in CSV files.
- Log test results with screenshots on failures.
- Support multi-page crawling (pagination).
- Run tests in parallel using pytest-xdist.

---

## Tools & Frameworks Used

- Python 3.x
- Selenium WebDriver
- ChromeDriver
- pytest (for test automation)
- pytest-xdist (for parallel test execution)
- pytest-html (for HTML reports)

---

## Setup & Installation

1. Clone the repository:
git clone https://github.com/Satya05000/ecommerce-crawler-selenium.git
cd ecommerce-crawler-selenium

2. Install required packages:
pip install -r requirements.txt

3. Download ChromeDriver matching your Chrome browser version and place it in the project root or system PATH.

How to Run
Crawling
Run the crawler script to search for products and save results:
python crawler.py
Default search term is "laptop". Modify inside the script or add input parameters as needed.

Testing
Run tests using pytest with parallel execution and HTML report generation:
pytest -n 2 --html=report.html --self-contained-html
Test cases cover search functionality (valid and invalid), product page validations, and CSV content validation.

Screenshots are saved on failures in the screenshots/ folder.

Assumptions & Constraints
The crawler requires manual CAPTCHA solving if prompted on Amazon.

The project targets Amazon India (https://www.amazon.in).

Ensure ChromeDriver is compatible with the installed Chrome browser version.

Pagination support is implemented to crawl multiple pages.

Parallel testing is demonstrated using pytest-xdist.

Responsiveness testing and Selenium Grid are not included in this version.

Project Structure
ecommerce-crawler-selenium/

crawler.py         # Script to crawl product data
tester.py          # Automated functional tests using Selenium
output/            # CSV files with crawled data
screenshots/       # Screenshots on test failures
requirements.txt   # Python dependencies
report.html        # Generated test report (after pytest run)
README.md          # This file

Sample Output
CSV files with product details saved in output/.

HTML test report report.html shows test summary and detailed results.

Screenshots for failed tests saved in screenshots/.

Contact
For any questions or issues, please contact:
Satya
Email: ssvgangadhar@gmail.com
GitHub: https://github.com/Satya05000
