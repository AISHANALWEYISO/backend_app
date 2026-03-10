
from flask import Blueprint
from app.controllers.weather.weather_controller import fetch_weather, fetch_forecast

weather_bp = Blueprint("weather", __name__)

# GET /api/weather?city=Kampala
weather_bp.route("/weather", methods=["GET"])(fetch_weather)

# GET /api/weather/forecast?city=Kampala
weather_bp.route("/weather/forecast", methods=["GET"])(fetch_forecast)