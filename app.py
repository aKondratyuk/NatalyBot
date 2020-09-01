import os
from urllib.parse import urlparse, urljoin

import flask
import numpy as np
from flask import Flask, flash, render_template, request, redirect, url_for
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename

from database import Ench_col, db
from forms import *
from main import *
from users import find_user, find_user_id

# dict of allowed extensions for uploaded files
ALLOWED_EXTENSIONS = {'xlsx'}


# check for allowed file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# args container for admin page
def load_args():
    args = {
        'current_user': current_user,
        'register_f': RegisterForm(),
        'add_profile_f': AddProfileForm(),
        'add_profile_description_f': AddProfileDescriptionForm(),
        'upload_profiles_f': UploadProfilesForm(),
        'users': db.Users.find(),
        'profiles': db.Profiles.find()
    }
    return args


# check for admin
def admin_check(func):
    def new_func():
        # Check user login
        if current_user.is_authenticated:
            return redirect(url_for('hello'))
        else:
            func()

    return new_func


# needed for safe connection, from tutorial
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


# settings for flask app
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    # Database URI format:
    # dialect+driver://username:password@host:port/database
    # dialect - mysql, mssql, postgresql...
    # host - database location
    # port - database server port
    # database - database nam

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    return app


app = create_app()
# login manager instance creation and setting
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'You are not authorized, please log in'


# You will need to provide a user_loader callback.
# This callback is used to reload the user object from the user ID stored in the session.
# It should take the unicode ID of a user, and return the corresponding user object.
# It should return None (not raise an exception) if the ID is not valid.
# (In that case, the ID will manually be removed from the session and processing will continue.)
@login_manager.user_loader
def load_user(user_id):
    return find_user_id(user_id)  # Return User object or None


@app.route('/')
@app.route('/index')
@login_required
def index():
    return redirect(url_for('hello'))


# login field
@app.route('/login', methods=['POST', 'GET'])
def user_login():
    # Check user login
    if current_user.is_authenticated:
        return redirect(url_for('hello'))

    form = LoginForm()

    if form.validate_on_submit():
        # Login and validate the user.
        # user should be an instance of your `User` class
        user = find_user(form.username.data)
        if user:
            if user.check_password(form.password.data):
                # User saving in session
                login_user(user, remember=form.remember.data)

                flash('Logged in successfully.')

                next = flask.request.args.get('next')
                # is_safe_url should check if the url is safe for redirects.
                if not is_safe_url(next):
                    return flask.abort(400)

                return flask.redirect(next or url_for('index'))

        flash("Invalid username/password", 'error')
        return redirect(url_for('login'))
    return render_template('main.html', form=form)


# successful authorization page
@app.route('/hello')
@login_required
def hello():
    # Assuming that there is a name property on your user object
    # returned by the callback
    return render_template('hello.html', current_user=current_user)


# admin page
@app.route('/admin', methods=['POST', 'GET'])
@login_required
def admin():
    add_profile_description_f = AddProfileDescriptionForm()

    return render_template('admin.html', **load_args())


# register
@app.route('/register', methods=['POST'])
@login_required
def register():
    register_f = RegisterForm()

    if register_f.validate_on_submit():
        ins_col = Ench_col(db.Users)
        if not ins_col.insert({
            field.id: field.data for field in register_f
            if field.id != 'submit' and field.id != 'confirm' and field.id != 'csrf_token'
        }, ['username']):
            flash('Such user already exists!', 'error')
            return render_template('admin.html', **load_args())
        return redirect(url_for('admin'))

    return render_template('admin.html', **load_args())


def profile_status(profile_id: str, profile_password: str):
    if login(profile_id, profile_password):
        if profile_deleted(profile_id):
            return 'hidden'
        return False
    elif profile_deleted(profile_id):
        return 'wrong'
    else:
        return 'deleted'


