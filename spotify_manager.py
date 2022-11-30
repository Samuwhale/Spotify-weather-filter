import numpy as np
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
        print(len(tracks))

        for index, item in enumerate(tracks):
            track_id = item['track']['id']
            features = self.sp.audio_features(track_id)[0]
            print(f"{index + 1}/{len(tracks)}: {item['track']['name']} - {item['track']['artists'][0]['name']} ")

            addable = True

            for feature in by:
                if not ranges[feature][0] < features[feature] < ranges[feature][1]:
                    addable = False

            if addable:
                matched_results.append(track_id)
        print("Matched resultss: ", matched_results)

        if len(matched_results) > 125:
            print(f"old ranges: {ranges} resulted in too many ({len(matched_results)}) results, tightening them up.")
            new_ranges = {}
            for feature in by:
                new_ranges[feature] = self.ease_ranges(ranges[feature], -0.10)
            print(f"Trying now with: {new_ranges}.")
            self.filter_playlist(tracks, new_ranges, by)
        elif len(matched_results) > 100:
            matched_results = matched_results[:100]

        if len(matched_results) < 50:
            if len(matched_results) > len(tracks) / 2:
                print(f"ranges: {ranges} resulted in {len(matched_results)}. Small playlist, so we'll stop here.")
                return matched_results
            else:
                print(f"old ranges: {ranges} resulted in {len(matched_results)}. Maybe we were too strict, easing them.")
                new_ranges = ranges
                for feature in by:
                    new_ranges[feature] = self.ease_ranges(ranges[feature], 0.10)
                print(f"Trying now with: {new_ranges}.")
                self.filter_playlist(tracks, new_ranges, by)



        return matched_results

    # gets a tuple and widens the range by the ease factor
    def ease_ranges(self, range_tuple, ease_factor):
        '''Positive ease factors increase range, negative ones decrease the range'''
        x = range_tuple[0]
        y = range_tuple[1]
        x = np.clip(x - x * ease_factor, 0, 0.9)
        y = np.clip(y + y * ease_factor, 0.1, 1)
        return (x, y)

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
