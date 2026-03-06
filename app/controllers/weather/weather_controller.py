from flask import Blueprint, request, jsonify
from app.models.weather import (
    get_current_weather, 
    get_forecast_10_days, 
    format_weather_data
)
from datetime import datetime
import requests
weather_bp = Blueprint('weather', __name__, url_prefix='/weather')


# Public Weather Forecast (No Authentication Required)
@weather_bp.route('/forecast', methods=['POST'])
def get_forecast():
    """
    Get current weather + 10-day forecast
    Public endpoint - no authentication required
    
    Request Body:
    {
        "lat": 40.71,
        "lon": -74.00
    }
    OR
    {
        "city": "London"
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({
            "success": False,
            "message": "Location data required. Provide lat/lon or city name."
        }), 400

    lat = data.get("lat")
    lon = data.get("lon")
    city = data.get("city")

    # If city name provided, geocode it first
    if city and (not lat or not lon):
        geocode_result = geocode_city(city)
        if not geocode_result:
            return jsonify({
                "success": False,
                "message": "City not found. Please provide latitude and longitude."
            }), 404
        lat = geocode_result['lat']
        lon = geocode_result['lon']
    
    # Validate coordinates
    if not lat or not lon:
        return jsonify({
            "success": False,
            "message": "Latitude and Longitude are required."
        }), 400

    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid coordinates format."
        }), 400

    # Fetch weather data
    current_weather = get_current_weather(lat, lon)
    forecast_data = get_forecast_10_days(lat, lon)

    if not current_weather or not forecast_data:
        return jsonify({
            "success": False,
            "message": "Failed to fetch weather data. Please try again later."
        }), 503

    # Format and return data
    formatted_data = format_weather_data(current_weather, forecast_data, lat, lon)
    
    if not formatted_data:
        return jsonify({
            "success": False,
            "message": "Error processing weather data."
        }), 500

    return jsonify({
        "success": True,
        "message": "Weather data retrieved successfully",
        "data": formatted_data
    }), 200


# Get Weather by City Name (Public)
@weather_bp.route('/city/<string:city_name>', methods=['GET'])
def get_weather_by_city(city_name):
    """
    Get weather by city name
    Public endpoint - no authentication required
    """
    geocode_result = geocode_city(city_name)
    
    if not geocode_result:
        return jsonify({
            "success": False,
            "message": "City not found."
        }), 404
    
    # Redirect to forecast endpoint with coordinates
    return get_forecast()


# Helper function to geocode city name
def geocode_city(city_name):
    """Converts city name to coordinates using OpenWeatherMap Geocoding API"""
    try:
        url = "http://api.openweathermap.org/geo/1.0/direct"
        params = {
            'q': city_name,
            'limit': 1,
            'appid': API_KEY
        }
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data:
            return {
                'lat': data[0]['lat'],
                'lon': data[0]['lon'],
                'name': data[0]['name'],
                'country': data[0]['country']
            }
        return None
    except:
        return None


# Simple Health Check (Public)
@weather_bp.route('/status', methods=['GET'])
def weather_status():
    """Check if weather service is available"""
    return jsonify({
        "success": True,
        "message": "Weather service is online",
        "timestamp": datetime.utcnow().isoformat()
    }), 200