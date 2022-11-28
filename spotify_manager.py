import spotipy
from pprint import pprint
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from datetime import datetime
import weather_manager

# THE SOURCE PLAYLISTS
SOURCES = ['6tTRqTBA9Gb95lgFzWEOT5', '5GP2yjY95zhnFiDXjBdgxu']
TARGET = '4rJtEiVdLyiimTiNiAyE5E'

# Ranges as min/max tuples.
RANGES = {
    'energy': (0, 0.4),
    'valence': (0, 0.4),
    'danceability': (0, 0.4)
}

# Scope rights
SCOPE = ["user-library-modify", "playlist-modify-public", "playlist-modify-private", "user-modify-playback-state"]


class SpotifyManager:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE))
        self.user_id = self.sp.current_user()['id']

    # filters track data by a list of filters (by),
    # these need to be in RANGES dict as well as in the spotify audio features
    def filter_playlist(self, tracks, by):
        matched_results = []

        for index, item in enumerate(tracks):
            track_id = item['track']['id']
            features = self.sp.audio_features(track_id)[0]
            print(f"{index + 1}/{len(tracks)}: {item['track']['name']} - {item['track']['artists'][0]['name']} ")

            addable = True

            for filter in by:
                if not RANGES[filter][0] < features[filter] < RANGES[filter][1]:
                    addable = False

            if addable:
                matched_results.append(track_id)

        return matched_results

    # aggregates sources into a large list of tracks
    def gather_tracks(self, sources):
        tracks = []
        for list_id in sources:
            results = self.sp.playlist_tracks(list_id)
            tracks.extend(results['items'])
            while results['next']:
                results = self.sp.next(results)
                tracks.extend(results['items'])

        return tracks

    def update_playlist(self):
        tracks = self.gather_tracks(SOURCES)
        matches = self.filter_playlist(tracks, ['valence', 'energy', 'danceability'])
        # Creates playlist:
        # TARGET = sp.user_playlist_create(user_id, "low energy", public=False)['id']
        self.sp.playlist_change_details(TARGET, name=f"CUSTOM FOR {datetime.now().strftime('%d %b, %y')}")
        self.sp.playlist_replace_items(TARGET, matches)
