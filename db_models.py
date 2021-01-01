# coding: utf8
import logging
import socket
import traceback
from uuid import uuid4

from flask import request
from flask_login import current_user
from sqlalchemy import Column, create_engine
from sqlalchemy.dialects.mysql import BINARY, BOOLEAN, FLOAT, INTEGER, \
    MEDIUMINT, TIMESTAMP, TINYINT, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_ADRESS = "localhost:3306"
DB_DIALECT = "mysql"
DB_DRIVER = "pymysql"
DB_ENCODING = "charset=utf8"
DB_NAME = "matchlov_nataly_schema"
DB_PASS = "Vi3mMe170z"
DB_USER = "matchlov_admin"
PYTHONUNBUFFERED = 1

engine = create_engine(f"{DB_DIALECT}+"
                       f"{DB_DRIVER}://"
                       f"{DB_USER}:"
                       f"{DB_PASS}@"
                       f"{DB_ADRESS}/"
                       f"{DB_NAME}"
                       f"?{DB_ENCODING}",
                       pool_recycle=3600,
                       encoding='utf8')

Base = declarative_base()
Session = sessionmaker()
Session.configure(bind=engine)
logger_db_session = Session()


class Categories(Base):
    __tablename__ = 'Categories'
    category_name = Column(VARCHAR(190), primary_key=True)

    def __repr__(self):
        return "<Categories(category_name='%s')>" % (
                self.category_name)


class CategoryLevel(Base):
    __tablename__ = 'Category_level'
    level_name = Column(VARCHAR(190), primary_key=True)
    category_name = Column(VARCHAR(190), primary_key=True)

    def __repr__(self):
        return "<Category_level(level_name='%s'," \
               "level_name='%s')>" % (
                self.level_name, self.category_name)


class ChatSessions(Base):
    __tablename__ = 'Chat_sessions'
    chat_id = Column(BINARY(16), primary_key=True)
    profile_id = Column(VARCHAR(190), primary_key=True)
    email_address = Column(VARCHAR(190), default=None)

    def __repr__(self):
        return "<Categories(chat_id='%s', profile_id='%s'," \
               "email_address='%s')>" % (
                       self.chat_id, self.profile_id,
                       self.email_address)


class Chats(Base):
    __tablename__ = 'Chats'
    chat_id = Column(BINARY(16), primary_key=True)

    def __repr__(self):
        return "<Chats(chat_id='%s')>" % self.chat_id


class Ethnicities(Base):
    __tablename__ = 'Ethnicities'
    ethnicity_name = Column(VARCHAR(190), primary_key=True)

    def __repr__(self):
        return "<Ethnicities(ethnicity_name='%s')>" % self.ethnicity_name


class Languages(Base):
    __tablename__ = 'Languages'
    language = Column(VARCHAR(190), primary_key=True)

    def __repr__(self):
        return "<Languages(language='%s')>" % self.language


class Levels(Base):
    __tablename__ = 'Levels'
    level_name = Column(VARCHAR(190), primary_key=True)

    def __repr__(self):
        return "<Levels(level_name='%s')>" % self.level_name


class Logs(Base):
    __tablename__ = 'Logs'
    log_id = Column(BINARY(16), primary_key=True)
    login = Column(VARCHAR(190), nullable=False)
    category = Column(VARCHAR(190), nullable=False)
    message = Column(VARCHAR(10000), nullable=False)
    ip = Column(VARCHAR(20))
    create_time = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return "<Logs(log_id='%s', login='%s', category='%s', " \
               "message='%s', ip='%s', create_time='%s', )>" % (
                       self.log_id, self.login, self.category,
                       self.message[:100] + '...', self.ip, self.create_time)


class Messages(Base):
    __tablename__ = 'Messages'
    message_token = Column(BINARY(16), primary_key=True)
    chat_id = Column(BINARY(16))
    profile_id = Column(VARCHAR(20))
    send_time = Column(TIMESTAMP)
    text_id = Column(BINARY(16))
    viewed = Column(BOOLEAN, default=0)
    delay = Column(BOOLEAN, default=0)

    def __repr__(self):
        return "<Messages(message_token='%s', chat_id='%s', " \
               "profile_id='%s', send_time='%s', " \
               "text_id='%s', viewed='%s', " \
               "delay='%s')>" % (
                       self.message_token, self.chat_id,
                       self.profile_id, self.send_time,
                       self.text_id, self.viewed,
                       self.delay)


class PrivilegesAssigns(Base):
    __tablename__ = 'Privileges_assigns'
    user_role = Column(VARCHAR(190), primary_key=True)
    privilege_name = Column(VARCHAR(190), primary_key=True)
    privilege_status = Column(BOOLEAN)

    def __repr__(self):
        return "<Privileges_assigns(user_role='%s', " \
               "privilege_name='%s', privilege_status='%s')>" % (
                       self.user_role,
                       self.privilege_name,
                       self.privilege_status)


