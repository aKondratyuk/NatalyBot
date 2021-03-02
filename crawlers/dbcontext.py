from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dbconnection import *

connection_string = '{base}://{user}:{pw}@{host}:{port}/{db}'.format(
    base=BASE, user=USERNAME, pw=PASSWORD,
    host=HOST, port=PORT, db=DATABASE
)

DBEngine = create_engine(connection_string)
Session = sessionmaker(bind=DBEngine)

ModelBase = declarative_base()
session = Session()
