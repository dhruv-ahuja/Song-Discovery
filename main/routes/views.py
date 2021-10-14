from flask import *
import spotipy
from .view_funcs import *
from random import randrange
import jsonify

# initialize the blueprint containing the base functions of the application
bp = Blueprint("main", __name__, template_folder="templates/routes")


@bp.route("/")
def index():
    """
    the index route, will guide the user to authorization,
    will connect the user with the application.
    """

    try:
        token_info = ast.literal_eval(request.cookies.get("token_info"))

    except ValueError as e:

        return render_template("index.html", token_info=None)

    # print(spotipy.SpotifyOAuth.is_token_expired(token_info))

    return render_template("index.html", token_info=token_info)


@bp.route("/auth")
def auth_user():
    """
    the auth route checks if the user has already logged in.
    if so, it lets the user proceed back to the main page and
    allows them to start using the application.

    Generates the authorization url which will contain the token information we need to get going.
    """

    token_info = request.cookies.get("token_info")

    if token_info is None:

        auth_url = init().get_authorize_url()

        return redirect(auth_url)

    # if "token_info" not in session:
    #     # Don't reuse a SpotifyOAuth object because they store token info
    #     # and you could leak user tokens if you do reuse it
    #     sp_auth = init()

    #     auth_url = sp_auth.get_authorize_url()

    #     return redirect(auth_url)

    return redirect(url_for("main.index"))


@bp.route("/api_callback")
def api_callback():
    """
    This is the page that Spotify will redirect the user to, after they have authorized our application.
    The activities of this page happen quickly so user won't notice the redirect.

    Here, we once again, use the oauth2 method but this time to get user token information.
    """

    code = request.args.get("code")

    token_info = init().get_access_token(code)

    resp = make_response(redirect(url_for("main.index")))
    resp.set_cookie("token_info", f"{token_info}", max_age=43200)

    flash("You've been authorized.")

    return resp

    # generate a new Oauth to prevent user token leaks
    # sp_auth = init()

    # token = init().get_cached_token()

    # # saving token information
    # session["token_info"] = token

    # # making the session data permanent so that we can access it b/w requests
    # session.permanent = True

    # flash("You have been authorized.")

    # return redirect(url_for("main.index"))


@bp.route("/search", methods=["POST"])
@token_required
def return_data():
    """
    Takes the user input, searches for it in Spotify's database and returns the 4 most relevant results.
    """

    token_info = ast.literal_eval(request.cookies.get("token_info"))

    # token = session["token_info"]["access_token"]

    # session.modified = True

    # request the form data submitted by the user
    item = request.form

    song_name = item["song_name"]
    artist_name = item["artist_name"]

    # join the artist and the song name to be searched
    song_name = artist_name + " " + song_name

    sp = spotipy.Spotify(auth=token_info.get("access_token"))

    try:
        search_song = sp.search(song_name, limit=4, type="track")

    except spotipy.exceptions.SpotifyException as e:

        flash("Invalid input or access method")
        return redirect(url_for("main.index"))

    except KeyError as e:

        flash("Invalid input or access method")
        return redirect(url_for("main.index"))

    if search_song["tracks"]["items"] == []:
        # the user query did not result in any parameters

        flash(
            "Your search did not bring up any songs. Please retry with different keywords."
        )

        return redirect(url_for("main.index"))

    # return search_song

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

    token_info = ast.literal_eval(request.cookies.get("token_info"))

    # connect to the spotify api
    sp = spotipy.Spotify(auth=token_info.get("access_token"))

    # check the length of the response, if it's less than 5, we need to regenerate the data set
    check_len = False
    while not check_len:
        song_rec = sp.recommendations(
            seed_tracks=[song_id], limit=10, min_popularity=randrange(30, 80)
        )

        if len(song_rec) == 0:
            song_rec = sp.recommendations(
                seed_tracks=[song_id], limit=10, min_popularity=0
            )

        if len(song_rec) <= 5:
            check_len = True

    # this is where we will store the extracted data to be sent to the html template
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

        # if there's only one artist
        if len(item["artists"]) == 1:
            song_artist = item["artists"][0]["name"]

            song_data.append((song_url, embed_url, song_artist, song_name, song_img))

        # if there are multiple artists, we'll add them one by one with commas as separators
        else:
            song_artist = ""
            for value in item["artists"]:
                song_artist = song_artist + value["name"] + ", "

            song_data.append(
                (song_url, embed_url, song_artist[:-2], song_name, song_img)
            )

    # if no songs are generated for some reason
    try:
        if song_name == None or song_artist == None:
            pass

    except:
        return redirect(url_for("main.recommendations", song_id=song_id))

    # return song_data

    return render_template("recommendations.html", data=song_data)


@bp.route("/save/<song_uri>")
def save_to_library(song_uri):
    """
    Saves the user-selected song to library
    """

    token_info = ast.literal_eval(request.cookies.get("token_info"))

    save_song = spotipy.Spotify(
        token_info.get("access_token")
    ).current_user_saved_tracks_add(tracks=[song_uri])

    return render_template("save_to_library.html")


@bp.route("/logout")
def logout():
    """
    Log the user out of the application.
    """
    resp = make_response(redirect(url_for("main.index")))
    resp.set_cookie("token_info", "", expires=0)

    flash("You have been logged out.")

    return resp