class Privileges(Base):
    __tablename__ = 'Privileges'
    privilege_name = Column(VARCHAR(190), primary_key=True)

    def __repr__(self):
        return "<Privileges(privilege_name='%s')>" % (
                self.privilege_name)


class ProfileCategories(Base):
    __tablename__ = 'Profile_categories'
    level_name = Column(VARCHAR(190), primary_key=True)
    category_name = Column(VARCHAR(190), primary_key=True)
    profile_id = Column(VARCHAR(20), primary_key=True)

    def __repr__(self):
        return "<Profile_categories(level_name='%s', " \
               "category_name='%s', " \
               "profile_id='%s')>" % (
                       self.level_name,
                       self.category_name,
                       self.profile_id)


class ProfileDescription(Base):
    __tablename__ = 'Profile_description'
    profile_id = Column(VARCHAR(190), primary_key=True)
    zodiac = Column(VARCHAR(190))
    ethnicity_name = Column(VARCHAR(20))
    religion = Column(VARCHAR(190))
    age = Column(TINYINT(4))
    city = Column(VARCHAR(190))
    credits_to_open_letter = Column(FLOAT)
    description = Column(VARCHAR(10000))
    income = Column(VARCHAR(190))
    last_online = Column(VARCHAR(190))
    looking_for_an_age_range = Column(VARCHAR(190))
    name = Column(VARCHAR(190))
    nickname = Column(VARCHAR(190))
    occupation = Column(VARCHAR(190))
    rate = Column(FLOAT)
    sex = Column(VARCHAR(190))
    votes = Column(MEDIUMINT(9))
    country = Column(VARCHAR(190))

    def __repr__(self):
        return "<Profile_description(" \
               "profile_id='%s', zodiac='%s', " \
               "ethnicity_name='%s', religion='%s', " \
               "age='%s', city='%s', " \
               "credits_to_open_letter='%s', description='%s', " \
               "income='%s', last_online='%s', " \
               "looking_for_an_age_range='%s', name='%s', " \
               "nickname='%s', occupation='%s', " \
               "rate='%s', sex='%s', " \
               "votes='%s', country='%s')>" % (
                       self.profile_id, self.zodiac,
                       self.ethnicity_name, self.religion,
                       self.age, self.city,
                       self.credits_to_open_letter,
                       self.description[:100] + '...',
                       self.income, self.last_online,
                       self.looking_for_an_age_range, self.name,
                       self.nickname, self.occupation,
                       self.rate, self.sex,
                       self.votes, self.country)


class ProfileLanguages(Base):
    __tablename__ = 'Profile_languages'
    language = Column(VARCHAR(190), primary_key=True)
    level_name = Column(VARCHAR(190), primary_key=True)
    profile_id = Column(VARCHAR(20), primary_key=True)

    def __repr__(self):
        return "<Profile_languages(language='%s', " \
               "level_name='%s', profile_id='%s')>" % (
                       self.language, self.level_name, self.profile_id)


class Profiles(Base):
    __tablename__ = 'Profiles'
    profile_id = Column(VARCHAR(20), primary_key=True)
    profile_password = Column(VARCHAR(190))
    available = Column(BOOLEAN, default=True)
    can_receive = Column(BOOLEAN, default=True)
    msg_limit = Column(INTEGER(11), default=999)
    profile_type = Column(VARCHAR(20))
    max_age_delta = Column(INTEGER(2), default=10)

    def __repr__(self):
        return "<Profiles(profile_id='%s', profile_password='%s', " \
               "available='%s', can_receive='%s', " \
               "msg_limit='%s', profile_type='%s'," \
               "max_age_delta='%s')>" % (
                       self.profile_id, self.profile_password,
                       self.available, self.can_receive,
                       self.msg_limit, self.profile_type,
                       self.max_age_delta)


class Religions(Base):
    __tablename__ = 'Religions'
    religion = Column(VARCHAR(190), primary_key=True)

    def __repr__(self):
        return "<Religions(religion='%s')>" % self.religion


class RolesOfUsers(Base):
    __tablename__ = 'Roles_of_users'
    login = Column(VARCHAR(190), primary_key=True)
    user_role = Column(VARCHAR(190), primary_key=True)

    def __repr__(self):
        return "<Roles_of_users(login='%s', user_role='%s')>" % (
                self.login, self.user_role)


class Countries(Base):
    __tablename__ = 'Countries'
    country = Column(VARCHAR(190), primary_key=True)

    def __repr__(self):
        return "<Roles_of_users(country='%s')>" % (
                self.country)


class Tagging(Base):
    __tablename__ = 'Tagging'
    text_id = Column(BINARY(16), primary_key=True)
    tag = Column(VARCHAR(190), primary_key=True)

    def __repr__(self):
        return "<Tagging(text_id='%s', tag='%s')>" % (
                self.text_id, self.tag)


