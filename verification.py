# coding: utf8
import requests

from control_panel import db_get_rows
from db_models import Tags
from scraping import collect_info_from_profile, get_parsed_page, \
    get_profile_page, send_request


def profile_in_inbox(session, profile_id, inbox=True):
    """Отправка сообщения

    Keyword arguments:
    session -- сессия залогиненого аккаунта
    profile_id -- ID профиля которого мы ищем в Inbox
    """
    # Ищем в Inbox сообщение профиля
    data = {
            "filterID": profile_id,
            "filterPPage": "20"
            }
    if inbox:
        link = "https://www.natashaclub.com/inbox.php"
    else:
        link = "https://www.natashaclub.com/outbox.php"
    response = send_request(session=session, method="POST",
                            link=link,
                            data=data)

    inbox_page = get_parsed_page(response)
    numbers = [int(number.text) for number in
               inbox_page.find("td", class_="panel").find_all("b")]
    # Эта переменная показывает общее количество сообщений от профиля,
    # что мы искали в инбоксе
    total_messages_in_inbox_from_profile = numbers[0]
    # Здесь показывается количетсво новых сообщений от этого профиля
    new_messages_in_inbox_from_profile = numbers[1]

    return total_messages_in_inbox_from_profile, \
           new_messages_in_inbox_from_profile


def first_letter_sent(session, profile_id) -> bool:
    """При нажатии на кнопку (отправить письмо), может перейти на страницу
    где написано
    You can write only 1 first letter. И данного профиля может не быть в
    Inbox и Outbox. Поэтому создана такая вот
    дополнительная проверка

    Keyword arguments:
    session -- сессия залогиненого аккаунта
    profile_id -- ID профиля которому будем отсылать письмо
    """
    response = send_request(session, method="GET",
                            link="https://www.natashaclub.com/compose.php?ID"
                                 "=" + profile_id)
    compose_new_message_page = get_parsed_page(response)
    text = compose_new_message_page.find("td", class_="text").text
    if text == "You can write only 1 first letter":
        return True

    return False


def limit_out(session, receiver_profile_id):
    """Бывает, что аккаунт который рассылает сообщения достигает лимита по
    рассылке. Это видно когда мы переходим
    на страницу какого-то профиля и нажимаем отправить бесплатное сообщение,
    тогда оно показывает что лимит исчерпан

    Keyword arguments:
    send_free_message_page -- страница, которая появляется при нажатии кнопи
    отправить сообщение
    """
    response = send_request(session=session, method="GET",
                            link="https://www.natashaclub.com/compose.php?ID"
                                 "=" +
                                 receiver_profile_id)
    send_free_message_page = get_parsed_page(response)
    text = send_free_message_page.find(
            "div",
            id="ContentDiv").find("td", class_="text").text
    if "Sorry, but you've reached your limit for today." in text:
        return True
    else:
        return False


def profile_country(profile_id):
    """Исключаем ненужные страны из списка рассылки

    Keyword arguments:
    profile_id -- ID профиля, которому собираемся отослать сообщение
    """
    profile_info = collect_info_from_profile(profile_id)
    country = profile_info["Country"]
    # Если страна в списке исключенных, то не отправляем письмо
    if country in ["Azerbaijan", "India", "Tajikistan"]:
        return True

    return False


def profile_deleted(profile_id):
    """Проверяем или профиль удален

    Keyword arguments:
    profile_id -- ID профиля, которому собираемся отослать сообщение
    """
    profile_page = get_profile_page(profile_id)
    text = profile_page.find("div", class_="DataDiv").text
    if "Profile not available for view." in text:
        return True
    else:
        return False


def not_in_age_bounds(messager_age, receiver_profile_id):
    """Возраст отправителя должен быть меньше или равен возрасту профиля
    которому мы отсылаем

    Keyword arguments:
    messager_age -- возраст отправителя
    receiver_profile_id -- ID профиля, которому собираемся отослать сообщение
    """
    receiver_age = collect_info_from_profile(receiver_profile_id)["Age"]
    if messager_age > receiver_age:
        return True

    return False


def login(profile_login, password):
    """Функция для входа на сайт

    Keyword arguments:
    profile_login -- логин аккаунта
    password -- пароль аккаунта
    """
    # Создаем сессию для отправщика (не имея фиксированую сессию залогинено
    # аккаунта не получится отправить сообщение)
    session = requests.Session()

    # Данные для отправки POST запроса
    data = {
            "rememberme": "1",
            "imageField": "log in",
            "ID": profile_login,
            "Password": password
            }
    # Отправляем запрос для входа на сайт
    request = send_request(session=session, method="POST",
                           link="https://www.natashaclub.com/member.php",
                           data=data)

    # Если успешно вошли на сайт, то должен создаться logtrackID для
    # залогиненого аккаунта
    if "logtrackID" in request.text:
        logtrack_id = request.text.split("'")[1]
        # Узнаем ID аккаунта, что вошел на сайт
        profile_id = logtrack_id.split("=")[1].split("&")[0]
        print("Successfully logged to the website!")
        # Функция возвращает ID аккаунта что вошел и его сессию
        return session, profile_id
    else:
        print("Wrong login or password!")
        # Функция возвращает False если логин или пароль оказались
        # неправильными
        return False


def forbidden_profile(profile_id):
    """Проверка на то, является ли профиль запрещенным (если отослать на
    него письмо, то наш аккаунт заблочат)

    Keyword arguments:
    profile_id -- ID профиля которому будет отправлено сообщение
    """
    # Собираем информацию о профиле
    data = collect_info_from_profile(profile_id)
    # Якорные слова которые обозначают профиль как ловушку
    anchor_words = db_get_rows([Tags.tag],
                               Tags.forbidden)
    # ищем якоря в DESCRIPTION
    for anchor in anchor_words:
        if anchor[0] in data["Description"]:
            return True

    # Если нету, то False
    return False


def check_for_filter(session, profile_id):
    from main import logger
    try:
        if profile_in_inbox(session, profile_id)[0]:
            logger.error(f"Неудалось отправить сообщение "
                         f"от profile_id: {profile_id} INBOX")
            return "INBOX"
        elif limit_out(session, profile_id):
            logger.error(f"Неудалось отправить сообщение "
                         f"от profile_id: {profile_id} "
                         f"LIMIT OUT")
            return "LIMIT OUT"
        elif profile_deleted(profile_id):
            logger.error(f"Неудалось отправить сообщение "
                         f"от profile_id: {profile_id} "
                         f"PROFILE DELETED")
            return "PROFILE DELETED"
        elif forbidden_profile(profile_id):
            logger.error(f"Неудалось отправить сообщение "
                         f"от profile_id: {profile_id} "
                         f"FORBIDDEN")
            return "FORBIDDEN"
        elif first_letter_sent(session, profile_id):
            logger.error(f"Неудалось отправить сообщение "
                         f"от profile_id: {profile_id} "
                         f"FIRST LETTER SENT")
            return "FIRST LETTER SENT"
        elif profile_country(profile_id):
            logger.error(f"Неудалось отправить сообщение "
                         f"от profile_id: {profile_id} "
                         f"INVALID COUNTRY")
            return "INVALID COUNTRY"
    except Exception as ex:
        print(ex)

    return False
