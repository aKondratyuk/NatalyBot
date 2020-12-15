# coding: utf8
# Imports the Flask class
import logging
import os
from logging import Logger
from urllib.parse import urljoin, urlparse

from flask import Flask, abort, jsonify, make_response, redirect, \
    render_template, request, url_for
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, \
    login_user, \
    logout_user
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import and_

from authentication import find_user
from control_panel import *
from db_models import Logs, MessageAnchors, Profiles, SQLAlchemyHandler, \
    Tagging, Tags, Users, Visibility
from email_service import send_email_instruction

# Creates an app and checks if its the main or imported
workers_number = 0  # counter for workers
app = Flask(__name__)
app.config.update(TESTING=True,
                  SECRET_KEY=os.environ.get('APP_SECRET_KEY'),
                  FLASK_DEBUG=1)
Bootstrap(app)
CSRFProtect(app)
# login manager instance creation and setting
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'You are not authorized, please log in'

# Werkzeug logging
"""If the logger level is not set, it will be set to 
INFO on first use. If there is no handler for 
that level, a StreamHandler is added."""


class MyLogger(Logger):
    def __init__(self, name, level=0):
        super().__init__(name, level)
        logging.addLevelName(30, "NOTIFICATION")
        logging.addLevelName(50, "STOPWATCH")

    def notification(self, message, *args, **kws):
        if self.isEnabledFor(30):
            # Yes, logger takes its '*args' as 'args'.
            self._log(30, message, args, **kws)

    def stopwatch(self, message, *args, **kws):
        if self.isEnabledFor(30):
            # Yes, logger takes its '*args' as 'args'.
            self._log(50, message, args, **kws)


logger = MyLogger("werkzeug")

stream_handler = logging.StreamHandler()
sql_handler = SQLAlchemyHandler()
logger.addHandler(stream_handler)
logger.addHandler(sql_handler)
app.logger = logger

# this logger work only with DB
db_logger = MyLogger("DB_logger")
db_logger.addHandler(sql_handler)


@login_manager.user_loader
def load_user(user_id):
    # Return User object or None
    return find_user(user_id=user_id)


# needed for safe connection, from tutorial
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return \
        test_url.scheme in ('http', 'https') \
        and ref_url.netloc == test_url.netloc


# logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/users/invite_user', methods=['POST'])
@login_required
def invite_user():
    invited_email = request.form.get('recipient-name')
    assigned_role = request.form.get('recipient-role')
    send_email_instruction(email_to=invited_email)
    error = not create_invite(creator=current_user,
                              invited_email=invited_email,
                              role=assigned_role)
    user_list = db_get_users()
    return render_template('users.html',
                           user_list=user_list,
                           error=error)


@app.route('/profile_dialogue', methods=['GET', 'POST'])
@login_required
def profile_dialogue():
    db_session = Session()
    if 'PROFILES_VISIBILITY' in list(current_user.privileges.keys()):
        # if user can view all profiles, we doesn't filter by access
        senders = db_get_rows([
                Profiles.profile_id,
                ProfileDescription.name,
                ProfileDescription.nickname
                ],
                Profiles.profile_password,
                Profiles.available == 1,
                ProfileDescription.profile_id == Profiles.profile_id)
    else:
        senders = db_get_rows([
                Profiles.profile_id,
                ProfileDescription.name,
                ProfileDescription.nickname
                ],
                Profiles.profile_password,
                Profiles.available == 1,
                Visibility.login == current_user.login,
                Visibility.profile_id == Profiles.profile_id,
                ProfileDescription.profile_id == Profiles.profile_id)
    receivers = None
    dialog = None
    sender = None
    receiver = None
    if request.method == "POST":
        sender = request.form.get('sender_id')
        if request.form.get('receiver_id_manual'):
            receiver = request.form.get('receiver_id_manual')
        else:
            receiver = request.form.get('receiver_id')
        if sender:
            # subquery for chats with sender
            sub_query_1 = db_session. \
                query(ChatSessions.chat_id). \
                filter(ChatSessions.profile_id == sender).subquery()
            receivers = db_get_rows([
                    ChatSessions.profile_id,
                    ProfileDescription.name,
                    ProfileDescription.nickname
                    ],
                    ChatSessions.chat_id.in_(sub_query_1),
                    ChatSessions.profile_id != sender,
                    Profiles.profile_id == ChatSessions.profile_id,
                    Profiles.available == 1,
                    Profiles.can_receive == 1,
                    ProfileDescription.profile_id == ChatSessions.profile_id)
        if receiver:
            if request.form.get('receiver_id_manual'):
                sender_info_list = db_get_profiles(
                        Profiles.profile_id == sender)
                sender_info = sender_info_list[0]
                dialog_download(
                        observer_login=sender_info['profile_id'],
                        observer_password=sender_info['profile_password'],
                        sender_id=receiver,
                        receiver_profile_id=receiver)
                dialog_download(
                        observer_login=sender_info['profile_id'],
                        observer_password=sender_info['profile_password'],
                        sender_id=sender_info['profile_id'],
                        receiver_profile_id=receiver)
                # load description for profile
                db_load_profile_description(receiver)
                # subquery for chats with sender
                sub_query_1 = db_session. \
                    query(ChatSessions.chat_id). \
                    filter(ChatSessions.profile_id == sender).subquery()
                receivers = db_get_rows([
                        ChatSessions.profile_id,
                        ProfileDescription.name,
                        ProfileDescription.nickname
                        ],
                        ChatSessions.chat_id.in_(sub_query_1),
                        ChatSessions.profile_id != sender,
                        Profiles.profile_id == ChatSessions.profile_id,
                        Profiles.available == 1,
                        Profiles.can_receive == 1,
                        ProfileDescription.profile_id == ChatSessions.profile_id)
            dialog = db_show_dialog(sender=sender,
                                    receiver=receiver)
    db_session.close()
    return render_template('profile_dialogue.html',
                           dialog=dialog,
                           senders=senders,
                           receivers=receivers,
                           selected_sender=sender,
                           selected_receiver=receiver)


