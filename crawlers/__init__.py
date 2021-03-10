import asyncio

from db.dbcontext import metadata
from db.services import fetch_all_accounts_async, create_tables_async


async def main():
    await create_tables_async()
    accounts = await fetch_all_accounts_async()
    print(accounts)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
print("Sync!")
