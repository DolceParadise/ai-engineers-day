# KhetSetu - Multi-Agent Agricultural Intelligence System

A sophisticated multi-agent system for agricultural queries combining weather analysis, climate history, and farming solutions.

[Demo]([url](https://drive.google.com/drive/folders/1HCyvUCX2ggbzPhvzeXBWSYC8adskfVum?usp=sharing))

## Features

- **Weather Analysis**: Real-time weather forecasts and historical climate data
- **Farming Solutions**: AI-powered recommendations based on local conditions
- **Multi-Language Support**: Responds in the user's language (English, Hindi, Swahili, Spanish, etc.)
- **Cost Tracking**: Detailed token usage and API cost calculations
- **Conversational AI**: Multi-agent orchestration with automatic feedback loops

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Web UI)                        │
│          (app.js, index.html, styles.css)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP POST /ask
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                          │
│              (backend_api.py)                               │
│  - Accepts user_input                                      │
│  - Returns structured agent responses                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Main Orchestrator (KhetSetu)                   │
│              (main.py)                                      │
│  - Language detection                                       │
│  - Agent group chat coordination                            │
│  - Token tracking and cost calculation                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
    ┌─────────┐  ┌────────┐  ┌──────────────┐
    │ Agents  │  │Kernel  │  │ Functions    │
    │ Group   │  │Config  │  │              │
    ├─────────┤  │        │  ├──────────────┤
    │ Prompt  │  │OpenAI  │  │ get_forecast │
    │ Parse   │  │Config  │  │ get_NASA_data│
    │ Forecast│  │        │  │              │
    │ History │  │────────┤  │              │
    │ Solution│            │ get_adaptation│
    │ Reviewer│            └──────────────┘
    └─────────┘
```

## Agents

### 1. ParseAgent
Extracts structured information from natural language queries:
- User intent (weather forecast, weather history, solution)
- Location
- Date ranges

### 2. PromptAgent
Natural language interface that greets users and summarizes responses.

### 3. ForecastAgent
Retrieves and summarizes weather forecasts using OpenWeatherMap API.

### 4. WeatherHistoryAgent
Accesses historical climate data via NASA POWER API.

### 5. SolutionAgent
Generates farming solutions and recommendations based on weather data.

### 6. VisionCropAgent
Analyzes crop/field images to provide diagnostics and recommendations.

### 7. ReviewerAgent
Evaluates agent responses and ensures quality before final answer.

## Quick Start

### Installation

```bash
# Clone and setup
git clone <repo>
cd ai-engineers-day

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your API keys:
# - OPENAI_API_KEY
# - GEO_API_KEY
# - OPEN_WEATHER_API_KEY
```

### Running the System

#### Option 1: Command Line (Interactive)
```bash
python main.py
```

#### Option 2: Web API (FastAPI)
```bash
# Terminal 1: Start backend API
uvicorn backend_api:app --host 127.0.0.1 --port 5001 --reload

# Terminal 2: Start web UI
python -m http.server 8000 --directory .
# Open http://localhost:8000 in your browser
```

## API Endpoints

### POST /ask - Process Agricultural Query

**Request:**
```json
{
  "user_input": "string (required) - The user's question or request",
  "user_input": "string (required) - The user's question or request"
}
```

**Response:**
```json
{
  "status": "success|error",
  "agents": [
    {
      "name": "agent_name",
      "status": "complete",
      "output": "agent response",
      "tokens": {"prompt_tokens": 100, "completion_tokens": 50}
    }
  ],
  "final_answer": "final answer for the user",
  "token_summary": {
    "total_prompt_tokens": 500,
    "total_completion_tokens": 300,
    "total_cost_usd": 0.042
  }
}
```

### GET /health - Health Check

Returns: `{"status": "healthy", "service": "KhetSetu Backend API", "timestamp": "2024-..."}`

## Configuration

Edit `.env` file with your API keys:

```env
# OpenAI API
OPENAI_API_KEY=sk-...

# Location services
GEO_API_KEY=your-opencage-api-key

# Weather data
OPEN_WEATHER_API_KEY=your-openweathermap-api-key

```

## Cost Tracking

Every query returns token usage and estimated costs:

- **Standard GPT Models**: ~$0.0005-0.003 per token pair
- **Summary**: Automatic calculation displayed after each query


## Performance Metrics

Typical query times:
- **Weather queries**: 3-8 seconds
- **Solution queries**: 5-12 seconds
- **Multi-agent coordination**: 2-3 rounds of refinement

Token usage:
- **Simple queries**: 200-500 tokens
- **Complex queries**: 1000-2000 tokens

## Contributing

To add new agents or kernel functions:

1. Create agent file in `src/agents/`
2. Implement `NAME`, `INSTRUCTIONS`, and `create(kernel)` method
3. Register in `src/agents/__init__.py`
4. Add to `src/agent_manager.py` agent list and selection strategy
5. Update selection strategy template to route correctly
6. Add tests to `tests/`

## License

See LICENSE file for details.

## Support

For issues, questions, or feature requests:
- Check the [docs/FRONTEND_INTEGRATION_GUIDE.md](docs/FRONTEND_INTEGRATION_GUIDE.md)
- Review [docs/MODULE_REFERENCE.md](docs/MODULE_REFERENCE.md)
- Check logs in `logs/` directory

---
