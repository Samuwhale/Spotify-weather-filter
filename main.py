import spotipy
from pprint import pprint
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from datetime import datetime
from weather_manager import WeatherManager
from spotify_manager import SpotifyManager

sm = SpotifyManager()
wm = WeatherManager()

# sm.update_playlist()

