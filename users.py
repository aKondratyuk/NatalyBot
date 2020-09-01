from bson.objectid import ObjectId
from flask_login import UserMixin

from database import Ench_col, db

users_col = Ench_col(db.Users)


class User(UserMixin):
    id = str()
    username = str()
    password = str()
    admin = False

    def __init__(self, iterator):
        self.id = iterator['_id']
        self.username = iterator['username']
        self.password = iterator['password']
        self.admin = iterator['admin']

    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)

    def set_password(self, password: str):
        self.password = password

    def check_password(self, password: str) -> bool:
        return self.password == password

    def get_admin(self) -> bool:
        try:
            return bool(self.admin)
        except AttributeError:
            raise NotImplementedError('No `admin` attribute - override `get_admin`')

    def set_admin(self, admin: bool):
        self.admin = admin


def find_user(username: str):
    if db.Users.find_one({'username': username}):
        return User(db.Users.find_one({'username': username}))
    return False


def find_user_id(id: str):
    if db.Users.find_one({'_id': ObjectId(id)}):
        return User(db.Users.find_one({'_id': ObjectId(id)}))
