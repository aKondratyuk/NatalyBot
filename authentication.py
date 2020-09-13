from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from db_models import *


class User(UserMixin):
    id = str()
    username = str()
    password = str()
    role = str()
    privileges = dict()

    def __init__(self, id: str, login: str, password: str,
                 role: str, privileges: dict):
        self.id = id
        self.login = login
        self.password = password
        self.role = role
        self.privileges = privileges

    def __repr__(self):
        return "<{}:{}>".format(self.login, self.password)

    def set_password(self, password: str):
        # Need to add encryption
        self.password = password

    def check_password(self, password: str) -> bool:
        # Need to add encryption
        return self.password == password

    def set_role(self, role: bool):
        # Need to add DB integration
        self.role = role


def find_user(login: str = None,
              user_id: str = None):
    session = Session()

    if user_id:
        db_user_logins = session.query(User).all()['login']
        for db_user_login in db_user_logins:
            if check_password_hash(user_id, login):
                login = db_user_login
        if not login:
            return None
    login, password = session.query(User).filter(login=login).one()
    if login != '':
        user_id = generate_password_hash(login, "sha256", salt_length=8)
        role = session.query(RolesOfUsers).filter(login=login).one()
        role = role['user_role']
        privileges_names = session.query(PrivilegesAssigns).filter(
                user_role=role)
        privileges_names = privileges_names['privilege_name']
        privileges = {
                privilege_name: session.query(Privileges).filter(
                        privilege_name=privilege_name).one()[
                    'privilege_status']
                for privilege_name in privileges_names}
        session.close()
        return User(id=user_id, login=login, password=password,
                    role=role, privileges=privileges)

    return False
