from content_ingestion.scrapers.site_scraper import SiteScraper


if __name__ == '__main__':

    crawl_configs = {
        "site_name": "faz",
        "base_url": "https://www.faz.net",
        "crawl_configs": {
            "request_params": {
                "block_resources": "image,media",
                "premium_proxy": "true",
                "proxy_country": "de",
                # "js_render": "true",
            },
            "extract_patterns": {
                "topics_urls_pattern": """//aside[contains(@class, 'burger-menu-sidebar')]//div[contains(@class, 'burger-menu-sidebar__departments')]//a/@href""",
                "must_exist_pattern": """//div[contains(@class, 'listed-items--wrapper')] | //div[contains(@class, 'paginator')]""",
                "articles_pattern": """//div[contains(@class, 'top1-teaser')]//a[contains(@class, 'top1-teaser__body')]//@href | //div[contains(@class, 'top2-teaser')]//div[contains(@class, 'teaser-object__body')]//a/@href | //div[contains(@class, 'listed-items--wrapper')]//div[contains(@class, 'teaser-object__body')]//a/@href""",
                "paginator_pattern": """//div[contains(@class, 'paginator')]""",
                "active_page_pattern": """//div[contains(@class, 'paginator')]//li[contains(@class, 'paginator__active-page')]""",
                "next_page_pattern": """//div[contains(@class, 'paginator')]//li[contains(@class, "paginator__active-page")]/following-sibling::li[1]""",
            },
        },
        "parse_configs": {
            "request_params": {
                "block_resources": "image,media",
                "premium_proxy": "true",
                "proxy_country": "de",
                # "js_render": "true",
                # "js_instructions": """[{"wait_for":".body-elements-container"}]""",
            },
            "extract_patterns": {
                "title": """//div[contains(@class, 'article-header')]//div[contains(@class, 'header-title')]//text()""",
                "description": """//div[contains(@class, 'article-header')]//div[contains(@class, 'header-teaser')]//text()""",
                "date": """//div[contains(@class, 'article-header')]//div[contains(@class, 'header-detail')]//time//text()""",
                "paragraphs": """//div[contains(@class, 'body-elements-container')]//p[contains(@class, 'body-elements__paragraph')]//text()""",
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

    crawler = SiteScraper(**crawl_configs)
    crawler.crawl_articles(max_num_pages=3)
