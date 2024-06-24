from content_ingestion.data_models import NewsArchiveScraperParams
from content_ingestion.utils.parse_functions import parse_date, string_join
from content_ingestion.scrapers.site_archive_scraper import NewsArchiveScraper


if __name__ == '__main__':

    params = {
        "site_name": "heise",
        "base_url": "https://www.heise.de",
        "search_url_template": "https://www.heise.de/newsticker/archiv/{year}/{month}",
        "crawler_request_params": {
            # "premium_proxy": "true",
            # "proxy_country": "de",
            # "js_render": "true",
        },
        "site_elements_patterns": {
            "articles_pattern": """//section[contains(@class, 'archive__day')]//article[contains(@class, 'a-article-teaser')]//a[contains(@class, 'a-article-teaser__link')]//@href""",
        },
        "scraper_request_params": {
            # "premium_proxy": "true",
            # "proxy_country": "de",
            # "js_render": "true",
            # "js_instructions": """[{"click":".selector"},{"wait":500},{"fill":[".input","value"]},{"wait_for":".slow_selector"}]""",
        },
        "scrape_patterns": {
            "title": {
                "pattern": """//header[contains(@class, 'a-article-header')]//h1[contains(@class, 'a-article-header__title')]//text()""",
                "extract_all": True,
                "parse_func": string_join,
            },
            "description": {
                "pattern": """//header[contains(@class, 'a-article-header')]//p[contains(@class, 'a-article-header__lead')]//text()""",
                "extract_all": True,
                "parse_func": string_join,
            },
            "raw_date": {
                "pattern": """//header[contains(@class, 'a-article-header')]//div[contains(@class, 'a-article-header__publish-info')]//time/@datetime""",
                "extract_all": False,
            },
            "parsed_date": {
                "pattern": """//header[contains(@class, 'a-article-header')]//div[contains(@class, 'a-article-header__publish-info')]//time/@datetime""",
                "extract_all": False,
                "parse_func": parse_date,
            },
            "paragraphs": {
                "pattern": """//div[contains(@class, 'article-layout__content-container')]//div[contains(@class, 'article-content')]//p//text() | //div[contains(@class, 'article-layout__content-container')]//div[contains(@class, 'article-content')]//*[contains(@class, 'subheading')]//text()""",
                "extract_all": True,
            },
        },
        "blacklisted_urls": [],
        "blacklisted_url_patterns": [],
    }

    pipeline_params = NewsArchiveScraperParams(**params)
    pipeline = NewsArchiveScraper(pipeline_params)
    pipeline.run(max_num_pages=5, start_date="2024-06-08", end_date="2024-06-10")
