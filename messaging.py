import re

from db_models import MessageAnchors, MessageTemplates, Tagging, Texts
from scraping import collect_info_from_profile, send_request


def create_custom_message(messager_profile_id, receiver_profile_id,
                          message_text):
    """Функция для создания кастомного сообщения. Есть шаблон письма. В нем
    есть ключевые места по тиму {name}
    функция будет заменять эти ключевые слова на собранные данные с
    получателя и отправителя пиьсма

    Keyword arguments:
    messager_profile_id -- ID того кто отправляет
    receiver_profile_id -- ID того кто отправляет
    path_to_file -- путь к файлу
    """
    # МОЖНО ЗАМЕНИТЬ НА ФУНКЦИЮ ВЫТЯГИВАНИЯ С БАЗЫ!!!
    receiver_data = collect_info_from_profile(receiver_profile_id)
    sender_data = collect_info_from_profile(messager_profile_id)

    # Провеяем или имя найдено, если нет то будем обращаться по никнейму, он есть в любом случае
    if receiver_data["Name"] == "Not specified":
        receiver_data["Name"] = receiver_data["Nickname"]

    # add to receiver_data My name, to replace it in 'for' cycle
    receiver_data['name lady'] = sender_data["Name"]


    #message_text = message_text.format(name=receiver_name, my_name=messager_name, country=country)
    for key in receiver_data.keys():
        #Check if user is dummy, and not use paragraph character
        message_text = re.sub(' {3,}', '\n', message_text)

        #Find key in text
        if message_text.find("{"+key+"}") + message_text.find("{"+key.lower()+"}") != -2:
            if receiver_data[key] == "Not specified":
                #print(re.sub("\n?[^\n]*{" + key + "}[^\n]*[\n]? {4,}", '', message_text))
                #replace all paragraph with 'Not Specified' key to empty string
                #args of re.sub: pattern, text fragment to replace, text where replace
                #full pattern:   \n?[^\n]*{Country}[^\n]*[\n]?
                message_text = re.sub("\n?[^\n]*{" + key + "}[^\n]*[\n]?", '', message_text)
                message_text = re.sub("\n?[^\n]*{" + key.lower() + "}[^\n]*[\n]?", '', message_text)
                #We don't need to continue replacement with Not specified key
                continue

            #Check if key is Name, Country
            text_to_replace = receiver_data[key]
            if key not in ['name', 'name lady', 'country', 'nickname', 'city']:
                text_to_replace = text_to_replace

            #Replacement
            message_text = message_text.replace("{"+key+"}", text_to_replace)
            message_text = message_text.replace("{"+key.lower()+"}", text_to_replace)

    return message_text


def create_message_response(template_number, sender_profile_id, receiver_profile_id, message_text):
    """Формирование шаблонного ответа на входящее письмо

    Keyword arguments:
    template_number -- номер шаблона, который будет использоваться за основу
    receiver_profile_id -- ID профиля которому будет отправлено сообщение
    message_text -- текст входящего письма от профиля
    """
    from control_panel import db_get_rows_2
    # Вытягиваем шаблон по номеру
    text_template = db_get_rows_2([Texts.text], [
              MessageTemplates.profile_id == receiver_profile_id,
              MessageTemplates.text_number == template_number,
              MessageTemplates.text_id == Texts.text_id])
    text_template = create_custom_message(sender_profile_id, receiver_profile_id, text_template[0][0])
    # Вытягиваем все якоря с базы
    anchors = db_get_rows_2([Tagging.tag], [
                MessageAnchors.profile_id == sender_profile_id,
                MessageAnchors.used == False,
                MessageAnchors.text_id == Texts.text_id,
                Texts.text_id == Tagging.text_id])
    # В тексте шаблона должно находиться {} - это место, где текст делится пополам До Якоре и После.
    # И в первую его часть в самый конец добавляются все тексты якорей
    temp_text_template = text_template.split("{}")
    i = 0
    for anchor in anchors:
        if anchor[0] in message_text:
            # Указываем индекс, куда помещяется текст якоря в списке. Он будет всегда добавляться перед {}
            i += 1
            anchor_text = db_get_rows_2([Texts.text, Texts.text_id], [
                 MessageAnchors.profile_id == sender_profile_id,
                 MessageAnchors.used == False,
                 MessageAnchors.text_id == Texts.text_id,
                 Texts.text_id == Tagging.text_id,
                 Tagging.tag == anchor[0]])
            # Вставляем текст якора
            temp_text_template.insert(i, anchor)
    # Соединяем все элементы списка в единый текст. Если якорей так и не было, то текст будет теперь без {}
    text_template = "".join(temp_text_template)

    return text_template


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
                            link=f"https://www.natashaclub.com/compose.php?ID={receiver_profile_id}", data=data)
    # Функция возвращает ответ сервера на запрос по отправке сообщения
    return response
