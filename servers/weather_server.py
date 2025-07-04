import requests
import os
import logging

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("weather_mcp")

load_dotenv()


@mcp.tool()
def get_forecast_weather_data(location: str) -> dict:
    """
    Fetches weather data for the 5 next days given a location.
    Please ask the user to provide a location before calling this function. location
    should be stripped and uncased.
    Args:
        location (str): Location for analysis.
    Returns: A dictionary with following information
    """
    base_url = "https://api.tomorrow.io/v4/weather/forecast"
    api_key = os.getenv("TOMORROW_API_KEY")
    url = f"{base_url}?location={location}&timesteps=1d&units=metric&apikey={api_key}"

    headers = {"accept": "application/json", "accept-encoding": "deflate, gzip, br"}
    response = requests.get(url, headers=headers)

    try:
        response.raise_for_status()
        weather_data = response.json()
        cleaned_weather_forecast = {
            "location": weather_data.get("location", {}).get("name", "Unknown"),
            "forecast": [
                {
                    "date": day.get("time", ""),
                    "precipitation_probability_avg": day.get("values", {}).get(
                        "precipitationProbabilityAvg", None
                    ),
                    "precipitation_probability_max": day.get("values", {}).get(
                        "precipitationProbabilityMax", None
                    ),
                    "precipitation_probability_min": day.get("values", {}).get(
                        "precipitationProbabilityMin", None
                    ),
                    "humidity_avg": day.get("values", {}).get("humidityAvg", None),
                    "sunrise_time": day.get("values", {}).get("sunriseTime", ""),
                    "sunset_time": day.get("values", {}).get("sunsetTime", ""),
                    "temperature_apparent_avg": day.get("values", {}).get(
                        "temperatureApparentAvg", None
                    ),
                    "temperature_apparent_max": day.get("values", {}).get(
                        "temperatureApparentMax", None
                    ),
                    "temperature_apparent_min": day.get("values", {}).get(
                        "temperatureApparentMin", None
                    ),
                    "temperature_avg": day.get("values", {}).get(
                        "temperatureAvg", None
                    ),
                    "temperature_max": day.get("values", {}).get(
                        "temperatureMax", None
                    ),
                    "temperature_min": day.get("values", {}).get(
                        "temperatureMin", None
                    ),
                    "wind_speed_avg": day.get("values", {}).get("windSpeedAvg", None),
                    "wind_speed_max": day.get("values", {}).get("windSpeedMax", None),
                }
                for day in weather_data["timelines"].get("daily", [])
            ],
        }
        return cleaned_weather_forecast

    except Exception as e:
        logging.error(f"Error fetching weather data: {e}")
        return None
