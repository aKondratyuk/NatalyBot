import logging
from datetime import datetime
from typing import List

from .dbcontext import Session
from .models import Dialogue, Account
from .queries import *


class DialogueService:
    def __init__(self, session: Session):
        self.session = session

    def record_dialogue(self,
                        dialogue_id: str,
                        sender_id: str,
                        send_time: datetime,
                        viewed: bool,
                        sender_message: str,
                        receiver_id: str):
        if len(self.session.query(Dialogue).filter_by(dialogue_id=dialogue_id).all()):
            logging.info(f"Entity with id {dialogue_id} already exists")
        else:
            dialogue = Dialogue(dialogue_id=dialogue_id,
                                sender_id=sender_id,
                                send_time=send_time,
                                viewed=viewed,
                                sender_message=sender_message,
                                receiver_id=receiver_id)

            logging.info(f"Recording entity: {dialogue}")
            self.session.add(dialogue)
            self.session.commit()

    def __del__(self):
        self.session.close()


class AccountService:
    def __init__(self, session: Session):
        self.session = session

    def fetch_accounts(self) -> List[Account]:
        proxies = self.session.query(Account).all()
        return [Account(account_id=proxy.account_id,
                        account_password=proxy.account_password) for proxy in proxies]

    def record_account(self,
                       account_id: str,
                       account_password: str):
        if len(self.session.query(Dialogue).filter_by(account_id=account_id).all()):
            logging.info(f"Entity with id {account_id} already exists")

        else:
            account = Account(account_id=account_id,
                              account_password=account_password)

            logging.info(f"Recording entity: {account}")
            self.session.add(account)
            self.session.commit()

    def __del__(self):
        self.session.close()


def create_tables():
    session = Session()
    session.execute(CREATE_TABLES_QUERY)

    session.commit()
    session.close()


def drop_tables():
    session = Session()
    session.execute(DROP_TABLES_QUERY)

    session.commit()
    session.close()