@app.route('/create_new_user:<login>:<user_password>:<role>')
def create_new_user(login, user_password, role):
    result = create_user(login=login,
                         user_password=user_password,
                         role=role)
    if result:
        logger.info(f"User {current_user.login} manualy create "
                    f"user with parameters:\n"
                    f"login = {login}\n"
                    f"password = {user_password}\n"
                    f"role = {role}")
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
# The function run on the index route
def login():
    error = False
    logger.info(f'User {current_user} opened site')
    if current_user.is_authenticated:
        return redirect(url_for('control_panel'))
    if request.method == 'POST':
        logger.info(f"User {current_user} tried to log in\n"
                    f"with email: {request.form.get('email')}\n"
                    f"and password: {request.form.get('password')}")
        # Login and validate the user.
        # user should be an instance of your `User` class
        user = find_user(login=request.form.get('email'))
        if user:
            if user.check_password(request.form.get('password')):
                # User saving in session
                login_user(user, remember=request.form.get('remember-me'))
                logger.info(f"User {request.form.get('email')} "
                            "Logged in successfully.")
                next_url = request.args.get('next')
                # is_safe_url should check if the url is safe for redirects.
                if not is_safe_url(next_url):
                    return abort(400)
                return redirect(next_url or url_for('control_panel'))
        error = True
        logger.error(
                f"Invalid username/password by {request.form.get('email')}")

    # Returns the html page to be displayed
    return render_template('login.html',
                           error=error)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = False
    if request.method == 'POST':
        error = register_user(login=request.form.get('email'),
                              user_password=request.form.get('password'))
        if not error:
            return render_template("confirmation.html")
        else:
            render_template('signup.html', error=error)
    return render_template('signup.html', error=error)


###############################################################################
#                                                                             #
#               Веб-страницы составляющие контрольную панель                  #
#                                                                             #
###############################################################################
@app.route('/control_panel', methods=['GET', 'POST'])
@login_required
def control_panel():
    if request.method == 'POST':
        logger.info(
                f'User {current_user.login} sent POST request on '
                f'control_panel')
        return render_template("confirmation.html")

    return render_template('dashboard.html')


@app.route('/icons', methods=['GET', 'POST'])
@login_required
def icons():
    return render_template('icons.html')


###############################################################################
#                                                                             #
#          Веб-страницы составляющие пользовательскую панель                  #
#                                                                             #
###############################################################################

@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():

    if request.method == "POST":
        invited_email = request.form.get('recipient-name')
        assigned_role = request.form.get('recipient-role')
        send_email_instruction(email_to=invited_email)
        error = not create_invite(creator=current_user,
                                  invited_email=invited_email,
                                  role=assigned_role)
        user_list = db_get_users(RolesOfUsers.user_role != 'deleted')
        return render_template('users.html',
                               user_list=user_list,
                               error=error)
    logger.info(f'User {current_user.login} opened user list')
    user_list = db_get_users(RolesOfUsers.user_role != 'deleted')
    return render_template('users.html', user_list=user_list)


@app.route('/users/edit/<login>', methods=['POST'])
@login_required
def users_edit(login):
    new_role = request.form.get('recipient-role')
    old_role = db_get_rows([RolesOfUsers.user_role],
                           Users.login == RolesOfUsers.login,
                           Users.login == login)[0][0]
    if not new_role == old_role:
        db_change_user_role(login, new_role)
        logger.info(f'User {current_user.login} '
                    f'update role for user: {login} with old '
                    f'role: {old_role} on role: {new_role}')
    return redirect(url_for('users'))


@app.route('/users/delete/<login>', methods=['POST'])
@login_required
def users_delete(login):
    if db_delete_user(login):
        logger.info(f'User {current_user.login} deleted: {login}')
    else:
        logger.info(f'User {current_user.login} tryed to '
                    f'delete: {login} but something gone wrong!')
    return redirect(url_for('users'))


@app.route('/users/selected/delete', methods=['POST'])
@login_required
def users_selected_delete():
    list_login = request.form.getlist('mycheckbox')
    logger.info(f'User {current_user.login} starting '
                f'delete users: {list_login}')
    for login in list_login:
        if db_delete_user(login):
            logger.info(f'User {current_user.login} delete: {login}')
        else:
            logger.info(f'User {current_user.login} tried to '
                        f'delete: {login} but something gone wrong!')
    return redirect(url_for('users'))


@app.route('/users/access', methods=['GET', 'POST'])
@login_required
def access():
    users = db_get_rows([Users.login, RolesOfUsers],
                        Users.login != 'server',
                        Users.login != 'anonymous',
                        Users.login == RolesOfUsers.login,
                        RolesOfUsers.user_role != 'deleted',
                        RolesOfUsers.user_role != 'admin')
    if request.form.get('user_login'):
        user = request.form.get('user_login')
        db_session = Session()
        other_profiles = db_get_rows_2([Visibility.profile_id],
                                       return_query=True)
        new_profiles = db_get_rows([
                Profiles.profile_id,
                ProfileDescription.name,
                ProfileDescription.nickname
                ],
                Profiles.profile_id.notin_(other_profiles),
                Profiles.profile_id == ProfileDescription.profile_id,
                Profiles.available,
                Profiles.profile_password)
        profiles = new_profiles
        db_session.close()
    else:
        profiles = []
    available_profiles = None
    user = None
    error = None
    if request.method == "POST":
        # show user's profiles
        if request.form.get('user_login_manual'):
            # user login is wrote in text input
            user = request.form.get('user_login_manual')
            user_in_db = db_duplicate_check(
                    [Users, RolesOfUsers],
                    Users.login == user,
                    Users.login != 'server',
                    Users.login != 'anonymous',
                    Users.login == RolesOfUsers.login,
                    RolesOfUsers.user_role != 'deleted',
                    RolesOfUsers.user_role != 'admin')
            if not user_in_db:
                logger.info(
                        f'User {current_user.login} tried to add profiles for '
                        f'{user} but such user not exists')
                user = None
                error = 'UserNotFound'
        else:
            user = request.form.get('user_login')
        # add user new profile
        if request.form.get('profile_id_manual'):
            # profile id is wrote in text input
            profile = request.form.get('profile_id_manual')
        else:
            profile = request.form.get('profile_id')
        if profile:
            # add user access to profile
            error = db_add_visibility(login=user,
                                      profile_id=profile)
        # load available profiles
        if user:
            other_profiles = db_get_rows_2([Visibility.profile_id],
                                           return_query=True)
            profiles = db_get_rows([
                    Profiles.profile_id,
                    ProfileDescription.name,
                    ProfileDescription.nickname
                    ],
                    Profiles.profile_id.notin_(other_profiles),
                    Profiles.profile_id == ProfileDescription.profile_id,
                    Profiles.available,
                    Profiles.profile_password)
            available_profiles = db_get_rows([
                    Visibility.profile_id,
                    ProfileDescription.name,
                    ProfileDescription.nickname
                    ],
                    Visibility.login == user,
                    Visibility.profile_id == ProfileDescription.profile_id,
                    Profiles.available == 1,
                    Profiles.profile_id == Visibility.profile_id)

    return render_template('access.html',
                           available_profiles=available_profiles,
                           users=users,
                           selected_user=user,
                           profiles=profiles,
                           error=error)


