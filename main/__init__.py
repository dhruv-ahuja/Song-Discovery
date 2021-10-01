from flask import *


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test"

    @app.route("/")
    def main_page():
        return render_template("home.html")

    return app
