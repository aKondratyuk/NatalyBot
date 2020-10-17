from datetime import datetime

import requests
from file_operations import create_custom_message, \
    get_list_of_all_files_in_directory, get_sheet_values, read_excel_file
from messaging import message
from tabulate import tabulate

from scraping import collect_info_from_profile, get_id_profiles, \
    search_for_profiles, send_request
from verification import first_letter_sent, forbidden_profile, limit_out, \
    not_in_age_bounds, profile_country, profile_deleted, profile_in_inbox


def check_for_file(session, my_age, profile_id, idx):
    try:
        if profile_in_inbox(session, profile_id)[0]:
            print(f"{idx}. Неудалось отправить сообщение {profile_id}",
                  datetime.now(), "INBOX")
            return "INBOX"
        elif limit_out(session, profile_id):
            print(f"{idx}. Неудалось отправить сообщение {profile_id}",
                  datetime.now(), "LIMIT OUT")
            return "LIMIT OUT"
        elif profile_deleted(profile_id):
            print(f"{idx}. Неудалось отправить сообщение {profile_id}",
                  datetime.now(), "PROFILE DELETED")
            return "PROFILE DELETED"
        elif forbidden_profile(profile_id):
            print(f"{idx}. Неудалось отправить сообщение {profile_id}",
                  datetime.now(), "FORBIDDEN")
            return "FORBIDDEN"
        elif not_in_age_bounds(my_age, profile_id):
            print(f"{idx}. Неудалось отправить сообщение {profile_id}",
                  datetime.now(), "AGE IS YOUNGER")
            return "AGE IS YOUNGER"
        elif first_letter_sent(session, profile_id):
            print(f"{idx}. Неудалось отправить сообщение {profile_id}",
                  datetime.now(), "FIRST LETTER SENT")
            return "FIRST LETTER SENT"
        elif profile_country(profile_id):
            print(f"{idx}. Неудалось отправить сообщение {profile_id}",
                  datetime.now(), "INVALID COUNTRY")
            return "INVALID COUNTRY"
    except Exception as ex:
        print(ex)

    return False


def check_for_filter(session, profile_id, idx):
    try:
        if profile_in_inbox(session, profile_id)[0]:
            print(f"{idx}. Неудалось отправить сообщение {profile_id}",
                  datetime.now(), "INBOX")
            return "INBOX"
        elif limit_out(session, profile_id):
            print(f"{idx}. Неудалось отправить сообщение {profile_id}",
                  datetime.now(), "LIMIT OUT")
            return "LIMIT OUT"
        elif profile_deleted(profile_id):
            print(f"{idx}. Неудалось отправить сообщение {profile_id}",
                  datetime.now(), "PROFILE DELETED")
            return "PROFILE DELETED"
        elif forbidden_profile(profile_id):
            print(f"{idx}. Неудалось отправить сообщение {profile_id}",
                  datetime.now(), "FORBIDDEN")
            return "FORBIDDEN"
        elif first_letter_sent(session, profile_id):
            print(f"{idx}. Неудалось отправить сообщение {profile_id}",
                  datetime.now(), "FIRST LETTER SENT")
            return "FIRST LETTER SENT"
        elif profile_country(profile_id):
            print(f"{idx}. Неудалось отправить сообщение {profile_id}",
                  datetime.now(), "INVALID COUNTRY")
            return "INVALID COUNTRY"
    except Exception as ex:
        print(ex)

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


def tabulated_table(sheet):
    """Оформление таблицы и ее вывод

    Keyword arguments:
    sheet -- лист со значениями
    """
    data = get_sheet_values(sheet)
    new_data = []
    for i, profile_id in enumerate(data["Login"]):
        try:
            profile = collect_info_from_profile(str(profile_id))
        except Exception as ex:
            print(
                f"Профиль номер {i + 1} с логином {profile_id} не существует")
        row = [i + 1, profile_id, data["Password"][i + 1], profile["Name"],
               profile["Nickname"], profile["Age"],
               data["Path to text file"][i + 1]]
        new_data.append(row)
    header = ["Номер", "Логин", "Пароль", "Имя", "Никнейм", "Возраст",
              "Имя инвайта"]
    print(tabulate(new_data, headers=header, tablefmt="grid"))

    return data


