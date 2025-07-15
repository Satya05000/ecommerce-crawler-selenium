import logging
from crawler import crawl_amazon

# Setup console logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def main():
    # List of search terms
    search_terms = ["laptop", "smartphone"]

    for term in search_terms:
        print(f"\n{'='*60}\nStarting crawl for: {term}\n{'='*60}")
        try:
            data = crawl_amazon(term, max_pages=1, headless=False)
            print(f"Scraped {len(data)} items for '{term}'\n")
        except Exception as e:
            logging.critical(f"Unexpected failure during crawl for '{term}': {e}", exc_info=True)

if __name__ == "__main__":
    main()
