import spotipy
from pprint import pprint
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from datetime import datetime
import weather_manager

# Scope rights
SCOPE = ["user-library-modify", "playlist-modify-public", "playlist-modify-private", "user-modify-playback-state"]


class SpotifyManager:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=SCOPE))
        self.user_id = self.sp.current_user()['id']

    # filters track data by a list of filters (by),
    # these need to be in RANGES dict as well as in the spotify audio features
    def filter_playlist(self, tracks, ranges, by=['energy', 'valence', 'danceability']):
        matched_results = []

        for index, item in enumerate(tracks):
            track_id = item['track']['id']
            features = self.sp.audio_features(track_id)[0]
            print(f"{index + 1}/{len(tracks)}: {item['track']['name']} - {item['track']['artists'][0]['name']} ")

            addable = True

            for filter in by:
                if not ranges[filter][0] < features[filter] < ranges[filter][1]:
                    addable = False

            if addable:
                matched_results.append(track_id)

        return matched_results

    # aggregates sources
    def gather_tracks(self, sources):
        tracks = []
        for list_id in sources:
            results = self.sp.playlist_tracks(list_id)
            tracks.extend(results['items'])
            while results['next']:
                results = self.sp.next(results)
                tracks.extend(results['items'])

        return tracks

    def update_playlist(self, tracklist, target_playlist=None):
        if target_playlist:
            targ = target_playlist
            self.sp.playlist_change_details(targ, name=f"CUSTOM FOR {datetime.now().strftime('%d %b, %y')}")

        else:
            targ = self.sp.user_playlist_create(user_id, "low energy", public=False)['id']

        self.sp.playlist_replace_items(targ, tracklist)
