# Библиотека для подключения к почтовому серверу и взаимодействия с ним
import smtplib
# Экзепляр Email сообщения
from email.message import EmailMessage

from db_models import EmailInfo, Session


def send_email_instruction(email_to):
    """Функция выполняет отправку сообщения на указанный email адресс с
    инструкцией для регистрации в системе NatalyBot

    Keyword arguments:
    email_to -- адрессат, которому будет доставлено сообщение с инструкцией

    """

    # Настройки по умолчанию
    db_session = Session()
    query = db_session.query(EmailInfo.email_host,
                             EmailInfo.email_port,
                             EmailInfo.email_address,
                             EmailInfo.email_password,
                             EmailInfo.email_subject,
                             EmailInfo.email_text).filter(
            EmailInfo.email_description == 'default_register')
    default_email_info = query.all()

    if len(default_email_info) > 0:
        HOST, PORT, EMAIL, PASSWORD, SUBJECT, TEXT = default_email_info[0]
    db_session.close()

    # Соединяемся с почтовым сервисом
    smtpObj = smtplib.SMTP(HOST, PORT)
    # Шифруем сообщение
    smtpObj.starttls()
    # Логинимся на почтовый ящик
    smtpObj.login(EMAIL, PASSWORD)

    # Экзепляр Email сообщения
    message = EmailMessage()
    # Текст сообщения
    message.set_content(TEXT)
    # Хедер сообщения. Нужен в соотвествии со стандартами Google
    # Тема сообщения
    message['Subject'] = SUBJECT
    # Почта с которой идет отправка
    message['From'] = EMAIL
    # Кому отправляем
    message['To'] = email_to

    # Отправляем сообщение через наш почтовый сервер
    smtpObj.send_message(message)

    # Закрываем соединение с почтовым сервером
    smtpObj.quit()
