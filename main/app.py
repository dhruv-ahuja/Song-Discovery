from flask import *
from dotenv import load_dotenv
import spotipy
from os import getenv

load_dotenv()

# setup env & scope to access spotify web api
client_id = getenv("CLIENT_ID")
client_secret = getenv("CLIENT_SECRET")
redirect_uri = getenv("REDIRECT_URI")

scope = "user-library-read user-top-read user-read-recently-played user-library-modify"


app = Flask(__name__)
app.secret_key = "test"


# authorization code flow for spotipy. requesting auth
# the user will log in and authorize access
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/auth")
def auth_user():

    if "token_info" not in session:
        # Don't reuse a SpotifyOAuth object because they store token info
        # and you could leak user tokens if you reuse a SpotifyOAuth object
        sp_auth = spotipy.oauth2.SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            show_dialog=True,
        )

        auth_url = sp_auth.get_authorize_url()

        return redirect(auth_url)

    flash("You have been authorized.")

    return redirect(url_for("index"))


# authorization code flow step 2
# have the app request auth and refresh tokens from spotify
@app.route("/api_callback")
def api_callback():
    # generate a new Oauth to prevent user token leaks
    sp_auth = spotipy.oauth2.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        show_dialog=True,
    )

    session.clear()

    token = sp_auth.get_cached_token()

    # saving info + access_token
    session["token_info"] = token
    session.permanent = True

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
