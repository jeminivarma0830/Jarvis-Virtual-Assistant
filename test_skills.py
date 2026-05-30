"""
tests/test_skills.py  –  Unit tests for skill functions
Run:  pytest tests/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import patch
from skills.weather import get_weather, _extract_city
from skills.search  import _extract_query


def test_extract_city_in_pattern():
    assert _extract_city("what is the weather in Mumbai") == "Mumbai"


def test_extract_city_weather_pattern():
    assert _extract_city("weather London") == "London"


def test_get_weather_no_key():
    """Without an API key, should return a helpful message."""
    with patch("skills.weather.WEATHER_API_KEY", ""):
        result = get_weather("weather in London")
    assert "API key" in result


def test_extract_query():
    assert _extract_query("search Python tutorials") == "Python tutorials"
    assert _extract_query("what is quantum computing") == "quantum computing"
