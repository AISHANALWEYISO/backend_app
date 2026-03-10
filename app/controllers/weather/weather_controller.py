
from flask import jsonify, request
from services.weather_service import get_weather, get_forecast


def fetch_weather():
    """
    GET /api/weather?city=Kampala
    Returns current weather for a city
    """
    city = request.args.get("city", "Kampala")

    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    weather = get_weather(city)

    if weather is None:
        return jsonify({"error": f"Unable to fetch weather for '{city}'"}), 400

    return jsonify(weather), 200


def fetch_forecast():
    """
    GET /api/weather/forecast?city=Kampala
    Returns 7-day forecast for a city
    """
    city = request.args.get("city", "Kampala")

    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    forecast = get_forecast(city)

    if forecast is None:
        return jsonify({"error": f"Unable to fetch forecast for '{city}'"}), 400

    return jsonify(forecast), 200