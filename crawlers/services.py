from datetime import datetime

from dbcontext import Session, DBEngine
from models import Dialogue

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
        dialogue = Dialogue(dialogue_id=dialogue_id,
                            sender_id=sender_id,
                            send_time=send_time,
                            viewed=viewed,
                            sender_message=sender_message,
                            receiver_id=receiver_id)
        self.session.add(dialogue)
        self.session.commit()


class AccountService:
    def __init__(self, session: Session):
        self.session = session


def create_tables():
    table_creation_script = text(open('scripts/create.sql').read())
    DBEngine.execute(table_creation_script)


def drop_tables():
    table_creation_script = text(open('scripts/drop.sql').read())
    DBEngine.execute(table_creation_script)
