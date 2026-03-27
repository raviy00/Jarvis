# modules/weather.py - Weather Skill
import requests
import os
from dotenv import load_dotenv

load_dotenv()

# We'll use OpenWeatherMap as suggested in the chat history
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
DEFAULT_CITY = os.getenv("YOUR_CITY", "Colombo")

def get_weather(city=None):
    if not city:
        from modules.location import get_current_location
        loc = get_current_location()
        if loc.get("lat") and loc.get("lon"):
            return get_weather_by_coords(loc["lat"], loc["lon"])
        city = loc.get("city", DEFAULT_CITY)

    if not WEATHER_API_KEY:
        return "⚠️ Weather API key not set in .env"
        
    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": city,
            "appid": WEATHER_API_KEY,
            "units": "metric"
        }
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        if data.get("cod") != 200:
            return f"Couldn't get weather for {city}."

        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"].capitalize()
        wind = data["wind"]["speed"]

        return (
            f"🌤️ Weather in {city}:\n"
            f"🌡️ Temp: {temp}°C (feels like {feels}°C)\n"
            f"☁️ {desc}\n"
            f"💧 Humidity: {humidity}%\n"
            f"💨 Wind: {wind} m/s"
        )
    except Exception as e:
        return f"Weather error: {e}"

def get_weather_by_coords(lat, lon):
    if not WEATHER_API_KEY:
        return "⚠️ Weather API key not set in .env"
        
    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": WEATHER_API_KEY,
            "units": "metric"
        }
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        temp = data["main"]["temp"]
        feels = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        desc = data["weather"][0]["description"].capitalize()
        city = data["name"]

        return (
            f"📍 Weather at your location ({city}):\n"
            f"🌡️ Temp: {temp}°C (feels like {feels}°C)\n"
            f"☁️ {desc}\n"
            f"💧 Humidity: {humidity}%"
        )
    except Exception as e:
        return f"Weather error: {e}"
