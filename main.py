import spotipy
from pprint import pprint
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from datetime import datetime
from weather_manager import WeatherManager
from spotify_manager import SpotifyManager

# User lon lat data
LON = 5.1214
LAT = 52.0907

sm = SpotifyManager()
wm = WeatherManager(lon=LON, lat=LAT)


print(wm.today, wm.historic_average)


# sm.update_playlist()

