# coding: utf8
import re
from datetime import datetime
from math import ceil
from uuid import uuid4

from flask_login import current_user
from sqlalchemy import exc, inspect, update
from werkzeug.security import check_password_hash, generate_password_hash

from authentication import User
from db_models import ChatSessions, Chats, Invites, Messages, Profiles, \
    RolesOfUsers, SentInvites, Session, Texts, Users
from scraping import get_parsed_page, send_request
from verification import login, profile_in_inbox


def create_invite(creator: User,
                  invited_email: str,
                  role: str) -> bool:
    from main import logger
    db_session = Session()
    invite = Invites(invite_id=uuid4().bytes)

    # new user creating
    new_user = Users(login=invited_email,
                     user_password=generate_password_hash(
                             invite.invite_id,
                             "sha256",
                             salt_length=8))
    # assign role to user
    new_user_role = RolesOfUsers(login=invited_email,
                                 user_role=role)
    # create invite from user
    sent_invite_from = SentInvites(invite_id=invite.invite_id,
                                   login=creator.login)
    # create invite to user
    sent_invite_to = SentInvites(invite_id=invite.invite_id,
                                 login=new_user.login)

    # database duplicate check
    users = db_get_users(Users.login == invited_email)
    if len(users) > 0:
        # user already created
        if users[0]['register_status']:
            # user already registered
            logger.info(f'User {current_user.login} '
                        f'tried to create invite for '
                        f'already registered user: {invited_email}')
            return False
        if users[0]['role'] != role:
            # user role another from db role
            update_q = update(RolesOfUsers).where(
                    RolesOfUsers.login == invited_email). \
                values(user_role=role)
            db_session.execute(update_q)
            db_session.commit()
            logger.info(f'User {current_user.login} '
                        f'update role for unregistered user: {invited_email}')

        logger.info(f'User {current_user.login} '
                    f'resend invite to: {invited_email}')
        return True
    else:
        # no user in DB
        db_session.add(invite)
        db_session.commit()
        db_session.add(new_user)
        db_session.commit()
        db_session.add(new_user_role)
        db_session.commit()
        db_session.add(sent_invite_from)
        db_session.add(sent_invite_to)
        db_session.commit()
        db_session.close()
        logger.info(f'created invite for e-mail: {invited_email}')
        return True


def create_user(login: str,
                user_password: str,
                role: str = 'default'):
    from main import logger
    session = Session()
    new_user = Users(login=login,
                     user_password=generate_password_hash(
                             user_password,
                             "sha256",
                             salt_length=8))
    try:
        session.add(new_user)
        session.commit()
    except exc.IntegrityError:
        session.rollback()
        logger.error(f"{current_user.login} get IntegrityError because "
                     f"user with such parameters already exists:\n"
                     f"login = {login}"
                     f"password = {user_password}"
                     f"role = {role}")
        return False
    new_user_role = RolesOfUsers(login=new_user.login,
                                 user_role=role)
    try:
        session.add(new_user_role)
        session.commit()
    except exc.IntegrityError:
        session.rollback()
        logger.error(f"{current_user.login} get IntegrityError because "
                     f"user {login} already has {role} role")
        return False
    session.close()
    logger.info(f'User {login} successfully created')
    return True


def register_user(login: str,
                  user_password: str):
    from main import logger

    db_session = Session()
    users = db_session.query(Users).filter(Users.login == login).all()
    test = inspect(Invites)
    if len(users) == 0:
        logger.info(f'User signup with wrong e-mail: {login}')
        return None
    db_invites = db_session.query(Invites).all()
    for db_invite in db_invites:
        if check_password_hash(users[0].user_password, db_invite.invite_id):
            invite_id = db_invite.invite_id
            update_q = update(Users).where(
                    Users.login == login). \
                values(user_password=generate_password_hash(
                    user_password,
                    "sha256",
                    salt_length=8))
            db_session.execute(update_q)
            db_session.commit()
            db_session.close()
            logger.info(f'User {login} successful registered '
                        f'with invite_id: {invite_id}')
            return None

    db_session.close()
    logger.info(f'User signup with e-mail: {login}, '
                f'but this account already exists')
    return 'Such account already exists'


