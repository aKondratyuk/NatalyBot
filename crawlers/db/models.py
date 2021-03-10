from sqlalchemy import Column, VARCHAR, DATETIME, BOOLEAN, ForeignKey

from .dbcontext import ModelBase


class Account(ModelBase):
    __tablename__ = 'Account'

    account_id = Column(VARCHAR(10), primary_key=True)
    account_password = Column(VARCHAR(50), nullable=False)

    def __repr__(self):
        return "<Account(account_id='%s', account_password='%s')>" % (self.account_id, self.account_password)


class Dialogue(ModelBase):
    __tablename__ = 'Dialogue'

    dialogue_id = Column(VARCHAR(10), primary_key=True)
    sender_id = Column(VARCHAR(10), nullable=False)
    send_time = Column(DATETIME, nullable=False)
    viewed = Column(BOOLEAN, default=0, nullable=False)
    sender_message = Column(VARCHAR(10000), nullable=False)

    receiver_id = Column(VARCHAR(10), ForeignKey('Account.account_id'))

    def __repr__(self):
        return "<Dialogue(dialogue_id='%s', send_time='%s', " \
               "viewed='%s', sender_message='%s', " \
               "receiver_id='%s', sender_id='%s')>" % (
                       self.dialogue_id, self.send_time,
                       self.viewed, self.sender_message,
                       self.receiver_id, self.sender_id)
