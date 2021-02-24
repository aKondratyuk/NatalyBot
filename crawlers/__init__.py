from scrapy.crawler import CrawlerProcess
from crawlers.natashaclub import NatashaclubSpider


def start_crawler(**kwargs):
    """
    Launches messages crawler directly from a script

    :Keyword Arguments:
        * *auth_id* (``str``) --
          Account login
        * *auth_password* (``str``) --
          Account password
        * *concurrent_requests* (``int``) --
          Crawler simultaneous worker count
        * *save_json* (``str``) --
          (Optional) Option for crawler to store collected records in JSON file
        * *save_json* (``str``) --
          (Optional) Option for crawler to store collected records in JSON file
    """

    if 'save_json' in kwargs:
        process = CrawlerProcess(settings={
            "FEEDS": {kwargs['save_json']: {"format": "json"}}
        })
    else:
        process = CrawlerProcess()

    process.crawl(NatashaclubSpider, **kwargs)
    process.start()