if __name__ == "__main__":
    # pass
    sheet = "Empty"
    table = "Empty"
    while True:
        print("ГЛАВНОЕ МЕНЮ")
        print("1. Загрузить аккаунты")
        print("2. Список загруженных аккаунтов")
        print("3. Рассылка по фильтру")
        print("4. Рассылка по списку")
        choice = input("\nВыберите пункт меню: \n")
        if choice == "1":
            print("Выберите excel файл с которого хотите загрузить аккаунты")
            files = get_list_of_all_files_in_directory("accounts")
            if len(files) > 0:
                for i, file_name in enumerate(files):
                    print(f"{i + 1}. {file_name}")
                i = input("\nВыберите номер файла: ")
                if int(i) <= len(files):
                    wb = read_excel_file("accounts/" + files[int(i) - 1])
                    sheets = wb.sheetnames
                    for i, sheet in enumerate(sheets):
                        print(f"{i + 1}. {sheet}")
                    i = input("\nВыберите нужный лист: ")
                    if int(i) <= len(sheets):
                        sheet = wb[sheets[int(i) - 1]]
                        print("Аккаунты успешно загружены!\n")
                    else:
                        print("Нету такого листа!\n")
                else:
                    print("Такого файла нету\n")
            else:
                print("Папка пуста\n")

        elif choice == "2":
            if sheet == "Empty":
                print("Аккаунты еще не загружены!\n")
            else:
                tabulated_table(sheet)
        elif choice == "3":
            looking_for = "male"
            date_of_birth_end = "40"
            page = 1
            messages_need_to_be_sent = 30
            photos_only = "off"
            if sheet == "Empty":
                print("Аккаунты еще не загружены!\n")
            else:
                while True:
                    print("\nФИЛЬТР:")
                    print("Я - (ставится пол профиля автоматически)")
                    if looking_for == "male":
                        print("Ищу - мужчины")
                    else:
                        print("Ищу - женщины")
                    print(
                        "Возраст от - (ставится возраст профиля "
                        "автоматически)")
                    print(f"Возраст до - {date_of_birth_end}")
                    print(f"Рассылка начинается со страницы - {page}")
                    print(
                        f"Будет отправлено сообщений - "
                        f"{messages_need_to_be_sent}")
                    if photos_only == "off":
                        print("Поиск только с фото - нет\n")
                    else:
                        print("Поиск только с фото - да")
                    print("1. Изменить фильтр")
                    print("2. Выбрать аккаунты, которые будут рассылать")
                    print("3. Начать рассылку всех аккаунтов")
                    print("0. Вернуться к главному меню")
                    choice = input("\nВыберите пункт меню: \n")
                    if choice == "1":
                        print("Выберите что изменить: ")
                        print("1. Ищу")
                        print("2. Возраст до")
                        print("3. Будет отправлено сообщений")
                        print("4. Страница")
                        print("5. Только с фото")
                        choice = input("\nВыберите что изменить: \n")
                        if choice == "1":
                            looking_for = "female"
                            print("Изменено на: Ищу - женщины")
                        elif choice == "2":
                            date_of_birth_end = input("Укажите возраст до: ")
                            print(
                                f"Изменено на: Возраст до - "
                                f"{date_of_birth_end}")
                        elif choice == "3":
                            messages_need_to_be_sent = int(
                                input("Укажите количетсво сообщний: "))
                            print(
                                f"Изменено на: Будет отправлено сообщений - "
                                f"{messages_need_to_be_sent}")
                        elif choice == "4":
                            page = int(input(
                                "Укажите номер страницы с какой начать: "))
                            print(
                                f"Изменено на: рассылка начинается со "
                                f"страницы - {page}")
                        elif choice == "5":
                            photos_only = "on"
                            print(f"Изменено на: только с фото - да")
                        else:
                            print("\nНету такого пункта в меню\n")
                    elif choice == "2":
                        data = tabulated_table(sheet)
                        choice = input(
                            "\nНапишите через запятую номера аккаунтов: \n")
                        numbers = [int(num) for num in choice.split(",")]
                        for i in numbers:
                            profile_login, password = str(data["Login"][i]), \
                                                      data["Password"][i]
                            values = login(profile_login, password)
                            if values:
                                session, my_profile_id = values
                                my_data = collect_info_from_profile(
                                    my_profile_id)
                                nickname = my_data["Nickname"]
                                print(
                                    f"\nПРОФИЛЬ {nickname} НАЧИНАЕТ "
                                    f"РАССЫЛКУ\n")
                                idx = 1
                                messages_has_sent = 0
                                STOP = False
                                while messages_has_sent != \
                                        messages_need_to_be_sent:
                                    if STOP:
                                        break
                                    profiles = search_for_profiles(
                                            my_data["Sex"], looking_for,
                                            my_data["Age"],
                                            date_of_birth_end, page,
                                            photos_only)
                                    profiles_id = get_id_profiles(profiles)
                                    for profile_id in profiles_id:
                                        check_response = check_for_filter(
                                            session, profile_id, idx)
                                        idx += 1
                                        if check_response:
                                            if check_response == "LIMIT OUT":
                                                STOP = True
                                        else:
                                            invite_path = "invite messages/"\
                                                          + \
                                                          data[
                                                              "Path to text " \
                                                              "file"][
                                                              i]
                                            message_text = \
                                                create_custom_message(
                                                my_profile_id, profile_id,
                                                invite_path)
                                            message(session, profile_id,
                                                    message_text)
                                            print(
                                                f"{idx}. Удалось отправить "
                                                f"сообщение {profile_id}. "
                                                f"Осталось отправить"
                                                f" {messages_need_to_be_sent - messages_has_sent}",
                                                datetime.now())
                                            idx += 1
                                            messages_has_sent += 1
                                            if messages_has_sent == \
                                                    messages_need_to_be_sent:
                                                print(
                                                    f"\nПРОФИЛЬ {nickname} "
                                                    f"ЗАВЕРШИЛ РАССЫЛКУ\n")
                                                break
                                    page += 1
                            else:
                                print(
                                    f"Неверный логин или пароль у профиля "
                                    f"{profile_login}")
                    elif choice == "3":
                        data = tabulated_table(sheet)
                        for i in range(1, len(data["Login"]) + 1):
                            profile_login, password = str(data["Login"][i]), \
                                                      data["Password"][i]
                            values = login(profile_login, password)
                            if values:
                                session, my_profile_id = values
                                my_data = collect_info_from_profile(
                                    my_profile_id)
                                if int(my_data["Age"]) > int(
                                        date_of_birth_end):
                                    print(
                                        f'Аккаунт номер {i} был пропущен, '
                                        f'потому что его возраст больше '
                                        f'максимального')
                                    continue
                                nickname = my_data["Nickname"]
                                print(
                                    f"\nПРОФИЛЬ {nickname} НАЧИНАЕТ "
                                    f"РАССЫЛКУ\n")
                                idx = 1
                                messages_has_sent = 0
                                STOP = False
                                while messages_has_sent != \
                                        messages_need_to_be_sent:
                                    if STOP:
                                        break
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
                                            print(
                                                f'Сайт не отобразил людей на '
                                                f'10 страницах подряд\n'
                                                f'Рассылка с профиля номер '
                                                f'{i} пропущена')
                                            messages_has_sent = \
                                                messages_need_to_be_sent
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
                                            session, profile_id, idx)
                                        idx += 1
                                        if check_response:
                                            if check_response == "LIMIT OUT":
                                                STOP = True
                                                break
                                        else:
                                            invite_path = "invite messages/"\
                                                          + \
                                                          data[
                                                              "Path to text " \
                                                              "file"][
                                                              i]
                                            try:
                                                message_text = \
                                                    create_custom_message(
                                                    my_profile_id, profile_id,
                                                    invite_path)
                                            except TypeError:
                                                print(
                                                    f"У профиля номер {i} "
                                                    f"указан несуществующий "
                                                    f"файл-шаблон сообщения\n"
                                                    f"Профиль пропущен")
                                                messages_has_sent = \
                                                    messages_need_to_be_sent
                                                break
                                            message(session, profile_id,
                                                    message_text)
                                            messages_has_sent += 1
                                            print(
                                                f"{idx}. Удалось отправить "
                                                f"сообщение {profile_id}. "
                                                f"Осталось отправить"
                                                f" {messages_need_to_be_sent - messages_has_sent}",
                                                datetime.now())
                                            idx += 1
                                            if messages_has_sent == \
                                                    messages_need_to_be_sent:
                                                print(
                                                    f"\nПРОФИЛЬ {nickname} "
                                                    f"ЗАВЕРШИЛ РАССЫЛКУ\n")
                                                break
                                    page += 1
                    elif choice == "0":
                        break
                    else:
                        print("\nНету такого пункта в меню")
        elif choice == "4":
            print("Выберите excel файл с которого хотите загрузить аккаунты")
            files = get_list_of_all_files_in_directory("payers")
            if len(files) > 0:
                for i, file_name in enumerate(files):
                    print(f"{i + 1}. {file_name}")
                i = input("\nВыберите номер файла: ")
                if int(i) <= len(files):
                    wb_payers = read_excel_file("payers/" + files[int(i) - 1])
                    sheets_payers = wb_payers.sheetnames
                    for i, sheet_payer in enumerate(sheets_payers):
                        print(f"{i + 1}. {sheet_payer}")
                    i = input("\nВыберите нужный лист: ")
                    if int(i) <= len(sheets_payers):
                        sheet_payer = wb_payers[sheets_payers[int(i) - 1]]
                        payers = get_sheet_values(sheet_payer)
                        temp = []
                        for payer in payers["ID"]:
                            temp.append(str(payer).strip())
                        payers = temp
                        print("Список успешно загружен!\n")
                        messages_need_to_be_sent = 30
                        # print(f"Будет отправлено {
                        # messages_need_to_be_sent} сообщений\n")
                        # print("1. Изменить количество отправляемых
                        # сообщений")
                        # print("2. Выбрать аккаунты, которые будут рассылать")
                        # print("3. Начать рассылку всех аккаунтов")
                        # print("0. Вернуться к главному меню")
                        # choice = input("\nВыберите пункт меню: \n")
                        while True:
                            print(
                                f"Будет отправлено "
                                f"{messages_need_to_be_sent} сообщений\n")
                            print(
                                "1. Изменить количество отправляемых "
                                "сообщений")
                            print(
                                "2. Выбрать аккаунты, которые будут рассылать")
                            print("3. Начать рассылку всех аккаунтов")
                            print("0. Вернуться к главному меню")
                            choice = input("\nВыберите пункт меню: \n")
                            if choice == "1":
                                messages_need_to_be_sent = int(
                                    input("Укажите количетсво сообщений: "))
                            elif choice == "2":
                                data = tabulated_table(sheet)
                                choice = input(
                                    "\nНапишите через запятую номера "
                                    "аккаунтов: \n")
                                numbers = [int(num) for num in
                                           choice.split(",")]
                                for i in numbers:
                                    profile_login, password = str(
                                            data["Login"][i]), \
                                                              data["Password"][
                                                                  i]
                                    values = login(profile_login, password)
                                    if values:
                                        session, my_profile_id = values
                                        my_data = collect_info_from_profile(
                                            my_profile_id)
                                        nickname = my_data["Nickname"]
                                        my_age = my_data["Age"]
                                        print(
                                            f"\nПРОФИЛЬ {nickname} НАЧИНАЕТ "
                                            f"РАССЫЛКУ\n")
                                        idx = 1
                                        messages_has_sent = 0
                                        STOP = False
                                        for profile_id in payers:
                                            if STOP:
                                                break
                                            check_response = check_for_file(
                                                session, my_age, profile_id,
                                                idx)
                                            idx += 1
                                            if check_response:
                                                if check_response == "LIMIT " \
                                                                     "OUT":
                                                    STOP = True
                                            else:
                                                invite_path = "invite " \
                                                              "messages/" + \
                                                              data[
                                                                  "Path to " \
                                                                  "text file"][
                                                                  i]
                                                message_text = \
                                                    create_custom_message(
                                                    my_profile_id, profile_id,
                                                    invite_path)
                                                message(session, profile_id,
                                                        message_text)
                                                print(
                                                    f"{idx}. Удалось "
                                                    f"отправить сообщение "
                                                    f"{profile_id}. Осталось "
                                                    f"отправить"
                                                    f" {messages_need_to_be_sent - messages_has_sent}",
                                                    datetime.now())
                                                idx += 1
                                                messages_has_sent += 1
                                                if messages_has_sent == messages_need_to_be_sent:
                                                    print(
                                                        f"\nПРОФИЛЬ {nickname} ЗАВЕРШИЛ РАССЫЛКУ\n")
                                                    break
                                    else:
                                        print(
                                            f"Неверный логин или пароль у профиля {profile_login}")
                            elif choice == "3":
                                data = tabulated_table(sheet)
                                for i in range(1, len(data["Login"]) + 1):
                                    profile_login, password = str(
                                            data["Login"][i]), \
                                                              data["Password"][
                                                                  i]
                                    values = login(profile_login, password)
                                    if values:
                                        session, my_profile_id = values
                                        my_data = collect_info_from_profile(
                                            my_profile_id)
                                        nickname = my_data["Nickname"]
                                        my_age = my_data["Age"]
                                        print(
                                            f"\nПРОФИЛЬ {nickname} НАЧИНАЕТ РАССЫЛКУ\n")
                                        idx = 1
                                        messages_has_sent = 0
                                        STOP = False
                                        for profile_id in payers:
                                            if STOP:
                                                break
                                            check_response = check_for_file(
                                                session, my_age, profile_id,
                                                idx)
                                            idx += 1
                                            if check_response:
                                                if check_response == "LIMIT OUT":
                                                    STOP = True
                                                    break
                                            else:
                                                invite_path = "invite messages/" + \
                                                              data[
                                                                  "Path to text file"][
                                                                  i]
                                                message_text = create_custom_message(
                                                    my_profile_id, profile_id,
                                                    invite_path)
                                                message(session, profile_id,
                                                        message_text)
                                                messages_has_sent += 1
                                                print(
                                                    f"{idx}. Удалось отправить сообщение {profile_id}. Осталось отправить"
                                                    f" {messages_need_to_be_sent - messages_has_sent}",
                                                    datetime.now())
                                                idx += 1
                                                if messages_has_sent == messages_need_to_be_sent:
                                                    print(
                                                        f"\nПРОФИЛЬ {nickname} ЗАВЕРШИЛ РАССЫЛКУ\n")
                                                    break
                            elif choice == "0":
                                break
                            else:
                                print("\nНету такого пункта в меню")
                    else:
                        print("Нету такого листа!\n")
                else:
                    print("Такого файла нету\n")
            else:
                print("Папка пуста\n")
        else:
            print("\nНесущетсвует такой опции. Повторите ввод!\n")
