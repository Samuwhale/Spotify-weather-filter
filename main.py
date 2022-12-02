import spotipy
from pprint import pprint
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from datetime import datetime
from weather_manager import WeatherManager
from spotify_manager import SpotifyManager

### SPOTIFY
# source and target playlists
SOURCES = ['6tTRqTBA9Gb95lgFzWEOT5', '5GP2yjY95zhnFiDXjBdgxu', '12YHegwMeIZJvA95VHmyz6'] #normal playlists
#SOURCES = ['05yEXmAndl3mWwTmOhH4dl']  # small playlist
TARGET = '4rJtEiVdLyiimTiNiAyE5E'
SONG_TARGET = 50

### WEATHER
# User lon lat data
LON = 5.1214
LAT = 52.0907

sm = SpotifyManager()
wm = WeatherManager(lon=LON, lat=LAT, treshold=0.1)

# get range tuples to filter features on
ranges = wm.feature_ranges
print(f"Ranges are: {ranges}")
tracks = sm.gather_tracks(SOURCES)
track_df = sm.get_track_features(tracks)
filtered_tracks = sm.filter_playlist(by=['energy', 'valence'], ranges=ranges, tracks_df=track_df, target=SONG_TARGET)
print("Filtered trackz", filtered_tracks)
sm.update_playlist(tracklist=filtered_tracks, target_playlist=TARGET)

# pprint(wm.today)
# pprint(wm.historic_average)
# sm.update_playlist()