class Tags(Base):
    __tablename__ = 'Tags'
    tag = Column(VARCHAR(190), primary_key=True)
    forbidden = Column(BOOLEAN, default=False)

    def __repr__(self):
        return "<Tags(tag='%s')>" % self.tag


class MessageTemplates(Base):
    __tablename__ = 'Message_templates'
    profile_id = Column(VARCHAR(20), primary_key=True)
    text_id = Column(BINARY(16), primary_key=True)
    text_number = Column(INTEGER(11), primary_key=True)

    def __repr__(self):
        return "<Roles_of_users(profile_id='%s', text_id='%s'" \
               ", text_number='%s')>" % (
                       self.profile_id, self.text_id,
                       self.text_number)


class MessageAnchors(Base):
    __tablename__ = 'Message_anchors'
    profile_id = Column(VARCHAR(20), primary_key=True)
    text_id = Column(BINARY(16), primary_key=True)

    def __repr__(self):
        return "<Roles_of_users(profile_id='%s', text_id='%s')>" % (
                self.profile_id, self.text_id)


class UsedAnchors(Base):
    __tablename__ = 'Used_anchors'
    profile_id = Column(VARCHAR(20), primary_key=True)
    text_id = Column(BINARY(16), primary_key=True)

    def __repr__(self):
        return "<Roles_of_users(profile_id='%s', text_id='%s')>" % (
                self.profile_id, self.text_id)


class Texts(Base):
    __tablename__ = 'Texts'
    text_id = Column(BINARY(16), primary_key=True)
    text = Column(VARCHAR(10000))

    def __repr__(self):
        return "<Texts(text_id='%s', text='%s')>" % (
                self.text_id, self.text[:100] + '...')


class UserRoles(Base):
    __tablename__ = 'User_roles'
    user_role = Column(VARCHAR(190), primary_key=True)

    def __repr__(self):
        return "<User_roles(user_role='%s')>" % self.user_role


class Users(Base):
    __tablename__ = 'Users'
    login = Column(VARCHAR(190), primary_key=True)
    user_password = Column(VARCHAR(190))

    def __repr__(self):
        return "<Users(login='%s', user_password='%s')>" % (
                self.login, self.user_password)


class Visibility(Base):
    __tablename__ = 'Visibility'
    profile_id = Column(VARCHAR(190), primary_key=True)
    login = Column(VARCHAR(190), primary_key=True)

    def __repr__(self):
        return "<Visibility(profile_id='%s', login='%s')>" % (
                self.profile_id, self.login)


class Zodiacs(Base):
    __tablename__ = 'Zodiacs'
    zodiac = Column(VARCHAR(190), primary_key=True)

    def __repr__(self):
        return "<Zodiacs(zodiac='%s')>" % self.zodiac


class Invites(Base):
    __tablename__ = 'Invites'
    invite_id = Column(BINARY(16), primary_key=True)
    create_time = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return "<Invites(invite_id='%s', invite_id='%s')>" % (
                self.invite_id, self.create_time)


class SentInvites(Base):
    __tablename__ = 'Sent_invites'
    invite_id = Column(BINARY(16), primary_key=True)
    login = Column(VARCHAR(190), primary_key=True)

    def __repr__(self):
        return "<Sent_invites(invite_id='%s', invite_id='%s')>" % (
                self.invite_id, self.login)


class EmailInfo(Base):
    __tablename__ = 'Email_info'
    email_address = Column(VARCHAR(190), primary_key=True)
    email_port = Column(INTEGER(11))
    email_host = Column(VARCHAR(190))
    email_password = Column(VARCHAR(190))
    email_subject = Column(VARCHAR(10000))
    email_text = Column(VARCHAR(10000))
    email_description = Column(VARCHAR(190))

    def __repr__(self):
        return "<Email_info(email_address='%s', email_port='%s'," \
               "email_host='%s', email_password='%s'," \
               "email_subject='%s', email_text='%s'," \
               "email_description='%s')>" % (
                       self.email_address, self.email_port,
                       self.email_host, self.email_password,
                       self.email_subject, self.email_text,
                       self.email_description)


class SQLAlchemyHandler(logging.Handler):
    # A very basic logger that commits a LogRecord to the SQL Db
    def emit(self, record):
        trace = None
        exc = record.__dict__['exc_info']
        if exc:
            trace = traceback.format_exc()

        if current_user:
            if current_user.is_anonymous:
                user_login = 'anonymous'
                user_ip = request.environ['REMOTE_ADDR']
            else:
                user_ip = current_user.ip
                user_login = current_user.login
        else:
            user_login = 'server'
            hostname = socket.gethostname()
            user_ip = socket.gethostbyname(hostname)
        log = Logs(
                log_id=uuid4().bytes,
                login=user_login,
                category=record.__dict__['levelname'],
                message=record.__dict__['msg'],
                ip=user_ip)
        logger_db_session.add(log)
        logger_db_session.commit()