@app.route('/users/access/delete/<selected_user>:<profile_id>', methods=[
        'POST'])
@login_required
def users_access_delete(selected_user, profile_id):
    deleted_rows = db_delete_rows_2([Visibility],
                                    [Visibility.login == selected_user,
                                     Visibility.profile_id == profile_id])
    if deleted_rows != 0:
        logger.info(f'User {current_user.login} successfully deleted '
                    f'visibility of {profile_id} for user {selected_user}')
    else:
        logger.info(f'User {current_user.login} tried to '
                    f'delete: {profile_id} for user '
                    f'{selected_user} but something gone wrong!')
    return redirect(request.referrer)


@app.route('/users/access/selected/delete', methods=['POST'])
@login_required
def users_access_selected_delete():
    list_profiles = request.form.getlist('mycheckbox')
    selected_user = request.form.get('selected_user')
    logger.info(f'User {current_user.login} starting '
                f'delete profiles: {list_profiles}')
    deleted_rows = db_delete_rows_2([Visibility],
                                    [Visibility.login == selected_user,
                                     Visibility.profile_id.in_(list_profiles)],
                                    synchronize_session='fetch')
    if deleted_rows != 0:
        logger.info(f'User {current_user.login} successfully deleted '
                    f'visibility of {list_profiles} for user {selected_user}')
    else:
        logger.info(f'User {current_user.login} tried to '
                    f'delete: {list_profiles} for user '
                    f'{selected_user} but something gone wrong!'
                    f'Deleted only {deleted_rows} profiles.')
    return redirect(request.referrer)


@app.route('/users/accounts', methods=['GET', 'POST'])
@login_required
def users_accounts():
    if request.method == "POST":
        account_login = request.form.get('account-login')
        account_password = request.form.get('account-password')
        error = db_add_profile(profile_id=account_login,
                               profile_password=account_password)
    user_visibility = db_get_rows_2([Visibility.profile_id],
                                    [Visibility.login == current_user.login],
                                    return_query=True)

    if 'PROFILES_VISIBILITY' in list(current_user.privileges.keys()):
        profiles = db_get_rows_2([
                ProfileDescription.profile_id,
                ProfileDescription.nickname,
                Profiles.profile_password,
                ProfileDescription.age,
                Profiles.available
                ],
                [ProfileDescription.profile_id == Profiles.profile_id,
                 Profiles.profile_password])
    else:
        profiles = db_get_rows_2([
                ProfileDescription.profile_id,
                ProfileDescription.nickname,
                Profiles.profile_password,
                ProfileDescription.age,
                Profiles.available
                ],
                [ProfileDescription.profile_id == Profiles.profile_id,
                 Profiles.profile_password,
                 Profiles.profile_id.in_(user_visibility)])
    return render_template("accounts.html", profiles=profiles)

@app.route('/users/accounts/delete:<account_id>', methods=['GET', 'POST'])
@login_required
def account_delete(account_id):
    error = delete_accounts([account_id])
    return redirect(url_for('users_accounts'))


@app.route('/users/accounts/selected/delete', methods=['GET', 'POST'])
@login_required
def account_selected_delete():
    list_accounts = request.form.getlist('mycheckbox')
    logger.info(f'User {current_user.login} starting '
                f'delete accounts: {list_accounts}')
    if delete_accounts(list_accounts):
        logger.info(f'User {current_user.login} deleted accounts: {list_accounts}')
    else:
        logger.info(f'User {current_user.login} tried to '
                    f'delete accounts: {list_accounts} but something gone wrong!')

    return redirect(url_for('users_accounts'))

@app.route('/dialogue', methods=['GET', 'POST'])
@login_required
def dialogue():
    # get accounts which this user can see
    if 'PROFILES_VISIBILITY' in list(current_user.privileges.keys()):

        accounts = db_get_rows_2([Profiles.profile_id],
                                 [Profiles.profile_password
                                  ],
                                 return_query=True)
    else:
        accounts = db_get_rows_2([Visibility.profile_id],
                                 [
                                         Visibility.login ==
                                         current_user.login,
                                         Visibility.profile_id ==
                                         Profiles.profile_id,
                                         Profiles.profile_password],
                                 return_query=True)
    if 'PROFILES_VISIBILITY' in list(current_user.privileges.keys()):

        accounts_subq = db_get_rows_2([ProfileDescription.nickname,
                                       Profiles.profile_id,
                                       ChatSessions.chat_id],
                                      [ChatSessions.profile_id ==
                                       Profiles.profile_id,
                                       Profiles.profile_password,
                                       Profiles.profile_id ==
                                       ProfileDescription.profile_id
                                       ],
                                      return_query=True).subquery()
    else:
        accounts_subq = db_get_rows_2([ProfileDescription.nickname,
                                       Visibility.profile_id,
                                       ChatSessions.chat_id],
                                      [ChatSessions.profile_id ==
                                       Visibility.profile_id,
                                       Visibility.login ==
                                       current_user.login,
                                       Visibility.profile_id ==
                                       Profiles.profile_id,
                                       Profiles.profile_password,
                                       Profiles.profile_id ==
                                       ProfileDescription.profile_id
                                       ],
                                      return_query=True).subquery()
    # load profiles which have chat with this account
    account_chats = db_get_rows_2([ChatSessions.chat_id],
                                  [ChatSessions.profile_id.in_(accounts)],
                                  return_query=True)
    profiles = db_get_rows_2([ChatSessions.profile_id,
                              ChatSessions.chat_id,
                              ProfileDescription.nickname],
                             [
                                     ChatSessions.chat_id.in_(account_chats),
                                     ChatSessions.profile_id.notin_(accounts),
                                     ProfileDescription.profile_id ==
                                     ChatSessions.profile_id],
                             return_query=True).subquery()
    chats = db_get_rows_2([ChatSessions.chat_id],
                          [ChatSessions.chat_id.in_(account_chats),
                           ChatSessions.profile_id.notin_(accounts)],
                          return_query=True)
    last_messages = db_get_rows_2([Texts.text,
                                   Messages.send_time,
                                   Messages.profile_id,
                                   Messages.viewed,
                                   Messages.delay,
                                   Messages.chat_id],
                                  [Messages.chat_id.in_(chats),
                                   Texts.text_id == Messages.text_id],
                                  group_by=[Messages.chat_id],
                                  order_by=[Messages.send_time],
                                  return_query=True).subquery()
    messages = db_get_rows_2([last_messages, profiles, accounts_subq],
                             [last_messages.c.chat_id == profiles.c.chat_id,
                              last_messages.c.chat_id ==
                              accounts_subq.c.chat_id],
                             group_by=[profiles.c.chat_id],
                             order_by=[last_messages.c.send_time])
    last_messages = [{'text': message[0],
                      'send_time': message[1],
                      'last_from': message[2],
                      'viewed': message[3],
                      'delay': message[4],
                      'profile_id': message[6],
                      'nickname': message[8],
                      'account_nickname': message[9],
                      'account_id': message[10]}
                     for message in messages]
    # all_messages.extend(last_messages)
    last_messages.sort(key=lambda x: x['send_time'], reverse=True)
    return render_template('dialogue.html', dialogue=last_messages)


