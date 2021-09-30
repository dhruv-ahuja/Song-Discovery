import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth, SpotifyOauthError
from dotenv import load_dotenv
import os

load_dotenv()


# scopes that allow access to segments of the python api
scope = "user-library-read user-top-read user-read-recently-played user-library-modify"


# set the environment variables
client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")


# initialize the spotify object with the apt authentication details
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
    )
)


# get a dict of recently played songs, updates real-time afaik
recent_songs = sp.current_user_recently_played(limit=1)
recent_songs = recent_songs["items"]


for index, item in enumerate(recent_songs):
    # use the track key to cut down on unnecessary info
    track = item["track"]

    # use a list slice or index to cut down on the amount of images displayed
    print(track["album"]["images"][0]["url"])

    # the response object is a json type-object full of nested data types, hence the use of [0] to extract what we need
    print(index + 1, track["artists"][0]["name"], "-", track["name"])
    last_song = track["name"]
    track_id = track["id"]
    album_data = track["album"]


# song recommendations system works similarly as well
# seeds are nothing but a list of identifiers such as object ID or URL
check_song = sp.recommendations(seed_tracks=[track_id])


# print(check_song["tracks"][0]["name"], check_song["tracks"][0]["album"])

for song in check_song:
    print(check_song["tracks"][0]["name"])


# song genres are not exposed by spotify, instead we can get artist and album genres, though album genres can be blank.
artist_genres = sp.artist(track["artists"][0]["id"])["genres"]
print("Artist genres: ", artist_genres)


# get a list of genres
genre_list = sp.recommendation_genre_seeds()
print(genre_list)
