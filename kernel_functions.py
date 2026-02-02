import os 
import asyncio
import json
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


@kernel_function
async def analyze_crop_image(image_base64: str = None, image_url: str = None, query: str = "Analyze this crop image") -> str:
    """
    Analyze a crop/field image using OpenAI's vision capabilities.
    
    Provides structured analysis of crop images including visual observations,
    crop identification, disease/pest detection, and answers user queries based
    on image analysis.
    
    Args:
        image_base64: Optional base64-encoded image data (without data: prefix)
        image_url: Optional URL to the image (public URL)
        query: User's question or analysis request about the image
        
    Returns:
        JSON string containing:
        {
            "observations": {
                "crop_type": str,
                "growth_stage": str,
                "visual_stress": [str],
                "pests_diseases": [str],
                "weeds_detected": bool,
                "irrigation_status": str,
                "soil_conditions": str,
                "anomalies": [str]
            },
            "likely_crop": [
                {"name": str, "confidence": float}
            ],
            "issues": [
                {"name": str, "evidence": str, "confidence": float}
            ],
            "recommended_next_photos": [str],
            "answer": str
        }
        
    Raises:
        ValueError: If neither image_base64 nor image_url is provided
        RuntimeError: If OpenAI API call fails
    """
    
    # Validate inputs
    if not image_base64 and not image_url:
        error_response = {
            "observations": {},
            "likely_crop": [],
            "issues": [],
            "recommended_next_photos": [
                "Please provide either image_base64 or image_url",
                "For best results, provide a clear photo of the affected plant/field"
            ],
            "answer": "I need an image to analyze. Please provide either a base64-encoded image or a public URL to an image."
        }
        return json.dumps(error_response)
    
    try:
        openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Build message content with vision capabilities
        content = [
            {
                "type": "text",
                "text": f"""Analyze this crop/field image and answer the following question: {query}

IMPORTANT: Respond ONLY with valid JSON (no markdown, no code blocks). Use this exact structure:

{{
    "observations": {{
        "crop_type": "identified crop type or 'unknown'",
        "growth_stage": "seedling/vegetative/flowering/fruiting/mature/harvested",
        "visual_stress": ["list of visible stress symptoms"],
        "pests_diseases": ["list of detected pests or diseases"],
        "weeds_detected": true/false,
        "irrigation_status": "description of irrigation state",
        "soil_conditions": "description of visible soil state",
        "anomalies": ["list of unusual features or damage"]
    }},
    "likely_crop": [
        {{"name": "crop name", "confidence": 0.95}},
        {{"name": "alternative crop", "confidence": 0.3}}
    ],
    "issues": [
        {{"name": "issue name", "evidence": "visual evidence from image", "confidence": 0.85}}
    ],
    "recommended_next_photos": [
        "close-up of affected leaves",
        "underside of leaves",
        "wider field view"
    ],
    "answer": "Direct answer to the user's question based on image analysis"
}}

Rules:
- Be specific about what you see, not what you assume
- Confidence scores: 0.0-1.0, where 1.0 is certain
- For uncertain items, include alternative hypotheses
- If something cannot be determined from the image, say "cannot determine"
- Return ONLY valid JSON, no explanation or markdown
"""
            }
        ]
        
        # Add image to content
        if image_base64:
            # Ensure image_base64 doesn't have data: prefix
            if image_base64.startswith("data:"):
                image_base64 = image_base64.split(",")[1]
            
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}",
                    "detail": "high"
                }
            })
        elif image_url:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                    "detail": "high"
                }
            })
        
        # Call OpenAI API with vision
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",  # Using GPT-4 Turbo for vision; fallback to GPT-4 if needed
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            temperature=0.3,  # Lower temperature for more consistent analysis
            max_tokens=1500
        )
        
        # Extract and validate response
        response_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.split("```")[0]
        
        response_text = response_text.strip()
        
        # Parse and validate JSON
        try:
            analysis_result = json.loads(response_text)
        except json.JSONDecodeError:
            # If parsing fails, return structured error
            analysis_result = {
                "observations": {},
                "likely_crop": [],
                "issues": [],
                "recommended_next_photos": [
                    "Unable to analyze image clearly",
                    "Please provide a clearer photo with better lighting"
                ],
                "answer": f"I encountered an error analyzing the image. Raw response: {response_text[:200]}"
            }
        
        return json.dumps(analysis_result)
        
    except Exception as e:
        # Handle API errors gracefully
        error_response = {
            "observations": {},
            "likely_crop": [],
            "issues": [],
            "recommended_next_photos": [
                "Technical error during image analysis",
                "Please try again or provide a different image"
            ],
            "answer": f"Sorry, I encountered an error analyzing the image: {str(e)}"
        }
        return json.dumps(error_response)