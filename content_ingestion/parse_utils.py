from scrapy import Selector

from content_ingestion.data_models import ScrapePattern, ScrapePatterns


def parse_pattern(selector: Selector, pattern: ScrapePattern):
    if pattern.extract_all:
        response = selector.xpath(pattern.pattern).getall()
    else:
        response = selector.xpath(pattern.pattern).get()
    if pattern.parse_func:
        response = pattern.parse_func(response)
    return response


def parse_website(page_source: str, extract_patterns: ScrapePatterns) -> dict | None:
    sel = Selector(text=page_source)
    response = {}
    for field, pattern in extract_patterns.items():
        response[field] = parse_pattern(sel, pattern)
    return response