def text_format(text: str):
    # deleting wrong new string
    text = re.sub(r' {3,}', '', text)
    # deleting new string character duplicate
    text = re.sub(r'\n+\W', '', text)
    return text


def get_message_text(session,
                     message_url: str):
    # get message text from link
    response = send_request(session=session,
                            method="POST",
                            link="https://www.natashaclub.com/" + message_url)
    message_page = get_parsed_page(response)
    message_text = message_page.find('td',
                                     class_='table').text
    message_text = text_format(message_text)
    return message_text


def db_message_create(chat_id: bytes,
                      send_time,
                      viewed: bool,
                      sender: str,
                      text: str) -> bool:
    db_session = Session()
    text_id = uuid4().bytes
    message_id = uuid4().bytes
    msg_text = Texts(text_id=text_id,
                     text=text)
    db_session.add(msg_text)
    db_session.commit()
    message = Messages(message_token=message_id,
                       chat_id=chat_id,
                       text_id=text_id,
                       send_time=send_time,
                       viewed=viewed,
                       profile_id=sender)
    db_session.add(message)
    db_session.commit()
    db_session.close()
    return True


def db_chat_create(observer_login: str,
                   observer_pass: str,
                   target_profile_id: str) -> bytes:
    # chat session require profiles in database
    # check profiles in database
    sender_profile = Profiles(profile_id=observer_login,
                              profile_password=observer_pass,
                              available=True,
                              can_receive=True)
    db_session = Session()
    # check if sender profile exists in database
    profiles = db_session.query(Profiles).filter(
        Profiles.profile_id == sender_profile.profile_id).all()
    if len(profiles) == 0:
        db_session.add(sender_profile)
        db_session.commit()
    # check receiver profile in database
    profiles = db_session.query(Profiles).filter(
        Profiles.profile_id == target_profile_id).all()
    if len(profiles) == 0:
        target_profile = Profiles(profile_id=target_profile_id,
                                  can_receive=True,
                                  available=True)
        db_session.add(target_profile)
        db_session.commit()

    # finding chat id for this users
    # find all chats with sender
    sub_query_1 = db_session.query(ChatSessions.chat_id). \
        filter(ChatSessions.profile_id == observer_login).subquery()
    # find all chats with receiver
    sub_query_2 = db_session.query(ChatSessions.chat_id). \
        filter(ChatSessions.profile_id == target_profile_id).subquery()
    # find chat from sender to receiver
    query = db_session.query(ChatSessions). \
        filter(ChatSessions.chat_id.in_(sub_query_1)). \
        filter(ChatSessions.chat_id.in_(sub_query_2))
    chat_sessions = query.all()

    # if chat found, we return chat_id
    if len(chat_sessions) != 0:
        db_session.close()
        return chat_sessions[0].chat_id

    # if chat not found, we create chat and chat session
    chat_id = uuid4().bytes
    new_chat = Chats(chat_id=chat_id)
    db_session.add(new_chat)
    db_session.commit()
    chat_session_1 = ChatSessions(chat_id=chat_id,
                                  profile_id=observer_login)
    db_session.close()
    db_session = Session()
    db_session.add(chat_session_1)
    db_session.commit()
    chat_session_2 = ChatSessions(chat_id=chat_id,
                                  profile_id=target_profile_id)
    db_session.add(chat_session_2)
    db_session.commit()
    db_session.close()
    return chat_id


def db_chat_length_check(chat_id: bytes,
                         total_msg: int,
                         sender_id: str) -> int:
    # return count of new messages, which not presented in database
    db_session = Session()
    messages = db_session.query(Messages).filter(
        Messages.chat_id == chat_id).filter(
        Messages.profile_id == sender_id)
    db_session.close()
    return total_msg - len(messages.all())


