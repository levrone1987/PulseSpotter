from scrapy import cmdline


if __name__ == '__main__':
    # cmdline.execute("scrapy crawl handelsblatt_crawler".split())
    # cmdline.execute("scrapy crawl handelsblatt_scraper".split())
    cmdline.execute("scrapy crawl llm_based_scraper".split())
    pass
