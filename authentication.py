from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from db_models import *


class User(UserMixin):
    id = str()
    username = str()
    password = str()
    role = str()
    privileges = dict()

    def __init__(self, user_id: str, login: str, password: str,
                 role: list, privileges: dict):
        self.user_id = user_id
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
        db_users = session.query(Users).all()
        for db_user in db_users:
            if check_password_hash(user_id, db_user.login):
                login = db_user.login
                break
        if not login:
            return None
    if login:
        user = session.query(Users).filter(Users.login == login).one()
        login = user.login
        password = user.user_password
        user_id = generate_password_hash(login, "sha256", salt_length=8)

        query = session.query(RolesOfUsers, Privileges)
        query = query.outerjoin(
                UserRoles,
                UserRoles.user_role == RolesOfUsers.user_role)
        query = query.outerjoin(
                PrivilegesAssigns,
                PrivilegesAssigns.user_role == UserRoles.user_role)
        query = query.outerjoin(
                Privileges,
                Privileges.privilege_name == PrivilegesAssigns.privilege_name)
        query = query.filter(RolesOfUsers.login == login)
        q_result = query.all()
        if len(q_result) == 0:
            role, privileges = [], {}
        elif len(q_result) == 1:
            role = [row[0].user_role for row in q_result]
            privileges = {}
        else:
            role = [row[0].user_role for row in q_result]
            privileges = {row[1].privilege_name: row[1].privilege_status
                          for row in q_result}

        session.close()
        return User(user_id=user_id, login=login, password=password,
                    role=role, privileges=privileges)
    return False