def dialog_page_upload(current_profile_session,
                       data: dict,
                       page: int,
                       open_msg_count: int,
                       chat_id: bytes,
                       sender_id: str,
                       inbox: bool,
                       download_new: bool = False):
    data['page'] = page

    if inbox:
        link = "https://www.natashaclub.com/inbox.php"
    else:
        link = "https://www.natashaclub.com/outbox.php"
    response = send_request(
        session=current_profile_session, method="GET",
        link=link + "?page={page}&"
                    "filterID={filterID}&"
                    "filterPPage={filterPPage}".format(**data))
    inbox_page = get_parsed_page(response)

    messages = [tr for tr in
                inbox_page.find_all('tr', class_='table')]
    messages = list(map(lambda x: [td for td in x.find_all('td')],
                        messages))
    messages = [col for col in messages if len(col) == 5 - int(not inbox)]

    for i in range(len(messages)):
        # if need to download less messages than exists on page
        if i == open_msg_count:
            break
        text_time = messages[i][3 - int(not inbox)].text
        time = datetime.strptime(text_time, " %Y-%m-%d %H:%M:%S ")
        text_preview = messages[i][4 - int(not inbox)].text
        message_url = messages[i][4 - int(not inbox)].find('a')["href"]
        if inbox:
            viewed = not messages[i][1 - int(not inbox)].contents[1]['src'] \
                         == '/templates/tmpl_nc/images_nc/new.gif'
        elif download_new:
            viewed = True
        else:
            viewed = not messages[i][1 - int(not inbox)].text == '\nNot read'

        if viewed or download_new:
            text = get_message_text(session=current_profile_session,
                                    message_url=message_url)
        else:
            text = text_preview
        db_message_create(chat_id=chat_id,
                          send_time=time,
                          viewed=viewed,
                          sender=sender_id,
                          text=text)


def dialog_download(observer_login: str,
                    observer_password: str,
                    sender_id: str,
                    receiver_profile_id: str,
                    download_new: bool = False) -> bool:
    """Отправка сообщения
    Keyword arguments:
    session -- сессия залогиненого аккаунта
    profile_id -- ID профиля которого мы ищем в Inbox
    """
    # Ищем в Inbox сообщение профиля
    data = {
            "page": "1",
            "filterID": receiver_profile_id,
            "filterPPage": "20"
            }

    current_profile_session, profile_id = login(
            profile_login=observer_login,
            password=observer_password)
    total_msg, new_msg = profile_in_inbox(
            session=current_profile_session,
            profile_id=receiver_profile_id,
            inbox=sender_id == receiver_profile_id)
    if total_msg == 0:
        return False
    chat_id = bytes(
            (bytearray(
                    db_chat_create(
                            observer_login=observer_login,
                            observer_pass=observer_password,
                            target_profile_id=receiver_profile_id))))

    db_new_msg_count = db_chat_length_check(chat_id=chat_id,
                                            total_msg=total_msg,
                                            sender_id=sender_id)
    if db_new_msg_count <= 0:
        # when database have messages that have been deleted in site
        pass
    if db_new_msg_count == 0:
        # when database already has this dialog with all messages
        return False

    last_page = ceil(db_new_msg_count / int(data['filterPPage']))
    open_msg_count = db_new_msg_count
    if sender_id == receiver_profile_id:
        inbox = True
    elif sender_id == observer_login:
        inbox = False
    else:
        return False
    for page in range(1, last_page + 1):
        dialog_page_upload(current_profile_session=current_profile_session,
                           data=data,
                           page=page,
                           open_msg_count=open_msg_count,
                           chat_id=chat_id,
                           sender_id=sender_id,
                           inbox=inbox,
                           download_new=download_new)
        open_msg_count -= int(data['filterPPage'])
    # function has added new messages
    return True


def db_show_dialog(sender: str,
                   receiver: str) -> list:
    # you can swap sender and receiver
    """Returns list of dicts, with messages in dialogue for admin panel"""
    db_session = Session()

    # subquery for chats with sender
    sub_query_1 = db_session.query(ChatSessions.chat_id). \
        filter(ChatSessions.profile_id == sender).subquery()
    # subquery for chats with receiver
    sub_query_2 = db_session.query(ChatSessions.chat_id). \
        filter(ChatSessions.profile_id == receiver).subquery()
    # subquery for chats with this users
    query_chat = db_session.query(ChatSessions.chat_id). \
        filter(ChatSessions.chat_id.in_(sub_query_1)). \
        filter(ChatSessions.chat_id.in_(sub_query_2)). \
        subquery()
    # query to show messages and texts
    query = db_session.query(Messages.profile_id,
                             Messages.send_time,
                             Messages.viewed,
                             Texts.text)
    query = query.filter(Messages.chat_id.in_(query_chat))
    query = query.outerjoin(Texts, Messages.text_id == Texts.text_id)
    query = query.order_by(Messages.send_time)
    result = query.all()
    db_session.close()
    return [{"profile_id": row[0],
             "send_time": row[1],
             "viewed": row[2],
             "text": row[3]} for row in result]


