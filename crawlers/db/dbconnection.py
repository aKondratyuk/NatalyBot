import os

BASE = 'postgresql+psycopg2'
USERNAME = os.getenv('VAR_USERNAME')
PASSWORD = os.getenv('VAR_PASSWORD')
HOST = os.getenv('VAR_HOST')
PORT = '5432'
DATABASE = os.getenv('VAR_DATABASE')

DSN = '{base}://{user}:{pw}@{host}:{port}/{db}'.format(
    base=BASE, user=USERNAME, pw=PASSWORD,
    host=HOST, port=PORT, db=DATABASE
)
