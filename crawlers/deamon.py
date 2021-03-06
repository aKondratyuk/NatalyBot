from datetime import timedelta
from datetime import datetime
from twisted.internet import reactor, task
from twisted.internet.defer import inlineCallbacks
from scrapy.crawler import CrawlerRunner, Settings
from natashaclub import NatashaclubSpider
from services import create_tables, AccountService
from dbcontext import session


def register_end():
    print("Crawler finished job on: " + datetime.now().strftime("%H:%M:%S"))


@inlineCallbacks
def crawl_job(**kwargs):
    print("Crawler started job on: " + datetime.now().strftime("%H:%M:%S"))

    create_tables()
    account_service = AccountService(session)
    accounts = account_service.fetch_accounts()

    if 'save_json' in kwargs and kwargs['save_json'] is True:
        settings = Settings(values={
            "FEEDS": {"profiles.json": {"format": "json"}},
            'CONCURRENT_REQUESTS': kwargs['concurrent_requests'],
            'CONCURRENT_REQUESTS_PER_DOMAIN': kwargs['concurrent_requests'],
            'CONCURRENT_REQUESTS_PER_IP': kwargs['concurrent_requests'],
            'RANDOMIZE_DOWNLOAD_DELAY': 0,
            'DOWNLOAD_DELAY': 0
        })
    else:
        settings = Settings(values={
            'CONCURRENT_REQUESTS': kwargs['concurrent_requests'],
            'CONCURRENT_REQUESTS_PER_DOMAIN': kwargs['concurrent_requests'],
            'CONCURRENT_REQUESTS_PER_IP': kwargs['concurrent_requests'],
            'RANDOMIZE_DOWNLOAD_DELAY': 0,
            'DOWNLOAD_DELAY': 0
        })

    runner = CrawlerRunner(settings)

    for account in accounts:
        yield runner.crawl(NatashaclubSpider,
                           auth_id=account.account_id,
                           auth_password=account.account_password,
                           show_new_messages=kwargs['show_new_messages'],
                           save_db=kwargs['save_db'],
                           save_json=kwargs['save_json'])

    return register_end()


loop = task.LoopingCall(crawl_job,
                        show_new_messages=True,
                        concurrent_requests=5,
                        save_db=True,
                        save_json=False)


def schedule_crawl(delay: timedelta):
    loop.start(delay.seconds)


def main():
    reactor.run()