@app.route('/mail', methods=['GET', 'POST'])
@login_required
def mail():
    # get accounts which this user can see
    if 'PROFILES_VISIBILITY' in list(current_user.privileges.keys()):

        accounts = db_get_rows_2([Profiles.profile_id],
                                 [Profiles.profile_password
                                  ],
                                 return_query=True)
    else:
        accounts = db_get_rows_2([Visibility.profile_id],
                                 [
                                         Visibility.login ==
                                         current_user.login,
                                         Visibility.profile_id ==
                                         Profiles.profile_id,
                                         Profiles.profile_password],
                                 return_query=True)
    if 'PROFILES_VISIBILITY' in list(current_user.privileges.keys()):

        accounts_subq = db_get_rows_2([ProfileDescription.nickname,
                                       Profiles.profile_id,
                                       ChatSessions.chat_id],
                                      [ChatSessions.profile_id ==
                                       Profiles.profile_id,
                                       Profiles.profile_password,
                                       Profiles.profile_id ==
                                       ProfileDescription.profile_id
                                       ],
                                      return_query=True).subquery()
    else:
        accounts_subq = db_get_rows_2([ProfileDescription.nickname,
                                       Visibility.profile_id,
                                       ChatSessions.chat_id],
                                      [ChatSessions.profile_id ==
                                       Visibility.profile_id,
                                       Visibility.login ==
                                       current_user.login,
                                       Visibility.profile_id ==
                                       Profiles.profile_id,
                                       Profiles.profile_password,
                                       Profiles.profile_id ==
                                       ProfileDescription.profile_id
                                       ],
                                      return_query=True).subquery()
    # load profiles which have chat with this account
    account_chats = db_get_rows_2([ChatSessions.chat_id],
                                  [ChatSessions.profile_id.in_(accounts)],
                                  return_query=True)
    profiles = db_get_rows_2([ChatSessions.profile_id,
                              ChatSessions.chat_id,
                              ProfileDescription.nickname],
                             [
                                     ChatSessions.chat_id.in_(account_chats),
                                     ChatSessions.profile_id.notin_(accounts),
                                     ProfileDescription.profile_id ==
                                     ChatSessions.profile_id],
                             return_query=True).subquery()
    chats = db_get_rows_2([ChatSessions.chat_id],
                          [ChatSessions.chat_id.in_(account_chats),
                           ChatSessions.profile_id.notin_(accounts)],
                          return_query=True)
    last_messages = db_get_rows_2([Texts.text,
                                   Messages.send_time,
                                   Messages.profile_id,
                                   Messages.viewed,
                                   Messages.delay,
                                   Messages.chat_id],
                                  [Messages.chat_id.in_(chats),
                                   Texts.text_id == Messages.text_id],
                                  group_by=[Messages.chat_id],
                                  order_by=[Messages.send_time],
                                  return_query=True).subquery()
    if len(db_get_rows_2([Texts])) != 0 \
            and len(db_get_rows_2([Messages])) != 0 \
            and len(accounts.all()) != 0:
        # if texts, messages, profiles table empty
        messages = db_get_rows_2([last_messages, profiles, accounts_subq],
                                 [
                                         last_messages.c.chat_id ==
                                         profiles.c.chat_id,
                                         last_messages.c.chat_id ==
                                         accounts_subq.c.chat_id],
                                 group_by=[profiles.c.chat_id],
                                 order_by=[last_messages.c.send_time])
        last_messages = [{'text': message[0],
                          'send_time': message[1],
                          'last_from': message[2],
                          # yellow lamp we sent message if last_from =
                          # account_id
                          'viewed': message[3],
                          # green lamp message viewed by man if last_from =
                          # account_id and viewed = True
                          'delay': message[4],
                          # blue lamp template is formed delay = 1
                          'profile_id': message[6],
                          'nickname': message[8],
                          'account_nickname': message[9],
                          'account_id': message[10]}
                         for message in messages]
    else:
        last_messages = []
    # all_messages.extend(last_messages)
    last_messages.sort(key=lambda x: x['send_time'], reverse=True)
    return render_template('mail.html', dialogue=last_messages)


@app.route('/mail/star', methods=['GET', 'POST'])
@login_required
def mail_star():
    return render_template('mail_star.html')


@app.route('/mail/future', methods=['GET', 'POST'])
@login_required
def mail_future():
    # get accounts which this user can see
    if 'PROFILES_VISIBILITY' in list(current_user.privileges.keys()):

        accounts = db_get_rows_2([Profiles.profile_id],
                                 [Profiles.profile_password
                                  ],
                                 return_query=True)
    else:
        accounts = db_get_rows_2([Visibility.profile_id],
                                 [
                                         Visibility.login ==
                                         current_user.login,
                                         Visibility.profile_id ==
                                         Profiles.profile_id,
                                         Profiles.profile_password],
                                 return_query=True)
    if 'PROFILES_VISIBILITY' in list(current_user.privileges.keys()):

        accounts_subq = db_get_rows_2([ProfileDescription.nickname,
                                       Profiles.profile_id,
                                       ChatSessions.chat_id],
                                      [ChatSessions.profile_id ==
                                       Profiles.profile_id,
                                       Profiles.profile_password,
                                       Profiles.profile_id ==
                                       ProfileDescription.profile_id
                                       ],
                                      return_query=True).subquery()
    else:
        accounts_subq = db_get_rows_2([ProfileDescription.nickname,
                                       Visibility.profile_id,
                                       ChatSessions.chat_id],
                                      [ChatSessions.profile_id ==
                                       Visibility.profile_id,
                                       Visibility.login ==
                                       current_user.login,
                                       Visibility.profile_id ==
                                       Profiles.profile_id,
                                       Profiles.profile_password,
                                       Profiles.profile_id ==
                                       ProfileDescription.profile_id
                                       ],
                                      return_query=True).subquery()
    # load profiles which have chat with this account
    account_chats = db_get_rows_2([ChatSessions.chat_id],
                                  [ChatSessions.profile_id.in_(accounts)],
                                  return_query=True)
    profiles = db_get_rows_2([ChatSessions.profile_id,
                              ChatSessions.chat_id,
                              ProfileDescription.nickname],
                             [
                                     ChatSessions.chat_id.in_(account_chats),
                                     ChatSessions.profile_id.notin_(accounts),
                                     ProfileDescription.profile_id ==
                                     ChatSessions.profile_id],
                             return_query=True).subquery()
    chats = db_get_rows_2([ChatSessions.chat_id],
                          [ChatSessions.chat_id.in_(account_chats),
                           ChatSessions.profile_id.notin_(accounts)],
                          return_query=True)
    last_messages = db_get_rows_2([Texts.text,
                                   Messages.send_time,
                                   Messages.profile_id,
                                   Messages.viewed,
                                   Messages.delay,
                                   Messages.chat_id],
                                  [Messages.chat_id.in_(chats),
                                   Texts.text_id == Messages.text_id,
                                   Messages.delay],
                                  group_by=[Messages.chat_id],
                                  order_by=[Messages.send_time],
                                  return_query=True).subquery()
    messages = db_get_rows_2([last_messages, profiles, accounts_subq],
                             [last_messages.c.chat_id == profiles.c.chat_id,
                              last_messages.c.chat_id ==
                              accounts_subq.c.chat_id],
                             group_by=[profiles.c.chat_id],
                             order_by=[last_messages.c.send_time])
    last_messages = [{'text': message[0],
                      'send_time': message[1],
                      'last_from': message[2],
                      'viewed': message[3],
                      'delay': message[4],
                      'profile_id': message[6],
                      'nickname': message[8],
                      'account_nickname': message[9],
                      'account_id': message[10]}
                     for message in messages]
    # all_messages.extend(last_messages)
    last_messages.sort(key=lambda x: x['send_time'], reverse=True)
    return render_template('mail_future.html', dialogue=last_messages)


