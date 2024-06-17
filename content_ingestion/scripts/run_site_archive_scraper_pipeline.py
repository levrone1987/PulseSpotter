from content_ingestion.data_models import SiteArchiveScraperPipelineParams
from content_ingestion.parse_functions import parse_date
from content_ingestion.scrapers.site_archive_scraper import SiteArchiveScraperPipeline


if __name__ == '__main__':

    params = {
        "site_name": "spiegel",
        "base_url": "https://www.spiegel.de",
        "search_url_template": "https://www.spiegel.de/nachrichtenarchiv/artikel-{day}.{month}.{year}.html",
        "crawler_request_params": {
            "premium_proxy": "true",
            "proxy_country": "de",
            # "js_render": "true",
        },
        "site_elements_patterns": {
            "articles_pattern": """//section[@data-area="article-teaser-list"]//div[@data-block-el="articleTeaser"]//a/@href""",
        },
        "scraper_request_params": {
            "premium_proxy": "true",
            "proxy_country": "de",
            # "js_render": "true",
            # "js_instructions": """[{"click":".selector"},{"wait":500},{"fill":[".input","value"]},{"wait_for":".slow_selector"}]""",
        },
        "scrape_patterns": {
            "title": {
                "pattern": """//main[@id='Inhalt']//article//header//h2//span[contains(@class, 'leading-tight')]//span//text()""",
                "extract_all": False,
            },
            "description": {
                "pattern": """//main[@id='Inhalt']//article//header//div[contains(@class, 'RichText') and contains(@class, 'leading-loose')]//text()""",
                "extract_all": False,
            },
            "raw_date": {
                "pattern": """//main[@id='Inhalt']//article//header//time[@class='timeformat']//text()""",
                "extract_all": False,
            },
            "parsed_date": {
                "pattern": """//main[@id='Inhalt']//article//header//time[@class='timeformat']//text()""",
                "extract_all": False,
                "parse_func": parse_date,
            },
            "paragraphs": {
                "pattern": """//main[@id='Inhalt']//article//section//div[@data-sara-click-el='body_element']//div[contains(@class, 'RichText')]//p//text()""",
                "extract_all": True,
            },
        },
        "blacklisted_urls": [],
        "blacklisted_url_patterns": [],
    }

    pipeline_params = SiteArchiveScraperPipelineParams(**params)
    pipeline = SiteArchiveScraperPipeline(pipeline_params)
    pipeline.run(max_num_pages=5, start_date="2024-06-08", end_date="2024-06-10")
