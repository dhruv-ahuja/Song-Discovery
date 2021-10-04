from datetime import timedelta
from flask import Flask


# setting up the Flask app
app = Flask(__name__)
app.secret_key = "test"
app.permanent_session_lifetime = timedelta(minutes=55)


# importing blueprint(s)
from routes import views

app.register_blueprint(views.bp)


if __name__ == "__main__":
    app.run(debug=True)
