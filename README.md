# KhetSetu - Multi-Agent Agricultural Intelligence System

A sophisticated multi-agent system for agricultural queries combining weather analysis, climate history, farming solutions, and **image-based crop diagnostics**.

## Features

- **Weather Analysis**: Real-time weather forecasts and historical climate data
- **Farming Solutions**: AI-powered recommendations based on local conditions
- **Image-Based Crop Analysis**: Diagnose crop diseases, pests, and health issues from photos
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
│  - Accepts user_input, image_base64, image_url             │
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
    │ Forecast│  │        │  │ analyze_crop │
    │ History │  │────────┤  │ _image       │
    │ Solution│            │ get_adaptation│
    │ Vision* │            │              │
    │ Reviewer│            └──────────────┘
    └─────────┘
    *NEW*
```

## Agents

### 1. ParseAgent
Extracts structured information from natural language queries:
- User intent (weather forecast, weather history, solution, image diagnosis)
- Location
- Date ranges
- **NEW**: Image presence and type flags

### 2. PromptAgent
Natural language interface that greets users and summarizes responses.

### 3. ForecastAgent
Retrieves and summarizes weather forecasts using OpenWeatherMap API.

### 4. WeatherHistoryAgent
Accesses historical climate data via NASA POWER API.

### 5. SolutionAgent
Generates farming solutions and recommendations based on weather data.

### 6. VisionCropAgent ⭐ NEW
**Analyzes crop/field images to diagnose health issues, pests, diseases, and provide recommendations.**

Key capabilities:
- Crop identification from photos
- Growth stage assessment
- Disease/pest detection with confidence scores
- Stress symptom analysis (wilting, yellowing, spotting)
- Soil condition evaluation
- Suggests follow-up photos for better diagnosis
- Provides actionable recommendations in user's language

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

#### Option 3: Run Tests
```bash
# Run smoke tests for VisionCropAgent
python tests/test_vision_crop_agent.py
```

## Image-Based Crop Analysis

The **VisionCropAgent** enables farmers to photograph their crops and get instant diagnostics.

### How It Works

1. **Send Image with Query**
   ```json
   {
     "user_input": "What's wrong with my tomato plants?",
     "image_base64": "base64_encoded_image_data",
     "image_url": "https://example.com/crop.jpg"
   }
   ```

2. **Vision Analysis Pipeline**
   - Image is analyzed using GPT-4 Vision
   - Extracts visual observations (crop type, growth stage, symptoms)
   - Identifies issues (diseases, pests, stress)
   - Suggests follow-up photos for better diagnosis
   - Provides actionable recommendations

3. **Response Format**
   ```json
   {
     "status": "success",
     "agents": [
       {
         "name": "VisionCropAgent",
         "output": "Based on the image, I observe [observations]. This appears to be [crop type]. The visible issues are [issues]. Recommended actions: [recommendations]",
         "tokens": {"prompt_tokens": 150, "completion_tokens": 200}
       }
     ],
     "final_answer": "Your tomato plants show signs of early blight. Apply copper fungicide immediately...",
     "token_summary": {"total_prompt_tokens": 500, "total_completion_tokens": 300, "total_cost_usd": 0.042}
   }
   ```

### Usage Examples

#### Example 1: Diagnose Plant Disease (using image URL)
```bash
curl -X POST http://localhost:5001/ask \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Is my rice crop diseased? Check for blast disease or any other issues.",
    "image_url": "https://example.com/rice_field.jpg"
  }'
```

#### Example 2: Analyze Pest Damage (using base64)
```bash
# Encode image to base64 first
IMAGE_BASE64=$(base64 < /path/to/crop_image.jpg | tr -d '\n')

curl -X POST http://localhost:5001/ask \
  -H "Content-Type: application/json" \
  -d "{
    \"user_input\": \"What pests are attacking my cotton crop? How should I treat it?\",
    \"image_base64\": \"$IMAGE_BASE64\"
  }"
