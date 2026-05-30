"""
skills/weather.py  –  Fetch current weather via OpenWeatherMap
"""
import requests
import logging
from config.settings import WEATHER_API_KEY

logger = logging.getLogger(__name__)

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def get_weather(user_input: str) -> str:
    """Extract a city from user_input and return a weather summary."""
    city = _extract_city(user_input)
    if not city:
        return "Which city would you like the weather for, Sir?"

    if not WEATHER_API_KEY:
        return "Weather API key is not configured. Please add WEATHER_API_KEY to your .env file."

    try:
        params = {"q": city, "appid": WEATHER_API_KEY, "units": "metric"}
        r = requests.get(BASE_URL, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()

        temp    = data["main"]["temp"]
        feels   = data["main"]["feels_like"]
        desc    = data["weather"][0]["description"]
        humidity= data["main"]["humidity"]
        city_r  = data["name"]

        return (
            f"Currently in {city_r}: {desc}, {temp:.1f}°C, "
            f"feels like {feels:.1f}°C, humidity {humidity}%."
        )
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            return f"I couldn't find weather data for '{city}'. Please check the city name."
        return f"Weather service returned an error: {e}"
    except Exception as e:
        logger.error(f"Weather error: {e}")
        return "I was unable to retrieve the weather at this time."


def _extract_city(text: str) -> str:
    """Very simple city extractor — looks for 'in <city>' pattern."""
    import re
    match = re.search(r"\bin\s+([A-Za-z\s]+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    # Fallback: grab last 1-2 words after "weather"
    match = re.search(r"weather\s+(?:for\s+)?([A-Za-z\s]+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""
