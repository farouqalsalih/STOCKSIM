import requests
import os
import pandas as pd
import sqlalchemy as db
import datetime
from pytz import timezone
# Weather code


# FUNTION GET_FORECAST, RETURN JSON RESPONSE
class Weather:
    def __init__(self, city):
        self.city = city

    def get_forecast(self, city):
        params = {
            # 'key': os.environ.get('WEATHERAPI_API_KEY'),
            'key': '51872ff903844da98c321057220607',
            'q': str(self.city),
            'days': '3',
            'aqi': "yes",
            'alerts': "yes"}
        BASE_URL = 'https://api.weatherapi.com/v1/forecast.json?'
        r = requests.get(BASE_URL, params)
        return(r.json())

    # this is to help get specific weather date forecasts
    def weather_by_date(self, date, forecast_data):
        i = 0
        date_forecast_info = None
        while i < len(forecast_data["forecast"]["forecastday"]):
            if forecast_data["forecast"]["forecastday"][i]['date'] == str(date):
                date_forecast_info = forecast_data["forecast"]["forecastday"][i]
            i += 1
        return date_forecast_info

    # gets the specific weather info on a day
    def get_forecast_info(self, forecast_info):
        forecast_list = []
        if forecast_info is None:
            print("nothing in the forecast_info")
        else:
            count = 0
            for key in forecast_info['day']:
                if key == "condition":
                    val = str(key) + " : " + str(forecast_info['day']
                                                              ["condition"]
                                                              ["text"])
                    forecast_list.insert(count, val)
                else:
                    val = str(key) + " : " + str(forecast_info['day'][key])
                    forecast_list.insert(count, val)
                count += 1

        return forecast_list

    def retrieve_weather_data(self):
        eastern = timezone('US/Eastern')
        date = datetime.datetime.now(eastern).date()
        NextDay_Date = (datetime.datetime.now(eastern) + datetime.timedelta(days=1)).date()
        NextNextDay_Date = (datetime.datetime.now(eastern) + datetime.timedelta(days=2)).date()

        forecast_data = self.get_forecast(self.city)
        forecast_dict = {"today": [], "tommorrow": [], "day_after": []}

        # parses to forecast
        day_forecast_info = forecast_data["forecast"]["forecastday"][0]

        # obtain the weather data for that day
        day_forecast_info = self.weather_by_date(date, forecast_data)
        tommorrow_forecast_info = self.weather_by_date(NextDay_Date,
                                                       forecast_data)
        day_after_forecast_info = self.weather_by_date(NextNextDay_Date,
                                                       forecast_data)

     
        today_forecast = self.get_forecast_info(day_forecast_info)
        tommorrow_forecast = self.get_forecast_info(tommorrow_forecast_info)
        day_after_forecast = self.get_forecast_info(day_after_forecast_info)

        forecast_dict["today"] = today_forecast
        forecast_dict["tommorrow"] = tommorrow_forecast
        forecast_dict["day_after"] = day_after_forecast

        return self.create_database(forecast_dict)

    def create_database(self, forecast_info_dict):
        if forecast_info_dict is None:
            return None
        # create dataframe from the extracted records
        forecast_df = pd.DataFrame.from_dict(forecast_info_dict)

        return forecast_df


