# coding: utf8
from datetime import datetime

import requests
from bs4 import BeautifulSoup


def specified(iterable, *index):
    try:
        value = iterable
        # Обрабатываем полученную информацию
        for i in index:
            value = iterable[i]
        # Если выдало как пусто, то
        if len(value) == 0:
            value = "Not specified"
    # При ошибки считывания данных, ставим не опознано
    except Exception:
        value = "Not specified"

    return value


def send_request(session, method, link, data=None):
    """Безопасная отправка запроса. В случае ошибки, снова отправляется запрос.

    Keyword arguments:
    session -- передача существующей сесси профиля
    method -- метод отправки запроса GET/POST
    link -- ссылка на страницу, на которую будет отправлен запрос
    data -- параметры запроса (default None)

    """
    # Отправка запроса
    while True:
        if method == "GET":
            try:
                if not data:
                    request = session.get(link)
                else:
                    request = session.get(link, data=data)
                if request.status_code == 200:
                    break
                if request.status_code == 404:
                    break
            except Exception:
                print("Connection Error. Trying to send message again")
        elif method == "POST":
            try:
                if not data:
                    request = session.post(link)
                else:
                    request = session.post(link, data=data)
                if request.status_code == 200:
                    break
                if request.status_code == 404:
                    break
            except Exception:
                print("Connection Error. Trying to send message again")
        else:
            print("Method are not specified!")

    return request
    # Конец отправки запроса


def get_parsed_page(response):
    """Получение HTML-разметки страницы.

    Keyword arguments:
    request -- отправка запроса на страницу, которая будет парсится

    """
    html_document = response.text
    parsed_page = BeautifulSoup(html_document, "html.parser")

    return parsed_page


def get_profile_page(profile_id):
    """Получение HTML-разметки страницы профиля.

    Keyword arguments:
    profile_id -- ID профиля

    """
    session = requests.Session()
    response = send_request(session=session, method="GET",
                            link="https://www.natashaclub.com/" + profile_id)
    profile_page = get_parsed_page(response)

    return profile_page


def search_for_profiles(sex, looking_for, date_of_birth_start,
                        date_of_birth_end, page=1, photos_only="off"):
    """Поиск профилей по заданным критериям.

    Keyword arguments:
    sex -- пол профиля
    looking_for -- поиск профилкй что имеют указанный пол
    date_of_birth_start -- минимальный возраст человека с кем профиль хочет
    познакомится
    date_of_birth_end -- максимальный возраст человека с кем профиль хочет
    познакомится
    page -- итерируемый параметр, указывает на страницу, где находится 10
    профилей (default 1)

    """
    session = requests.Session()
    if photos_only == "on":
        search_link = f"https://www.natashaclub.com/search_result.php" \
                      f"?p_per_page=10&photos_only=on&Sex={sex}" \
                      f"&LookingFor={looking_for}&Date" \
                      f"OfBirth_start={date_of_birth_start}" \
                      f"&DateOfBirth_end=" \
                      f"{date_of_birth_end}&CityST=0&City=&&page=" \
                      f"{page}&LastOnline=7"
        request = send_request(session=session, method="POST",
                               link=search_link)
    else:
        search_link = f"https://www.natashaclub.com/search_result.php" \
                      f"?p_per_page=10&Sex={sex}" \
                      f"&LookingFor={looking_for}&Date" \
                      f"OfBirth_start={date_of_birth_start}" \
                      f"&DateOfBirth_end=" \
                      f"{date_of_birth_end}&CityST=0&City=&&page=" \
                      f"{page}&LastOnline=7"
        request = send_request(session=session, method="POST",
                               link=search_link)

    return get_parsed_page(request)


def get_id_profiles(searched_profiles_page):
    """Формирование списка ID профилей, вытянутых со страницы (поиск
    профилей по заданым критериям).

    Keyword arguments:
    searched_profiles_page -- страница профилей, отобранных по заданым
    киртериям
    """
    # Массив для внесения всех ссылок, что имеют target = _blank
    profiles_id = []
    # Перебираем все ссылки и оставляем только те, которые ведут на профиль
    # зарегестрированого аккаунта
    """
    Пример собранных ссылок: /flowers.html, 
    https://www.1st-international.com/html/check/ladycheckorder.html,
    # Fergt88.html, Fergt88.html, vkiss.php?sendto=1001615983, 
    BRITO1985.html, BRITO1985.html

    Нам нужны ссылки vkiss.php?sendto=1001615983, в них есть ID профиля, 
    его и будем вытягивать
    """
    for link in searched_profiles_page.find_all('a', target="_blank"):
        # Проверяем первые 5 символов, если совпадают с vkiss значит нужная
        # ссылка
        if link.get("href")[:5] == "vkiss":
            # Вытягиваем ID профиля, он начинается с 17 символа в вытянутой
            # ссылке
            profile_id = link.get("href")[17:]
            profiles_id.append(profile_id)

    return profiles_id