def db_download_new_msg(observer_login: str,
                        observer_password: str,
                        sender_id: str,
                        receiver_profile_id: str) -> bool:
    # find chat in db to delete new messages
    chat_id = db_chat_create(observer_login=observer_login,
                             observer_pass=observer_password,
                             target_profile_id=receiver_profile_id)
    db_session = Session()
    msg_delete = db_session.query(Messages). \
        filter(Messages.chat_id == chat_id). \
        filter(Messages.viewed is False)
    msg_delete.delete()  # return number of deleted msg
    db_session.commit()
    db_session.close()
    dialog_download(observer_login=observer_login,
                    observer_password=observer_password,
                    sender_id=sender_id,
                    receiver_profile_id=receiver_profile_id,
                    download_new=True)
    return True


def db_show_receivers(sender: str) -> list:
    # you can swap sender and receiver
    """Returns list of dicts, with messages in dialogue for admin panel"""
    db_session = Session()

    # subquery for chats with sender
    sub_query_1 = db_session.query(ChatSessions.chat_id). \
        filter(ChatSessions.profile_id == sender).subquery()
    # subquery for chats with this users
    query = db_session.query(ChatSessions.profile_id). \
        filter(ChatSessions.chat_id.in_(sub_query_1)). \
        filter(ChatSessions.profile_id != sender)
    # query to show messages and texts
    receivers = query.all()
    db_session.close()
    return [{"profile_id": row[0]} for row in receivers]


def db_change_user_role(user_login: str, role: str):
    db_session = Session()
    update_q = update(RolesOfUsers).where(
        RolesOfUsers.login == user_login). \
        values(user_role=role)
    db_session.execute(update_q)
    db_session.commit()
    db_session.close()

    return None


def db_get_users(*statements) -> list:
    db_session = Session()
    query = db_session.query(
            Users.login,
            Users.user_password,
            SentInvites.invite_id,
            RolesOfUsers.user_role)
    query = query.outerjoin(SentInvites,
                            Users.login == SentInvites.login)
    query = query.outerjoin(RolesOfUsers,
                            Users.login == RolesOfUsers.login)
    query = query.group_by(Users.login)
    query = query.filter(Users.login != 'anonymous')
    query = query.filter(Users.login != 'server')
    for statement in statements:
        query = query.filter(statement != '')
    users = query.all()
    users = [{
            "login": user[0],
            "register_status": not check_password_hash(user[1], user[2]),
            "role": user[3]
            }
            for user in users
            ]
    db_session.close()
    return users


def db_get_profiles(*args) -> list:
    db_session = Session()
    query = db_session.query(
            Profiles.profile_id,
            Profiles.profile_password,
            Profiles.available,
            Profiles.can_receive,
            Profiles.msg_limit,
            Profiles.profile_type)
    for statement in args:
        query = query.filter(statement != '')
    profiles = query.all()
    profiles = [{
            "profile_id": profile[0],
            "profile_password": profile[1],
            "available": profile[2],
            "can_receive": profile[3],
            "msg_limit": profile[4],
            "profile_type": profile[5]
            }
            for profile in profiles
            ]
    db_session.close()
    return profiles


def db_get_rows(tables: list,
                *statements) -> list:
    db_session = Session()
    query = db_session.query(*tables)
    for statement in statements:
        query = query.filter(statement != '')
    result = query.all()
    db_session.close()
    return result


def db_duplicate_check(tables: list,
                       *statements) -> bool:
    result_rows = db_get_rows(tables, *statements)
    if len(result_rows) > 0:
        return True
    else:
        return False


"""print(db_show_dialog('1000868043',
                     '1001716782'))"""
"""print(db_get_users())"""
"""print(create_invite(creator='admin@gmail.com',
                    invited_email='test@gmail.com',
                    role='admin'))"""
"""print(db_download_new_msg("1000868043",
                          "SWEETY777",
                          "1001485714",
                          "1001485714"))"""
"""print(dialog_download("1000868043",
                      "SWEETY777",
                      "1001485714",
                      "1001485714"))"""
