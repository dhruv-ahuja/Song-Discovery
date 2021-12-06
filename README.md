# Introduction
### NOTE: The app currently only works with selected test accounts. 
A simple web app built using Flask that helps the user find new music. The app generates song recommendations based on a user-selected song, with the ability to listen to the generated recommendations online and save them to the user's Spotify song library with a click.

# How Does It Work
The app uses Spotify's song recommendation system used to generate song radioes, with a few tweaks to allow for a wider diversity of music choices. The "popularity" parameter in the recommendation system is tweaked each time the Recommendations page is loaded to allow the user to find unique set of recommendations, although duplicates do occur since the system is bound by the user-selected song and its genre and other related parameters.

The user has to connect their Spotify account with the web app to allow the ability to play the generated song recommendations (displayed in the form of embeds) and to save them to the user's library. 
