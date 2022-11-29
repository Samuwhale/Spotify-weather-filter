import requests
import os
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

APPID = os.getenv('OWD_KEY')
ENDPOINT = "https://api.openweathermap.org/data/2.5/onecall"

columns = [
    "dt",
    "sunrise",
    "sunset",
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
    "wind_gust",
]


class WeatherManager:
    def __init__(self, lon, lat):
        self.lon = lon
        self.lat = lat
        self.energy = (0, 1)
        self.dance = (0, 1)
        self.valence = (0, 1)
        self.today = self.get_current_weather()
        self.historic_average = self.get_historic_weather()
        self.deltas = self.calc_delta()

    def get_current_weather(self):
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

    def calc_delta(self):
        delta = {}
        for column in columns:
            dividend = self.today[column] - self.historic_average[column]
            divisor = self.today[column] + self.historic_average[column]
            if not divisor == 0:
                delta[column] = dividend / divisor
            else:
                delta[column] = dividend

        return delta
