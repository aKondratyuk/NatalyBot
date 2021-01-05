# coding: utf8
from flask_login import UserMixin
from sqlalchemy import update
from werkzeug.security import check_password_hash, generate_password_hash

from db_models import *


class User(UserMixin):
    id = str()
    login = str()
    password = str()
    role = list()
    privileges = dict()
    ip = str()

    def __init__(self, user_id: str, login: str, password: str,
                 role: list, privileges: dict, ip: str):
        self.id = user_id
        self.login = login
        self.password = password
        self.role = role
        self.privileges = privileges
        self.ip = ip

    def __repr__(self):
        return "<{}:{}>".format(self.login, self.password)

    def set_password(self, password: str):
        session = Session()
        self.password = generate_password_hash(password,
                                               "sha256",
                                               salt_length=8)

        update_q = update(Users).where(Users.login == self.login). \
            values(password=self.password)
        session.execute(update_q)
        session.close()

    def check_password(self, password: str) -> bool:
        # Need to add encryption
        return check_password_hash(self.password, password)

    def set_role(self, role: bool):
        # Need to add DB integration
        self.role = role


def find_user(login: str = None,
              user_id: str = None):
    from control_panel import db_get_rows_2
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
        user = session.query(Users).filter(Users.login == login).all()
        if len(user) == 0:
            return None
        user = user[0]
        login = user.login
        password = user.user_password
        user_id = generate_password_hash(login, "sha256", salt_length=8)

        """query = session.query(RolesOfUsers, PrivilegesAssigns)
        query = query.outerjoin(
                UserRoles,
                UserRoles.user_role == RolesOfUsers.user_role)
        query = query.outerjoin(
                PrivilegesAssigns,
                PrivilegesAssigns.user_role == UserRoles.user_role)
        query = query.filter(RolesOfUsers.login == login)
        q_result = query.all()"""
        user_roles = db_get_rows_2([RolesOfUsers.user_role],
                                   [RolesOfUsers.login == login])
        role = [role[0] for role in user_roles]

        user_privileges = db_get_rows_2([PrivilegesAssigns.privilege_name,
                                         PrivilegesAssigns.privilege_status],
                                        [PrivilegesAssigns.user_role.in_(
                                            role)])
        """if len(q_result) == 0:
            role, privileges = [], {}
        elif q_result[0][1]:
            role = [row[0].user_role for row in q_result]
            privileges = {row[1].privilege_name: row[1].privilege_status
                          for row in q_result}
        else:
            role = [row[0].user_role for row in q_result]
            privileges = {}"""

        privileges = {privilege[0]: privilege[1]
                      for privilege in user_privileges}

        session.close()
        if request.environ['REMOTE_ADDR']:
            user_ip = request.environ['REMOTE_ADDR']
        else:
            hostname = socket.gethostname()
            user_ip = socket.gethostbyname(hostname)
        return User(user_id=user_id, login=login,
                    password=password, role=role,
                    privileges=privileges, ip=user_ip)
    return None
