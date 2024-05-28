import requests

from content_ingestion.config import ZENROWS_API_KEY
from content_ingestion.scrapers.article_scraper import NewsArticleScraper


if __name__ == '__main__':

    site_scrape_configs = {
        "request_params": {
            "js_render": "true",
            "js_instructions": """[{"click":".selector"},{"wait":500},{"fill":[".input","value"]},{"wait_for":".slow_selector"}]""",
        },
        "extract_patterns": {
            "title": """//main[contains(@class, 'content-wrapper')]//div[@class='seitenkopf__title']//h1[@class='seitenkopf__headline']//span[@class='seitenkopf__headline--text']//text()""",
            "description": """//main[contains(@class, 'content-wrapper')]//p[contains(@class, 'textabsatz')]//strong//text()""",
            "date": """//main[contains(@class, 'content-wrapper')]//div[@class='seitenkopf__title']//p[@class='metatextline']//text()""",
            "paragraphs": """//main[contains(@class, 'content-wrapper')]//p[contains(@class, 'textabsatz')]//text() | //main[contains(@class, 'content-wrapper')]//div[contains(@class, 'columns')]//h2[@class='meldung__subhead']//text()""",
        }
    }
    site_url = "https://www.tagesschau.de/wirtschaft/finanzen/marktberichte/marktbericht-dax-dow-112.html#US-Wirtschaft-weiter-robust"

    request_params = site_scrape_configs.get("request_params", {})
    extract_patterns = site_scrape_configs.get("extract_patterns", {})

    request_params["url"] = site_url
    request_params["apikey"] = ZENROWS_API_KEY
    response = requests.get("https://api.zenrows.com/v1/", params=request_params)
    response.raise_for_status()

    scraper = NewsArticleScraper({})
    parsed_content = scraper._parse_website(response.text, extract_patterns)
    print(parsed_content)
