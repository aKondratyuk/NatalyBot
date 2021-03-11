import asyncio
import threading

from .crawler import Crawler
from .db import AccountService, session


async def crawl_single(**kwargs):
    worker = Crawler(**kwargs)
    await worker.index()


async def main_event_loop(delay: float, show_new_messages: bool):
    service = AccountService(session)
    accounts = service.fetch_accounts()

    await asyncio.sleep(delay)
    await asyncio.gather(*[
        crawl_single(auth_id=account.account_id,
                     auth_password=account.account_password,
                     show_new_messages=show_new_messages,
                     save_db=True) for account in accounts
    ])


def crawler_fire_and_forget_in_loop(master_loop, delay: float, show_new_messages: bool):
    asyncio.set_event_loop(master_loop)

    try:
        master_loop.run_until_complete(main_event_loop(delay, show_new_messages))
    finally:
        master_loop.run_until_complete(master_loop.shutdown_asyncgens())
        master_loop.close()


def crawler_fire_and_forget(delay: float, join_after_complete=False, show_new_messages=True):
    loop = asyncio.get_event_loop()
    crawler_thread = threading.Thread(target=crawler_fire_and_forget_in_loop,
                                      args=(loop, delay, show_new_messages,))
    crawler_thread.start()

    if join_after_complete:
        crawler_thread.join()