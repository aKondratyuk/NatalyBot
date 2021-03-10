import logging

from datetime import datetime
from aiopg.sa import create_engine
from sqlalchemy.sql import select

from .dbconnection import *
from .dbcontext import dialogue_table, account_table, metadata


async def record_dialogue_async(dialogue_id: str,
                                sender_id: str,
                                send_time: datetime,
                                viewed: bool,
                                sender_message: str,
                                receiver_id: str):
    async with create_engine(DSN) as engine:
        async with engine.acquire() as connection:
            query = select(dialogue_table).where(dialogue_table.c.dialogue_id == dialogue_id)
            existing_entity = await connection.execute(query)

            if existing_entity.fetchone():
                logging.info(f"Entity with id {dialogue_id} already exists")
            else:
                logging.info(f"Recording entity: {dialogue_id}")
                await connection.execute(dialogue_table.insert(), [
                    {
                        'dialogue_id': dialogue_id,
                        'sender_id': sender_id,
                        'send_time': send_time,
                        'viewed': viewed,
                        'sender_message': sender_message,
                        'receiver_id': receiver_id
                    }
                ])


async def fetch_all_accounts_async():
    async with create_engine(user=USERNAME,
                             database=DATABASE,
                             host=HOST,
                             password=PASSWORD) as engine:
        async with engine.acquire() as connection:
            accounts = await connection.execute(select(account_table))

    return accounts


async def create_tables_async():
    async with create_engine(user=USERNAME,
                             database=DATABASE,
                             host=HOST,
                             password=PASSWORD) as engine:
        await metadata.create_all(engine)
