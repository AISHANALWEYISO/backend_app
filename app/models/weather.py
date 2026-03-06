import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("WEATHER_API_KEY")
BASE_URL = os.getenv("WEATHER_API_URL", "https://api.openweathermap.org/data/2.5")
ONE_CALL_URL = os.getenv("WEATHER_ONE_CALL_URL", "https://api.openweathermap.org/data/3.0/onecall")

def get_current_weather(lat, lon, units='metric'):
    """Fetches current weather data"""
    try:
        url = f"{BASE_URL}/weather"
        params = {
            'lat': lat,
            'lon': lon,
            'appid': API_KEY,
            'units': units
        }
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Weather API Error: {e}")
        return None

def get_forecast_10_days(lat, lon, units='metric'):
    """Fetches 10-day forecast using One Call API 3.0"""
    try:
        params = {
            'lat': lat,
            'lon': lon,
            'appid': API_KEY,
            'units': units,
            'exclude': 'minutely,hourly,alerts'  # We only need daily
        }
        response = requests.get(ONE_CALL_URL, params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Weather API Error: {e}")
        return None

def generate_agri_advice(current_weather, forecast_data):
    """Converts weather data into farming advice"""
    advice = []
    
    # Current conditions
    if current_weather:
        temp = current_weather.get('main', {}).get('temp', 0)
        humidity = current_weather.get('main', {}).get('humidity', 0)
        wind_speed = current_weather.get('wind', {}).get('speed', 0)
        weather_main = current_weather.get('weather', [{}])[0].get('main', '')
        
        # Temperature advice
        if temp > 35:
            advice.append("🌡️ High heat alert! Ensure livestock have shade and adequate water supply.")
        elif temp < 5:
            advice.append("❄️ Cold warning! Protect sensitive crops from frost damage.")
        
        # Humidity advice
        if humidity > 80:
            advice.append("💧 High humidity detected. Monitor for fungal diseases in crops.")
        elif humidity < 30:
            advice.append("🏜️ Low humidity. Increase irrigation frequency to prevent crop stress.")
        
        # Wind advice
        if wind_speed > 15:
            advice.append("💨 Strong winds! Avoid spraying pesticides (drift risk). Secure greenhouse structures.")
        
        # Rain advice
        if weather_main == 'Rain':
            advice.append("🌧️ Currently raining. Delay fertilizer application and field work.")
        elif weather_main == 'Clear':
            advice.append("☀️ Clear weather. Good conditions for harvesting and field activities.")
    
    # Forecast advice
    if forecast_data and 'daily' in forecast_data:
        rain_days = 0
        hot_days = 0
        
        for day in forecast_data['daily'][:5]:  # Next 5 days
            if day.get('rain', 0) > 0:
                rain_days += 1
            if day.get('temp', {}).get('max', 0) > 35:
                hot_days += 1
        
        if rain_days >= 3:
            advice.append("📅 Multiple rainy days ahead. Plan indoor activities and delay planting.")
        elif rain_days == 0:
            advice.append("📅 Dry week ahead. Schedule irrigation and water-intensive tasks.")
        
        if hot_days >= 3:
            advice.append("📅 Several hot days forecasted. Monitor crop heat stress and increase watering.")
    
    if not advice:
        advice.append("✅ Weather conditions are favorable for normal farming activities.")
    
    return advice

def format_weather_data(current_weather, forecast_data, lat, lon):
    """Formats all weather data into a clean response"""
    if not current_weather or not forecast_data:
        return None
    
    # Current weather
    current = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "temperature": f"{current_weather['main']['temp']}°C",
        "feels_like": f"{current_weather['main']['feels_like']}°C",
        "humidity": f"{current_weather['main']['humidity']}%",
        "pressure": f"{current_weather['main']['pressure']} hPa",
        "wind_speed": f"{current_weather['wind']['speed']} m/s",
        "wind_direction": current_weather['wind'].get('deg', 0),
        "weather": current_weather['weather'][0]['main'],
        "description": current_weather['weather'][0]['description'].title(),
        "icon": current_weather['weather'][0]['icon'],
        "sunrise": datetime.fromtimestamp(current_weather['sys']['sunrise']).strftime("%H:%M:%S"),
        "sunset": datetime.fromtimestamp(current_weather['sys']['sunset']).strftime("%H:%M:%S"),
        "location": {
            "name": current_weather.get('name', 'Unknown'),
            "country": current_weather['sys']['country'],
            "latitude": lat,
            "longitude": lon
        }
    }
    
    # 10-day forecast
    forecast = []
    for i, day in enumerate(forecast_data['daily'][:10]):
        forecast_date = datetime.fromtimestamp(day['dt'])
        forecast.append({
            "day": i + 1,
            "date": forecast_date.strftime("%Y-%m-%d"),
            "day_name": forecast_date.strftime("%A"),
            "temp_max": f"{day['temp']['max']}°C",
            "temp_min": f"{day['temp']['min']}°C",
            "temp_morning": f"{day['temp']['morn']}°C",
            "temp_evening": f"{day['temp']['eve']}°C",
            "humidity": f"{day['humidity']}%",
            "pressure": f"{day['pressure']} hPa",
            "wind_speed": f"{day['wind_speed']} m/s",
            "weather": day['weather'][0]['main'],
            "description": day['weather'][0]['description'].title(),
            "icon": day['weather'][0]['icon'],
            "rain_probability": f"{day.get('pop', 0) * 100:.0f}%",
            "rain_amount": f"{day.get('rain', 0)} mm" if day.get('rain', 0) > 0 else "0 mm",
            "uv_index": day.get('uvi', 0),
            "sunrise": datetime.fromtimestamp(day['sunrise']).strftime("%H:%M:%S"),
            "sunset": datetime.fromtimestamp(day['sunset']).strftime("%H:%M:%S")
        })
    
    # Agriculture advice
    agri_advice = generate_agri_advice(current_weather, forecast_data)
    
    return {
        "current": current,
        "forecast": forecast,
        "agriculture_advice": agri_advice,
        "last_updated": datetime.utcnow().isoformat()
    }