# coding: utf8
# Imports the Flask class
import logging
import os
from urllib.parse import urljoin, urlparse

from flask import Flask, abort, jsonify, redirect, render_template, request, \
    url_for
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required, \
    login_user, \
    logout_user
from flask_wtf.csrf import CSRFProtect

from authentication import find_user
from control_panel import *
from email_service import send_email_instruction

# Creates an app and checks if its the main or imported
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
logger = logging.getLogger("werkzeug")
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)
app.logger = logger
"""You will need to provide a user_loader callback.
This callback is used to reload the user object from 
the user ID stored in the session.
It should take the unicode ID of a user, and return 
the corresponding user object.
It should return None (not raise an exception) 
if the ID is not valid.
(In that case, the ID will manually be removed 
from the session and processing will continue.)"""


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


@app.route('/invite_user', methods=['POST'])
@login_required
def invite_user():
    invited_email = request.form.get('recipient-name')
    send_email_instruction(email_to=invited_email)
    error = not create_invite(creator=current_user,
                              invited_email=invited_email,
                              role='default')
    user_list = db_get_users()
    return render_template('users.html',
                           user_list=user_list,
                           error=error)


# logout
@app.route('/profile_dialogue', methods=['GET', 'POST'])
@login_required
def profile_dialogue():
    """
    invited_email = f'{randint(1, 999)}@gmail.com'
    create_invite(creator=current_user,
                  invited_email=invited_email,
                  role='default')
    logger.info(f'created invite for e-mail: {invited_email}')"""
    senders = db_get_profiles(Profiles.profile_password)
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
            receivers = db_show_receivers(sender)
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
                receivers = db_show_receivers(sender)
            dialog = db_show_dialog(sender=sender,
                                    receiver=receiver)
    return render_template('profile_dialogue.html',
                           dialog=dialog,
                           senders=senders,
                           receivers=receivers,
                           selected_sender=sender,
                           selected_receiver=receiver)


# logout
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
        logger.error(
                f"Invalid username/password by {request.form.get('email')}")

    # Returns the html page to be displayed
    return render_template('login.html',
                           error='Неправильный логин или пароль!')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        error = register_user(login=request.form.get('email'),
                              user_password=request.form.get('password'))
        if not error:
            return render_template("confirmation.html")
        else:
            render_template('signup.html', error=error)
    return render_template('signup.html')


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


@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    logger.info(f'User {current_user.login} opened user list')
    user_list = db_get_users()
    return render_template('users.html', user_list=user_list)


@app.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    sending = False

    if request.method == 'POST':
        for k, v in zip(request.form.keys(), request.form.values()):
            print(f"{k}:", v, type(v))
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


if __name__ == "__main__":

    # Run the app until stopped
    app.run(debug=True)
