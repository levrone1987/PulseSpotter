from pulsespotter.ingestion.utils.parse_functions import parse_date, string_join
from pulsespotter.ingestion.scrapers.site_archive_scraper import NewsArchiveScraper
from pulsespotter.ingestion.scrapers.site_scraper import NewsSiteScraper


SCRAPE_CONFIGS = {
    "spiegel": {
        "site_name": "spiegel",
        "enabled": False,
        "base_url": "https://www.spiegel.de",
        "search_url_templates": [
            "https://www.spiegel.de/nachrichtenarchiv/artikel-{day}.{month}.{year}.html"
        ],
        "scraper_class": NewsArchiveScraper,
        "crawler_request_params": {
            "premium_proxy": "true",
            "proxy_country": "de",
            "js_render": "true",
            "js_instructions": """[{"wait":500},{"wait_for":"section.article-teaser-list"}]"""
        },
        "site_elements_patterns": {
            "articles_pattern": (
                "//section[@data-area='article-teaser-list']//div[@data-block-el='articleTeaser']//a/@href"
            ),
        },
        "scraper_request_params": {
            "premium_proxy": "true",
            "proxy_country": "de",
            "js_render": "true",
            "js_instructions": """[{"wait":500},{"wait_for":"main#Inhalt"}]""",
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
        "enabled": False,
        "base_url": "https://www.handelsblatt.com",
        "search_url_templates": [
            "https://www.handelsblatt.com/archiv/?date={year}-{month}-{day}"
        ],
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
        "enabled": False,
        "base_url": "https://www.tagesschau.de",
        "search_url_templates": [
            "https://www.tagesschau.de/archiv?datum={year}-{month}-{day}"
        ],
        "scraper_class": NewsArchiveScraper,
        "crawler_request_params": {
            "js_render": "true",
            "js_instructions": """[{"wait":500},{"wait_for":"div.teaser-right"}]""",
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
            "js_render": "true",
            "js_instructions": """[{"wait_for":"main.content-wrapper"}]""",
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
                "/following-sibling::li[1]//a/@href"
            ),
        },
        "scraper_request_params": {
            "premium_proxy": "true",
            "proxy_country": "de",
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
        "enabled": False,
        "base_url": "https://www.tagesspiegel.de",
        "search_url_templates": [
            "https://www.tagesspiegel.de/archiv/{year}/{month}/{day}"
        ],
        "scraper_class": NewsArchiveScraper,
        "crawler_request_params": {
            "js_render": "true",
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
                "/following-sibling::li[1]//a/@href"
            ),
        },
        "scraper_request_params": {
            "js_render": "true",
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
        "blacklisted_url_patterns": ["www.tagesspiegel.de/test/"]
    },
    "heise": {
        "site_name": "heise",
        "enabled": False,
        "base_url": "https://www.heise.de",
        "search_url_templates": [
            "https://www.heise.de/newsticker/archiv/{year}/{month}"
        ],
        "scraper_class": NewsArchiveScraper,
        "crawler_request_params": {
            "premium_proxy": "true",
            "proxy_country": "de",
            "js_render": "true",
            "js_instructions": """[{"wait":500},{"wait_for":"section.archive__day"}]""",
        },
        "site_elements_patterns": {
            "articles_pattern": (
                "//section[contains(@class, 'archive__day')]//article[contains(@class, 'a-article-teaser')]"
                "//a[contains(@class, 'a-article-teaser__link')]//@href"
            ),
        },
        "scraper_request_params": {
            "premium_proxy": "true",
            "proxy_country": "de",
            "js_render": "true",
            "js_instructions": """[{"wait":500},{"wait_for":"header.a-article-header"}]""",
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
    "presseportal": {
        "site_name": "presseportal",
        "enabled": True,
        "base_url": "https://www.presseportal.de",
        "search_url_templates": [
            "https://www.presseportal.de/blaulicht/nr/50510?startDate={year}-{month}-{day}&endDate={year}-{month}-{day}",
            "https://www.presseportal.de/blaulicht/nr/121243?startDate={year}-{month}-{day}&endDate={year}-{month}-{day}",
            "https://www.presseportal.de/nr/62259?startDate={year}-{month}-{day}&endDate={year}-{month}-{day}",
            "https://www.presseportal.de/nr/171676?startDate={year}-{month}-{day}&endDate={year}-{month}-{day}",
            "https://www.presseportal.de/blaulicht/r/Essen%20-%20Duisburg?startDate={year}-{month}-{day}&endDate={year}-{month}-{day}",
            "https://www.presseportal.de/blaulicht/r/Duisburg?startDate={year}-{month}-{day}&endDate={year}-{month}-{day}",
            "https://www.presseportal.de/r/Duisburg?startDate={year}-{month}-{day}&endDate={year}-{month}-{day}",
        ],
        "scraper_class": NewsArchiveScraper,
        "crawler_request_params": {
            "js_render": "true",
            "js_instructions": """[{"wait":500},{"wait_for":"ul.article-list"}]""",
        },
        "site_elements_patterns": {
            "articles_pattern": "//article[contains(@class, 'news')]//h3[contains(@class, 'news-headline-clamp')]//a/@href",
            "paginator_pattern": "//div[contains(@class, 'pagination')]",
            "active_page_pattern": "//div[contains(@class, 'pagination')]//span[contains(@class, 'active')]",
            "next_page_pattern": "//div[contains(@class, 'pagination')]//span[contains(@class, 'pagination-next')]/@data-url"
        },
        "scraper_request_params": {
            "js_render": "true",
            "js_instructions": """[{"wait":500},{"wait_for":"div.card"}]""",
        },
        "scrape_patterns": {
            "title": {
                "pattern": "//article[contains(@class, 'story')]//h1//text()",
            },
            "description": {
                "pattern": None,
            },
            "raw_date": {
                "pattern": "//article[contains(@class, 'story')]//p[contains(@class, 'date')]//text()",
            },
            "parsed_date": {
                "pattern": "//article[contains(@class, 'story')]//p[contains(@class, 'date')]//text()",
                "parse_func": parse_date,
            },
            "paragraphs": {
                "pattern": "//article[contains(@class, 'story')]//p[not(@class)]//text()",
                "extract_all": True,
            },
        },
        "blacklisted_urls": [],
        "blacklisted_url_patterns": [],
    },
    "rheinischepost": {
        "site_name": "rheinischepost",
        "enabled": True,
        "base_url": "https://rp-online.de",
        "search_url_templates": [
            "https://rp-online.de/nrw/staedte/duisburg/archiv/{year}/{month}/{day}/"
        ],
        "scraper_class": NewsArchiveScraper,
        "crawler_request_params": {
            "js_render": "true",
            "js_instructions": """[{"click":"custom-button#consentAccept"},{"wait":500},{"wait_for":"div.content-list"}]""",
        },
        "site_elements_patterns": {
            "articles_pattern": "//div[contains(@class, 'content-list')]//article//div[@data-teaser-grid]//a/@href",
        },
        "scraper_request_params": {
            "js_render": "true",
            "js_instructions": """[{"click":"custom-button#consentAccept"},{"wait":500},{"wait_for":"article"}]""",
        },
        "scrape_patterns": {
            "title": {
                "pattern": "//article[@data-park-article]//header//span[@data-cy='article_headline']//text()",
            },
            "description": {
                "pattern": "//article[@data-park-article]//p//strong[@data-cy='intro']//text()",
            },
            "raw_date": {
                "pattern": "//article[@data-park-article]//div[@data-cy='date']//text()",
            },
            "parsed_date": {
                "pattern": "//article[@data-park-article]//div[@data-cy='date']//text()",
                "parse_func": parse_date,
            },
            "paragraphs": {
                "pattern": (
                    "//article[@data-park-article]"
                    "//div[@data-cy='article_content']"
                    "//div[@data-cy='article-content-text']"
                    "//p//text()"
                ),
                "extract_all": True,
            },
        },
        "blacklisted_urls": [],
        "blacklisted_url_patterns": [],
    },
    "duisburg-de": {
        "site_name": "duisburg-de",
        "enabled": True,
        "base_url": "https://www.duisburg.de",
        "search_url_templates": [
            (
                "https://www.duisburg.de/allgemein/newsdesk/index_54228.php?"
                "form=newsdeskSearch-1.form&sp%3Afulltext%5B%5D=&sp%3Acategories%5B30338%5D%5B%5D=-"
                "&sp%3Acategories%5B30338%5D%5B%5D=__last__"
                "&sp%3AdateFrom%5B%5D={year}-{month}-{day}"
                "&sp%3AdateTo%5B%5D={year}-{month}-{day}"
                "&action=submit"
            )
        ],
        "scraper_class": NewsArchiveScraper,
        "overwrite_date_if_not_exists": True,
        "crawler_request_params": {
            "js_render": "true",
            "js_instructions": """[{"wait":500},{"wait_for":"div.SP-TeaserList"}]""",
        },
        "site_elements_patterns": {
            "articles_pattern": (
                "//div[contains(@class, 'SP-TeaserList')]"
                "//li[contains(@class, 'SP-TeaserList__item')]"
                "//a[contains(@class, 'SP-Teaser SP-Teaser--textual')]"
                "/@href"
            ),
        },
        "scraper_request_params": {
            "js_render": "true",
            "js_instructions": """[{"wait":500},{"wait_for":"article#SP-Content"}]""",
        },
        "scrape_patterns": {
            "title": {
                "pattern": (
                    "//article[contains(@id, 'SP-Content')]"
                    "//header[contains(@class, 'SP-ArticleHeader')]"
                    "//h1[contains(@class, 'SP-Headline--article')]"
                    "//text()"
                ),
            },
            "description": {
                "pattern": (
                    "//article[contains(@id, 'SP-Content')]"
                    "//div[contains(@class, 'SP-Intro')]"
                    "//p//text()"
                ),
            },
            "raw_date": {
                "pattern": (
                    "//article[contains(@id, 'SP-Content')]"
                    "//div[contains(@class, 'SP-Text')]"
                    "//p//em//text()"
                ),
            },
            "parsed_date": {
                "pattern": (
                    "//article[contains(@id, 'SP-Content')]"
                    "//div[contains(@class, 'SP-Text')]"
                    "//p//em//text()"
                ),
                "parse_func": parse_date,
            },
            "paragraphs": {
                "pattern": (
                    "//article[contains(@id, 'SP-Content')]"
                    "//div[contains(@class, 'SP-Text')]"
                    "//p//text()"
                ),
                "extract_all": True,
            },
        },
        "blacklisted_urls": [],
        "blacklisted_url_patterns": [],
    },
    "lokalklick": {
        "site_name": "lokalklick",
        "enabled": True,
        "base_url": "https://lokalklick.eu",
        "search_url_templates": [
            "https://lokalklick.eu/category/ort/duisburg/",
        ],
        "scraper_class": NewsArchiveScraper,
        "crawler_request_params": {
            "js_render": "true",
            "js_instructions": """[{"wait":500},{"wait_for":"div.td-container"}]""",
        },
        "site_elements_patterns": {
            "articles_pattern": (
                "//div[contains(@class, 'td-container')]"
                "//div[contains(@class, 'td-ss-main-content')]"
                "//div[contains(@class, 'item-details')]"
                "//h3[contains(@class, 'entry-title')]"
                "//a//@href"
            ),
            "paginator_pattern": "//div[contains(@class, 'page-nav')]",
            "active_page_pattern": "//div[contains(@class, 'page-nav')]//span[contains(@class, 'current')]",
            "next_page_pattern": (
                "//div[contains(@class, 'page-nav')]//a//i[contains(@class, 'td-icon-menu-right')]/parent::a/@href"
            ),
        },
        "scraper_request_params": {
            "js_render": "true",
            "js_instructions": """[{"wait":500},{"wait_for":"article.post"}]""",
        },
        "scrape_patterns": {
            "title": {
                "pattern": (
                    "//article[contains(@class, 'post')]"
                    "//div[contains(@class, 'td-post-header')]"
                    "//header[contains(@class, 'td-post-title')]"
                    "//h1[contains(@class, 'entry-title')]"
                    "//text()"
                ),
            },
            "description": {
                "pattern": None,
            },
            "raw_date": {
                "pattern": (
                    "//article[contains(@class, 'post')]"
                    "//div[contains(@class, 'td-post-header')]"
                    "//header[contains(@class, 'td-post-title')]"
                    "//div[contains(@class, 'td-module-meta-info')]"
                    "//time[contains(@class, 'entry-date')]"
                    "//text()"
                ),
            },
            "parsed_date": {
                "pattern": (
                    "//article[contains(@class, 'post')]"
                    "//div[contains(@class, 'td-post-header')]"
                    "//header[contains(@class, 'td-post-title')]"
                    "//div[contains(@class, 'td-module-meta-info')]"
                    "//time[contains(@class, 'entry-date')]"
                    "//text()"
                ),
                "parse_func": parse_date,
            },
            "paragraphs": {
                "pattern": (
                    "//article[contains(@class, 'post')]"
                    "//div[contains(@class, 'td-post-content')]"
                    "/p[not(@class)]//text()"
                ),
                "extract_all": True,
            },
        },
        "blacklisted_urls": [],
        "blacklisted_url_patterns": [],
    },
    "lokalkompass": {
        "site_name": "lokalkompass",
        "enabled": True,
        "base_url": "https://www.lokalkompass.de",
        "search_url_templates": [
            "https://lokalkompass.de/tag/duisburg/",
        ],
        "scraper_class": NewsArchiveScraper,
        "crawler_request_params": {
            "js_render": "true",
            "js_instructions": """[{"wait":500},{"wait_for":"div#content-main"}]""",
        },
        "site_elements_patterns": {
            "articles_pattern": (
                "//div[@id='content-main']"
                "//div[contains(@class, 'article-group-list-loop')]"
                "//article[contains(@class, 'article-list-item')]"
                "//h3[contains(@class, 'article-card-headline')]"
                "//a//@href"
            ),
            "paginator_pattern": "//div[@id='content-main']//ul[contains(@class, 'pagination')]",
            "active_page_pattern": (
                "//div[@id='content-main']"
                "//ul[contains(@class, 'pagination')]"
                "//li[contains(@class, 'current')]"
            ),
            "next_page_pattern": (
                "//div[@id='content-main']"
                "//ul[contains(@class, 'pagination')]"
                "//li//i[contains(@class, 'fa-angle-right')]"
                "/parent::a/@href"
            ),
        },
        "scraper_request_params": {
            "js_render": "true",
            "js_instructions": """[{"wait":500},{"wait_for":"div#content-main"}]""",
        },
        "scrape_patterns": {
            "title": {
                "pattern": (
                    "//div[@role='content']"
                    "//article[contains(@class, 'article-main')]"
                    "//header/h1/text()"
                ),
            },
            "description": {
                "pattern": (
                    "//div[@role='content']"
                    "//article[contains(@class, 'article-main')]"
                    "//div[@id='content-main']"
                    "//div[@data-content-text]"
                    "//p[1]/b/text()"
                ),
            },
            "raw_date": {
                "pattern": (
                    "//div[@role='content']"
                    "//article[contains(@class, 'article-main')]"
                    "//header"
                    "//div[contains(@class, 'article-author')]"
                    "//ul[contains(@class, 'article-meta')]"
                    "/li[1]/text()"
                ),
            },
            "parsed_date": {
                "pattern": (
                    "//div[@role='content']"
                    "//article[contains(@class, 'article-main')]"
                    "//header"
                    "//div[contains(@class, 'article-author')]"
                    "//ul[contains(@class, 'article-meta')]"
                    "/li[1]/text()"
                ),
                "parse_func": parse_date,
            },
            "paragraphs": {
                "pattern": (
                    "//div[@role='content']"
                    "//article[contains(@class, 'article-main')]"
                    "//div[@id='content-main']"
                    "//div[@data-content-text]"
                    "//p//text()"
                    " | "
                    "//div[@role='content']"
                    "//article[contains(@class, 'article-main')]"
                    "//div[@id='content-main']"
                    "//div[@data-content-text]"
                    "//h2//text()"
                ),
                "extract_all": True,
            },
        },
        "blacklisted_urls": [],
        "blacklisted_url_patterns": [],
    },
}
