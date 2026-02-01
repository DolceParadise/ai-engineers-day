import os 
import asyncio
import requests
from dotenv import load_dotenv
from openai import AsyncOpenAI
from datetime import datetime, timedelta, timezone


from semantic_kernel.kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import  kernel_function

# Load .env file 
load_dotenv()

# Connect to the NASA POWER API to get accurate weather data in the chosen location
# returns Total Precipitation (T2M) and Temperature at 2 Meters (T2M)

@kernel_function
async def get_NASA_data (location: str, start_year: int, end_year: int):
    api_key= os.getenv("GEO_API_KEY")
    url = f"https://api.opencagedata.com/geocode/v1/json"
    params = {"q": location, "key":api_key}
    response = requests.get(url, params = params)
    data = response.json()
    coords = data["results"][0]["geometry"]
    
    def blocking_fetch():
    # Connect to NASA POWER API with url using the above parameters
        base_url = (
            f"https://power.larc.nasa.gov/api/temporal/monthly/point?"
            f"start={start_year}&end={end_year}"
            f"&latitude={coords['lat']}&longitude={coords['lng']}"
            f"&community=ag"
            f"&parameters=T2M,PRECTOT"
            f"&format=csv&header=false"
        )
        
        # Make the actual request to NASA API
        nasa_response = requests.get(base_url)
        if nasa_response.status_code != 200:
            return f"Error: {nasa_response.status_code}, {nasa_response.text}"

    # Write results to a .txt file  (including the header)
        data = nasa_response.text
        with open('./datasets/weather_data.txt', "a") as file:
            file.write(f"{data}\n")
        return data
    data = await asyncio.get_event_loop().run_in_executor(None, blocking_fetch)
    return data 
        
@kernel_function
async def get_forecast(location: str, forecast_date):  # date: YYYY-MM-DD
    url = f"https://api.opencagedata.com/geocode/v1/json"
    api_key=os.getenv("GEO_API_KEY")
    params = {"q": location, "key":api_key}
    response = requests.get(url, params = params)
    data = response.json()
    coords = data["results"][0]["geometry"]
    lat = coords["lat"]
    lon = coords["lng"]

    now = datetime.now()
    if isinstance(forecast_date, datetime):
        forecast_date = forecast_date.strftime("%Y-%m-%d")
    elif isinstance(forecast_date, bool): # 1 or 0
        forecast_date = int(forecast_date)
    elif (isinstance(forecast_date, str) and "-" not in forecast_date): # "1" or "0"
        forecast_date = int(forecast_date)
    elif isinstance(forecast_date,int):
        if forecast_date == 0:
            forecast_date = now
        elif forecast_date != 0:
            forecast_date = datetime.now(timezone.utc).date() + timedelta(days=forecast_date)
        forecast_date = forecast_date.strftime("%Y-%m-%d")

    api_key = os.getenv("OPEN_WEATHER_API_KEY")
    # Use the 2.5 API which is free, instead of 3.0 which requires subscription
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "appid": api_key,
        "lat": lat,
        "lon": lon,
        "units": "metric",
        "cnt": 40  # Get 5 days of forecast (8 per day)
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return f"Error: {response.status_code}, {response.text}"

    data = response.json()

    # Find the matching forecast day - aggregate 3-hour forecasts by date
    forecasts_by_date = {}
    for item in data.get("list", []):
        dt = datetime.fromtimestamp(item["dt"], tz=timezone.utc).date().isoformat()
        if dt not in forecasts_by_date:
            forecasts_by_date[dt] = []
        forecasts_by_date[dt].append(item)
    
    # Get the closest date to the requested forecast_date
    if forecast_date not in forecasts_by_date:
        available_dates = list(forecasts_by_date.keys())
        if not available_dates:
            return f"No forecast data available. API Returns: {data}"
        # Use the first available date if exact match not found
        forecast_date = available_dates[0]
    
    day_forecasts = forecasts_by_date[forecast_date]
    
    # Aggregate the day's forecasts
    temps = [f["main"]["temp"] for f in day_forecasts]
    humidities = [f["main"]["humidity"] for f in day_forecasts]
    wind_speeds = [f["wind"]["speed"] for f in day_forecasts]
    
    summary = {
        "date": forecast_date,
        "temp_avg": round(sum(temps) / len(temps), 1),
        "temp_max": round(max(temps), 1),
        "temp_min": round(min(temps), 1),
        "weather": day_forecasts[0]["weather"][0]["description"],
        "humidity_avg": round(sum(humidities) / len(humidities), 0),
        "wind_speed_kph": round(sum(wind_speeds) / len(wind_speeds) * 3.6, 1),
        "conditions": [f["weather"][0]["description"] for f in day_forecasts]
    }

    with open('./datasets/weather_data.txt', "a") as file:
        file.write(f"{summary}\n")
    return summary

@kernel_function
async def get_adaptations():
    with open('./datasets/adaptations.txt', "r") as file:
        content = file.read()
        return content