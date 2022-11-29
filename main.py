import spotipy
from pprint import pprint
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from datetime import datetime
from weather_manager import WeatherManager
from spotify_manager import SpotifyManager

### SPOTIFY
# source and target playlists
SOURCES = ['6tTRqTBA9Gb95lgFzWEOT5', '5GP2yjY95zhnFiDXjBdgxu']
TARGET = '4rJtEiVdLyiimTiNiAyE5E'

# Ranges as min/max tuples.
RANGES = {
    'energy': (0, 0.4),
    'valence': (0, 0.4),
    'danceability': (0, 0.4)
}

### WEATHER
# User lon lat data
LON = 5.1214
LAT = 52.0907

sm = SpotifyManager()
wm = WeatherManager(lon=LON, lat=LAT)

tracks = sm.gather_tracks(SOURCES)
filtered_tracks = sm.filter_playlist(tracks=tracks, by=['energy', 'valence', 'danceability'], ranges=RANGES)
sm.update_playlist(tracklist=filtered_tracks, target_playlist=TARGET)

print("\n\n\n\n", wm.today, "\n\n\n\n", wm.historic_average, "\n\n\n\n", wm.deltas)

# sm.update_playlist()
