# AgroAskAI

AgroAskAI is an AI-powered assistant designed to answer **agriculture-related questions**. It provides insights on farming, weather forecasts, and historical climate data to support decision-making in agriculture.

# Setup
## Requirements
   - Python 3.11+
   - A GitHub Account - For Access to the GitHub Models Marketplace
## Install dependencies
  We have included a ```requirements.txt``` file in the root of this repository that contains all the required Python packages to run the code samples.
    
  You can install them by running the following command in your terminal at the root file:
  
  ```pip install -r requirements.txt```
## **Create your .env file**

  Run the following command in your terminal at the root file:
   ```cp .env.example .env```

  This will copy the example file and create a .env in your directory and where you fill in the values for the environment variables.

  With your tokens copied, open the .env file in a text editor and paste the required tokens into their fields.

## Retrieve an OpenAI API Key ```OPENAI_API_KEY```

This project uses OpenAI's GPT models for AI-powered agricultural assistance.

To use OpenAI, you will need to create an [OpenAI API Key](https://platform.openai.com/api-keys).

1. Sign up for an account at [OpenAI Platform](https://platform.openai.com/) (or log in if you already have one).

2. Go to your [API Keys page](https://platform.openai.com/api-keys).

3. Click "Create new secret key".

4. Copy the generated key (it starts with `sk-`).

5. Add it to your `.env` file like this:

   ```OPENAI_API_KEY=sk-your_openai_api_key```

## Retrieve an OpenCage API Key ```GEO_API_KEY```

This project leverages geocoding information obtained from OpenCage's Geocoder API endpoint.

To use OpenCage, you will need to create an [OpenCage User Profile](https://opencagedata.com/)

1. Sign up for a free account (or log in if you already have one).

2. Once logged in, go to your dashboard.

3. Click “Create API Key” or “Generate API Key”.

4. Copy the generated key.

5. Add it to your .env file like this:

   ```GEO_API_KEY=your_opencage_api_key```

## Retrieve an OpenWeather API Key ```OPEN_WEATHER_API_KEY```

This project leverages weather forecast data obtained from OpenWeather’s API.

To use OpenWeather, you will need to create an [OpenWeather Account](https://openweathermap.org/api)

1. Sign up for a free account (or log in if you already have one).

2. Once logged in, select **API** from the top bar and click **Subscribe**. This will prompt you to begin an OpenWeather subscription plan. The **Free tier** is sufficient for this project.

3. Go to your **API Keys** section in your profile/dashboard.

4. Click **“Create Key”** or **“Generate API Key”**.

5. Copy the generated key.

6. Add it to your `.env` file like this:

   ```OPEN_WEATHER_API_KEY=your_openweather_api_key```
   
# Running AgroAskAI

From the root directory, run:

```python main.py```

You will be prompted to enter a user input and, if needed, additional clarification.



