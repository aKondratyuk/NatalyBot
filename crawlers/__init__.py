import os

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
        * *save_db* (``bool``) --
          (Optional) Option for crawler to store collected records in SQL Server
    """

    if 'save_json' in kwargs:
        process = CrawlerProcess(settings={
            "FEEDS": {kwargs['save_json']: {"format": "json"}}
        })
    else:
        process = CrawlerProcess()

    process.crawl(NatashaclubSpider, **kwargs)
    process.start()


if __name__ == "__main__":
    start_crawler(auth_id=os.getenv('VAR_AUTH_ID'),
                  auth_password=os.getenv('VAR_AUTH_PASSWORD'),
                  show_new_messages=os.getenv('VAR_NEW_MESSAGES') == 'True',
                  concurrent_requests=int(os.getenv('VAR_CONCURRENT_REQUESTS')),
                  save_db=os.getenv('VAR_SAVE_DB') == 'True')