# add_profile
@login_required
@app.route('/profile_table', methods=['POST'])
def profile_table():
    add_profile_f = AddProfileForm()
    print(request)
    if request.form['btn'] == "Delete":
        profiles_col = Ench_col(db.Profiles)
        for id in request.form.keys():
            if id != 'btn':
                if not profiles_col.delete({'login': id}):
                    flash(f'Detele error with profile id: {id}')
        return redirect(url_for('admin'))
    elif request.form['btn'] == "Отправить от выбранных профилей":
        profiles_col = Ench_col(db.Profiles)
        for id in request.form.keys():
            if id != 'btn':
                if not profiles_col.delete({'login': id}):
                    flash(f'Detele error with profile id: {id}')
        return redirect(url_for('admin'))
    elif request.form['btn'] == "Отправить от всех профилей":
        profiles_col = Ench_col(db.Profiles)
        for id in request.form.keys():
            if id != 'btn':
                if not profiles_col.delete({'login': id}):
                    flash(f'Detele error with profile id: {id}')
        return redirect(url_for('admin'))


# add_profile
@app.route('/add_profile', methods=['POST'])
def add_profile():
    add_profile_f = AddProfileForm()

    if add_profile_f.validate_on_submit():
        hidden_status = False
        if profile_status(add_profile_f.login.data, add_profile_f.password.data) == 'wrong':
            flash('Такого профиля не существует, неверный логин или пароль', 'error')
            return render_template('admin.html', **load_args())
        elif profile_status(add_profile_f.login.data, add_profile_f.password.data) == 'hidden':
            # проверка на скрытность, внешняя
            profile = {key: "Not specified" for key in ['Name', 'Nickname', 'Age']}
            hidden_status = True
        else:
            profile = collect_info_from_profile(str(add_profile_f.login.data))

        db_profile = {
            field.id: field.data for field in add_profile_f
            if
            field.id != 'submit' and field.id != 'csrf_token' and field.id != 'invite_name' and field.id != 'msg_limit'
        }

        db_profile["name"] = profile["Name"]
        db_profile["nickname"] = profile["Nickname"]
        db_profile["age"] = profile["Age"]
        db_profile["deleted"] = False
        db_profile["hidden"] = hidden_status
        db_profile["msg_limit"] = add_profile_f.msg_limit.data
        db_profile["invite_name"] = add_profile_f.invite_name.data
        ins_col = Ench_col(db.Profiles)
        print(db_profile)
        if not ins_col.insert(db_profile, ['login']):
            flash('Such profile already exists!', 'error')
            return render_template('admin.html', **load_args())
        return redirect(url_for('admin'))

    return render_template('admin.html', **load_args())


# upload file
@login_required
def upload_file(form):
    if form.validate_on_submit():
        file = form.file.data
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return False
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.instance_path, filename))
            return os.path.join(app.instance_path, filename)
        flash('Wrong format')
    return False


def load_excel(filepath, form):
    # open saved file
    wb = read_excel_file(filepath)
    sheets = wb.sheetnames
    i = form.sheet_number.data

    # check wrong page number
    if int(i) > len(sheets):
        flash("Нету такого листа!\n")
        return render_template('admin.html', **load_args())

    return wb[sheets[int(i) - 1]]


def check_accounts(sheet):
    data = get_sheet_values(sheet)

    # add new columns
    for col in ['Name', 'Nickname', 'Age']:
        data[col] = [None for i in range(data['Login'].count())]
    for col in ['msg_limit', 'deleted', 'hidden']:
        data[col] = [False for i in range(data['Login'].count())]

    print(data)
    for index in data.index:
        try:
            profile = collect_info_from_profile(str(data['Login'][index]))
        except Exception as ex:
            flash(f"Профиль номер с логином {data['Login'][index]} не существует")
            # delete row with wrong account
            data = data.drop(index=index)
            continue
        data["Name"][index] = profile["Name"]
        data["Nickname"][index] = profile["Nickname"]
        data["Age"][index] = profile["Age"]
    # reindex after rows delete
    data.index = np.arange(1, len(data['Login']) + 1)

    # move 'Path to text file' to end of representation view
    last_col = data.pop('Path to text file')
    data.insert(data.columns.size, 'invite_name', last_col)

    # Change column names to low register
    data.columns = [col.lower() for col in data.columns]
    return data


