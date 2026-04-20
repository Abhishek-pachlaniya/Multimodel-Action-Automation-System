"""
Weather.py — OpenWeatherMap API integration
Add OPENWEATHER_API_KEY to your .env file
Get free key at: https://openweathermap.org/api
"""
import requests
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
API_KEY  = env_vars.get("OPENWEATHER_API_KEY")

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def GetWeather(city: str) -> str:
    """
    Fetches current weather for a city and returns a natural language summary.
    """
    if not API_KEY:
        return "OpenWeather API key not found. Please add OPENWEATHER_API_KEY to your .env file."

    # Clean city name
    city = city.strip().replace("weather in", "").replace("weather of", "").strip()
    if not city:
        city = "Lucknow"  # default city

    try:
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric",   # Celsius
            "lang": "en"
        }
        response = requests.get(BASE_URL, params=params, timeout=8)
        data = response.json()

        if data.get("cod") != 200:
            return f"Could not get weather for '{city}'. Please check the city name."

        # Parse response
        city_name   = data["name"]
        country     = data["sys"]["country"]
        temp        = round(data["main"]["temp"])
        feels_like  = round(data["main"]["feels_like"])
        humidity    = data["main"]["humidity"]
        description = data["weather"][0]["description"].capitalize()
        wind_speed  = data["wind"]["speed"]
        visibility  = data.get("visibility", 0) // 1000  # convert to km

        # Build natural language answer
        result = (
            f"Weather in {city_name}, {country}:\n"
            f"{description}. Temperature is {temp}°C, feels like {feels_like}°C.\n"
            f"Humidity: {humidity}%. Wind speed: {wind_speed} m/s. "
            f"Visibility: {visibility} km."
        )

        # Add advice
        if temp > 35:
            result += "\nIt's very hot outside. Stay hydrated and avoid direct sunlight."
        elif temp < 10:
            result += "\nIt's quite cold. Please wear warm clothes."
        if "rain" in description.lower():
            result += "\nDon't forget to carry an umbrella!"

        return result

    except requests.Timeout:
        return "Weather request timed out. Please try again."
    except Exception as e:
        return f"Weather error: {str(e)}"


def GetWeatherForecast(city: str) -> str:
    """5-day weather forecast (3-hour intervals)."""
    if not API_KEY:
        return "OpenWeather API key not found."

    city = city.strip()
    try:
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric",
            "cnt": 5   # 5 time slots (today + near future)
        }
        url = "https://api.openweathermap.org/data/2.5/forecast"
        response = requests.get(url, params=params, timeout=8)
        data = response.json()

        if data.get("cod") != "200":
            return f"Could not get forecast for '{city}'."

        result = f"Forecast for {city}:\n"
        for item in data["list"]:
            time  = item["dt_txt"]
            temp  = round(item["main"]["temp"])
            desc  = item["weather"][0]["description"].capitalize()
            result += f"  {time}: {temp}°C, {desc}\n"

        return result.strip()

    except Exception as e:
        return f"Forecast error: {str(e)}"


if __name__ == "__main__":
    city = input("Enter city name: ")
    print(GetWeather(city))
