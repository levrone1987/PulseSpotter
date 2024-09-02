from typing import Optional, Callable, Dict, List

from pydantic import BaseModel, ConfigDict


class ZenrowsRequestParams(BaseModel):
    model_config = ConfigDict(frozen=True)
    block_resource: Optional[str] = None
    premium_proxy: Optional[str] = None
    proxy_country: Optional[str] = None
    js_render: Optional[str] = "false"
    js_instructions: Optional[str] = None


class SiteElementsPatterns(BaseModel):
    model_config = ConfigDict(frozen=True)
    topics_urls_pattern: Optional[str] = None
    must_exist_pattern: Optional[str] = None
    articles_pattern: Optional[str] = None
    paginator_pattern: Optional[str] = None
    active_page_pattern: Optional[str] = None
    next_page_pattern: Optional[str] = None


class ScrapePattern(BaseModel):
    model_config = ConfigDict(frozen=True)
    pattern: Optional[str] = None
    extract_all: bool = False
    parse_func: Optional[Callable] = None


ScrapePatterns = Dict[str, ScrapePattern]


class NewsScraperParams(BaseModel):
    model_config = ConfigDict(frozen=True)
    site_name: str
    base_url: str
    crawler_request_params: ZenrowsRequestParams
    site_elements_patterns: SiteElementsPatterns
    scraper_request_params: ZenrowsRequestParams
    scrape_patterns: ScrapePatterns
    blacklisted_urls: Optional[list] = []
    blacklisted_url_patterns: Optional[list] = []


class NewsArchiveScraperParams(NewsScraperParams):
    search_url_templates: List[str]
    overwrite_date_if_not_exists: Optional[bool] = False
