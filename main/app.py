# from datetime import timedelta
from logging import debug
from flask import Flask
from os import getenv, urandom

# setting up the Flask app
app = Flask(__name__)

# check for environment
is_prod = getenv("IS_HEROKU", None)

# if we are in a production environment:
if is_prod:
    app.secret_key = urandom(24)
    # app.config["SESSION_COOKIE_NAME"] = "current_session"
    # app.config["SESSION_TYPE"] = "filesystem"

else:
    app.secret_key = "test"
    # app.config["SESSION_COOKIE_NAME"] = "current_session"
    # app.config["SESSION_TYPE"] = "filesystem"

# importing blueprint(s)
from routes import views

# test
app.register_blueprint(views.bp)


if __name__ == "__main__":
    app.run(debug=True)
