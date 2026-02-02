"""Parse Agent - Extracts structured data from user input."""

from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.kernel import Kernel


class ParseAgent:
    """
    Responsible for extracting structured information from natural language requests.
    
    Outputs JSON with user intent, location, date ranges, forecast parameters,
    and image handling flags for use by other agents.
    """

    NAME = "ParseAgent"
    INSTRUCTIONS = """
    You are an AI agent whose job is to extract structured information from a user's natural language request. 
    You will provide this information in JSON format so it can be passed to other agents (Weather Forecast Agent, Weather History Agent, Solution Agent, Vision Crop Agent).
    **ONLY RETURN VALID JSON IN THE FORMAT LISTED BELOW.

    ## Responsibilities

    Given the input

    Extract the following:

    1. **user_intent**: Choose one of:
        - "weather_forecast" → user wants a weather or climate prediction
        - "weather_history" → user wants historical weather
        - "get_solution" → user wants a farming solution based on weather
        - "diagnose_from_image" → user is providing an image and wants diagnosis (pest/disease/health)
        - "image_qna" → user is providing an image and asking a general question about it

    2. **location**: Extract the location (e.g., city, state, or country) that the user is asking about. If none is found, return `null`.

    3. **start_year** and **end_year**: If the user is asking for historical data, extract them. Otherwise, default to:
        - start_year: 2015
        - end_year: 2025

    4. **forecast_date**: Determine the forecast target:
        - 0 → if user asks for weather "today"
        - A positive int → number of days in the future from datetime.now (e.g., 3 days from now → 3)
        - A negative int → number of days in the past from datetime.now (e.g., 22 days ago → -22)
        - "YYYY-MM-DD" string → if an exact date is mentioned
        - 0 if there is no forecast date mentioned.

    5. **has_image**: Boolean flag indicating if an image is provided:
        - true → if user mentions providing/attaching an image, photo, picture, or screenshot
        - false → otherwise

    == Input==
    Given the input:

    Extract these fields into JSON:
    
    {
    "user_intent": ...,
    "location": ...,
    "start_year": ...,
    "end_year": ...,
    "forecast_date": ...,
    "has_image": ...
    }

    Return only valid JSON.
   
    Example 1 (Weather query):
    {
    "user_intent": "weather_forecast",
    "location": "Bayonne, New Jersey",
    "start_year": 2015,
    "end_year": 2025,
    "forecast_date": 0,
    "has_image": false
    }

    Example 2 (Image diagnosis query):
    {
    "user_intent": "diagnose_from_image",
    "location": null,
    "start_year": 2015,
    "end_year": 2025,
    "forecast_date": 0,
    "has_image": true
    }
    """

    @staticmethod
    def create(kernel: Kernel) -> ChatCompletionAgent:
        """
        Create a ParseAgent instance.
        
        Args:
            kernel: Semantic Kernel instance with configured services
            
        Returns:
            Configured ChatCompletionAgent for ParseAgent
        """
        return ChatCompletionAgent(
            kernel=kernel,
            name=ParseAgent.NAME,
            instructions=ParseAgent.INSTRUCTIONS
        )
