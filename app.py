# Imports the Flask class
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap
# Creates an app and checks if its the main or imported
app = Flask(__name__)
Bootstrap(app)

# Specifies what URL triggers hello_world()
@app.route('/')
# The function run on the index route
def login():
    # Returns the text to be displayed
    return render_template('login.html')
# If this script isn't an import

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