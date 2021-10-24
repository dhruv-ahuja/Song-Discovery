# storing the functions to be used alongside/in the views of the main views file
import spotipy
from functools import wraps
from flask import *
from os import getenv
import ast


# setup env & scope to define access to the spotify web api
client_id = getenv("CLIENT_ID")
client_secret = getenv("CLIENT_SECRET")
redirect_uri = getenv("REDIRECT_URI")

scope = "user-library-read user-top-read user-library-modify playlist-modify-public"


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


def get_token_info():

    token_info = ast.literal_eval(request.cookies.get("token_info"))

    return token_info


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        token_info = request.cookies.get("token_info")

        try:

            token_info = ast.literal_eval(token_info)

        except ValueError:

            # means that token_info is none, happens when token is expired or is being renewed

            return redirect(url_for("main.index"))

        if spotipy.SpotifyOAuth.is_token_expired(token_info):
            refresh_token = token_info.get("refresh_token")

            new_token_info = init().refresh_access_token(refresh_token)

            flash("Your token has been renewed.")

            resp = make_response(f(*args, **kwargs))

            resp.set_cookie("token_info", f"{new_token_info}", max_age=43200)

            return resp

        return f(*args, **kwargs)

    return decorated_function
