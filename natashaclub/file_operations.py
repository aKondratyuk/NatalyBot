import os
import re
from itertools import islice

import pandas as pd
from openpyxl import load_workbook

from scraping import collect_info_from_profile


def read_file(path_to_file):
    """Фукнция для открытия файла и его чтения

    Keyword arguments:
    path_to_file -- путь к файлу
    """
    try:
        file = open(path_to_file, "r")
        try:
            data = file.read()
            return data
        except Exception as e:
            print(e)
        finally:
            file.close()
    except Exception as ex:
        print(ex)


def read_csv_file(path_to_file):
    """Фукнция для открытия csv файла и его чтения

    Keyword arguments:
    path_to_file -- путь к файлу
    """
    try:
        data = pd.read_csv(path_to_file)
        return data
    except Exception as ex:
        print(ex)


def read_excel_file(path_to_file):
    """Фукнция для открытия excle файла и его чтения

    Keyword arguments:
    path_to_file -- путь к файлу
    """
    try:
        wb = load_workbook(path_to_file)
        return wb
    except Exception as ex:
        print(ex)


def get_list_of_all_files_in_directory(path_to_directory):
    """Фукнция показывает все файлы содержащиеся в папке

    Keyword arguments:
    path_to_directory -- путь к директории
    """
    return os.listdir(path_to_directory)


def get_sheet_values(sheet):
    """Возвращает данные, которые находятся в Листе excel файла

    Keyword arguments:
    sheet -- действущий лист
    """
    data = sheet.values
    cols = next(data)[1:]
    data = list(data)
    idx = [r[0] for r in data]
    data = (islice(r, 1, None) for r in data)
    df = pd.DataFrame(data, index=idx, columns=cols)

    return df


def create_custom_message(messager_profile_id, receiver_profile_id,
                          path_to_file):
    """Функция для создания кастомного сообщения. Есть шаблон письма. В нем
    есть ключевые места по тиму {name}
    функция будет заменять эти ключевые слова на собранные данные с
    получателя и отправителя пиьсма

    Keyword arguments:
    messager_profile_id -- ID того кто отправляет
    receiver_profile_id -- ID того кто отправляет
    path_to_file -- путь к файлу
    """
    receiver_data = collect_info_from_profile(receiver_profile_id)
    messager_data = collect_info_from_profile(messager_profile_id)
    message_text = read_file(path_to_file)

    # Receiver name check
    if receiver_data["Name"] == "Not specified":
        receiver_data["Name"] = receiver_data["Nickname"]
    # add to receiver_data My name, to replace it in 'for' cycle
    receiver_data['my_name'] = messager_data["Name"]

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
