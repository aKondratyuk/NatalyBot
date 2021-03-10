from sqlalchemy import MetaData, Table, Column, String,\
    DateTime, Boolean, Text, ForeignKey

metadata = MetaData()
account_table = Table('Account',
                      metadata,
                      Column('account_id', String(10), primary_key=True),
                      Column('account_password', String(50), nullable=False))

dialogue_table = Table('Dialogue',
                       metadata,
                       Column('dialogue_id', String(10), primary_key=True),
                       Column('sender_id', String(10), nullable=False),
                       Column('send_time', DateTime, nullable=False),
                       Column('viewed', Boolean, nullable=False),
                       Column('sender_message', Text, nullable=False),
                       Column('receiver_id', None, ForeignKey('Account.account_id')))