@app.route('/mail/outbox', methods=['GET', 'POST'])
@login_required
def mail_outbox():
    # get accounts which this user can see
    if 'PROFILES_VISIBILITY' in list(current_user.privileges.keys()):

        accounts = db_get_rows_2([ProfileDescription.nickname,
                                  Profiles.profile_id],
                                 [
                                         Profiles.profile_password,
                                         Profiles.profile_id ==
                                         ProfileDescription.profile_id
                                         ])
    else:
        accounts = db_get_rows_2([ProfileDescription.nickname,
                                  Visibility.profile_id],
                                 [
                                         Visibility.login == current_user.login,
                                         Visibility.profile_id ==
                                         Profiles.profile_id,
                                         Profiles.profile_password,
                                         Profiles.profile_id ==
                                         ProfileDescription.profile_id
                                         ])
    all_messages = []
    for account in accounts:
        # download dialogue for this account, from DB
        dialogue = db_show_dialog(sender=account[1],
                                  outbox_filter=True,
                                  descending=True)
        for message_i in range(len(dialogue)):
            # add account nickname and id, in messages
            dialogue[message_i]['account_nickname'] = account[0]
            dialogue[message_i]['account_id'] = account[1]
        all_messages.extend(dialogue)
    all_messages.sort(key=lambda x: x['send_time'], reverse=True)
    return render_template('mail_outbox.html', dialogue=all_messages)


@app.route('/mail/star/<sender>', methods=['GET', 'POST'])
@login_required
def mail_star_it(sender):
    logger.info(current_user.login + " set star to message with sender name " +
                sender)

    return render_template("mail.html")


@app.route('/mail/selected/delete', methods=['POST'])
@login_required
def mail_selected_delete():
    list_login = request.form.getlist('mycheckbox')
    logger.info(f'User {current_user.login} starting '
                f'delete users: {list_login}')
    for login in list_login:
        if db_delete_user(login):
            logger.info(f'User {current_user.login} delete: {login}')
        else:
            logger.info(f'User {current_user.login} tried to '
                        f'delete: {login} but something gone wrong!')
    return redirect(url_for('users'))


@app.route('/mail/dialogue:<sender>:<receiver>', methods=['GET', 'POST'])
@login_required
def dialogue_profile(sender, receiver):
    if request.method == "POST":
        print(request.get_json())
        request_data = request.get_json()
        if 'method' in request_data.keys():
            if request_data['method'] == 'send_template_message':
                account = db_get_rows_2([Profiles.profile_id,
                                         Profiles.profile_password],
                                        [Profiles.profile_id == sender],
                                        one=True)
                account_session, account_id = site_login(account[0],
                                                         account[1])
                result = message(session=account_session,
                                 receiver_profile_id=receiver,
                                 message_text=request_data['text'])
                if result:
                    # add update for message in DB, to delete from delayed
                    db_session = Session()
                    text_id = db_get_rows_2([Texts.text_id],
                                            [Texts.text_id == Messages.text_id,
                                             Messages.message_token == UUID(
                                                     request_data[
                                                         'message_token']).bytes],
                                            return_query=True)
                    update_q = update(Texts).where(
                            Texts.text_id.in_(text_id)). \
                        values(text=request_data['text'])
                    db_session.execute(update_q)
                    db_session.commit()
                    update_q = update(Messages).where(
                            Messages.message_token == UUID(request_data[
                                                               'message_token']).bytes). \
                        values(delay=False,
                               send_time=datetime.now())
                    db_session.execute(update_q)
                    db_session.commit()
                    db_session.close()
                    logger.info(f'User {current_user.login} changed template '
                                f'for account {sender} in dialogue with '
                                f'profile {receiver}')

                    logger.info(f'User {current_user.login} sended template '
                                f'from account {sender} to '
                                f'profile {receiver}')
                    response = make_response(
                            jsonify({'status': 'message_send'}))
                else:
                    response = make_response(
                        jsonify({'status': 'message_not_send'}))
                return response
            elif request_data['method'] == 'send_no_template_message':
                account = db_get_rows_2([Profiles.profile_id,
                                         Profiles.profile_password],
                                        [Profiles.profile_id == sender],
                                        one=True)
                chats_sender = db_get_rows_2([ChatSessions.chat_id],
                                             [
                                                     ChatSessions.profile_id
                                                     == sender],
                                             return_query=True)
                chat = db_get_rows_2([ChatSessions.chat_id],
                                     [ChatSessions.profile_id == receiver,
                                      ChatSessions.chat_id.in_(chats_sender)],
                                     one=True)
                account_session, account_id = site_login(account[0],
                                                         account[1])
                result = message(session=account_session,
                                 receiver_profile_id=receiver,
                                 message_text=request_data['text'])
                if result:
                    db_message_create(
                            chat_id=chat[0],
                            send_time=datetime.now(),
                            viewed=False,
                            sender=account[0],
                            text=request_data['text'],
                            delay=False)

                    logger.info(f'User {current_user.login} created message '
                                f'for account {sender} in dialogue with '
                                f'profile {receiver}')
                    response = make_response(
                            jsonify({'status': 'message_send'}))
                else:
                    response = make_response(
                        jsonify({'status': 'message_not_send'}))
                return response
            elif request_data['method'] == 'edit_template':
                # Здесь обновляем в базе темлпейт
                db_session = Session()
                text_id = db_get_rows_2([Texts.text_id],
                                        [Texts.text_id == Messages.text_id,
                                         Messages.message_token == UUID(
                                                 request_data[
                                                     'message_token']).bytes],
                                        return_query=True)
                update_q = update(Texts).where(
                        Texts.text_id.in_(text_id)). \
                    values(text=request_data['text'])
                db_session.execute(update_q)
                db_session.commit()
                db_session.close()
                logger.info(f'User {current_user.login} changed template '
                            f'for account {sender} in dialogue with '
                            f'profile {receiver}')

    sender_password = db_get_rows([Profiles.profile_password],
                                  Profiles.profile_id == sender)[0][0]
    # load dialogue
    dialogue = db_show_dialog(sender=sender,
                              receiver=receiver)
    error_in_chat = db_dialogue_checker(dialogue=dialogue)
    db_download_new_msg(sender,
                        sender_password,
                        sender,
                        receiver,
                        delete_chat=error_in_chat)
    db_session = Session()
    temp_txt = "{name}, it/'s a crime❗️❗️❗️ ⚡️💥 ❄️🌬 💋👩💻💌  🌅 🏖 " \
               "🏝💄💋🔥🛀📖 😘"
    update_q = update(Texts).where(
            and_(Messages.message_token == UUID(
                    '70cf4cae-7633-40f4-a628-f79f5cfb7bac').bytes,
                 Texts.text_id == Messages.text_id)). \
        values(text=temp_txt)
    db_session.execute(update_q)
    db_session.commit()
    db_session.close()
    # load dialogue
    dialogue = db_show_dialog(sender=sender,
                              receiver=receiver)

    receiver_data = db_get_rows([
            ProfileDescription.nickname,
            Profiles.available
            ],
            ProfileDescription.profile_id == receiver,
            ProfileDescription.profile_id == Profiles.profile_id)
    receiver_nickname = receiver_data[0][0]
    receiver_availability = receiver_data[0][1]

    return render_template('dialogue_profile.html',
                           dialogue=dialogue,
                           sender=sender,
                           receiver=receiver,
                           receiver_nickname=receiver_nickname,
                           receiver_availability=receiver_availability)


