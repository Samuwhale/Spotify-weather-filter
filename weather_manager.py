import requests
import os

LON = 5.1214
LAT = 52.0907
APPID = os.getenv('OWD_KEY')
ENDPOINT = "https://api.openweathermap.org/data/2.5/onecall"

PARAMS = {
    "lon": LON,
    "lat": LAT,
    "appid": APPID,
    "exclude": "minutely,hourly,daily,alerts"
}


class WeatherManager:
    def __init__(self):
        self.temperature = 0
        self.precip = 0
        print(self.get_data())

    def get_data(self):
        self.response = requests.get(ENDPOINT, params=PARAMS)
        self.response.raise_for_status()
        return self.response.json()
