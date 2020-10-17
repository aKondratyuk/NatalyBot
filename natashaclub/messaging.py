from scraping import send_request


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