```

#### Example 3: Identify Crop Type
```bash
curl -X POST http://localhost:5001/ask \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "What crop is this? Is it healthy?",
    "image_base64": "<base64_encoded_image>"
  }'
```

#### Example 4: Check Soil Health
```bash
curl -X POST http://localhost:5001/ask \
  -H "Content-Type: application/json" \
  -d '{
    "user_input": "Is my soil healthy? What does the color and texture tell you?",
    "image_url": "https://example.com/soil_sample.jpg"
  }'
```

### Image Guidelines

For best results when sending crop photos:

1. **Composition**
   - Include affected plant parts in frame
   - Show both healthy and diseased areas if possible
   - Capture close-ups of symptoms (leaves, stems, fruits)

2. **Lighting**
   - Use natural daylight (avoid shadows)
   - Photograph in morning or evening for best colors
   - Avoid glare or strong backlighting

3. **Multiple Photos**
   - Whole plant overview
   - Close-up of symptoms (leaf spot, lesion, damage)
   - Leaf underside (for pest eggs, webbing)
   - Stem base (for wilting, rot)
   - Wider field view (for spread patterns)

4. **Image Quality**
   - Minimum: 640x480 pixels
   - Recommended: 1280x720 or higher
   - Format: JPG, PNG, GIF, WEBP
   - Max file size: 20MB

### Supported Diagnoses

VisionCropAgent can identify:

**Common Diseases**
- Fungal: Blast, blight, powdery mildew, rust, septoria
- Bacterial: Leaf blight, wilt, bacterial spot
- Viral: Mosaic, yellowing, leaf curl

**Pest Damage**
- Insects: Aphids, thrips, mites, caterpillars, beetles
- Vertebrates: Rodent, bird, wild boar damage

**Nutrient Deficiencies**
- Nitrogen: Yellowing lower leaves
- Phosphorus: Purple/red coloration
- Potassium: Edge burn, weak stalks
- Iron/Manganese: Chlorosis patterns

**Environmental Stress**
- Water: Wilting, leaf roll, cracking
- Temperature: Scorching, frost damage
- Light: Etiolation, leaf bleaching

**Crop Growth**
- Growth stage identification
- Maturity assessment
- Harvest readiness

### API Response Fields

The VisionCropAgent response includes:

```json
{
  "observations": {
    "crop_type": "tomato",
    "growth_stage": "flowering",
    "visual_stress": ["yellow leaves on lower stem", "small brown spots on leaves"],
    "pests_diseases": ["possible early blight", "possibly septoria leaf spot"],
    "weeds_detected": false,
    "irrigation_status": "appears adequately watered",
    "soil_conditions": "dark soil, good structure",
    "anomalies": ["leaf yellowing pattern suggests fungal disease"]
  },
  "likely_crop": [
    {"name": "tomato", "confidence": 0.95},
    {"name": "pepper", "confidence": 0.15}
  ],
  "issues": [
    {
      "name": "early blight (Alternaria solani)",
      "evidence": "brown concentric spots with yellow halos on older leaves",
      "confidence": 0.82
    },
    {
      "name": "septoria leaf spot",
      "evidence": "small circular lesions with dark borders and gray centers",
      "confidence": 0.65
    }
  ],
  "recommended_next_photos": [
    "close-up of leaf underside to check for spore production",
    "stem lesions to assess blight progression",
    "wider field view to estimate disease spread percentage"
  ],
  "answer": "Your tomato crop shows signs of early blight (82% confidence). Apply copper fungicide immediately, remove lower affected leaves, and improve air circulation..."
}
```

## API Endpoints

### POST /ask - Process Agricultural Query

**Request:**
```json
{
  "user_input": "string (required) - The user's question or request",
  "image_base64": "string (optional) - Base64-encoded image without data: prefix",
  "image_url": "string (optional) - Public URL to the image"
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

# Optional: Model selection
OPENAI_MODEL=gpt-4o-mini  # Default for vision analysis
```

## Cost Tracking

Every query returns token usage and estimated costs:

- **GPT-4o-mini Vision**: ~$0.00015 per input token, ~$0.0006 per output token
- **Standard GPT Models**: ~$0.0005-0.003 per token pair
- **Summary**: Automatic calculation displayed after each query

## Testing

Run the comprehensive smoke test suite:

```bash
python tests/test_vision_crop_agent.py
```

This tests:
- VisionCropAgent creation
- Kernel function setup
- Backend API request models (with backwards compatibility)
- ParseAgent image intent detection
- AgentManager agent registration
- KhetSetu method signatures
- Image encoding utilities

## Troubleshooting

### Vision Analysis Returns Errors
- Ensure OPENAI_API_KEY is set and has sufficient credits
- Check image format (JPG, PNG, GIF, WEBP supported)
- Verify image size (max 20MB)
- Image must be public URL or valid base64

### Agent Not Responding
- Check that VisionCropAgent is registered in agent_manager.py
- Verify all kernel functions are properly decorated with @kernel_function
- Check logs for token limit errors

### Image Not Processing
- Ensure image_base64 or image_url is provided (not both omitted)
- If using base64, remove `data:image/jpeg;base64,` prefix
- Test with public URL first (easier to debug)

## Architecture Notes

### Agent Communication Flow

For image diagnosis queries:
1. **User sends** image + question
2. **ParseAgent** detects intent="diagnose_from_image"
3. **PromptAgent** acknowledges and clarifies the request
4. **VisionCropAgent** analyzes image using analyze_crop_image kernel function
5. **ReviewerAgent** validates the diagnosis quality
6. **PromptAgent** finalizes and presents the answer

### Kernel Functions

New kernel function added for vision analysis:

```python
@kernel_function
async def analyze_crop_image(
    image_base64: str = None,
    image_url: str = None,
    query: str = "Analyze this crop image"
) -> str:
    """
    Analyze crop/field image using OpenAI vision capabilities.
    Returns JSON with observations, identified crops, issues, and recommendations.
    """
```

## Performance Metrics

Typical query times:
- **Weather queries**: 3-8 seconds
- **Solution queries**: 5-12 seconds
- **Image analysis**: 4-10 seconds (includes vision API latency)
- **Multi-agent coordination**: 2-3 rounds of refinement

Token usage:
- **Simple queries**: 200-500 tokens
- **Complex queries**: 1000-2000 tokens
- **Image analysis**: 300-800 tokens (depends on image complexity)

## Future Enhancements

- [ ] Batch image analysis (analyze multiple photos in one request)
- [ ] Historical trend analysis (compare images over time)
- [ ] Automated irrigation recommendations based on soil moisture images
- [ ] Crop yield prediction from growth stage photos
- [ ] Precision agriculture integration (GPS coordinates, field boundaries)
- [ ] Mobile app with camera integration
- [ ] Offline mode with cached model predictions
- [ ] Community reporting (crowd-sourced disease tracking)

## Contributing

To add new agents or kernel functions:

1. Create agent file in `src/agents/`
2. Implement `NAME`, `INSTRUCTIONS`, and `create(kernel)` method
3. Register in `src/agents/__init__.py`
4. Add to `src/agent_manager.py` agent list and selection strategy
5. Update selection strategy template to route correctly
6. Add tests to `tests/test_vision_crop_agent.py`

## License

See LICENSE file for details.

## Support

For issues, questions, or feature requests:
- Check the [docs/FRONTEND_INTEGRATION_GUIDE.md](docs/FRONTEND_INTEGRATION_GUIDE.md)
- Review [docs/MODULE_REFERENCE.md](docs/MODULE_REFERENCE.md)
- Check logs in `logs/` directory

---

**Last Updated**: 2026-02-02  
**Vision Crop Agent Added**: ⭐ New Feature