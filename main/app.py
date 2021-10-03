from datetime import timedelta
from flask import *
from dotenv import load_dotenv
import spotipy
from os import getenv
from sys import exc_info
from json import dumps

# from spotipy_auth import get_token

# from spotipy_auth import get_token

load_dotenv()

# setup env & scope to access spotify web api
client_id = getenv("CLIENT_ID")
client_secret = getenv("CLIENT_SECRET")
redirect_uri = getenv("REDIRECT_URI")

scope = "user-library-read user-top-read user-read-recently-played user-library-modify"


app = Flask(__name__)
app.secret_key = "test"
app.permanent_session_lifetime = timedelta(minutes=50)

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
    global sp_auth
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


@app.route("/data", methods=["GET", "POST"])
def return_data():
    # take user input, search for it, pick the most relevant results, extract seed data from the results and then feed it to the recommendations system.

    if request.method == "GET":
        flash("Not authorized.")

        return redirect(url_for("index"))

    if request.method == "POST":

        # check if the token is expired or not
        token_expired = spotipy.SpotifyOAuth.is_token_expired(session["token_info"])

        if not token_expired:

            token = session["token_info"]["access_token"]

            session.modified = True

            item = request.form

            song_name = item["song_name"]
            artist_name = item["artist_name"]

            song_name = artist_name + " " + song_name

            sp = spotipy.Spotify(auth=session.get("token_info").get("access_token"))

            try:
                search_song = sp.search(song_name, limit=2, type="track")

            except spotipy.exceptions.SpotifyException as e:

                flash("Invalid input or access method")
                return redirect(url_for("index.html"))

            except KeyError as e:

                flash("Invalid input or access method")
                return redirect(url_for("index.html"))

            search_data = []

            # pretty = dumps(search_song, indent=4, sort_keys=True)

            # print(pretty)
            # return "OK"

            # if len(search_song) == 1:
            #     pass

            for item in search_song["tracks"]["items"]:

                song_id = item["id"]
                song_artist = item["artists"][0]["name"]

                song_name = item["name"]
                song_img = item["album"]["images"][0]["url"]

                search_data.append((song_id, song_artist, song_name, song_img))

            # except:
            #     e = exc_info()[0]
            #     print(e)

            return render_template("data.html", data=search_data)

        else:
            session.clear()

            flash("You aren't logged in or your token has expired.")

            return redirect(url_for("auth_user"))


if __name__ == "__main__":
    app.run(debug=True)
