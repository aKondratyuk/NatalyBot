from uuid import uuid4

from sqlalchemy import update
from werkzeug.security import check_password_hash, generate_password_hash

from app import logger
from authentication import User
from db_models import Invites, RolesOfUsers, SentInvites, Session, Users


def create_invite(creator: User,
                  invited_email: str,
                  role: str):
    session = Session()
    invite = Invites(invite_id=uuid4().bytes)
    new_user = Users(login=invited_email,
                     user_password=generate_password_hash(
                             invite.invite_id,
                             "sha256",
                             salt_length=8))

    new_user_role = RolesOfUsers(login=invited_email,
                                 user_role=role)
    sent_invite_from = SentInvites(invite_id=invite.invite_id,
                                   login=creator.login)
    sent_invite_to = SentInvites(invite_id=invite.invite_id,
                                 login=new_user.login)
    session.add(invite)
    session.add(new_user)
    session.commit()

    session.add(new_user_role)
    session.commit()

    session.add(sent_invite_from)
    session.add(sent_invite_to)
    session.commit()
    session.close()


def create_user(login: str,
                user_password: str,
                role: str = 'default'):
    session = Session()
    new_user = Users(login=login,
                     user_password=generate_password_hash(
                             user_password,
                             "sha256",
                             salt_length=8))
    session.add(new_user)
    session.commit()
    new_user_role = RolesOfUsers(login=new_user.login,
                                 user_role=role)
    session.add(new_user_role)
    session.commit()
    session.close()
    logger.info(f'User {login} successful created')


def register_user(login: str,
                  user_password: str):
    session = Session()
    users = session.query(Users).filter(Users.login == login).all()
    if len(users) == 0:
        logger.info(f'User signup with wrong e-mail: {login}')
        return None
    db_invites = session.query(Invites).all()
    for db_invite in db_invites:
        print(db_invite.invite_id)
        print(type(db_invite.invite_id))
        if check_password_hash(user_password, db_invite.invite_id):
            update_q = update(Users).where(
                    Users.login == login). \
                values(user_password=generate_password_hash(
                    user_password,
                    "sha256",
                    salt_length=8))
            session.add(update_q)
            session.commit()
            session.close()
            logger.info(f'User {login} successful registered '
                        f'with invite_id: {db_invite.invite_id}')
            return None

    logger.info(f'User signup with e-mail: {login}, '
                f'but this account already exists')
    return 'Such account already exists'
