import json
import requests

from content_ingestion.config import ZENROWS_API_KEY
from content_ingestion.data_models import ScrapePattern
from content_ingestion.utils.parse_utils import parse_website

if __name__ == '__main__':

    request_params = {
        "premium_proxy": "true",
        "proxy_country": "de",
        # "js_render": "true",
        # "js_instructions": """[{"wait_for":"#page-container"}]""",
    }

    # for crawling article URLs
    extract_patterns = {
        "articles": ScrapePattern(
            pattern="""//div[@id='page-container']//main[@id='main-content']//section//article//div//a/@href""",
            extract_all=True,
        ),
        "paginator": ScrapePattern(
            pattern="""//div[@id='page-container']//main[@id='main-content']//nav""",
            extract_all=False,
        ),
        "active_page": ScrapePattern(
            pattern="""//div[@id='page-container']//main[@id='main-content']//nav//li//a[@aria-current='page']/parent::li""",
            extract_all=False,
        ),
        "next_page": ScrapePattern(
            pattern="""//div[@id='page-container']//main[@id='main-content']//nav//li//a[@aria-current='page']/parent::li/following-sibling::li[1]""",
            extract_all=False,
        ),
    }
    # site_url = "https://www.tagesspiegel.de/archiv/2024/06/03"
    # site_url = "https://www.tagesspiegel.de/archiv/2024/06/03/2"
    # site_url = "https://www.tagesspiegel.de/archiv/2024/06/03/3"
    site_url = "https://www.tagesspiegel.de/archiv/2024/06/03/4"

    # # for scraping content from article pages
    # extract_patterns = {
    #     "title": ScrapePattern(
    #         pattern="""//main[@id='main-content']/article/header/div//h1//text()""",
    #         extract_all=True,
    #         parse_func=string_join,
    #     ),
    #     "description": ScrapePattern(
    #         pattern="""//main[@id='main-content']/article/header/div/div/p/text()""",
    #         extract_all=True,
    #         parse_func=string_join,
    #     ),
    #     "raw_date": ScrapePattern(
    #         pattern="""//main[@id='main-content']/article/header/div//p/time/text()""",
    #         extract_all=False,
    #     ),
    #     "parsed_date": ScrapePattern(
    #         pattern="""//main[@id='main-content']/article/header/div//p/time/text()""",
    #         extract_all=False,
    #         parse_func=parse_date,
    #     ),
    #     "paragraphs": ScrapePattern(
    #         pattern="""//main[@id='main-content']/article//div[contains(@id, 'story-elements')]/p//text()""",
    #         extract_all=True,
    #     ),
    # }
    # # site_url = "https://www.tagesspiegel.de/berlin/berliner-wirtschaft/grosse-eroffnungsfeier-fur-den-gasometer-ein-altes-und-neues-wahrzeichen-fur-berlin-11753027.html"
    # site_url = "https://www.tagesspiegel.de/sport/real-madrid-siegt-borussia-dortmund-verliert-das-champions-league-finale-11753156.html"

    request_params["url"] = site_url
    request_params["apikey"] = ZENROWS_API_KEY
    response = requests.get("https://api.zenrows.com/v1/", params=request_params)
    response.raise_for_status()

    parsed_content = parse_website(response.text, extract_patterns)
    print(json.dumps(parsed_content))