@app.route('/mail/templates', methods=['GET', 'POST'])
@login_required
def message_templates():
    if 'PROFILES_VISIBILITY' in list(current_user.privileges.keys()):
        # if user can view all profiles, we doesn't filter by access
        accounts = db_get_rows([
                Profiles.profile_id,
                ProfileDescription.name,
                ProfileDescription.nickname
                ],
                Profiles.profile_password,
                Profiles.available == 1,
                ProfileDescription.profile_id == Profiles.profile_id)
    else:
        accounts = db_get_rows([
                Profiles.profile_id,
                ProfileDescription.name,
                ProfileDescription.nickname
                ],
                Profiles.profile_password,
                Profiles.available == 1,
                Visibility.login == current_user.login,
                Visibility.profile_id == Profiles.profile_id,
                ProfileDescription.profile_id == Profiles.profile_id)

    if request.method == "POST":
        profile_id = request.form.get('account_id')
        for account in accounts:
            if account[0] == profile_id:
                selected_account_nickname = account[2]
                break
        if profile_id:

            if 'PROFILES_VISIBILITY' in list(current_user.privileges.keys()):
                templates = db_get_rows([
                        Texts.text_id,
                        Texts.text,
                        MessageTemplates.text_number],
                        Texts.text_id == MessageTemplates.text_id,
                        Profiles.profile_id == MessageTemplates.profile_id,
                        Profiles.profile_password,
                        Profiles.profile_id == profile_id)
            else:
                templates = db_get_rows([
                        Texts.text_id,
                        Texts.text,
                        MessageTemplates.text_number],
                        Texts.text_id == MessageTemplates.text_id,
                        Profiles.profile_id == MessageTemplates.profile_id,
                        Profiles.profile_password,
                        Profiles.profile_id == profile_id,
                        Visibility.profile_id == profile_id,
                        Visibility.login == current_user.login)
        else:
            templates = []
        templates = sorted(templates,
                           key=lambda x: x[2])

        # If this is only accounts select form
        if not request.files:
            return render_template(
                    'message_templates.html',
                    templates=templates,
                    accounts=accounts,
                    selected_account=profile_id,
                    selected_account_nickname=selected_account_nickname)

        # Добавить проверку на расширение файла
        # Количество знаков в тексте не должно превышать 1500 символов
        # Полученнй текст занести в базу данных в таблицу шаблонов
        # Если получаемый номер шаблона совпадает уже с существующим,
        # то переписать файл заново
        text_number = request.form.get("number")
        file = request.files['file']
        contents = file.read().decode('UTF-8')
        text = contents

        # Может пригодится если нужно будет сохранять файлы на сервере
        # file.save(os.path.join('static/images', file.filename))

        logger.info(f'User {current_user.login} load new template')
        # If text number already exists
        if db_duplicate_check([

                MessageTemplates
                ],
                MessageTemplates.text_number == text_number,
                MessageTemplates.profile_id == profile_id):
            #
            # UPDATE SECTION
            #
            text_id = db_get_rows([MessageTemplates.text_id],
                                  MessageTemplates.text_number == text_number)[
                0][0]
            update_error = db_text_update(text_id=text_id,
                                          text=text)
            if not update_error:
                return render_template('message_templates.html',
                                       error='Не удалось обновить шаблон')
            #
            # END UPDATE SECTION
            #
            if 'PROFILES_VISIBILITY' in list(current_user.privileges.keys()):
                templates = db_get_rows([
                        Texts.text_id,
                        Texts.text,
                        MessageTemplates.text_number],
                        Texts.text_id == MessageTemplates.text_id,
                        Profiles.profile_id == MessageTemplates.profile_id,
                        Profiles.profile_password,
                        Profiles.profile_id == profile_id)
            else:
                templates = db_get_rows([
                        Texts.text_id,
                        Texts.text,
                        MessageTemplates.text_number],
                        Texts.text_id == MessageTemplates.text_id,
                        Profiles.profile_id == MessageTemplates.profile_id,
                        Profiles.profile_password,
                        Profiles.profile_id == profile_id,
                        Visibility.profile_id == profile_id,
                        Visibility.login == current_user.login)
            return render_template(
                    'message_templates.html',
                    templates=templates,
                    accounts=accounts,
                    selected_account=profile_id,
                    selected_account_nickname=selected_account_nickname)
        create_error = True
        if not create_error:
            return render_template('message_templates.html',
                                   error='Не удалось создать шаблон')
        #
        # CREATE SECTION
        #
        logger.info(f'User {current_user.login} start load template')
        text_id = uuid4().bytes
        db_session = Session()
        text_row = Texts(text_id=text_id,
                         text=text)
        text_to_profile_row = MessageTemplates(text_id=text_id,
                                               profile_id=profile_id,
                                               text_number=text_number)
        tagging_row = Tagging(text_id=text_id,
                              tag='template')
        # add text to DB
        db_session.add(text_row)
        db_session.commit()

        # add text assign to profile to DB
        db_session.add(text_to_profile_row)
        db_session.commit()
        db_session.close()
        db_session = Session()
        # add tagging to text in DB
        db_session.add(tagging_row)
        db_session.commit()
        db_session.close()

        logger.info(f'User {current_user.login} ended load template'
                    f'with template_number: {text_number} and'
                    f' text_id: {text_id}')
        #
        # END CREATE SECTION
        #
        if 'PROFILES_VISIBILITY' in list(current_user.privileges.keys()):
            templates = db_get_rows([
                    Texts.text_id,
                    Texts.text,
                    MessageTemplates.text_number],
                    Texts.text_id == MessageTemplates.text_id,
                    Profiles.profile_id == MessageTemplates.profile_id,
                    Profiles.profile_password,
                    Profiles.profile_id == profile_id)
        else:
            templates = db_get_rows([
                    Texts.text_id,
                    Texts.text,
                    MessageTemplates.text_number],
                    Texts.text_id == MessageTemplates.text_id,
                    Profiles.profile_id == MessageTemplates.profile_id,
                    Profiles.profile_password,
                    Profiles.profile_id == profile_id,
                    Visibility.profile_id == profile_id,
                    Visibility.login == current_user.login)
        templates = sorted(templates,
                           key=lambda x: x[2])

        return render_template(
                'message_templates.html',
                templates=templates,
                accounts=accounts,
                selected_account=profile_id,
                selected_account_nickname=selected_account_nickname)


    return render_template('message_templates.html',
                           accounts=accounts)


