# coding: utf8
import re
from datetime import datetime, timedelta
from math import ceil
from threading import Thread
from time import time
from uuid import UUID, uuid4

from flask_login import current_user
from sqlalchemy import desc, exc, update
from werkzeug.security import check_password_hash, generate_password_hash

from authentication import User
from db_models import Categories, CategoryLevel, ChatSessions, Chats, \
    Invites, \
    Levels, MessageAnchors, MessageTemplates, Messages, ProfileCategories, \
    ProfileDescription, ProfileLanguages, Profiles, RolesOfUsers, \
    SentInvites, \
    Session, Tagging, Texts, UsedAnchors, UserRoles, Users, Visibility
from messaging import create_message_response
from scraping import collect_info_from_profile, get_id_profiles, \
    get_parsed_page, search_for_profiles, send_request
from verification import check_for_filter, login, profile_deleted, \
    profile_in_inbox


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
        if users[0]['role'] == 'deleted':
            db_session = Session()
            # create new invite id
            db_session.add(invite)
            db_session.commit()
            # create new users-invite link
            db_session.add(sent_invite_from)
            db_session.add(sent_invite_to)
            db_session.commit()
            # change password from deleted to new, based on invite_id
            update_q = update(Users).where(
                    Users.login == invited_email). \
                values(user_password=new_user.user_password)
            db_session.execute(update_q)
            db_session.commit()
            db_session.close()
            # reload users, for next checks
            users = db_get_users(Users.login == invited_email)
        # user already created
        if users[0]['register_status']:
            # user already registered
            logger.info(f'User {current_user.login} '
                        f'tried to create invite for '
                        f'already registered user: {invited_email}')
            return False
        if users[0]['role'] != role:
            # user role another from db role
            # check user role is valid
            query = db_session.query(UserRoles).filter(
                    UserRoles.user_role == role
                    )
            if len(query.all()) == 0:
                return False
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

    role = db_session.query(RolesOfUsers.user_role).filter(
            RolesOfUsers.login == login).all()
    if role[0][0] == 'deleted':
        logger.info(f'User signup with e-mail: {login}, '
                    f'but this account deleted')
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
                      text: str,
                      delay: bool = False) -> bool:
    db_session = Session()
    text_id = uuid4().bytes
    message_id = uuid4().bytes
    msg_text = Texts(text_id=text_id,
                     text=text)
    db_session.add(msg_text)
    db_session.commit()
    new_message = Messages(message_token=message_id,
                           chat_id=chat_id,
                           text_id=text_id,
                           send_time=send_time,
                           viewed=viewed,
                           profile_id=sender,
                           delay=delay)
    db_session.add(new_message)
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
                    download_new: bool = False,
                    account_session=None) -> bool:
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
    if not account_session:
        account_session, profile_id = login(
                profile_login=observer_login,
                password=observer_password)

    total_msg, new_msg = profile_in_inbox(
            session=account_session,
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
        dialog_page_upload(current_profile_session=account_session,
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


def get_account_nickname_from_dialog(message_token: bytes):
    """Return account nickname from message token"""
    result = db_get_rows([ProfileDescription.nickname],
                         Messages.message_token == message_token,
                         Messages.chat_id == ChatSessions.chat_id,
                         ChatSessions.profile_id == Visibility.profile_id,
                         Visibility.login == current_user.login,
                         Profiles.profile_id == ChatSessions.profile_id,
                         ProfileDescription.profile_id == Profiles.profile_id,
                         Profiles.profile_password)
    return result[0][0]


"""def db_show_dialog(sender: str = None,
                   receiver: str = None,
                   email_filter: bool = False,
                   inbox_filter: bool = False,
                   outbox_filter: bool = False,
                   descending: bool = False) -> list:
    # you can swap sender and receiver
    Returns list of dicts, with messages in dialogue for admin panel
    db_session = Session()

    # Check visibility of profiles for current user
    sub_query_0 = db_session.query(ChatSessions.chat_id). \
        filter(ChatSessions.profile_id == Visibility.profile_id). \
        filter(Visibility.login == current_user.login)
    # subquery for chats with this profiles
    query_chat = db_session.query(ChatSessions.chat_id). \
        filter(ChatSessions.chat_id.in_(sub_query_0))
    if sender:
        # subquery for chats with sender
        sub_query_1 = db_session.query(ChatSessions.chat_id). \
            filter(ChatSessions.profile_id == sender).subquery()
        # subquery for chats with this profiles
        query_chat = db_session.query(ChatSessions.chat_id). \
            filter(ChatSessions.chat_id.in_(sub_query_1))
    if receiver:
        # subquery for chats with receiver, if we have receiver id
        sub_query_2 = db_session.query(ChatSessions.chat_id). \
            filter(ChatSessions.profile_id == receiver).subquery()
        # subquery for chats with this profiles
        query_chat = query_chat. \
            filter(ChatSessions.chat_id.in_(sub_query_2))
    # filter only email dialogues
    if email_filter:
        query_chat = query_chat.filter(
                ChatSessions.email_address)
    query_chat = query_chat.subquery()
    # query to find accounts which have dialog
    find_account_query = db_session.query(ChatSessions.profile_id). \
        filter(ChatSessions.chat_id.in_(sub_query_0)). \
        filter(Profiles.profile_id == ChatSessions.profile_id). \
        filter(Profiles.profile_password != '').subquery()

    # QUERY FOR MESSAGES
    # query to show messages and texts
    query = db_session.query(Messages.profile_id,
                             Messages.send_time,
                             Messages.viewed,
                             Texts.text,
                             ProfileDescription.nickname,
                             Messages.message_token)
    query = query.filter(Messages.chat_id.in_(query_chat))
    query = query.outerjoin(Texts, Messages.text_id == Texts.text_id)
    query = query.filter(ProfileDescription.profile_id == Messages.profile_id)
    if inbox_filter:
        # show only inbox messages
        query = query.filter(Messages.profile_id.notin_(find_account_query))
    elif outbox_filter:
        # show only inbox messages
        query = query.filter(Messages.profile_id.in_(find_account_query))

    # sorting
    if descending:
        query = query.order_by(desc(Messages.send_time))
    else:
        query = query.order_by(Messages.send_time)

    # QUERY FOR ACCOUNTS
    # query to show messages and texts
    query_a = db_session.query(Messages.message_token)
    query_a = query_a.filter(Messages.chat_id.in_(query_chat))
    query_a = query_a.outerjoin(Texts, Messages.text_id == Texts.text_id)
    query_a = query_a.filter(
            ProfileDescription.profile_id == Messages.profile_id)
    if inbox_filter:
        # show only inbox messages
        query_a = query_a.filter(
                Messages.profile_id.notin_(find_account_query))
    elif outbox_filter:
        # show only inbox messages
        query_a = query_a.filter(Messages.profile_id.in_(find_account_query))
    query_a = query_a.order_by(Messages.send_time).subquery()
    # final query to link messages with accounts
    accounts = db_session.query(ProfileDescription.nickname,
                                ProfileDescription.profile_id,
                                Messages.message_token
                                )
    accounts = accounts. \
        filter(ChatSessions.chat_id == Messages.chat_id). \
        filter(ChatSessions.profile_id == Profiles.profile_id). \
        filter(ProfileDescription.profile_id == Profiles.profile_id). \
        filter(Profiles.profile_password != '')
    accounts = accounts.join(
            query_a,
            Messages.message_token == query_a.c.message_token)

    result_accounts = accounts.all()
    result = query.all()
    db_session.close()
    return [{"profile_id": result[i][0],
             "send_time": result[i][1],
             "viewed": result[i][2],
             "text": result[i][3],
             "nickname": result[i][4],
             "message_token": result[i][5],
             "account_nickname": result_accounts[i][0],
             "account_id": result_accounts[i][1]
             } for i in range(len(result))]


def db_show_dialog_2(sender: str = None,
                     receiver: str = None) -> list:

    # find chats with receiver and with sender
    chats_with_sender = db_get_rows_2([ChatSessions.chat_id],
                                      [ChatSessions.profile_id == sender])
    chats_with_receiver = db_get_rows_2([ChatSessions.chat_id],
                                      [ChatSessions.profile_id == receiver])
    messages = db_get_rows([
            Messages.profile_id,
            Messages.send_time,
            Messages.viewed,
            Texts.text,
            ProfileDescription.nickname,
            Messages.message_token
            ],
            [
            Messages.text_id == Texts.text_id,
            Messages.chat_id == chats_with_sender,
            Messages.chat_id == chats_with_receiver,
            Messages.profile_id == ProfileDescription.profile_id
            ])
    return messages"""


def db_show_dialog(sender: str,
                   receiver: str = None,
                   email_filter: bool = False,
                   inbox_filter: bool = False,
                   outbox_filter: bool = False,
                   descending: bool = False) -> list:
    # you can swap sender and receiver
    """Returns list of dicts, with messages in dialogue for admin panel"""
    db_session = Session()

    # subquery for chats with sender
    sub_query_1 = db_session.query(ChatSessions.chat_id). \
        filter(ChatSessions.profile_id == sender)
    # subquery for chats with this profiles
    query_chat = db_session.query(ChatSessions.chat_id). \
        filter(ChatSessions.chat_id.in_(sub_query_1))

    if receiver:
        # subquery for chats with receiver, if we have receiver id
        sub_query_2 = db_session.query(ChatSessions.chat_id). \
            filter(ChatSessions.profile_id == receiver)
        # subquery for chats with this profiles
        query_chat = query_chat. \
            filter(ChatSessions.chat_id.in_(sub_query_2))
    # filter only email dialogues
    if email_filter:
        query_chat = query_chat.filter(
                ChatSessions.email_address)
    query_chat = query_chat.subquery()

    # query to show messages and texts
    query = db_session.query(Messages.profile_id,
                             Messages.send_time,
                             Messages.viewed,
                             Texts.text,
                             ProfileDescription.nickname,
                             Messages.message_token,
                             Messages.delay)
    query = query.filter(Messages.chat_id.in_(query_chat))
    query = query.outerjoin(Texts, Messages.text_id == Texts.text_id)
    query = query.filter(ProfileDescription.profile_id == Messages.profile_id)

    if inbox_filter or not receiver:
        # show only inbox messages
        query = query.filter(Messages.profile_id != sender)
    elif outbox_filter:
        # show only inbox messages
        query = query.filter(Messages.profile_id != receiver)
    # sorting
    if descending:
        query = query.order_by(desc(Messages.send_time))
    else:
        query = query.order_by(Messages.send_time)

    query = query.order_by(Messages.send_time)
    result = query.all()
    db_session.close()
    return [{"profile_id": row[0],
             "send_time": row[1],
             "viewed": row[2],
             "text": row[3],
             "nickname": row[4],
             "message_token": row[5],
             "delay": row[6]
             } for row in result]


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
        filter(Messages.viewed == False)
    msg_delete.delete()  # return number of deleted msg
    db_session.commit()
    db_session.close()
    dialog_download(observer_login=observer_login,
                    observer_password=observer_password,
                    sender_id=sender_id,
                    receiver_profile_id=receiver_profile_id,
                    download_new=True)
    dialog_download(observer_login=observer_login,
                    observer_password=observer_password,
                    sender_id=receiver_profile_id,
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
    query = query.filter(RolesOfUsers.user_role != 'deleted')
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
    """Select all rows from tables list,
    which have been filtered with 'statements'"""
    db_session = Session()
    query = db_session.query(*tables)
    for statement in statements:
        query = query.filter(statement != '')
    result = query.all()
    db_session.close()
    return result


def db_get_rows_2(tables: list,
                  statements: list = None,
                  order_by: list = None,
                  descending: bool = False,
                  limit: int = None,
                  return_query: bool = False) -> list:
    """Select all rows from tables list,
    which have been filtered with 'statements'"""
    db_session = Session()
    query = db_session.query(*tables)
    if statements:
        for statement in statements:
            query = query.filter(statement != '')
    if order_by:
        for sort in order_by:
            if descending:
                query = query.order_by(sort.desc())
            else:
                query = query.order_by(sort)
    if limit:
        query = query.limit(limit)
    if return_query:
        db_session.close()
        return query
    result = query.all()
    db_session.close()
    return result


def db_delete_rows_2(tables: list,
                     statements: list = None,
                     order_by: list = None,
                     descending: bool = False,
                     limit: int = None,
                     return_query: bool = False,
                     synchronize_session=None) -> list:
    """Select all rows from tables list,
    which have been filtered with 'statements'"""
    db_session = Session()
    query = db_session.query(*tables)
    if statements:
        for statement in statements:
            query = query.filter(statement != '')
    if order_by:
        for sort in order_by:
            if descending:
                query = query.order_by(sort.desc())
            else:
                query = query.order_by(sort)
    if limit:
        query = query.limit(limit)
    if synchronize_session != None:
        rows = query.delete(synchronize_session=synchronize_session)
    else:
        rows = query.delete()  # return number of deleted msg
    db_session.commit()  # return number of deleted msg
    db_session.close()
    return rows


def db_delete_rows(tables: list,
                   *statements) -> int:
    """Delete all rows from tables list,
    which have been filtered with 'statements'.
    Returns number of deleted rows"""
    db_session = Session()
    query = db_session.query(*tables)
    for statement in statements:
        query = query.filter(statement != '')
    rows = query.delete()  # return number of deleted msg
    db_session.commit()  # return number of deleted msg
    db_session.close()
    return rows


def db_text_update(text_id: bytes,
                   text: str) -> bool:
    if not db_duplicate_check([Texts.text_id],
                              Texts.text_id == text_id):
        return False
    db_session = Session()
    update_q = update(Texts).where(
            Texts.text_id == text_id). \
        values(text=text)
    db_session.execute(update_q)
    db_session.commit()
    db_session.close()
    return True


def db_delete_user(user_login: str) -> bool:
    """Delete user by login in database,
    changes user role to 'deleted',
    also delete all invites and visibility statuses for this user"""
    db_session = Session()
    update_q = update(RolesOfUsers).where(
            RolesOfUsers.login == user_login). \
        values(user_role='deleted')
    db_session.execute(update_q)
    db_session.commit()

    update_q = update(Users).where(
            Users.login == user_login). \
        values(user_password='deleted')
    db_session.execute(update_q)
    db_session.commit()
    db_session.close()
    db_delete_rows([Visibility],
                   Visibility.login == user_login)
    invite_id = bytes(
            (bytearray(db_get_rows([SentInvites.invite_id],
                                   SentInvites.login == user_login)[0][0])))
    db_delete_rows([SentInvites],
                   SentInvites.invite_id == invite_id)
    db_delete_rows([Invites],
                   Invites.invite_id == invite_id)
    return True


def db_duplicate_check(tables: list,
                       *statements) -> bool:
    """Use SELECT statement to find row of table in database"""
    result_rows = db_get_rows(tables, *statements)
    if len(result_rows) > 0:
        return True
    else:
        return False


def db_duplicate_check_2(tables: list,
                         statements: list) -> bool:
    """Use SELECT statement to find row of table in database"""
    result_rows = db_get_rows_2(tables, statements)
    if len(result_rows) > 0:
        return True
    else:
        return False


def db_fill_visibility(login: str) -> bool:
    """Adds visibility status of all profiles for user by login value,
    in database"""
    db_session = Session()
    query = db_session.query(Profiles.profile_id)
    for profile in query.all():
        query_check = db_session.query(Visibility.profile_id,
                                       Visibility.login)
        query_check = query_check.filter(Visibility.login == login)
        query_check = query_check.filter(Visibility.profile_id == profile[0])
        check_result = query_check.all()
        if len(check_result) > 0:
            continue
        access = Visibility(login=login,
                            profile_id=profile[0])
        db_session.add(access)
        db_session.commit()
    db_session.close()
    return True


def db_add_visibility(login: str,
                      profile_id: str) -> str:
    """Adds visibility status of profiles for user by login value,
    in database"""
    db_session = Session()
    from main import logger
    # check user in database
    user_in_db = db_duplicate_check([Users.login],
                                    Users.login == login,
                                    Users.login != 'server',
                                    Users.login != 'anonymous')
    if not user_in_db:
        logger.info(f'User {current_user.login} tried to add profiles for '
                    f'{login} but such user not exists')
        # profile not in database
        return 'UserNotFound'

    # check profile in database
    profile_in_db = db_duplicate_check([Profiles.profile_id],
                                       Profiles.profile_id == profile_id)
    if not profile_in_db:
        logger.info(f'User {current_user.login} tried to add profile '
                    f'{profile_id}  for '
                    f'{login} but such profile not exists')
        # profile not in database
        return 'ProfileNotFound'

    # check if user already has access to profile
    access_in_db = db_duplicate_check([
            Visibility.profile_id,
            Visibility.login
            ],
            Visibility.login == login,
            Visibility.profile_id == profile_id)
    if access_in_db:
        logger.info(f'User {current_user.login} tried to add '
                    f'profile {profile_id} for '
                    f'{login} but this account already has this profile')
        # user already has access to profile
        return 'ProfileAlreadyAvailable'
    # user already hasn't access to profile
    access = Visibility(login=login,
                        profile_id=profile_id)
    db_session.add(access)
    db_session.commit()
    db_session.close()
    logger.info(f'User {current_user.login} added '
                f'profile {profile_id} for user '
                f'{login}')
    return 'Success'


def db_add_category_level(category_name: str,
                          level_list: str):
    from main import logger
    db_session = Session()
    if not db_duplicate_check([Categories],
                              Categories.category_name == category_name):
        new_category = Categories(category_name=category_name)
        db_session.add(new_category)
        db_session.commit()
        logger.info('Added category: ', category_name)
    db_session.close()
    logger.info('START ADD LEVELS LEVELS')
    for row in level_list:
        db_session = Session()
        if not db_duplicate_check([Levels],
                                  Levels.level_name == row):
            new_row = Levels(level_name=row)
            db_session.add(new_row)
            db_session.commit()
            logger.info(f'Added level_name: ', row)
        db_session.close()
    logger.info('START ADD CATEGORY LEVELS')
    for row in level_list:
        db_session = Session()
        if not db_duplicate_check([CategoryLevel],
                                  CategoryLevel.category_name == category_name,
                                  CategoryLevel.level_name == row):
            new_row = CategoryLevel(category_name=category_name,
                                    level_name=row)
            db_session.add(new_row)
            db_session.commit()
            logger.info(
                    f'Added CategoryLevel: {category_name} with level: {row}')
        db_session.close()


def db_profile_available(profile_id: str) -> bool:
    """Update profile availability info in DB"""
    from main import logger
    if not db_duplicate_check([Profiles],
                              Profiles.profile_id == profile_id):
        # profile not exist in DB
        return False
    db_session = Session()
    if profile_deleted(profile_id=profile_id):
        # profile deleted on site
        update_q = update(Profiles).where(
                Profiles.profile_id == profile_id). \
            values(available=False)
        db_session.execute(update_q)
        db_session.commit()
        db_session.close()
        logger.info(f'User {current_user} updated profile_id: {profile_id} '
                    f'and changed availability to 0,'
                    f'because profile deleted on site')
        return False
    else:
        # profile not deleted on site
        update_q = update(Profiles).where(
                Profiles.profile_id == profile_id). \
            values(available=True)
        db_session.execute(update_q)
        db_session.commit()
        db_session.close()
        logger.info(f'User {current_user} updated profile_id: {profile_id} '
                    f'and changed availability to 1,'
                    f'because profile not deleted on site')
        return True


def db_load_profile_description(profile_id: str) -> bool:
    from main import logger

    # check profile delete status
    if not db_profile_available(profile_id=profile_id):
        logger.info(f'User {current_user} opened load of profile '
                    f'description for profile_id: {profile_id},'
                    f'but this profile deleted on site')
        return False
    else:
        logger.info(f'User {current_user} opened load of profile '
                    f'description for profile_id: {profile_id}')
    db_session = Session()
    # collect info from site
    profile_details = collect_info_from_profile(profile_id=profile_id)

    # delete old profile info
    if db_duplicate_check([ProfileDescription],
                          ProfileDescription.profile_id == profile_id):
        logger.info(f'User {current_user} deleted old profile '
                    f'description for profile_id: {profile_id}')
    # delete profile description
    db_delete_rows([ProfileDescription],
                   ProfileDescription.profile_id == profile_id)
    # delete old category level
    db_delete_rows([ProfileCategories],
                   ProfileCategories.profile_id == profile_id)
    # delete old languages
    db_delete_rows([ProfileLanguages],
                   ProfileLanguages.profile_id == profile_id)

    # create new profile info
    new_pr_desc = ProfileDescription(profile_id=profile_id)
    for i in range(len(profile_details)):
        key = list(profile_details.keys())[i]
        val = profile_details[key]
        if type(val) == str:
            if val.lower() == 'not specified':
                val = None
        if key == 'Languages':
            # add new languages
            for lang in profile_details[key].keys():
                language = lang
                level_name = profile_details[key][lang]
                # check if user not specified languages
                if language.lower() == 'not specified':
                    continue
                elif level_name.lower() == 'not specified':
                    level_name = None

                new_lang_lvl = ProfileLanguages(
                        profile_id=profile_id,
                        language=language,
                        level_name=level_name)
                db_session.add(new_lang_lvl)
                db_session.commit()
            continue

        # check if key in categories table
        elif db_duplicate_check([Categories],
                                Categories.category_name == key.lower()):
            # add new category levels
            new_category_lvl = ProfileCategories(
                    category_name=key.lower(),
                    profile_id=profile_id,
                    level_name=val)
            db_session.add(new_category_lvl)
            db_session.commit()
            continue
        setattr(new_pr_desc, key.lower(), val)
    db_session.close()
    db_session = Session()
    db_session.add(new_pr_desc)
    db_session.commit()
    logger.info(f'User {current_user} added profile '
                f'description for profile_id: {profile_id}')
    db_session.close()
    return True


def db_load_all_profiles_description() -> bool:
    """Load profiles description for all profiles"""
    profiles = db_get_rows([Profiles.profile_id])
    for profile_id in profiles:
        db_load_profile_description(profile_id[0])
    return True


def db_add_profile(profile_id: str,
                   profile_password: str):
    """Add profile to DB"""

    from main import logger
    if profile_deleted(profile_id=profile_id):
        logger.info(f'User {current_user} tried to add profile info, '
                    f'for profile_id: {profile_id}, '
                    f'but this profile deleted on site')
        return False
    db_session = Session()
    if db_duplicate_check([Profiles],
                          Profiles.profile_id == profile_id):
        # profile already in DB, update password
        update_q = update(Profiles). \
            where(Profiles.profile_id == profile_id). \
            values(profile_password=profile_password)
        db_session.execute(update_q)
        logger.info(f'User {current_user} updated profile info, '
                    f'for profile_id: {profile_id}')
    else:
        # create new profile
        new_profile = Profiles(profile_id=profile_id,
                               profile_password=profile_password,
                               available=True,
                               can_receive=True)
        db_session.add(new_profile)
        logger.info(f'User {current_user} added profile, '
                    f'with profile_id: {profile_id}')
    db_session.commit()
    db_session.close()

    db_load_profile_description(profile_id=profile_id)
    return True


def create_custom_message(sender_profile_id, receiver_profile_id):
    """Функция для создания кастомного сообщения. Есть шаблон письма. В нем
    есть ключевые места по тиму {name}
    функция будет заменять эти ключевые слова на собранные данные с
    получателя и отправителя пиьсма

    Keyword arguments:
    sender_profile_id -- ID того кто отправляет
    receiver_profile_id -- ID того кому отправляем
    """
    receiver_data = collect_info_from_profile(receiver_profile_id)
    sender_data = collect_info_from_profile(sender_profile_id)
    # load message template from database
    message_text = db_get_rows([
            Texts.text
            ],
            MessageTemplates.profile_id == sender_profile_id,
            Texts.text_id == MessageTemplates.text_id,
            Texts.text_id != Messages.text_id)
    if len(message_text) >= 0:
        message_text = message_text[0]
    else:
        return False
    # Receiver name check
    if receiver_data["Name"] == "Not specified":
        receiver_data["Name"] = receiver_data["Nickname"]
    # add to receiver_data My name, to replace it in 'for' cycle
    receiver_data['my_name'] = sender_data["Name"]

    # message_text = message_text.format(name=receiver_name,
    # my_name=messager_name, country=country)
    for key in receiver_data.keys():
        # Check if user is dummy, and not use paragraph character
        message_text = re.sub(' {3,}', '\n', message_text)

        # Find key in text
        if message_text.find("{" + key + "}") + message_text.find(
                "{" + key.lower() + "}") != -2:
            if receiver_data[key] == "Not specified":
                # print(re.sub("\n?[^\n]*{" + key + "}[^\n]*[\n]? {4,}", '',
                # message_text))
                # replace all paragraph with 'Not Specified' key to empty
                # string
                # args of re.sub: pattern, text fragment to replace,
                # text where replace
                # full pattern:   \n?[^\n]*{Country}[^\n]*[\n]?
                message_text = re.sub("\n?[^\n]*{" + key + "}[^\n]*[\n]?", '',
                                      message_text)
                message_text = re.sub("\n?[^\n]*{" + key.lower() + "}[^\n]*["
                                                                   "\n]?",
                                      '', message_text)
                # We don't need to continue replacement with Not specified key
                continue

            # Check if key is Name, Country
            text_to_replace = receiver_data[key]
            if key not in ['name', 'my_name', 'country', 'nickname', 'city']:
                text_to_replace = text_to_replace

            # Replacement
            message_text = message_text.replace("{" + key + "}",
                                                text_to_replace)
            message_text = message_text.replace("{" + key.lower() + "}",
                                                text_to_replace)

    return message_text


def message(session, receiver_profile_id, message_text):
    """Отправка сообщения

    Keyword arguments:
    receiver_profile_id -- ID профиля которому будет отправлено сообщение
    session -- сессия залогиненого аккаунта
    message_text -- текст сообщения, что будет отправлен
    """
    # Данные для отправки сообщения
    data = {
            "ID": receiver_profile_id,
            "textcounter": len(message_text),
            "text": message_text,
            "sendto": "both",
            "SEND_MESSAGE": "YES"
            }
    # Отправка сообщения
    response = send_request(session=session, method="POST",
                            link=f"https://www.natashaclub.com/compose.php"
                                 f"?ID={receiver_profile_id}",
                            data=data)
    # Функция возвращает ответ сервера на запрос по отправке сообщения
    return response


def send_messages(profile_id_list: str,
                  looking_for: str = None,
                  photos_only: str = "off",
                  profiles: list = None) -> bool:
    """Send messages from profiles,
    checks how much messages each profile has already send today,
    calculate max available age with profile max_age_delta and profile age"""
    from main import logger
    # load profiles from DB
    profiles_list = db_get_rows([
            Profiles.profile_id,
            Profiles.profile_password,
            Profiles.msg_limit,
            Profiles.max_age_delta,
            ProfileDescription.age,
            ProfileDescription.sex
            ],
            Profiles.profile_id.in_(profile_id_list),
            Profiles.profile_password,
            ProfileDescription.profile_id == Profiles.profile_id)
    for i in range(1, len(profiles_list) + 1):
        msg_have_sent_today = db_get_rows([
                Messages.message_token
                ],
                Profiles.profile_id == ChatSessions.profile_id,
                Messages.chat_id == ChatSessions.chat_id,
                Messages.send_time == datetime.now().date())
        msg_need_to_be_sent = profiles_list[i][2] - msg_have_sent_today

        # calculate max_age for message receivers
        date_of_birth_end = profiles_list[i][3] + profiles_list[i][4]

        profile_login, password = str(profiles_list[i][0]), \
                                  profiles_list[i][1]
        values = login(profile_login, password)
        # start page in site for search
        page = 1
        if not looking_for:
            if profiles_list[i][5] == 'male':
                looking_for = 'female'
            else:
                looking_for = 'male'
        if values:
            session, my_profile_id = values
            my_data = collect_info_from_profile(
                    my_profile_id)
            logger.info(
                    f"Profile with profile_id: {my_profile_id} "
                    f"start send messages")
            messages_has_sent = 0
            stop = False
            while messages_has_sent < msg_need_to_be_sent:
                if stop:
                    break
                if not profiles:
                    profiles = search_for_profiles(
                            my_data["Sex"], looking_for,
                            my_data["Age"],
                            date_of_birth_end, page,
                            photos_only)
                profiles_id = get_id_profiles(profiles)
                profile_try_counter = 0
                page_try_counter = 0
                while len(profiles_id) == 0:
                    if profile_try_counter == 2:
                        page += 1
                        page_try_counter += 1
                    elif page_try_counter == 10:
                        logger.info(
                                f"Site don't show any profiles in 10 pages,"
                                f"messages sent from profile with"
                                f"profile_id: {my_profile_id} ended.")
                        messages_has_sent = \
                            msg_need_to_be_sent
                        break
                    profiles = search_for_profiles(
                            my_data["Sex"], looking_for,
                            my_data["Age"],
                            date_of_birth_end, page,
                            photos_only)
                    profiles_id = get_id_profiles(profiles)
                    profile_try_counter += 1
                for profile_id in profiles_id:
                    check_response = check_for_filter(
                            session, profile_id)
                    if check_response:
                        if check_response == "LIMIT OUT":
                            stop = True
                            break
                    else:
                        message_text = create_custom_message(
                                my_profile_id, profile_id)
                        if message_text is False:
                            logger.info(
                                    f"Profile with profile_id {my_profile_id},"
                                    f" without unused message templates")
                            messages_has_sent = \
                                msg_need_to_be_sent
                            break
                        message(session, profile_id,
                                message_text)
                        dialog_download(
                                observer_login=profiles_list[i][0],
                                observer_password=profiles_list[i][1],
                                sender_id=profiles_list[i][0],
                                receiver_profile_id=profile_id)
                        messages_has_sent += 1
                        logger.info(
                                f"Successfully sent message to profile "
                                f"with profile_id: {profile_id}. "
                                f"Left to send: "
                                f" {msg_need_to_be_sent - messages_has_sent}")
                        if messages_has_sent == \
                                msg_need_to_be_sent:
                            logger.info(
                                    f"Profile with profile_id: "
                                    f"{my_profile_id}, "
                                    f"successfully sent messages")
                            break
                page += 1
    return True


def account_dialogs_checker(observed_profile_id: str,
                            observed_profile_password: str,
                            max_page: int = None) -> bool:
    from main import logger
    logger.info(f'Message update worker start load dialog from:'
                f'account: {observed_profile_id}')

    current_profile_session, observed_profile_id = login(
            profile_login=observed_profile_id,
            password=observed_profile_password)
    start_time = time()
    profiles = set()
    page = 1
    for inbox in [True, False]:
        while True:
            if inbox:
                link = "https://www.natashaclub.com/inbox.php"
            else:
                link = "https://www.natashaclub.com/outbox.php"
            response = send_request(
                    session=current_profile_session, method="GET",
                    link=link + f"?page={page}")
            inbox_page = get_parsed_page(response)

            messages = [tr for tr in
                        inbox_page.find_all('tr', class_='table')]
            messages = list(map(lambda x: [td for td in x.find_all('td')],
                                messages))
            messages = [col for col in messages if
                        len(col) == 5 - int(not inbox)]
            if len(messages) == 0:
                break
            for another_profile_id in messages:
                another_profile_id = another_profile_id[2 - int(not inbox)] \
                                         .a.attrs['href'][15:]
                profiles.add(another_profile_id)
            page += 1
            if max_page:
                if max_page <= page:
                    break
        page = 1
    """print(f"Время считывания профилей для аккаунта: {observed_profile_id}, "
          f"{time() - start_time} sec")"""
    # start_time = time()
    profiles_threads = []
    for profile_id in profiles:
        t = Thread(target=profile_dialogs_checker,
                   args=(observed_profile_id,
                         observed_profile_password,
                         profile_id,
                         current_profile_session))
        t.start()
        profiles_threads.append(t)
        """profile_dialogs_checker(
                observed_profile_id=observed_profile_id,
                observed_profile_password=observed_profile_password,
                profile_id=profile_id)"""
    """print(f"Время загрузки диалогов для аккаунта:"
          f" {observed_profile_id}, "
          f"{time() - start_time} sec")"""
    for i in range(len(profiles_threads)):
        profiles_threads[i].join()
    logger.info(f'Message update worker finished load dialog from:'
                f'account: {observed_profile_id}')
    return True


def profile_dialogs_checker(observed_profile_id,
                            observed_profile_password,
                            profile_id,
                            account_session):
    from main import logger
    # start_time_for_profile = time()
    logger.info(f'Start load dialog for profile_id: {profile_id}')
    # start_time_for_profile_dialogue = time()
    dialog_download(
            observer_login=observed_profile_id,
            observer_password=observed_profile_password,
            sender_id=profile_id,
            receiver_profile_id=profile_id,
            account_session=account_session)
    dialog_download(
            observer_login=observed_profile_id,
            observer_password=observed_profile_password,
            sender_id=observed_profile_id,
            receiver_profile_id=profile_id,
            account_session=account_session)
    """print(f"Время загрузки диалогов профиля: {profile_id}, "
          f"{time() - start_time_for_profile_dialogue} sec")"""
    # load description for profile
    # start_time_for_profile_desc = time()
    db_load_profile_description(profile_id)
    """print(f"Время загрузки описания профиля: {profile_id}, "
          f"{time() - start_time_for_profile_desc} sec")
    print(f"Все время загрузки диалогов для аккаунта:"
          f" {observed_profile_id} и профиля: {profile_id}, "
          f"{time() - start_time_for_profile} sec")"""


def prepare_answer(account: list,
                   profile: list,
                   account_session,
                   text_templates: list,
                   sent_delay: int = 2) -> bool:
    from main import logger
    # get dialogue with profile
    dialogue = db_show_dialog(sender=account[0],
                              receiver=profile[0],
                              descending=True)
    if len(dialogue) == 0:
        logger.error(f'Account {account[0]} '
                     f'and profile {profile[0]} have chat, '
                     f'but this chat without messages')
        return False
    messages = ''
    # add last messages from profile
    for message in dialogue:
        if message['profile_id'] == account:
            break
        else:
            messages += message['text']

    if len(messages) != 0:
        # get count of account messages
        msg_num = 0
        for message in dialogue[::-1]:
            if message['profile_id'] == account[0]:
                msg_num += 1
        # PLACE FOR ANDREYCHIK FUNCTION
        MESSAGE_CREATED = True
        if msg_num == 0:
            logger.info(f'In dialogue with account {account[0]} and '
                        f'profile: {profile[0]} we not send any message,'
                        f"so we stop prepare answer")
            return False
        logger.info(f'Account {account[0]} tried to create answer for '
                    f'profile: {profile[0]}')
        for i in range(3):
            text, used_texts = create_message_response(
                    template_number=msg_num,
                    sender_profile_id=account[0],
                    receiver_profile_id=profile[0],
                    message_text=messages,
                    text_templates=text_templates)
            if text is False:
                logger.info(f'Account {account[0]} tried to create '
                            f'answer for profile: {profile[0]},'
                            f"but it hasn't template with num {msg_num}")
                return False
            try:
                pass
            except Exception as e:
                if i == 2:
                    MESSAGE_CREATED = False
            if len(text) != 0:
                break
        if MESSAGE_CREATED:
            # create message with delay, in DB
            db_message_create(
                    chat_id=profile[1],
                    send_time=datetime.now()
                              + timedelta(hours=sent_delay),
                    viewed=False,
                    sender=account[0],
                    text=text,
                    delay=True)
            for text_id in used_texts:
                db_session = Session()
                if db_duplicate_check_2([UsedAnchors],
                                        [UsedAnchors.profile_id == profile[0],
                                         UsedAnchors.text_id == text_id]):
                    logger.error('Worker_sender tried to add used anchor '
                                 f'for profile: {profile[0]} '
                                 f'and with text_id: '
                                 f'{UUID(bytes=text_id)}')
                    continue
                used_anchor = UsedAnchors(profile_id=profile[0],
                                          text_id=text_id)
                db_session.add(used_anchor)
                db_session.commit()
                db_session.close()
                logger.error('Worker_sender added used anchor '
                             f'for profile: {profile[0]} '
                             f'and with text_id: '
                             f'{UUID(bytes=text_id)}')
            if len(used_texts) == 0:
                logger.info(f'Account {account[0]} created answer for '
                            f'profile: {profile[0]} without any key words')
            else:
                logger.info(f'Account {account[0]} created answer for '
                            f'profile: {profile[0]}')
            return MESSAGE_CREATED
    else:

        if dialogue[0]['delay']:
            if (datetime(dialogue[0]['send_time'] - datetime.now()).hour < 2) \
                    and (datetime.time(9)
                         <= dialogue[0]['send_time']
                         <= datetime.time(22)):
                # sent message on site
                result = False
                """result = send_msg(session = account_session,
                             profile_id = profile[0],
                             text = dialogue[0]['text'])"""
                if result:
                    # add update for message in DB, to delete from delayed
                    db_session = Session()
                    update_q = update(Messages).where(
                            Messages.message_token == dialogue[0][
                                'message_token']). \
                        values(send_time=datetime.now(),
                               delay=False)
                    db_session.execute(update_q)
                    db_session.commit()
                    db_session.close()
                    return True
                else:
                    logger.error(f'Failed to sent message '
                                 f'from account {account[0]} '
                                 f'to profile_id {profile[0]}')
                    return False
    return False


def db_error_check(empty_chats=False,
                   profiles_without_chats=False):
    from main import logger
    if empty_chats:
        # find empty chats and delete them
        logger.info('Start empty chats searching')
        chats = db_get_rows_2([Chats.chat_id])
        for chat_id in chats:
            messages = db_get_rows_2([Messages.message_token],
                                     [Messages.chat_id == chat_id[0]])
            if len(messages) == 0:
                logger.info(f'Found empty chat: '
                            f'{UUID(bytes=chat_id[0])}')
                db_delete_rows_2([ChatSessions],
                                 [ChatSessions.chat_id == chat_id[0]])
                db_delete_rows_2([Chats],
                                 [Chats.chat_id == chat_id[0]])
        logger.info('Error check in database complete, empty chats deleted')
    if profiles_without_chats:
        # find empty chats and delete them
        logger.info('Start profiles without chats searching')
        profiles = db_get_rows_2([Profiles.profile_id],
                                 [Profiles.profile_password == None])
        for profile_id in profiles:
            chats = db_get_rows_2([ChatSessions.chat_id],
                                  [ChatSessions.profile_id == profile_id[0]])
            if len(chats) == 0:
                logger.info(f'Found profile without chat: '
                            f'{profile_id[0]}')
                db_delete_rows_2([ProfileDescription],
                                 [ProfileDescription.profile_id == profile_id[
                                     0]])
                db_delete_rows_2([ProfileCategories],
                                 [ProfileCategories.profile_id == profile_id[
                                     0]])
                db_delete_rows_2([ProfileLanguages],
                                 [ProfileLanguages.profile_id == profile_id[
                                     0]])
                db_delete_rows_2([Visibility],
                                 [Visibility.profile_id == profile_id[0]])
                db_delete_rows_2([ProfileCategories],
                                 [ProfileCategories.profile_id == profile_id[
                                     0]])
                templates = db_get_rows_2([Texts.text_id],
                                          [MessageTemplates.profile_id ==
                                           profile_id[0],
                                           MessageTemplates.text_id ==
                                           Texts.text_id])
                anchors = db_get_rows_2([Texts.text_id],
                                        [MessageAnchors.profile_id ==
                                         profile_id[0],
                                         MessageAnchors.text_id ==
                                         Texts.text_id])
                texts = templates + anchors
                for text_id in texts:
                    db_delete_rows_2([Tagging],
                                     [Tagging.text_id == text_id[0]])
                    db_delete_rows_2([MessageTemplates],
                                     [MessageTemplates.text_id == text_id[0]])
                    db_delete_rows_2([MessageAnchors],
                                     [MessageAnchors.text_id == text_id[0]])
                    db_delete_rows_2([Texts],
                                     [Texts.text_id == text_id[0]])

        logger.info('Error check in database complete, '
                    'profiles without chats')

    return True


"""db_error_check(empty_chats=True,
               profiles_without_chats=True)"""

"""print(profile_dialogs_checker(observed_profile_id='1000868043',
                              observed_profile_password='SWEETY777',
                              max_page=3))"""

"""print(db_load_all_profiles_description())"""

"""print(db_load_profile_description('1001721974'))"""

"""print(db_delete_user('111@gmail.com'))"""

"""print(db_fill_visibility('admin@gmail.com'))"""
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
