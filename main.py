# coding: utf8
# Imports the Flask class
import logging
import os
from urllib.parse import urljoin, urlparse

from flask import Flask, abort, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, current_user, login_required, \
    login_user, \
    logout_user
from flask_wtf.csrf import CSRFProtect

from authentication import find_user
from control_panel import *

# Creates an app and checks if its the main or imported
app = Flask(__name__)
app.config.update(TESTING=True,
                  SECRET_KEY=os.environ.get('APP_SECRET_KEY'))
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


# logout
@app.route('/test')
@login_required
def test():
    create_invite(creator=current_user,
                  invited_email='test_invite@gmail.com',
                  role='default')
    return redirect(url_for('login'))


# logout
@app.route('/test_create_user')
def test_create_user():
    create_user(login='admin@gmail.com',
                user_password='adminadmin',
                role='admin')
    return redirect(url_for('login'))


@app.route('/', methods=['GET', 'POST'])
# The function run on the index route
def login():

    print(current_user)
    print(request.form.get('email'))
    print(request.form.get('password'))
    if current_user.is_authenticated:
        return redirect(url_for('control_panel'))
    if request.method == 'POST':
        # Login and validate the user.
        # user should be an instance of your `User` class
        user = find_user(login=request.form.get('email'))
        if user:
            if user.check_password(request.form.get('password')):
                # User saving in session
                login_user(user, remember=request.form.get('remember-me'))
                print(current_user)
                logger.info(f"User {request.form.get('email')} "
                            "Logged in successfully.")
                print(request.args)
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


@app.route('/control_panel', methods=['GET', 'POST'])
@login_required
def control_panel():
    if request.method == 'POST':
        print(request.form.get('email'))
        print(request.form.get('password'))
        return render_template("confirmation.html")

    return render_template('control_panel.html')
