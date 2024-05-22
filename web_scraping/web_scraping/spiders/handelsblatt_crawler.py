import logging

import scrapy
from pymongo import MongoClient
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..spider_config import SPIDER_CONFIG, MONGO_URI, MONGO_COLLECTION, MONGO_DATABASE
from ..spider_utils import get_page_number


class HandelsblattCrawler(scrapy.Spider):
    name = 'handelsblatt_crawler'
    custom_settings = {
        'LOG_LEVEL': 'INFO',
    }
    start_urls = SPIDER_CONFIG.get(name, {}).get('start_urls', [])

    def __init__(self, *args, **kwargs):
        super(HandelsblattCrawler, self).__init__(*args, **kwargs)
        self._spider_configs = SPIDER_CONFIG.get(self.name, {})
        self._start_url_max_pages = self._spider_configs.get('max_pages')

        # setup selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=chrome_options)
        logging.info("Selenium WebDriver initialized.")
        self.wait = WebDriverWait(self.driver, 10)

        # Initialize MongoDB connection
        self.mongo_client = MongoClient(MONGO_URI)
        self.db = self.mongo_client[MONGO_DATABASE]
        self.collection = self.db[MONGO_COLLECTION]
        logging.info("MongoDB client initialized.")

    def parse(self, response, **kwargs):
        logging.info(f"Processing URL: {response.url}")
        self.driver.get(response.url)

        # wait for app-default-teaser elements to be present
        self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//app-default-teaser')))
        sel = Selector(text=self.driver.page_source)

        # extract links
        links = sel.xpath('//app-default-teaser//a/@href').getall()
        logging.info(f"Found {len(links)} articles.")

        current_page = get_page_number(response.url)
        for link in links:
            full_url = response.urljoin(link)
            if not self.collection.find_one({'url': full_url}):
                self.collection.insert_one({'url': full_url, 'visited': False})

        # stop scraping if we're at the final page
        if self._start_url_max_pages is not None and current_page >= self._start_url_max_pages:
            logging.info(f'Stopping proces. - maximum number of pages visited.')
            return

        # otherwise find and follow the next page link
        next_page = sel.xpath('//a[@title="Nächste Seite"]/@href').get()
        if next_page:
            next_page_url = response.urljoin(next_page)
            logging.info(f'Following next page: {next_page_url}')
            yield scrapy.Request(next_page_url, callback=self.parse)

    def closed(self, reason):
        logging.info("Closing Selenium WebDriver.")
        self.driver.quit()
        self.mongo_client.close()
