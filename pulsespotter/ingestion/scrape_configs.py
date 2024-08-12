from pulsespotter.config import PROJECT_DIR
from pulsespotter.ingestion.utils.parse_functions import parse_date, string_join
from pulsespotter.ingestion.scrapers.site_archive_scraper import NewsArchiveScraper
from pulsespotter.ingestion.scrapers.site_scraper import NewsSiteScraper


SCRAPE_CONFIGS = {
    "spiegel": {
        "site_name": "spiegel",
        "enabled": True,
        "base_url": "https://www.spiegel.de",
        "search_url_template": "https://www.spiegel.de/nachrichtenarchiv/artikel-{day}.{month}.{year}.html",
        "scraper_class": NewsArchiveScraper,
        "crawler_request_params": {
            # "premium_proxy": "true",
            # "proxy_country": "de",
            "js_render": "true",
        },
        "site_elements_patterns": {
            "articles_pattern": (
                "//section[@data-area='article-teaser-list']//div[@data-block-el='articleTeaser']//a/@href"
            ),
        },
        "scraper_request_params": {
            # "premium_proxy": "true",
            # "proxy_country": "de",
            "js_render": "true",
            # "js_instructions": (
            #     """[{"click":".selector"},{"wait":500},{"fill":[".input","value"]},{"wait_for":".slow_selector"}]"""
            # ),
        },
        "scrape_patterns": {
            "title": {
                "pattern": (
                    "//main[@id='Inhalt']//article//header//h2//span[contains(@class, 'leading-tight')]"
                    "//span//text()"
                )
            },
            "description": {
                "pattern": (
                    "//main[@id='Inhalt']//article//header//div[contains(@class, 'RichText') "
                    "and contains(@class, 'leading-loose')]//text()"
                )
            },
            "raw_date": {
                "pattern": "//main[@id='Inhalt']//article//header//time[@class='timeformat']//text()",
            },
            "parsed_date": {
                "pattern": "//main[@id='Inhalt']//article//header//time[@class='timeformat']//text()",
                "parse_func": parse_date,
            },
            "paragraphs": {
                "pattern": (
                    "//main[@id='Inhalt']//article//section//div[@data-sara-click-el='body_element']"
                    "//div[contains(@class, 'RichText')]//p//text()"
                ),
                "extract_all": True,
            },
        },
        "blacklisted_urls": [],
        "blacklisted_url_patterns": [],
    },
    "handelsblatt": {
        "site_name": "handelsblatt",
        "enabled": True,
        "base_url": "https://www.handelsblatt.com",
        "search_url_template": "https://www.handelsblatt.com/archiv/?date={year}-{month}-{day}",
        "scraper_class": NewsArchiveScraper,
        "crawler_request_params": {
            "premium_proxy": "true",
            "proxy_country": "de",
            "js_render": "true",
            "js_instructions": """[{"wait_for": "app-default-teaser"}]""",
        },
        "site_elements_patterns": {
            "articles_pattern": "//app-default-teaser//a/@href",
        },
        "scraper_request_params": {
            "premium_proxy": "true",
            "proxy_country": "de",
            "js_render": "true",
            "js_instructions": """[{"wait_for":"app-storyline-elements"}]""",
        },
        "scrape_patterns": {
            "title": {
                "pattern": "//app-header-content-headline//h2/text()",
            },
            "description": {
                "pattern": "//app-header-content-lead-text/text()",
            },
            "raw_date": {
                "pattern": "//app-story-date/text()",
            },
            "parsed_date": {
                "pattern": "//app-story-date/text()",
                "parse_func": parse_date,
            },
            "paragraphs": {
                "pattern": "//app-storyline-elements//app-storyline-paragraph//p//text()",
                "extract_all": True,
            },
        },
        "blacklisted_urls": [],
        "blacklisted_url_patterns": ["""downloads.*\.ics""", """handelsblatt\.com\/themen""",],
    },
    "tagesschau": {
        "site_name": "tagesschau",
        "enabled": True,
        "base_url": "https://www.tagesschau.de",
        "search_url_template": "https://www.tagesschau.de/archiv?datum={year}-{month}-{day}",
        "scraper_class": NewsArchiveScraper,
        "crawler_request_params": {
            # "premium_proxy": "true",
            # "proxy_country": "de",
            "js_render": "true",
        },
        "site_elements_patterns": {
            "articles_pattern": (
                "//div[@class='copytext-element-wrapper__vertical-only']"
                "//div[contains(@class, 'teaser-right')][not(.//span[contains(@class, 'label') "
                "and (contains(., 'podcast') or contains(., 'liveblog'))])]//div[@class='teaser-right__teaserheadline']"
                "//a/@href"
            ),
        },
        "scraper_request_params": {
            # "premium_proxy": "true",
            # "proxy_country": "de",
            "js_render": "true",
            # "js_instructions": """[{"wait_for":".content-wrapper"}]""",
        },
        "scrape_patterns": {
            "title": {
                "pattern": (
                    "//main[contains(@class, 'content-wrapper')]//div[@class='seitenkopf__title']"
                    "//h1[@class='seitenkopf__headline']//span[@class='seitenkopf__headline--text']//text()"
                ),
            },
            "description": {
                "pattern": (
                    "//main[contains(@class, 'content-wrapper')]//p[contains(@class, 'textabsatz')]//strong//text()"
                ),
            },
            "raw_date": {
                "pattern": (
                    "//main[contains(@class, 'content-wrapper')]//div[@class='seitenkopf__title']"
                    "//p[@class='metatextline']//text()"
                ),
            },
            "parsed_date": {
                "pattern": (
                    "//main[contains(@class, 'content-wrapper')]//div[@class='seitenkopf__title']"
                    "//p[@class='metatextline']//text()"
                ),
                "parse_func": parse_date,
            },
            "paragraphs": {
                "pattern": (
                    "//main[contains(@class, 'content-wrapper')]//p[contains(@class, 'textabsatz')]//text() | "
                    "//main[contains(@class, 'content-wrapper')]//div[contains(@class, 'columns')]"
                    "//h2[@class='meldung__subhead']//text()"
                ),
                "extract_all": True,
            },
        },
        "blacklisted_urls": [],
        "blacklisted_url_patterns": ["multimedia", "livestream"],
    },
    "faz": {
        "site_name": "faz",
        "enabled": False,
        "base_url": "https://www.faz.net",
        "scraper_class": NewsSiteScraper,
        "crawler_request_params": {
            "premium_proxy": "true",
            "proxy_country": "de",
            # "js_render": "true",
        },
        "site_elements_patterns": {
            "topics_urls_pattern": (
                "//aside[contains(@class, 'burger-menu-sidebar')]"
                "//div[contains(@class, 'burger-menu-sidebar__departments')]//a/@href"
            ),
            "must_exist_pattern": (
                "//div[contains(@class, 'listed-items--wrapper')] | //div[contains(@class, 'paginator')]"
            ),
            "articles_pattern": (
                "//div[contains(@class, 'top1-teaser')]//a[contains(@class, 'top1-teaser__body')]//@href | "
                "//div[contains(@class, 'top2-teaser')]//div[contains(@class, 'teaser-object__body')]//a/@href | "
                "//div[contains(@class, 'listed-items--wrapper')]//div[contains(@class, 'teaser-object__body')]"
                "//a/@href"
            ),
            "paginator_pattern": "//div[contains(@class, 'paginator')]",
            "active_page_pattern": (
                "//div[contains(@class, 'paginator')]//li[contains(@class, 'paginator__active-page')]/a"
            ),
            "next_page_pattern": (
                "//div[contains(@class, 'paginator')]//li[contains(@class, 'paginator__active-page')]"
                "/following-sibling::li[1]"
            ),
        },
        "scraper_request_params": {
            "premium_proxy": "true",
            "proxy_country": "de",
            # "js_render": "true",
            # "js_instructions": """[{"wait_for":".body-elements-container"}]""",
        },
        "scrape_patterns": {
            "title": {
                "pattern": (
                    "//div[contains(@class, 'article-header')]//div[contains(@class, 'header-title')]//text()"
                ),
            },
            "description": {
                "pattern": (
                    "//div[contains(@class, 'article-header')]//div[contains(@class, 'header-teaser')]//text()"
                ),
                "extract_all": True,
                "parse_func": string_join,
            },
            "raw_date": {
                "pattern": (
                    "//div[contains(@class, 'article-header')]//div[contains(@class, 'header-detail')]//time//text()"
                ),
            },
            "parsed_date": {
                "pattern": (
                    "//div[contains(@class, 'article-header')]//div[contains(@class, 'header-detail')]//time//text()"
                ),
                "parse_func": parse_date,
            },
            "paragraphs": {
                "pattern": (
                    "//div[contains(@class, 'body-elements-container')]"
                    "//p[contains(@class, 'body-elements__paragraph')]//text()"
                ),
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
    },
    "tagesspiegel": {
        "site_name": "tagesspiegel",
        "enabled": True,
        "base_url": "https://www.tagesspiegel.de",
        "search_url_template": "https://www.tagesspiegel.de/archiv/{year}/{month}/{day}",
        "scraper_class": NewsArchiveScraper,
        "crawler_request_params": {
            # "premium_proxy": "true",
            # "proxy_country": "de",
            "js_render": "true",
            # "js_instructions": """[{"wait_for":"#page-container"}]""",
        },
        "site_elements_patterns": {
            "articles_pattern": (
                "//div[@id='page-container']//main[@id='main-content']//section//article//div//a/@href"
            ),
            "paginator_pattern": "//div[@id='page-container']//main[@id='main-content']//nav",
            "active_page_pattern": (
                "//div[@id='page-container']//main[@id='main-content']//nav//li//a[@aria-current='page']"
            ),
            "next_page_pattern": (
                "//div[@id='page-container']//main[@id='main-content']//nav//li//a[@aria-current='page']/parent::li"
                "/following-sibling::li[1]"
            ),
        },
        "scraper_request_params": {
            # "premium_proxy": "true",
            # "proxy_country": "de",
            "js_render": "true",
            # "js_instructions": """[{"wait_for":"#main-content"}]""",
        },
        "scrape_patterns": {
            "title": {
                "pattern": "//main[@id='main-content']/article/header/div/div/div/h1//text()",
                "extract_all": True,
                "parse_func": string_join,
            },
            "description": {
                "pattern": "//main[@id='main-content']/article/header/div/div//p//text()",
                "extract_all": True,
                "parse_func": string_join,
            },
            "raw_date": {
                "pattern": "//main[@id='main-content']/article/header/div/div/div//p/time/@datetime",
            },
            "parsed_date": {
                "pattern": "//main[@id='main-content']/article/header/div/div/div//p/time/@datetime",
                "parse_func": parse_date,
            },
            "paragraphs": {
                "pattern": (
                    "//main[@id='main-content']//article//div[@id='story-elements']//p//text()"
                ),
                "extract_all": True,
            },
        },
        "blacklisted_urls": [],
        "blacklisted_url_patterns": ["kultur/fka-twigs-will-einen-ki-klon-gute-idee-schon-jetzt-klingen-die-meisten-kunstler-wie-maschinen-11621471.html"]
    },
    "heise": {
        "site_name": "heise",
        "enabled": True,
        "base_url": "https://www.heise.de",
        "search_url_template": "https://www.heise.de/newsticker/archiv/{year}/{month}",
        "scraper_class": NewsArchiveScraper,
        "crawler_request_params": {
            # "premium_proxy": "true",
            # "proxy_country": "de",
            "js_render": "true",
        },
        "site_elements_patterns": {
            "articles_pattern": (
                "//section[contains(@class, 'archive__day')]//article[contains(@class, 'a-article-teaser')]"
                "//a[contains(@class, 'a-article-teaser__link')]//@href"
            ),
        },
        "scraper_request_params": {
            # "premium_proxy": "true",
            # "proxy_country": "de",
            "js_render": "true",
            # "js_instructions": (
            #     """[{"click":".selector"},{"wait":500},{"fill":[".input","value"]},{"wait_for":".slow_selector"}]"""
            # ),
        },
        "scrape_patterns": {
            "title": {
                "pattern": (
                    "//header[contains(@class, 'a-article-header')]//h1[contains(@class, 'a-article-header__title')]"
                    "//text()"
                ),
                "extract_all": True,
                "parse_func": string_join,
            },
            "description": {
                "pattern": (
                    "//header[contains(@class, 'a-article-header')]"
                    "//p[contains(@class, 'a-article-header__lead')]//text()"
                ),
                "extract_all": True,
                "parse_func": string_join,
            },
            "raw_date": {
                "pattern": (
                    "//header[contains(@class, 'a-article-header')]"
                    "//div[contains(@class, 'a-article-header__publish-info')]//time/@datetime"
                ),
            },
            "parsed_date": {
                "pattern": (
                    "//header[contains(@class, 'a-article-header')]"
                    "//div[contains(@class, 'a-article-header__publish-info')]//time/@datetime"
                ),
                "parse_func": parse_date,
            },
            "paragraphs": {
                "pattern": (
                    "//div[contains(@class, 'article-layout__content-container')]"
                    "//div[contains(@class, 'article-content')]//p//text() | "
                    "//div[contains(@class, 'article-layout__content-container')]"
                    "//div[contains(@class, 'article-content')]//*[contains(@class, 'subheading')]//text()"
                ),
                "extract_all": True,
            },
        },
        "blacklisted_urls": [],
        "blacklisted_url_patterns": [],
    },
}
