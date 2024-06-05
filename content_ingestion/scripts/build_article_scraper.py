import requests
from datetime import datetime

from content_ingestion.config import ZENROWS_API_KEY
from content_ingestion.utils import parse_website


if __name__ == '__main__':

    request_params = {
        "block_resources": "image,media",
        "premium_proxy": "true",
        "proxy_country": "de",
        # "js_render": "true",
        # "js_instructions": """[{"wait_for":".body-elements-container"}]""",
    }
    extract_patterns = {
        "title": """//div[contains(@class, 'article-header')]//div[contains(@class, 'header-title')]//text()""",
        "description": """//div[contains(@class, 'article-header')]//div[contains(@class, 'header-teaser')]//text()""",
        "date": """//div[contains(@class, 'article-header')]//div[contains(@class, 'header-detail')]//time//text()""",
        "paragraphs": """//div[contains(@class, 'body-elements-container')]//p[contains(@class, 'body-elements__paragraph')]//text()""",
    }
    site_url = "https://www.faz.net/aktuell/wissen/krebsmedizin/corona-experten-raten-krebs-patienten-zu-impfungen-18448598.html"

    request_params["url"] = site_url
    request_params["apikey"] = ZENROWS_API_KEY
    print(datetime.now())
    response = requests.get("https://api.zenrows.com/v1/", params=request_params)
    response.raise_for_status()
    print(datetime.now())

    parsed_content = parse_website(response.text, extract_patterns)
    print(parsed_content)

