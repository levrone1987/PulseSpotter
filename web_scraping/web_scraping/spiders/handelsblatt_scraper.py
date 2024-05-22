import logging
from datetime import datetime

import scrapy
from pymongo import MongoClient
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..items import NewsContent
from ..spider_config import MONGO_URI, MONGO_DATABASE, MONGO_COLLECTION


class HandelsblattScraper(scrapy.Spider):
    name = 'handelsblatt_scraper'
    custom_settings = {
        'LOG_LEVEL': 'INFO',
    }

    def __init__(self, *args, **kwargs):
        super(HandelsblattScraper, self).__init__(*args, **kwargs)

        # setup selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(options=chrome_options)
        logging.info("Selenium WebDriver initialized.")
        self.wait = WebDriverWait(self.driver, 10)  # Adjust the timeout as necessary

        # Initialize MongoDB connection
        self.mongo_client = MongoClient(MONGO_URI)
        self.db = self.mongo_client[MONGO_DATABASE]
        self.collection = self.db[MONGO_COLLECTION]
        logging.info("MongoDB client initialized.")

    def start_requests(self):
        for doc in self.collection.find({'visited': False}):
            url = doc['url']
            content = self.extract_content(url)

            # update item in the database
            self.collection.update_one(
                {'_id': doc['_id']},
                {
                    '$set': {
                        'visited': True,
                        'title': content["title"],
                        'description': content["description"],
                        'published_date': content["published_date"],
                        'full_text': content["full_text"],
                    }
                },
            )

    def extract_content(self, url: str):
        logging.info(f"Processing URL: {url}")
        self.driver.get(url)

        # Wait for paragraphs to be present
        self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//app-storyline-elements')))
        sel = Selector(text=self.driver.page_source)

        # extract content
        title = sel.xpath('//app-header-content-headline//h2/text()').get().strip()
        short_description = sel.xpath('//app-header-content-lead-text/text()').get().strip()
        raw_date = sel.xpath('//app-story-date/text()').get().strip()
        raw_date = ' '.join(raw_date.split(' ')[:3])
        formatted_date = datetime.strptime(raw_date, "%d.%m.%Y - %H:%M").strftime("%Y-%m-%d %H:%M:%S")
        paragraphs = sel.xpath('//app-storyline-elements//app-storyline-paragraph//p//text()').getall()
        full_text = ' '.join(paragraphs)

        return NewsContent(
            title=title,
            description=short_description,
            published_date=formatted_date,
            full_text=full_text
        )

    def closed(self, reason):
        logging.info("Closing Selenium WebDriver.")
        self.driver.quit()
        self.mongo_client.close()
