import asyncio
import threading
from crawler import Crawler


async def main_event_loop():
    c = Crawler(show_new_messages=True,
                save_db=False)

    await c.index()


def crawler_fire_and_forget_in_loop(master_loop):
    asyncio.set_event_loop(master_loop)

    try:
        master_loop.run_until_complete(main_event_loop())
    finally:
        master_loop.run_until_complete(master_loop.shutdown_asyncgens())
        master_loop.close()


def crawler_fire_and_forget():
    loop = asyncio.get_event_loop()

    crawler_thread = threading.Thread(target=crawler_fire_and_forget_in_loop,
                                      args=(loop,))

    crawler_thread.start()
    crawler_thread.join()


if __name__ == '__main__':
    crawler_fire_and_forget()
