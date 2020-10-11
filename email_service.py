# Библиотека для подключения к почтовому серверу и взаимодействия с ним
import smtplib
# Экзепляр Email сообщения
from email.message import EmailMessage

# Настройки по умолчанию
HOST = "euhost01.twinservers.net"
PORT = 587
EMAIL = "ladyjuly@a2.kh.ua"
PASSWORD = "iX}srvOfUH!p"
SUBJECT = "Инструкция для регистрации в системе NatalyBot"
TEXT = "Hello, admin writing to you!"


def send_email_instruction(email_to):
    """Функция выполняет отправку сообщения на указанный email адресс с инструкцией для регистрации в системе NatalyBot

    Keyword arguments:
    email_to -- адрессат, которому будет доставлено сообщение с инструкцией

    """
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
