from file_operations import read_file
from scraping import collect_info_from_profile, send_request, get_parsed_page, get_profile_page


def forbidden_profile(profile_id):
    """Проверка на то, является ли профиль запрещенным (если отослать на него письмо, то наш аккаунт заблочат)

    Keyword arguments:
    profile_id -- ID профиля которому будет отправлено сообщение
    """
    # Собираем информацию о профиле
    data = collect_info_from_profile(profile_id)
    # Якорные слова которые обозначают профиль как ловушку
    anchor_words = read_file("anchor_words.csv").splitlines()[1:]
    # ищем якоря в DESCRIPTION
    for anchor in anchor_words:
        if anchor in data["Description"]:
            return True

    # Если нету, то False
    return False


def profile_in_inbox(session, profile_id):
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
    response = send_request(session=session, method="POST", link="https://www.natashaclub.com/inbox.php", data=data)
    inbox_page = get_parsed_page(response)
    numbers = [int(number.text) for number in inbox_page.find("td", class_="panel").find_all("b")]
    # Эта переменная показывает общее количество сообщений от профиля, что мы искали в инбоксе
    total_messages_in_inbox_from_profile = numbers[0]
    # Здесь показывается количетсво новых сообщений от этого профиля
    new_messages_in_inbox_from_profile = numbers[1]

    return total_messages_in_inbox_from_profile, new_messages_in_inbox_from_profile


def first_letter_sent(session, profile_id):
    """При нажатии на кнопку (отправить письмо), может перейти на страницу где написано
    You can write only 1 first letter. И данного профиля может не быть в Inbox и Outbox. Поэтому создана такая вот
    дополнительная проверка

    Keyword arguments:
    session -- сессия залогиненого аккаунта
    profile_id -- ID профиля которому будем отсылать письмо
    """
    response = send_request(session, method="GET", link="https://www.natashaclub.com/compose.php?ID=" + profile_id)
    compose_new_message_page = get_parsed_page(response)
    text = compose_new_message_page.find("td", class_="text").text
    if text == "You can write only 1 first letter":
        return True

    return False


def limit_out(session, receiver_profile_id):
    """Бывает, что аккаунт который рассылает сообщения достигает лимита по рассылке. Это видно когда мы переходим
    на страницу какого-то профиля и нажимаем отправить бесплатное сообщение, тогда оно показывает что лимит исчерпан

    Keyword arguments:
    send_free_message_page -- страница, которая появляется при нажатии кнопи отправить сообщение
    """
    response = send_request(session=session, method="GET", link="https://www.natashaclub.com/compose.php?ID=" +
                                                                receiver_profile_id)
    send_free_message_page = get_parsed_page(response)
    text = send_free_message_page.find("div", id="ContentDiv").find("td", class_="text").text
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
    """Возраст отправителя должен быть меньше или равен возрасту профиля которому мы отсылаем

    Keyword arguments:
    messager_age -- возраст отправителя
    receiver_profile_id -- ID профиля, которому собираемся отослать сообщение
    """
    receiver_age = collect_info_from_profile(receiver_profile_id)["Age"]
    if messager_age > receiver_age:
        return True

    return False
