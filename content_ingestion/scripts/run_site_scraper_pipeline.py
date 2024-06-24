from content_ingestion.data_models import NewsScraperParams
from content_ingestion.utils.parse_functions import parse_date, string_join
from content_ingestion.scrapers.site_scraper import NewsSiteScraper


if __name__ == '__main__':

    params = {
        "site_name": "faz",
        "base_url": "https://www.faz.net",
        "crawler_request_params": {
            "premium_proxy": "true",
            "proxy_country": "de",
            # "js_render": "true",
        },
        "site_elements_patterns": {
            "topics_urls_pattern": """//aside[contains(@class, 'burger-menu-sidebar')]//div[contains(@class, 'burger-menu-sidebar__departments')]//a/@href""",
            "must_exist_pattern": """//div[contains(@class, 'listed-items--wrapper')] | //div[contains(@class, 'paginator')]""",
            "articles_pattern": """//div[contains(@class, 'top1-teaser')]//a[contains(@class, 'top1-teaser__body')]//@href | //div[contains(@class, 'top2-teaser')]//div[contains(@class, 'teaser-object__body')]//a/@href | //div[contains(@class, 'listed-items--wrapper')]//div[contains(@class, 'teaser-object__body')]//a/@href""",
            "paginator_pattern": """//div[contains(@class, 'paginator')]""",
            "active_page_pattern": """//div[contains(@class, 'paginator')]//li[contains(@class, 'paginator__active-page')]""",
            "next_page_pattern": """//div[contains(@class, 'paginator')]//li[contains(@class, "paginator__active-page")]/following-sibling::li[1]""",
        },
        "scraper_request_params": {
            "premium_proxy": "true",
            "proxy_country": "de",
            # "js_render": "true",
            # "js_instructions": """[{"wait_for":".body-elements-container"}]""",
        },
        "scrape_patterns": {
            "title": {
                "pattern": """//div[contains(@class, 'article-header')]//div[contains(@class, 'header-title')]//text()""",
            },
            "description": {
                "pattern": """//div[contains(@class, 'article-header')]//div[contains(@class, 'header-teaser')]//text()""",
                "extract_all": True,
                "parse_func": string_join,
            },
            "raw_date": {
                "pattern": """//div[contains(@class, 'article-header')]//div[contains(@class, 'header-detail')]//time//text()""",
            },
            "parsed_date": {
                "pattern": """//div[contains(@class, 'article-header')]//div[contains(@class, 'header-detail')]//time//text()""",
                "parse_func": parse_date,
            },
            "paragraphs": {
                "pattern": """//div[contains(@class, 'body-elements-container')]//p[contains(@class, 'body-elements__paragraph')]//text()""",
                "extract_all": True,
            },
        },
        "blacklisted_urls": [
            "https://www.faz.net/pro/d-economy/",
            "https://www.faz.net/faz-net-services/sport-live-ticker/",
            "https://www.faz.net/einspruch/",
            "https://www.faz.net/aktuell/",
            "https://www.faz.net/aktuell/wirtschaft/schneller-schlau/",
        ]
    }

    pipeline_params = NewsScraperParams(**params)
    pipeline = NewsSiteScraper(pipeline_params)
    pipeline.run(max_num_pages=11, until_date="2024-06-10")
