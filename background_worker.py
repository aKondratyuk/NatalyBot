from threading import Thread
from time import sleep, time

from control_panel import account_dialogs_checker, db_error_check, \
    db_get_rows, \
    db_get_rows_2, dialog_download, prepare_answer
from db_models import ChatSessions, MessageTemplates, Profiles, Texts
from verification import site_login


def worker_invites() -> None:
    """Send first messages in dialogue from 1:00 PM to 2:00 PM,
    works in background, time delta: 5 min"""
    # 5 min in seconds
    time_delta = 300

    while True:
        # code
        sleep(time_delta)


def worker_msg_sender() -> None:
    """Send messages with delay,
    works in background with exists dialogs, time delta: 5 min"""
    from main import logger

    time_delta = 3600
    # Sent delay in hours
    sent_delay = 1
    start_time = time()

    # while True:
    # code
    # get accounts from DB
    accounts = db_get_rows_2([Profiles.profile_id,
                              Profiles.profile_password],
                             [
                                     Profiles.profile_password
                                     ])
    for account in accounts:
        chat_id_query = db_get_rows_2([ChatSessions.chat_id],
                                      [ChatSessions.profile_id == account[
                                          0]],
                                      return_query=True)
        # get profiles which are available and have chat with account
        profiles = db_get_rows_2([ChatSessions.profile_id,
                                  ChatSessions.chat_id],
                                 [
                                         ChatSessions.profile_id ==
                                         Profiles.profile_id,
                                         ChatSessions.chat_id.in_(
                                                 chat_id_query),
                                         Profiles.profile_password == None,
                                         Profiles.available
                                         ])
        logger.error(f"worker_sender start process Account {account[0]} "
                     f'with {len(profiles)} profiles')
        if len(profiles) != 0:
            # if account has dialogs with active profiles
            account_session, account_id = site_login(
                    profile_login=account[0],
                    password=account[1])
        # Вытягиваем шаблон по номеру
        text_templates = db_get_rows_2([
                MessageTemplates.text_number,
                Texts.text
                ],
                [
                        MessageTemplates.profile_id == account[0],
                        MessageTemplates.text_id == Texts.text_id
                        ],
                order_by=[MessageTemplates.text_number])
        if len(text_templates) == 0:
            # we can't find any template
            logger.error(f"Account {account[0]} without templates, passed")
            continue

        for profile in profiles:
            prepare_answer(account=account,
                           profile=profile,
                           account_session=account_session,
                           sent_delay=sent_delay,
                           text_templates=text_templates)
    logger.error(f'Worker_sender end prepare answers and go to sleep')
    logger.stopwatch(f'Worker_msg_sender time spend: {time() - start_time} '
                     f'sec')
    # sleep(time_delta)


def worker_msg_updater() -> None:
    """Check inbox for all profiles with password
    and add new profiles which have written message,
    works in background, time delta: 5 min"""
    """Обновляет диалоги на основе текущих диалогов, не добавляя новые"""
    from main import logger
    time_delta = 3600

    while True:
        # code
        chats = db_get_rows([ChatSessions.chat_id,
                             Profiles.profile_id,
                             Profiles.profile_password],
                            ChatSessions.profile_id == Profiles.profile_id,
                            Profiles.profile_password)
        for chat in chats:
            chat_id = chat[0]
            account_id = chat[1]
            account_pass = chat[2]
            profiles = db_get_rows([
                    Profiles.profile_id
                    ],
                    ChatSessions.profile_id == Profiles.profile_id,
                    ChatSessions.chat_id == chat_id)
            for profile in profiles:
                profile_id = profile[0]
                logger.info(f'Message update worker start load dialog from:'
                            f'account: {account_id} and profile: {profile_id}')
                dialog_download(observer_login=account_id,
                                observer_password=account_pass,
                                sender_id=account_id,
                                receiver_profile_id=profile_id)
                dialog_download(observer_login=account_id,
                                observer_password=account_pass,
                                sender_id=profile_id,
                                receiver_profile_id=profile_id)
                logger.info(f'Message update worker finished load dialog from:'
                            f'account: {account_id} and profile: {profile_id}')
        sleep(time_delta)


def worker_profile_and_msg_updater() -> None:
    """Check inbox for all profiles with password
    and add new profiles which have written message,
    works in background, time delta: 5 min"""
    """Ищет в инбоксе и оутбоксе сообщения, первые 10 страниц, и загружает 
    их, попутно добавляя профиля и диалоги в базу"""
    from main import logger
    time_delta = 3600
    max_page = 3
    # while True:
    # code
    db_error_check(empty_chats=True,
                   profiles_without_chats=True,
                   unused_texts=True)
    start_time = time()
    threads = []
    profiles = db_get_rows([
            Profiles.profile_id,
            Profiles.profile_password
            ],
            Profiles.profile_password)
    for profile in profiles:
        profile_id = profile[0]
        profile_pass = profile[1]

        t = Thread(target=account_dialogs_checker,
                   args=(profile_id, profile_pass, max_page))
        t.start()

        threads.append(t)
        """account_dialogs_checker(observed_profile_id=profile_id,
                                observed_profile_password=profile_pass,
                                max_page=max_page)"""
    for i in range(len(threads)):
        print(f'Waiting thread №{i}')
        threads[i].join()
    db_error_check(empty_chats=True,
                   profiles_without_chats=True,
                   unused_texts=True)
    logger.info('Worker which update dialogs end work')
    logger.stopwatch(f'worker_profile_and_msg_updater '
                     f'time spend: {time() - start_time} sec')
    # sleep(time_delta)


def worker_timer(num) -> None:
    """Check inbox for all profiles with password
    and add new profiles which have written message,
    works in background, time delta: 5 min"""
    time_delta = 1
    i = 1
    while True:
        # code
        print(f"{num}: {i}")
        i += 1


def main_worker() -> None:
    time_delta = 3600
    # Function for dialogues refreshing
    worker_profile_and_msg_updater()
    # Function for template prepare and sending templates
    worker_msg_sender()
    sleep(time_delta)


main_worker()
