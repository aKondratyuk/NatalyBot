import logging
from datetime import datetime
from typing import List

from dbcontext import Session, DBEngine
from models import Dialogue, Account
from sqlalchemy import text


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


class AccountService:
    def __init__(self, session: Session):
        self.session = session

    def fetch_accounts(self) -> List[Account]:
        proxies = self.session.query(Account).all()
        return [Account(account_id=proxy.account_id,
                        account_password=proxy.account_password) for proxy in proxies]


def create_tables():
    logging.info("Creating missing table infrastructure")
    table_creation_script = text(open('scripts/create.sql').read())
    DBEngine.execute(table_creation_script)


def drop_tables():
    logging.info("Dropping table infrastructure")
    table_creation_script = text(open('scripts/drop.sql').read())
    DBEngine.execute(table_creation_script)