@app.route('/mail/templates/edit', methods=['POST'])
@login_required
def message_template_edit():
    info = request.get_json(force=True)
    #
    # UPDATE SECTION
    #
    text = info['text']
    profile_id = info['profile_id']
    text_number = int(info['num'])
    if db_duplicate_check([
            MessageTemplates
            ],
            MessageTemplates.text_number == text_number,
            MessageTemplates.profile_id == profile_id):
        text_id = db_get_rows([MessageTemplates.text_id],
                              MessageTemplates.text_number == text_number,
                              MessageTemplates.text_number == text_number)[0][
            0]
        update_error = db_text_update(text_id=text_id,
                                      text=text)
        if not update_error:
            return render_template('message_templates.html',
                                   error='Не удалось обновить шаблон')
    #
    # END UPDATE SECTION
    #
    return redirect(url_for('message_templates'))


@app.route('/mail/templates/delete', methods=['POST'])
@login_required
def message_template_delete():
    info = request.get_json(force=True)
    text_number = int(info['num'])
    #
    # DELETE SECTION
    #
    text_id = db_get_rows([MessageTemplates.text_id],
                          MessageTemplates.text_number == text_number)
    if len(text_id) != 0:
        text_id = text_id[0][0]
    else:
        return render_template('message_templates.html',
                               error='Текст уже удален')
    delete_templates_count = db_delete_rows([
            MessageTemplates
            ],
            MessageTemplates.text_id == text_id)
    text_in_msg = db_duplicate_check([Messages],
                                     Messages.text_id == text_id)
    if not text_in_msg:
        deleted_tags = db_delete_rows([
                Tagging
                ],
                Tagging.text_id == text_id)
        deleted_texts = db_delete_rows([
                Texts
                ],
                Texts.text_id == text_id)
        if deleted_texts == 0:
            return render_template('message_templates.html',
                                   error='Текст уже удален')

    #
    # END DELETE SECTION
    #
    return redirect(url_for('message_templates'))


@app.route('/mail/templates/<account>', methods=['GET', 'POST'])
@login_required
def message_template_account(account):
    return render_template("message_templates.html")


