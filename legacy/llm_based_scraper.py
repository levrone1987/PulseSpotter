import json
import logging
from datetime import datetime

import scrapy

from bs4 import BeautifulSoup, Comment, Tag
from pymongo import MongoClient
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import DATA_DIR
from core.llm import extract_news_article_text
from web_scraping.web_scraping.items import NewsContent
from web_scraping.web_scraping.spider_config import MONGO_URI, MONGO_DATABASE, MONGO_COLLECTION


def clean_html(soup_element):
    if isinstance(soup_element, Comment):
        soup_element.extract()
        return
    if hasattr(soup_element, 'find_all'):
        # Remove style and script tags
        blacklisted_elements = ['head', 'style', 'script', 'footer', 'nav', 'noscript', 'table']
        for element in soup_element.find_all(blacklisted_elements):
            element.decompose()

        # Additionally remove elements containing 'nav' or 'menu' in their tag name
        blacklisted_patterns = [
            'nav', 'menu', 'image', 'img', 'button', 'btn', 'footer', 'table', 'breadcrumb', 'swipe', 'slide',
            'video', 'banner',
        ]
        for element in soup_element.find_all(lambda tag: any([x in tag.name for x in blacklisted_patterns])):
            element.decompose()

        # Remove comments
        for comment in soup_element.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # Remove all attributes
        if hasattr(soup_element, 'attrs'):
            soup_element.attrs = {}

        # Process children first
        children = list(soup_element.children)
        for child in children:
            clean_html(child)

        # Remove unnecessary nesting
        if len(soup_element.contents) == 1 and isinstance(soup_element.contents[0], Tag):
            child = soup_element.contents[0]
            if not child.attrs and len(child.contents) == 1 and isinstance(child.contents[0], Tag):
                grandchild = child.contents[0]
                if grandchild.text.strip():
                    soup_element.replace_with(grandchild)
                else:
                    soup_element.replace_with(child)

        # Remove empty elements after children are processed
        if soup_element.name:
            # Check if element has no text and no non-empty children
            non_empty_children = [child for child in soup_element.children if
                                  not (isinstance(child, str) and not child.strip())]
            if not soup_element.text.strip() and not non_empty_children:
                soup_element.decompose()


class LLMBasedScraper(scrapy.Spider):
    name = 'llm_based_scraper'
    custom_settings = {
        'LOG_LEVEL': 'INFO',
    }

    def __init__(self, *args, **kwargs):
        super(LLMBasedScraper, self).__init__(*args, **kwargs)

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

            # # update item in the database
            # self.collection.update_one(
            #     {'_id': doc['_id']},
            #     {
            #         '$set': {
            #             'visited': True,
            #             'title': content["title"],
            #             'description': content["description"],
            #             'published_date': content["published_date"],
            #             'full_text': content["full_text"],
            #         }
            #     },
            # )

    def extract_content(self, url: str):
        logging.info(f"Processing URL: {url}")
        self.driver.get(url)

        # Wait for paragraphs to be present
        self.wait.until(EC.presence_of_all_elements_located((By.XPATH, '//app-storyline-elements')))
        sel = Selector(text=self.driver.page_source)

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        clean_html(soup)
        cleaned_html_content = soup.prettify()

        outfile = url.split("/")[-1]
        out_path = DATA_DIR.joinpath(outfile)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        json.dump(cleaned_html_content, open(out_path, "w"))

        # todo: send this to gpt-4 to retrieve the content
        return

    def closed(self, reason):
        logging.info("Closing Selenium WebDriver.")
        self.driver.quit()
        self.mongo_client.close()
