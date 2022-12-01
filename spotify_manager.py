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
        self.last_tracklist = ""
        self.last_tracklist_df = ""

    # filters track data by a list of filters (by),
    # these need to be in RANGES dict as well as in the spotify audio features
    def filter_playlist(self, ranges, tracks_df, by=['energy', 'valence', 'danceability'], target=100):
        print(f"Starting Ranges: {ranges}")

        if target > 100:
            target = 100
        if target < 1:
            target = 1
        print(f"Starting target: {target}")
        selection = tracks_df
        for feature in by:
            low_bound = ranges[feature][0]
            upper_bound = ranges[feature][1]
            print(f"feature: {feature}", low_bound, upper_bound)
            selection = selection.loc[(selection[feature] <= upper_bound) & (selection[feature] >= low_bound)]

        if len(selection) > target:
            print(f"IF Too many results, sampling {target} songs.")
            selection = selection.sample(target)
            return selection
        elif len(selection) < target:
            print(f"ELIF Too little results ({len(selection)}), easing ranges.")
            new_ranges = {}
            for key in ranges:
                print(ranges[key])
                new_ranges[key] = self.ease_ranges(ranges[key], 0.02)
            print(f"OLD RANGES: {ranges}\nNEW RANGES: {new_ranges}")
            return self.filter_playlist(ranges=new_ranges, tracks_df=tracks_df, by=by, target=target)
        else:
            print(f"ELSE: Returning selection: {selection}")
            return selection


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

        self.last_tracklist = tracks
        return tracks

    def get_track_features(self, tracks=None):
        '''Gets a list of tracks and returns a pandas dataframe with features stored in it'''
        if not tracks:
            tracks = self.last_tracklist
        track_features = {}

        for track in tracks:
            track_id = track['track']['id']
            track_name = track['track']['name']
            print(f"{tracks.index(track) + 1} / {len(tracks)} {track_name} (id: {track_id})")
            features = self.sp.audio_features(track_id)[0]
            track_features[track_id] = {}
            track_features[track_id]['song_name'] = track_name
            for feature in features:
                track_features[track_id][feature] = features[feature]

        track_df = pd.DataFrame(track_features)
        track_df = track_df.transpose()
        self.last_tracklist_df = track_df
        return track_df

    def update_playlist(self, tracklist, target_playlist=None):
        if target_playlist:
            targ = target_playlist
            self.sp.playlist_change_details(targ, name=f"CUSTOM FOR {datetime.now().strftime('%d %b, %y')}")

        else:
            targ = self.sp.user_playlist_create(self.user_id, "low energy", public=False)['id']

        tracklist = tracklist['id'].tolist()
        print(tracklist)
        self.sp.playlist_replace_items(targ, tracklist)
        print(f"Succesfully added {len(tracklist)} songs to playlist {self.sp.playlist(targ)['name']}")
