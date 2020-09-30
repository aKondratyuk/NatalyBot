import re
from datetime import datetime
from math import ceil
from uuid import uuid4

from sqlalchemy import update
from werkzeug.security import check_password_hash, generate_password_hash

from authentication import User
from db_models import ChatSessions, Chats, Invites, Messages, Profiles, \
    RolesOfUsers, SentInvites, Session, Texts, Users
from scraping import get_parsed_page, send_request
from verification import login, profile_in_inbox


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
    from app import logger
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
    from app import logger

    session = Session()
    users = session.query(Users).filter(Users.login == login).all()

    if len(users) == 0:
        logger.info(f'User signup with wrong e-mail: {login}')
        return None
    db_invites = session.query(Invites).all()
    for db_invite in db_invites:
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


def db_show_dialog(sender: str,
                   receiver: str):
    db_session = Session()
    db_session.execute()
    db_session.close()


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
                   target_profile: str) -> bytes:
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
            Profiles.profile_id == target_profile).all()
    if len(profiles) == 0:
        target_profile = Profiles(profile_id=target_profile,
                                  can_receive=True,
                                  available=True)
        db_session.add(target_profile)
        db_session.commit()

    # finding chat id for this users
    # find all chats with sender
    query = db_session.query(ChatSessions).filter(
            ChatSessions.profile_id == observer_login)
    # find all chats with receiver
    sub_query = db_session.query(ChatSessions).filter(
            ChatSessions.profile_id == observer_login).subquery()
    # find chat from sender to receiver
    query.join(sub_query, ChatSessions.chat_id == ChatSessions.chat_id)
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
    chat_session_2 = ChatSessions(chat_id=chat_id,
                                  profile_id=target_profile)
    db_session.add(chat_session_1)
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
            Messages.chat_id == chat_id
            and Messages.profile_id == sender_id)
    db_session.close()
    return total_msg - len(messages.all())


def dialog_page_upload(current_profile_session,
                       data: dict,
                       page: int,
                       open_msg_count: int,
                       chat_id: bytes,
                       sender_id: str,
                       inbox: bool):
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
                         == \
                         '/templates/tmpl_nc/images_nc/new.gif'
        else:
            viewed = not messages[i][1 - int(not inbox)].text == '\nNot read'

        if viewed:
            text = get_message_text(session=current_profile_session,
                                    message_url=message_url)
        else:
            text = text_preview
        db_message_create(chat_id=chat_id,
                          send_time=time,
                          viewed=viewed,
                          sender=sender_id,
                          text=text)


def dialog_download(observer_login,
                    obeserver_password,
                    sender_id: str,
                    receiver_profile_id: str):
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
            password=obeserver_password)
    total_msg, new_msg = profile_in_inbox(
            session=current_profile_session,
            profile_id=receiver_profile_id,
            inbox=sender_id == receiver_profile_id)
    chat_id = db_chat_create(observer_login=observer_login,
                             observer_pass=obeserver_password,
                             target_profile=receiver_profile_id)

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
                           inbox=inbox)
        open_msg_count -= int(data['filterPPage'])
    return True


print(dialog_download(observer_login="1000868043",
                      obeserver_password="SWEETY777",
                      sender_id="1000868043",
                      receiver_profile_id="1001597106"))
