import json

from scrapy.crawler import CrawlerProcess
from crawlers.natashaclub import NatashaclubSpider


def start_crawling():
    crawler_settings = json.loads(open('.env/creds.json').read())
    user_profiles = crawler_settings['profiles']

    if 'save_json' in crawler_settings:
        process = CrawlerProcess(settings={
            "FEEDS": {"profiles.json": {"format": "json"}},
            'CONCURRENT_REQUESTS': crawler_settings['concurrent_requests'],
            'CONCURRENT_REQUESTS_PER_DOMAIN': crawler_settings['concurrent_requests'],
            'CONCURRENT_REQUESTS_PER_IP': crawler_settings['concurrent_requests'],
            'RANDOMIZE_DOWNLOAD_DELAY': 0,
            'DOWNLOAD_DELAY': 0
        })
    else:
        process = CrawlerProcess(settings={
            'CONCURRENT_REQUESTS': crawler_settings['concurrent_requests'],
            'CONCURRENT_REQUESTS_PER_DOMAIN': crawler_settings['concurrent_requests'],
            'CONCURRENT_REQUESTS_PER_IP': crawler_settings['concurrent_requests'],
            'RANDOMIZE_DOWNLOAD_DELAY': 0,
            'DOWNLOAD_DELAY': 0
        })

    for profile in user_profiles:
        process.crawl(NatashaclubSpider,
                      auth_id=profile['auth_id'],
                      auth_password=profile['auth_password'],
                      show_new_messages=crawler_settings['show_new_messages'],
                      save_db=crawler_settings['save_db'],
                      save_json=crawler_settings['save_json'])

    process.start()


if __name__ == "__main__":
    start_crawling()
