import os

from dotenv import load_dotenv

from config import ROOT_DIR


load_dotenv(ROOT_DIR.joinpath(".env"))

MONGO_HOST = os.getenv('MONGO_HOST')
MONGO_DATABASE = 'insightfinder-dev'
MONGO_COLLECTION = 'content'
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ZENROWS_API_KEY = os.getenv('ZENROWS_API_KEY')


WEBSITES = {
    "spiegel": {
        "base_url": "https://www.spiegel.de",
        "enabled": False,
    },
    "handelsblatt": {
        "base_url": "https://www.handelsblatt.com",
        "enabled": True,
    },
    "tagesschau": {
        "base_url": "https://www.tagesschau.de",
        "enabled": True,
    }
}

CRAWL_CONFIGS = {
    "spiegel": {
        "search_url_template": "https://www.spiegel.de/nachrichtenarchiv/artikel-{date}.html",
        "date_format": "%d.%m.%Y",
        "request_params": {
        },
        "articles_pattern": """//section[@data-area="article-teaser-list"]//div[@data-block-el="articleTeaser"]//a/@href""",
    },
    "handelsblatt": {
        "search_url_template": "https://www.handelsblatt.com/archiv/?date={date}",
        "date_format": "%Y-%m-%d",
        "request_params": {
            # "premium_proxy": "true",
            # "proxy_country": "de",
            "js_render": "true",
            "js_instructions": """[{"click":".selector"},{"wait":500},{"fill":[".input","value"]},{"wait_for":".slow_selector"}]""",
        },
        "articles_pattern": "//app-default-teaser//a/@href",
    },
    "tagesschau": {
        "search_url_template": "https://www.tagesschau.de/archiv?datum={date}",
        "date_format": "%Y-%m-%d",
        "request_params": {
        },
        "articles_pattern": """//div[@class="copytext-element-wrapper__vertical-only"]//div[contains(@class, "teaser-right")][not(.//span[contains(@class, "label") and (contains(., 'podcast') or contains(., 'liveblog'))])]//div[@class="teaser-right__teaserheadline"]//a/@href""",
    },
}

SCRAPE_CONFIGS = {
    "spiegel": {
        "request_params": {
            "premium_proxy": "true",
            "proxy_country": "de",
            "js_render": "true",
            "js_instructions": """[{"click":".selector"},{"wait":500},{"fill":[".input","value"]},{"wait_for":".slow_selector"}]""",
        },
        "extract_patterns": {
            "title": """//main[@id='Inhalt']//article//header//h2//span[contains(@class, 'leading-tight')]//span//text()""",
            "description": """//main[@id='Inhalt']//article//header//div[contains(@class, 'RichText') and contains(@class, 'leading-loose')]//text()""",
            "date": """//main[@id='Inhalt']//article//header//time[@class='timeformat']//text()""",
            "paragraphs": """//main[@id='Inhalt']//article//section//div[@data-sara-click-el='body_element']//div[contains(@class, 'RichText')]//p//text()""",
        },
    },
    "handelsblatt": {
        "request_params": {
            "premium_proxy": "true",
            "proxy_country": "de",
            "js_render": "true",
            "js_instructions": """[{"click":".selector"},{"wait":500},{"fill":[".input","value"]},{"wait_for":".slow_selector"}]""",
        },
        "extract_patterns": {
            "title": "//app-header-content-headline//h2/text()",
            "description": "//app-header-content-lead-text/text()",
            "date": "//app-story-date/text()",
            "paragraphs": "//app-storyline-elements//app-storyline-paragraph//p//text()",
        },
    },
    "tagesschau": {
        "request_params": {
        },
        "extract_patterns": {
            "title": """//main[contains(@class, 'content-wrapper')]//div[@class='seitenkopf__title']//h1[@class='seitenkopf__headline']//span[@class='seitenkopf__headline--text']//text()""",
            "description": """//main[contains(@class, 'content-wrapper')]//p[contains(@class, 'textabsatz')]//strong//text()""",
            "date": """//main[contains(@class, 'content-wrapper')]//div[@class='seitenkopf__title']//p[@class='metatextline']//text()""",
            "paragraphs": """//main[contains(@class, 'content-wrapper')]//p[contains(@class, 'textabsatz')]//text() | //main[contains(@class, 'content-wrapper')]//div[contains(@class, 'columns')]//h2[@class='meldung__subhead']//text()""",
        },
    },
    "default": {

    },
}
