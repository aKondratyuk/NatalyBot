from uuid import uuid4
from sqlalchemy import Column, create_engine, MetaData
from sqlalchemy.dialects.mysql import BINARY, BOOLEAN, TIMESTAMP, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DB_ADDRESS = "mysql:3306"
DB_DIALECT = "mysql"
DB_DRIVER = "pymysql"
DB_ENCODING = "charset=utf8"
DB_NAME = "matchlov_nataly_schema"
DB_PASS = "Vi3mMe170z"
DB_USER = "matchlov_admin"
PYTHONUNBUFFERED = 1

engine = create_engine(f"{DB_DIALECT}+"
                       f"{DB_DRIVER}://"
                       f"{DB_USER}:"
                       f"{DB_PASS}@"
                       f"{DB_ADDRESS}/"
                       f"{DB_NAME}"
                       f"?{DB_ENCODING}",
                       pool_recycle=3600,
                       encoding='utf8',
                       echo=True)

Base = declarative_base()
Session = sessionmaker()
meta = MetaData()
Session.configure(bind=engine)
meta.create_all(engine)

logger_db_session = Session()


class Messages(Base):
    __tablename__ = 'Messages'
    message_token = Column(BINARY(16), primary_key=True)
    chat_id = Column(BINARY(16))
    profile_id = Column(VARCHAR(20))
    send_time = Column(TIMESTAMP)
    text_id = Column(BINARY(16))
    viewed = Column(BOOLEAN, default=0)
    delay = Column(BOOLEAN, default=0)

    def __repr__(self):
        return "<Messages(message_token='%s', chat_id='%s', " \
               "profile_id='%s', send_time='%s', " \
               "text_id='%s', viewed='%s', " \
               "delay='%s')>" % (
                       self.message_token, self.chat_id,
                       self.profile_id, self.send_time,
                       self.text_id, self.viewed,
                       self.delay)


class Texts(Base):
    __tablename__ = 'Texts'
    text_id = Column(BINARY(16), primary_key=True)
    text = Column(VARCHAR(10000))

    def __repr__(self):
        return "<Texts(text_id='%s', text='%s')>" % (
                self.text_id, self.text[:100] + '...')


def db_message_create(db_session: Session,
                      chat_id: bytes,
                      send_time,
                      viewed: bool,
                      sender: str,
                      text: str,
                      delay: bool = False):
    text_id = uuid4().bytes
    message_id = uuid4().bytes
    msg_text = Texts(text_id=text_id,
                     text=text)
    db_session.add(msg_text)
    db_session.commit()

    new_message = Messages(message_token=message_id,
                           chat_id=chat_id,
                           text_id=text_id,
                           send_time=send_time,
                           viewed=viewed,
                           profile_id=sender,
                           delay=delay)
    db_session.add(new_message)
    db_session.commit()
