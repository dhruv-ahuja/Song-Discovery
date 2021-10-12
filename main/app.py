# from datetime import timedelta
from flask import Flask
from os import getenv

# setting up the Flask app
app = Flask(__name__)

# check for environment
is_prod = getenv("IS_HEROKU", None)

# if we are in a production environment:
if is_prod:
    app.secret_key = getenv("SECRET_KEY")
else:
    app.secret_key = "test"

# importing blueprint(s)
from routes import views

# test
app.register_blueprint(views.bp)


if __name__ == "__main__":
    app.run(debug=True)
