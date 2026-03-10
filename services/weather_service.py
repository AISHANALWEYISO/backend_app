
import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")


def get_weather(city):
    """Get current weather for a city"""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    weather = {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "temp_min": data["main"]["temp_min"],
        "temp_max": data["main"]["temp_max"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"],
        "icon": data["weather"][0]["icon"],
        "wind_speed": data["wind"]["speed"],
        "visibility": data.get("visibility", 0),
        "pressure": data["main"]["pressure"],
        "lat": data["coord"]["lat"],
        "lon": data["coord"]["lon"],
    }

    return weather


def get_forecast(city):
    """Get 7-day forecast for a city using 5-day/3-hour forecast API"""
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    # Group forecasts by day and pick one reading per day (midday ~12:00)
    days = {}
    for item in data["list"]:
        date = item["dt_txt"].split(" ")[0]  # e.g. "2024-03-10"
        time = item["dt_txt"].split(" ")[1]  # e.g. "12:00:00"

        # Prefer midday forecast for each day
        if date not in days or time == "12:00:00":
            days[date] = {
                "date": date,
                "temp_max": item["main"]["temp_max"],
                "temp_min": item["main"]["temp_min"],
                "temperature": item["main"]["temp"],
                "description": item["weather"][0]["description"],
                "icon": item["weather"][0]["icon"],
                "humidity": item["main"]["humidity"],
                "wind_speed": item["wind"]["speed"],
                "rain_chance": int(item.get("pop", 0) * 100),  # probability of precipitation
            }

    # Return up to 7 days
    forecast_list = list(days.values())[:7]

    return {
        "city": data["city"]["name"],
        "country": data["city"]["country"],
        "forecast": forecast_list
    }