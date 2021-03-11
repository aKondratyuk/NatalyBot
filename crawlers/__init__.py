import asyncio
import threading

from crawler import Crawler
from db import AccountService, Session, create_tables


async def crawl_single(**kwargs):
    worker = Crawler(**kwargs)
    await worker.index()


async def main_event_loop(delay: float):
    service = AccountService(Session())
    accounts = service.fetch_accounts()

    await asyncio.sleep(delay)
    await asyncio.gather(*[
        crawl_single(auth_id=account.account_id,
                     auth_password=account.account_password,
                     show_new_messages=False,
                     save_db=True) for account in accounts
    ])


def crawler_fire_and_forget_in_loop(master_loop, delay: float):
    asyncio.set_event_loop(master_loop)

    try:
        master_loop.run_until_complete(main_event_loop(delay))
    finally:
        master_loop.run_until_complete(master_loop.shutdown_asyncgens())
        master_loop.close()


def crawler_fire_and_forget(delay: float):
    loop = asyncio.get_event_loop()

    crawler_thread = threading.Thread(target=crawler_fire_and_forget_in_loop,
                                      args=(loop, delay,))

    crawler_thread.start()
    crawler_thread.join()


if __name__ == '__main__':
    create_tables()
    crawler_fire_and_forget(delay=0.0)
