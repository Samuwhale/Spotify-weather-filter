import requests
import os
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

APPID = os.getenv('OWD_KEY')
ENDPOINT = "https://api.openweathermap.org/data/2.5/onecall"

columns = [
    # "dt",
    # "sunrise",
    # "sunset",
    "temp",
    "feels_like",
    "pressure",
    "humidity",
    "dew_point",
    "uvi",
    "clouds",
    "visibility",
    "wind_speed",
    "wind_deg",
    "wind_gust"]


class WeatherManager:
    def __init__(self, lon, lat, treshold):
        self.lon = lon
        self.lat = lat
        self.treshold = treshold
        self.today = self.get_current_weather()
        self.historic_average = self.get_historic_weather()
        self.deltas = self.calc_delta(self.today, self.historic_average)
        self.feature_ranges = self.calc_spotify_ranges(self.deltas)

    def get_current_weather(self):
        """Returns the current weather as a dictionary"""
        today_dict = {}
        for column in columns:
            today_dict[column] = []

        curr_params = {
            "lon": self.lon,
            "lat": self.lat,
            "appid": APPID,
            "exclude": "minutely,hourly,daily,alerts",
            "units": "metric"
        }
        curr_data = requests.get(ENDPOINT, params=curr_params)
        curr_data.raise_for_status()
        curr_data = curr_data.json()

        for column in columns:
            value = float(curr_data['current'][column])
            today_dict[column] = value

        return today_dict

    def get_historic_weather(self):
        """Returns weather of past five days as dictionary of lists"""
        past_five_dict = {}
        for column in columns:
            past_five_dict[column] = []

        for i in range(1, 6):
            five_days = datetime.utcnow() - timedelta(i)
            hist_params = {
                "lon": self.lon,
                "lat": self.lat,
                "appid": APPID,
                "units": "metric",
                "dt": str(five_days.timestamp()).split('.')[0],
                "only_current": True
            }
            hist_data = requests.get(f"{ENDPOINT}/timemachine", params=hist_params)

            hist_data.raise_for_status()
            hist_data = hist_data.json()

            for column in columns:
                value = float(hist_data['current'][column])
                past_five_dict[column].append(value)

        average_dict = {}

        for column in columns:
            average_dict[column] = np.mean(past_five_dict[column])

        return average_dict

    def calc_delta(self, today_weather, history_average):
        """Takes weather dictionaries and calculates the normalized difference between them
               the result is a dictionary of floats between -1 and 1 representing the amount of change"""
        delta = {}
        for column in columns:
            difference = today_weather[column] - history_average[column]
            if difference != 0:
                pct_float = np.divide(difference, today_weather[column])
            else:
                pct_float = 0
            delta[column] = pct_float
        return delta

    def calc_spotify_ranges(self, delta_values):
        total_selection = {"temp": 0.5,
                           "feels_like": 0.5,
                           "pressure": 0.5,
                           "humidity": 0.5,
                           "dew_point": 0.5,
                           "uvi": 0.5,
                           "clouds": 0.5,
                           "visibility": 0.5,
                           "wind_speed": 0.5,
                           "wind_deg": 0.5,
                           "wind_gust": 0.5
                           }
        # weights that affect how strongly and in what direction they affect the resulting feature
        feature_weights = {
            'energy': {
                "wind_speed": -0.5,
                "wind_gust": -0.5,
                "humidity": -0.5,
                "dew_point": -0.5
            },
            'valence': {
                "temp": 0.5,
                "feels_like": 0.5,
                "uvi": 0.5,
                "clouds": 0.5,
                "visibility": 0.5
            },
            'danceability': {
            }
        }

        # weights multiplied by the weather delta values, and their averages
        feature_weighted_deltas = {
            'energy': [],
            'valence': [],
            'danceability': []
        }

        feauture_averages = {
            'energy': 0.5,
            'valence': 0.5,
            'danceability': 0.5
        }

        # the averages normalized, defaulted to 0.5
        feature_scores = {
            'energy': 0.5,
            'valence': 0.5,
            'danceability': 0.5
        }

        # Go through the dictionaries and calculates the values for the appropriate dictionaries
        for feature, feature_weights in feature_weights.items():
            for column in columns:
                if column in feature_weights:
                    value = feature_weights[column] * self.deltas[column]
                    feature_weighted_deltas[feature].append(value)

            if feature_weighted_deltas[feature]:
                feauture_averages[feature] = np.mean(feature_weighted_deltas[feature])
                feature_scores[feature] = (feauture_averages[feature] - np.min(feature_weighted_deltas[feature])) / (
                        np.max(feature_weighted_deltas[feature]) - np.min(feature_weighted_deltas[feature]))
            else:
                feauture_averages[feature] = 0

        # creates a dictionary of ranges around the feature scores, clipped between 0 and 1.
        feature_ranges = {}
        for key, value in feature_scores.items():
            feature_ranges[key] = (
                np.clip(value - self.treshold, a_min=0, a_max=0.9), (np.clip(value + self.treshold, a_min=0.1, a_max=1)))

        print("Feature ranges are :", feature_ranges)
        return feature_ranges
