# Imports the Flask class
import logging

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

from authentication import find_user

# Creates an app and checks if its the main or imported
app = Flask(__name__)
Bootstrap(app)
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
    return find_user(user_id=user_id)  # Return User object or None


@app.route('/')
# The function run on the index route
def login():
    # Returns the html page to be displayed
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        print(request.form.get('email'))
        print(request.form.get('password'))
        return render_template("confirmation.html")

    return render_template('signup.html')


if __name__ == "__main__":
    # Run the app until stopped
    app.run()
