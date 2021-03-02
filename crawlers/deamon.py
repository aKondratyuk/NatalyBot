from scrapy.crawler import CrawlerProcess
from natashaclub import NatashaclubSpider
from services import create_tables, AccountService
from dbcontext import session


def start_crawling(**kwargs):
    account_service = AccountService(session)
    accounts = account_service.fetch_accounts()

    if 'save_json' in kwargs:
        process = CrawlerProcess(settings={
            "FEEDS": {"profiles.json": {"format": "json"}},
            'CONCURRENT_REQUESTS': kwargs['concurrent_requests'],
            'CONCURRENT_REQUESTS_PER_DOMAIN': kwargs['concurrent_requests'],
            'CONCURRENT_REQUESTS_PER_IP': kwargs['concurrent_requests'],
            'RANDOMIZE_DOWNLOAD_DELAY': 0,
            'DOWNLOAD_DELAY': 0
        })
    else:
        process = CrawlerProcess(settings={
            'CONCURRENT_REQUESTS': kwargs['concurrent_requests'],
            'CONCURRENT_REQUESTS_PER_DOMAIN': kwargs['concurrent_requests'],
            'CONCURRENT_REQUESTS_PER_IP': kwargs['concurrent_requests'],
            'RANDOMIZE_DOWNLOAD_DELAY': 0,
            'DOWNLOAD_DELAY': 0
        })

    for account in accounts:
        process.crawl(NatashaclubSpider,
                      auth_id=account.account_id,
                      auth_password=account.account_password,
                      show_new_messages=kwargs['show_new_messages'],
                      save_db=kwargs['save_db'],
                      save_json=kwargs['save_json'])

    process.start()


if __name__ == "__main__":
    create_tables()
    start_crawling(show_new_messages=False,
                   concurrent_requests=5,
                   save_db=True,
                   save_json=False)
