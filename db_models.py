from sqlalchemy import Column, create_engine
from sqlalchemy.dialects.mysql import \
    BINARY, BOOLEAN, FLOAT, MEDIUMINT, TIMESTAMP, \
    TINYINT, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import env_variables as env

engine = create_engine(f'{env.DB_DIALECT}+{env.DB_DRIVER}://'
                       f'{env.DB_USER}:{env.DB_PASS}@'
                       f'{env.DB_ADRESS}/{env.DB_NAME}',
                       pool_recycle=3600)
Base = declarative_base()
Session = sessionmaker()
Session.configure(bind=engine)


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
    chat_id = Column(VARCHAR(190), primary_key=True)
    profile_id = Column(VARCHAR(190), primary_key=True)

    def __repr__(self):
        return "<Categories(chat_id='%s', profile_id='%s')>" % (
                self.chat_id, self.profile_id)


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


class LanguageLevel(Base):
    __tablename__ = 'Language_level'
    language = Column(VARCHAR(190), primary_key=True)
    level_name = Column(VARCHAR(190), primary_key=True)

    def __repr__(self):
        return "<Language_level(language='%s', level_name='%s')>" % (
                self.language,
                self.level_name)


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
    viewed = Column(BOOLEAN)

    def __repr__(self):
        return "<Messages(message_token='%s', chat_id='%s', " \
               "profile_id='%s', send_time='%s', " \
               "text_id='%s', viewed='%s', )>" % (
                       self.message_token, self.chat_id,
                       self.profile_id, self.send_time,
                       self.text_id, self.viewed)


class PrivilegesAssigns(Base):
    __tablename__ = 'Privileges_assigns'
    user_role = Column(VARCHAR(190), primary_key=True)
    privilege_name = Column(VARCHAR(190), primary_key=True)

    def __repr__(self):
        return "<Privileges_assigns(user_role='%s', " \
               "privilege_name='%s')>" % (
                       self.user_role,
                       self.privilege_name)


class Privileges(Base):
    __tablename__ = 'Privileges'
    privilege_name = Column(VARCHAR(190), primary_key=True)
    privilege_status = Column(BOOLEAN)

    def __repr__(self):
        return "<Privileges(privilege_name='%s', " \
               "privilege_status='%s')>" % (
                       self.privilege_name,
                       self.privilege_status)


class ProfileCategories(Base):
    __tablename__ = 'Profile_categories'
    level_name = Column(VARCHAR(190), primary_key=True)
    privilege_status = Column(BOOLEAN, primary_key=True)
    profile_id = Column(VARCHAR(20), primary_key=True)

    def __repr__(self):
        return "<Profile_categories(level_name='%s', " \
               "privilege_status='%s', " \
               "profile_id='%s')>" % (
                       self.level_name,
                       self.privilege_status,
                       self.profile_id)


class ProfileDescription(Base):
    __tablename__ = 'Profile_description'
    profile_id = Column(VARCHAR(190), primary_key=True)
    zodiac = Column(BOOLEAN)
    ethnicity_name = Column(VARCHAR(20))
    religion = Column(VARCHAR(20))
    age = Column(TINYINT(4))
    city = Column(VARCHAR(20))
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

    def __repr__(self):
        return "<Profile_description(" \
               "profile_id='%s', zodiac='%s', " \
               "ethnicity_name='%s', religion='%s', " \
               "age='%s', city='%s', " \
               "credits_to_open_letter='%s', description='%s', " \
               "income='%s', last_online='%s', " \
               "looking_for_an_age_range='%s', name='%s', " \
               "nickname='%s', occupation='%s', " \
               "rate='%s', sex='%s', votes='%s')>" % (
                self.profile_id, self.zodiac,
                self.ethnicity_name, self.religion,
                self.age, self.city,
                self.credits_to_open_letter,
                self.description[:100] + '...',
                self.income, self.last_online,
                self.looking_for_an_age_range, self.name,
                self.nickname, self.occupation,
                self.rate, self.sex, self.votes)


class ProfileLanguages(Base):
    __tablename__ = 'Profile_languages'
    language = Column(VARCHAR(190), primary_key=True)
    level_name = Column(BOOLEAN, primary_key=True)
    profile_id = Column(VARCHAR(20), primary_key=True)

    def __repr__(self):
        return "<Profile_languages(language='%s', " \
               "level_name='%s', profile_id='%s')>" % (
                       self.language, self.level_name, self.profile_id)


class Profiles(Base):
    __tablename__ = 'Profiles'
    profile_id = Column(VARCHAR(190), primary_key=True)
    profile_password = Column(BOOLEAN)
    available = Column(VARCHAR(20))
    can_receive = Column(VARCHAR(20))
    msg_limit = Column(VARCHAR(20))
    profile_type = Column(VARCHAR(20))

    def __repr__(self):
        return "<Profiles(profile_id='%s', profile_password='%s', " \
               "available='%s', can_receive='%s', " \
               "msg_limit='%s', profile_type='%s')>" % (
                       self.profile_id, self.profile_password,
                       self.available, self.can_receive,
                       self.msg_limit, self.profile_type)


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

    def __repr__(self):
        return "<Tags(tag='%s')>" % self.tag


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
        return "<Profile_languages(profile_id='%s', login='%s')>" % (
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
