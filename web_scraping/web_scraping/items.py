# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NewsContent(scrapy.Item):
    title = scrapy.Field()
    description = scrapy.Field()
    published_date = scrapy.Field()
    full_text = scrapy.Field()