def collect_info_from_profile(profile_id):
    """Сбор информации о профиле.

    Keyword arguments:
    profile_id -- ID профиля с которого будет собираться информация
    """
    # Открываем страницу профиля
    session = requests.Session()
    response = send_request(session=session, method="GET",
                            link="https://www.natashaclub.com/" + profile_id)
    profile_page = get_parsed_page(response)

    # Начинаем сбор информации

    # Имя
    name = \
        profile_page.find("td", class_="ContentHeaders").find("h1").text.split(
                ":")[0]
    if not name:
        name = "Not specified"

    # Никнейм профиля
    nickname = profile_page.find_all("div", class_="GreenText")[0].get_text()

    # Парсим таблицу что находится возле фото профиля
    table = profile_page.find_all("table", class_="text2")
    # Вытягиваем все
    info = []
    for ul in table[0].find_all("ul", style="list-style-type: none;"):
        row = ul.find_all("li")
        for item in row:
            info.append(item.text)

        first_row = info[0].split(" ")
        second_row = info[1].split(", ")
        third_row = info[2].split(", ")
        fourth_row = info[3]
        fifth_row = info[4]
        sixth_row = info[5]
        seventh_row = info[6]
        # Возраст
        age = specified(first_row, 0)
        if age != 'Not specified':
            age = int(age[:-3])
        # Пол
        gender = specified(first_row, 2)
        if gender != 'Not specified':
            gender = gender[:-1]
        # Зодиак
        zodiac = specified(first_row, 3)
        # Город
        city = specified(second_row, 0)
        # Страна
        country = specified(second_row, 1)

        # Знание языков
        languages = {}
        # Проверяем или не пуста информация об этом
        if len(third_row[0]) > 0:
            for item in third_row:
                # Проверяем указан ли уровень владения языком
                values = item.split("(")
                if len(values) == 2:
                    language = values[0]
                    level = values[1][:-1]
                    languages[language] = level
                # Указан только язык
                elif len(values) == 1:
                    language = values[0]
                    level = "Not specified"
                    languages[language] = level
        # Ничего не указано
        else:
            language = "Not Specified"
            level = "Not specified"
            languages[language] = level

        # Вид деятельности / кем работает
        occupation = specified(fourth_row)
        # Есть ли дети
        children = specified(fifth_row)

        # Последний раз в онлайне
        date_string = " ".join(sixth_row.split(" ")[2:])
        last_online = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")

        # Сколько кредитов стоит, написать письмо
        credit_str = seventh_row.split(" ")[0]
        cost_credits_function = lambda x: float(x) if len(x) > 0 else 0.0
        cost_credits = cost_credits_function(credit_str)

    # Собираем информацию с таблицы PERSONAL DETAILS и DETAILS OF THE PERSON
    # YOU ARE LOOKING FOR
    table_personal_details = profile_page.find_all("table",
                                                   class_="profile_table")
    personal_details = {}
    for row in table_personal_details[0].find_all("tr")[2].find_all("tr"):
        key = row.find("td", class_="profile_td_1")
        value = row.find("td", class_="profile_td_2")
        if value and key:
            key = key.text
            value = " ".join(value.text.split())
            if len(value) == 0:
                value = "Not specified"
            # Проверка есть ли 1 в value означает что пользователь указал
            # свой рост (все росты начинаются с цифры 1)
            if key == "Height" and "1" in value:
                value = value.split("(")[1][:-3]
            personal_details[key] = value

    # Извелкаем DESCRIPTION
    profile_desc_text = profile_page.find_all("td", class_="profile_desc_text")
    description = " ".join(profile_desc_text[0].text.split())

    # Извелкаем IDEAL MATCH DESCRIPTION
    ideal_match_description = " ".join(profile_desc_text[1].text.split())

    # Собираем рейтинг и сколько человек проголосовало
    rating_table = profile_page.find_all("table", class_="rate_profile")
    rate = float(rating_table[0].find_all("table", class_="text2")[0].find(
            "td").text.split(" ")[1])
    votes = int(rating_table[0].find_all("table", class_="text2")[1].find(
            "td").text.split(" ")[1])

    # Формируем словарь, который имеет в себе все собранные данные
    collected_data = {"Name": name, "Nickname": nickname, "Age": age,
                      "Sex": gender, "Zodiac": zodiac,
                      "Country": country, "City": city, "Languages": languages,
                      "Occupation": occupation,
                      "Children": children, "Last online": str(last_online),
                      "Credits to open letter": cost_credits}
    collected_data.update(personal_details)
    collected_data.update(
            {"Rate": rate, "Votes": votes, "Description": description,
             "Ideal match description": ideal_match_description})

    # Данные сформированы и функция их возвращает как словарь
    return collected_data