@app.route('/mail/anchors', methods=['GET', 'POST'])
@login_required
def message_anchor():
    if 'PROFILES_VISIBILITY' in list(current_user.privileges.keys()):
        # if user can view all profiles, we doesn't filter by access
        accounts = db_get_rows([
                Profiles.profile_id,
                ProfileDescription.name,
                ProfileDescription.nickname
                ],
                Profiles.profile_password,
                Profiles.available == 1,
                ProfileDescription.profile_id == Profiles.profile_id)
    else:
        accounts = db_get_rows([
                Profiles.profile_id,
                ProfileDescription.name,
                ProfileDescription.nickname
                ],
                Profiles.profile_password,
                Profiles.available == 1,
                Visibility.login == current_user.login,
                Visibility.profile_id == Profiles.profile_id,
                ProfileDescription.profile_id == Profiles.profile_id)

    if request.method == "POST":
        profile_id = request.form.get('account_id')
        for account in accounts:
            if account[0] == profile_id:
                selected_account_nickname = account[2]
                break
        if profile_id:

            if 'PROFILES_VISIBILITY' in list(current_user.privileges.keys()):
                anchors = db_get_rows([
                        Texts.text_id,
                        Texts.text],
                        Texts.text_id == MessageAnchors.text_id,
                        Profiles.profile_id == MessageAnchors.profile_id,
                        Profiles.profile_password,
                        Profiles.profile_id == profile_id)
            else:
                anchors = db_get_rows([
                        Texts.text_id,
                        Texts.text],
                        Texts.text_id == MessageAnchors.text_id,
                        Profiles.profile_id == MessageAnchors.profile_id,
                        Profiles.profile_password,
                        Profiles.profile_id == profile_id,
                        Visibility.profile_id == profile_id,
                        Visibility.login == current_user.login)
            anchors = list(anchors)
            for anchor_i in range(len(anchors)):
                anchors[anchor_i] = list(anchors[anchor_i])
                anchors[anchor_i].append(
                        db_get_rows([Tags.tag],
                                    Tags.tag == Tagging.tag,
                                    Tagging.text_id == anchors[anchor_i][0]))
                anchors[anchor_i][0] = UUID(bytes=anchors[anchor_i][0])
        else:
            anchors = []


        # If this is only accounts select form
        if not request.form.get('key_text'):
            return render_template(
                    'anchor_templates.html',
                    anchors=anchors,
                    accounts=accounts,
                    selected_account=profile_id,
                    selected_account_nickname=selected_account_nickname)

        # Load anchor text
        key_names = request.form.getlist('key_name')
        key_text = request.form.get('key_text')
        logger.info(f'User {current_user.login} load new anchor')
        #
        # CREATE SECTION
        #
        logger.info(f'User {current_user.login} start load anchor')
        text_id = uuid4().bytes
        db_session = Session()
        text_row = Texts(text_id=text_id,
                         text=key_text)
        text_to_profile_row = MessageAnchors(text_id=text_id,
                                             profile_id=profile_id)
        # add text to DB
        db_session.add(text_row)
        db_session.commit()

        # add text assign to profile to DB
        db_session.add(text_to_profile_row)
        db_session.commit()
        db_session.close()

        for key_n in key_names:
            db_session = Session()
            if not db_duplicate_check([Tags],
                                      Tags.tag == key_n):
                # if in DB no such tag, we create new
                tag = Tags(tag=key_n)
                db_session.add(tag)
                db_session.commit()

            tagging_row = Tagging(text_id=text_id,
                                  tag=key_n)
            # add tagging to text in DB
            db_session.add(tagging_row)
            db_session.commit()
            db_session.close()

        logger.info(f'User {current_user.login} ended load anchor'
                    f'with text_id: {text_id}')
        #
        # END CREATE SECTION
        #
        if profile_id:
            if 'PROFILES_VISIBILITY' in list(current_user.privileges.keys()):
                anchors = db_get_rows([
                        Texts.text_id,
                        Texts.text],
                        Texts.text_id == MessageAnchors.text_id,
                        Profiles.profile_id == MessageAnchors.profile_id,
                        Profiles.profile_password,
                        Profiles.profile_id == profile_id)
            else:
                anchors = db_get_rows([
                        Texts.text_id,
                        Texts.text],
                        Texts.text_id == MessageAnchors.text_id,
                        Profiles.profile_id == MessageAnchors.profile_id,
                        Profiles.profile_password,
                        Profiles.profile_id == profile_id,
                        Visibility.profile_id == profile_id,
                        Visibility.login == current_user.login)
            anchors = list(anchors)
            for anchor_i in range(len(anchors)):
                anchors[anchor_i] = list(anchors[anchor_i])
                anchors[anchor_i].append(
                        db_get_rows([Tags.tag],
                                    Tags.tag == Tagging.tag,
                                    Tagging.text_id == anchors[anchor_i][0]))
                anchors[anchor_i][0] = UUID(bytes=anchors[anchor_i][0])
        else:
            anchors = []
        return render_template(
                'anchor_templates.html',
                anchors=anchors,
                accounts=accounts,
                selected_account=profile_id,
                selected_account_nickname=selected_account_nickname)
    return render_template(
            'anchor_templates.html',
            accounts=accounts)


@app.route('/mail/anchors/edit', methods=['POST'])
@login_required
def message_anchor_edit():
    info = request.get_json(force=True)
    #
    # UPDATE SECTION
    #
    text_id = UUID(info['id']).bytes
    profile_id = info['profile_id']
    text = info['text']
    if db_duplicate_check([
            MessageAnchors
            ],
            MessageAnchors.text_id == text_id,
            MessageAnchors.profile_id == profile_id):

        update_error = db_text_update(text_id=text_id,
                                      text=text)
        if not update_error:
            return render_template('anchor_templates.html',
                                   error='Не удалось обновить якорь')
    #
    # END UPDATE SECTION
    #
    return redirect(url_for('message_anchor'))


@app.route('/mail/anchors/delete', methods=['POST'])
@login_required
def message_anchor_delete():
    info = request.get_json(force=True)
    text_id = UUID(info['id']).bytes
    #
    # DELETE SECTION
    #
    delete_templates_count = db_delete_rows([
            MessageAnchors
            ],
            MessageAnchors.text_id == text_id)
    text_in_msg = db_duplicate_check([Messages],
                                     Messages.text_id == text_id)
    if not text_in_msg:
        # find tags which used for template
        anchor_tags = db_get_rows_2([Tagging.tag],
                                    [Tagging.text_id == text_id])
        anchor_tags = set([tag[0] for tag in anchor_tags])
        # delete_tags_assign
        deleted_tags_assign = db_delete_rows([
                Tagging
                ],
                Tagging.text_id == text_id)
        # find similar tags which used for
        # another templates and this template
        shared_anchor_tags = db_get_rows_2([Tagging.tag],
                                           [Tagging.tag.in_(anchor_tags)])
        shared_anchor_tags = set([tag[0] for tag in shared_anchor_tags])
        tags_to_delete = anchor_tags - shared_anchor_tags
        detele_tags = db_delete_rows_2([Tags],
                                       [Tags.tag.in_(tags_to_delete)],
                                       synchronize_session='fetch')
        deleted_texts = db_delete_rows([
                Texts
                ],
                Texts.text_id == text_id)
        if deleted_texts == 0:
            return render_template('anchor_templates.html',
                                   error='Якорь уже удален')

    #
    # END DELETE SECTION
    #
    return redirect(url_for('message_anchor'))


@app.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    sending = False
    if request.method == 'POST':
        sending = True
        return render_template("messages.html",
                               sending=sending)
    return render_template('messages.html', sending=sending)


@app.route('/users_list', methods=['GET', 'POST'])
@login_required
def users_list():
    logger.info(f'User {current_user.login} load user list')
    user_list = db_get_users()
    return jsonify(rows=user_list)


@app.route('/logs', methods=['GET', 'POST'])
@login_required
def logs():
    logs = db_get_rows_2([Logs.login,
                          Logs.category,
                          Logs.message,
                          Logs.ip,
                          Logs.create_time
                          ],
                         order_by=[Logs.create_time],
                         descending=True,
                         limit=1000)
    return render_template('logs.html', logs=logs)


if __name__ == "__main__":
    # Проверка базы данных на ошибки
    """db_error_check(empty_chats=True,
                   profiles_without_chats=True,
                   unused_texts=True)"""

    # Обработка сообщений и подготовка шаблонов с якорями
    """from background_worker import worker_msg_sender
    print(worker_msg_sender())"""

    # Обновление диалогов с сайта
    """from background_worker import worker_profile_and_msg_updater
    from multiprocessing import Process

    t1 = Process(target=worker_profile_and_msg_updater)
    t1.start()
    workers_number += 1"""
    # Основной бот:
    """from background_worker import main_worker
    from multiprocessing import Process
    p_mainbot = Process(target=main_worker)
    p_mainbot.start()
    workers_number += 1"""
    # Run the app until stopped
    app.run()
