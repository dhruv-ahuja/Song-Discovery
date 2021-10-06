from flask import *
import spotipy
from os import getenv
from functools import wraps


# initialize the blueprint containing the base functions of the application
bp = Blueprint("main", __name__, template_folder="templates/routes")

# setup env & scope to define access to the spotify web api
client_id = getenv("CLIENT_ID")
client_secret = getenv("CLIENT_SECRET")
redirect_uri = getenv("REDIRECT_URI")

scope = "user-library-read user-top-read user-read-recently-played user-library-modify"


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        # if the user hasn't logged in
        if not session.get("token_info"):

            return redirect(url_for("main.index"))

        # refresh the token if it has expired
        if spotipy.SpotifyOAuth.is_token_expired(session.get("token_info")):

            refresh_token = session["token_info"]["refresh_token"]

            get_new_token = init().refresh_access_token(refresh_token)

            session["token_info"] = get_new_token

            flash("Your token has been renewed.")
            return redirect(url_for("main.index"))

        return f(*args, **kwargs)

    return decorated_function


@bp.route("/")
def index():
    """
    the index route, will guide the user to authorization,
    will connect the user with the application.
    """

    return render_template("index.html")


@bp.route("/auth")
def auth_user():
    """
    the auth route checks if the user has already logged in.
    if so, it lets the user proceed back to the main page and
    allows them to start using the application.

    Generates the authorization url which will contain the token information we need to get going.
    """

    if "token_info" not in session:
        # Don't reuse a SpotifyOAuth object because they store token info
        # and you could leak user tokens if you do reuse it
        sp_auth = init()

        auth_url = sp_auth.get_authorize_url()

        return redirect(auth_url)

    flash("You have been authorized.")

    return redirect(url_for("main.index"))


@bp.route("/api_callback")
def api_callback():
    """
    This is the page that Spotify will redirect the user to, after they have authorized our application.
    The activities of this page happen quickly so user won't notice the redirect.

    Here, we once again, use the oauth2 method but this time to get user token information.
    """

    # generate a new Oauth to prevent user token leaks
    sp_auth = init()

    token = sp_auth.get_cached_token()

    # saving token information
    session["token_info"] = token

    # making the session data permanent so that we can access it b/w requests
    session.permanent = True

    return redirect(url_for("main.index"))


@bp.route("/search", methods=["POST"])
@token_required
def return_data():
    """
    Takes the user input, searches for it in Spotify's database and returns the 4 most relevant results.

    """
    # check if the token is valid or not
    token_expired = spotipy.SpotifyOAuth.is_token_expired(session["token_info"])

    # if the token has expired, use the logout function
    # if token_expired:

    #     flash("Your token has expired.")
    #     return redirect(url_for("main.logout"))

    token = session["token_info"]["access_token"]

    session.modified = True

    # request the form data submitted by the user
    item = request.form

    song_name = item["song_name"]
    artist_name = item["artist_name"]

    # join the artist and the song name to be searched
    song_name = artist_name + " " + song_name

    sp = spotipy.Spotify(auth=session.get("token_info").get("access_token"))

    try:
        search_song = sp.search(song_name, limit=4, type="track")

    except spotipy.exceptions.SpotifyException as e:

        flash("Invalid input or access method")
        return redirect(url_for("main.index"))

    except KeyError as e:

        flash("Invalid input or access method")
        return redirect(url_for("main.index"))

    search_data = []

    # there can be many artists, arrange for that so that no artist is left out of search results

    for idx, item in enumerate(search_song["tracks"]["items"]):

        song_id = item["id"]

        song_name = item["name"]

        song_img = item["album"]["images"][0]["url"]

        if len(item["artists"]) == 1:
            song_artist = item["artists"][0]["name"]

            search_data.append((song_id, song_artist, song_name, song_img, idx + 1))

        else:
            song_artist = ""
            for value in item["artists"]:
                song_artist = song_artist + value["name"] + ", "

            search_data.append(
                (song_id, song_artist[:-2], song_name, song_img, idx + 1)
            )

    return render_template("search.html", data=search_data)


@bp.route("/song/<song_id>")
@token_required
def recommendations(song_id):
    """
    Generate recommendations for the user based on the selected song.
    """
    return "OK"


@bp.route("/logout")
def logout():
    """
    Log the user out of the application.
    """
    session.clear()
    flash("You have been logged out.")

    return redirect(url_for("main.index"))


def init():
    """
    Initialize the Spotify API object here
    """
    sp = spotipy.oauth2.SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
        show_dialog=True,
    )

    return sp