# upload_profiles
@app.route('/upload_profiles', methods=['POST'])
@login_required
def upload_profiles():
    upload_profiles_f = UploadProfilesForm()
    filepath = upload_file(upload_profiles_f)

    # check file path is exists
    if filepath:
        # open excel file
        sheet = load_excel(filepath, upload_profiles_f)
        # check accounts
        data = check_accounts(sheet)

        # data transform from [[val, val], [..]] format to [{header:val, header:val}, {..}]
        profiles = data.to_dict('records')
        # Add profiles to database ### need refactoring to another func
        ins_col = Ench_col(db.Profiles)
        for profile in profiles:
            if not ins_col.insert(profile, ['login']):
                flash(f'Such login:{profile["login"]} already exists!', 'error')
                print(f'Such login:{profile["login"]} already exists!')
        flash("Аккаунты успешно загружены!\n")
        redirect(url_for('admin'))

    # flashing all errors
    for error in upload_profiles_f.errors.keys():
        flash(*upload_profiles_f.errors[error], 'error')
    return render_template('admin.html', **load_args())


"""
    if load_profiles_f.validate_on_submit():
        ins_col = Ench_col(db.Profiles)
        if not ins_col.insert({
            field.id: field.data for field in add_profile_f
            if field.id != 'submit' and field.id != 'csrf_token'
        }, ['login']):
            flash('Such profile already exists!', 'error')
            return render_template('admin.html', **load_args())
        return redirect(url_for('admin'))
"""


def send_from_profile(profile_login, password,
                      data,
                      looking_for="male",
                      date_of_birth_end="40",
                      page=1,
                      messages_need_to_be_sent=30,
                      photos_only="off"):
    values = login(profile_login, password)
    if values:
        session, my_profile_id = values
        my_data = collect_info_from_profile(my_profile_id)
        nickname = my_data["Nickname"]
        print(f"\nПРОФИЛЬ {nickname} НАЧИНАЕТ РАССЫЛКУ\n")
        idx = 1
        messages_has_sent = 0
        STOP = False
        while messages_has_sent != messages_need_to_be_sent:
            if STOP:
                break
            profiles = search_for_profiles(my_data["Sex"], looking_for, my_data["Age"],
                                           date_of_birth_end, page, photos_only)
            profiles_id = get_id_profiles(profiles)
            for profile_id in profiles_id:
                check_response = check_for_filter(session, profile_id, idx)
                idx += 1
                if check_response:
                    if check_response == "LIMIT OUT":
                        STOP = True
                else:
                    invite_path = "invite messages/" + data["path to text file"][i]
                    message_text = create_custom_message(my_profile_id, profile_id, invite_path)
                    message(session, profile_id, message_text)
                    print(f"{idx}. Удалось отправить сообщение {profile_id}. Осталось отправить"
                          f" {messages_need_to_be_sent - messages_has_sent}", datetime.now())
                    idx += 1
                    messages_has_sent += 1
                    if messages_has_sent == messages_need_to_be_sent:
                        print(f"\nПРОФИЛЬ {nickname} ЗАВЕРШИЛ РАССЫЛКУ\n")
                        return True
            page += 1
    else:
        print(f"Неверный логин или пароль у профиля {profile_login}")
        return False


# old 3 choice in menu "3. Рассылка по фильтру"
def spam_filter(data,
                looking_for="male",
                date_of_birth_end="40",
                page=1,
                messages_need_to_be_sent=30,
                photos_only="off",
                ):
    # choice = input("\nНапишите через запятую номера аккаунтов: \n")
    # changed profile from number in printed table to id

    # manual profile_id set with form on site
    senders_id_list = []  # temporary accounts id's
    if len(senders_id_list) == 0:  # if no manual selection
        senders_id_list = data['login']

    for id in senders_id_list:
        # profile finded successfully
        profile_login, password = str(data["login"][i]), data["password"][i]
        send_from_profile(profile_login, password, looking_for,
                          date_of_birth_end,
                          page,
                          messages_need_to_be_sent,
                          photos_only)


# add_profile_description
@app.route('/add_profile_description', methods=['POST'])
@login_required
def add_profile_description():
    add_profile_description_f = AddProfileDescriptionForm()

    # Form validation
    if add_profile_description_f.validate_on_submit():
        # create enchanced form
        ins_col = Ench_col(db.Profiles_description)
        if not ins_col.insert({
            field.id: field.data for field in add_profile_description_f
            if field.id != 'submit' and field.id != 'csrf_token'
        }, ['login']):
            # Failed to insert
            flash('Such add profile description already exists!', 'error')
            return render_template('admin.html', **load_args())
        # Successfuly added profile
        return redirect(url_for('admin'))
    for error in add_profile_description_f.errors.keys():
        flash(*add_profile_description_f.errors[error], 'error')
    return render_template('admin.html', **load_args())


# logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run()
