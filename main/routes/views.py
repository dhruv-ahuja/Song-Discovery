from flask import *
import spotipy
from .view_funcs import *
from random import randrange

# initialize the blueprint containing the base functions of the application
bp = Blueprint("main", __name__, template_folder="templates/routes")


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
    # connect to the spotify api
    sp = spotipy.Spotify(auth=session.get("token_info").get("access_token"))

    check_len = False

    while not check_len:
        song_rec = sp.recommendations(
            seed_tracks=[song_id], limit=10, min_popularity=randrange(30, 80)
        )

        if len(song_rec) < 5:
            check_len = True

    song_data = []

    for _, item in enumerate(song_rec["tracks"]):

        # song_id = item["id"]
        song_url = item["external_urls"]["spotify"]

        # need to make spotify url embeddable by adding "/embed" before "/tracks"
        embed_url = song_url.split(".com")
        embed_url.insert(1, ".com/embed")
        embed_url = "".join(embed_url)

        song_url = item["uri"]

        song_name = item["name"]

        song_img = item["album"]["images"][0]["url"]

        if len(item["artists"]) == 1:
            song_artist = item["artists"][0]["name"]

            song_data.append((song_url, embed_url, song_artist, song_name, song_img))

        else:
            song_artist = ""
            for value in item["artists"]:
                song_artist = song_artist + value["name"] + ", "

            song_data.append(
                (song_url, embed_url, song_artist[:-2], song_name, song_img)
            )

    if song_name is None:
        flash(f"{song_name} is None, perhaps problems with the API.")

    if song_artist is None:
        flash(f"{song_artist} is None, perhaps problems with the API.")

    return render_template("recommendations.html", data=song_data)


@bp.route("/save/<song_uri>")
def save_to_library(song_uri):
    """
    Saves the user-selected song to library
    """
    save_song = spotipy.Spotify(
        session["token_info"]["access_token"]
    ).current_user_saved_tracks_add(tracks=[song_uri])

    return "Saved the track to your library."


@bp.route("/logout")
def logout():
    """
    Log the user out of the application.
    """
    session.clear()
    flash("You have been logged out.")

    return redirect(url_for("main.index"))
