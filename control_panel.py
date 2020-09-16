from uuid import uuid4

from werkzeug.security import generate_password_hash

from authentication import User
from db_models import Invites, SentInvites, Session, Users


def create_invite(creator: User,
                  invited_email: str):
    session = Session()
    invite = Invites(invite_id=uuid4().bytes)
    new_user = Users(login=invited_email,
                     user_password=generate_password_hash(
                             invite.invite_id,
                             "sha256",
                             salt_length=8))

    sent_invite_from = SentInvites(invite_id=invite.invite_id,
                                   login=creator.login)
    sent_invite_to = SentInvites(invite_id=invite.invite_id,
                                 login=new_user.login)
    session.add(invite)
    session.add(new_user)
    session.commit()
    session.add(sent_invite_from)
    session.add(sent_invite_to)
    print(session)
    session.commit()
    session.close()


def create_user(login: str,
                user_password: str):
    session = Session()
    new_user = Users(login=login,
                     user_password=generate_password_hash(
                             user_password,
                             "sha256",
                             salt_length=8))
    session.add(new_user)
    session.commit()
    session.close()
