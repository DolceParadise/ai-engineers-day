# KhetSetu Web UI - Integration Guide

## Overview

The web UI is a professional, single-page application that communicates with the Python backend through a REST API. This guide explains how to connect the frontend to your backend.

## Files Created

- **`index.html`** - HTML structure and layout
- **`styles.css`** - Complete styling with 400+ lines of CSS
- **`app.js`** - Frontend logic and API integration

## Quick Start

### 1. Set Up Backend API Endpoint

The frontend expects a REST API endpoint at:
```
POST /ask
```

Update the endpoint in `app.js`:
```javascript
// Line ~16 in app.js
const API_ENDPOINT = '/ask'; // or 'http://localhost:8000/ask'
```

### 2. Create Backend Endpoint

You need to create a new endpoint in your Python backend. Here's a Flask example:

```python
from flask import Flask, request, jsonify
import asyncio
from main import KhetSetu

app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask():
    """
    Backend endpoint that receives user queries and returns agent responses.
    
    Request format:
    {
        "user_input": "What crops should I plant in Kenya?"
    }
    
    Response format:
    {
        "status": "success",
        "agents": [
            {
                "name": "PromptAgent",
                "status": "complete",
                "output": "...",
                "tokens": {
                    "prompt_tokens": 150,
                    "completion_tokens": 75
                }
            },
            ...
        ],
        "final_answer": "Based on weather...",
        "token_summary": {
            "total_prompt_tokens": 1200,
            "total_completion_tokens": 800,
            "total_cost_usd": 0.0125
        }
    }
    """
    try:
        data = request.get_json()
        user_input = data.get('user_input', '').strip()
        
        if not user_input:
            return jsonify({
                "status": "error",
                "message": "user_input is required"
            }), 400
        
        # Run the KhetSetu system
        khet_setu = KhetSetu()
        
        # Create a modified version that collects agent responses
        agent_responses = []
        final_answer = None
        
        # Run the main async logic here
        # This is a simplified example - you'll need to refactor
        # main.py to expose the agent execution in a way that
        # the web UI can consume
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            process_query_with_tracking(agro_ask, user_input)
        )
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def process_query_with_tracking(agro_ask, user_input):
    """
    Process query and track agent responses for frontend display.
    This function should:
    1. Run KhetSetu.main()
    2. Capture each agent's response as it executes
    3. Return structured data matching the API contract
    """
    # TODO: Implement this based on your main.py structure
    pass

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### 3. Alternative: FastAPI Implementation

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from main import KhetSetu

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    user_input: str

class AgentResponse(BaseModel):
    name: str
    status: str
    output: str
    tokens: dict = {}

class AskResponse(BaseModel):
    status: str
    agents: list
    final_answer: str
    token_summary: dict

@app.post("/ask", response_model=AskResponse)
async def ask(request: QueryRequest):
    """
    Process agricultural query through multi-agent system.
    """
    try:
        user_input = request.user_input.strip()
        
        if not user_input:
            raise HTTPException(
                status_code=400,
                detail="user_input is required"
            )
        
        # Run KhetSetu
        khet_setu = KhetSetu()
        result = await process_query(agro_ask, user_input)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

async def process_query(agro_ask, user_input):
    """
    Execute query and track agent responses.
    """
    # Implement based on your main.py structure
    pass

# Run with: uvicorn filename:app --reload
```

## API Response Format

The frontend expects this exact JSON structure:

```json
{
  "status": "success",
  "agents": [
    {
      "name": "PromptAgent",
      "status": "complete",
      "output": "Hello! I'm working on your agricultural query...",
      "tokens": {
        "prompt_tokens": 150,
        "completion_tokens": 75
      }
    },
    {
      "name": "ParseAgent",
      "status": "complete",
      "output": "{\"user_intent\": \"get_solution\", \"location\": \"Siwan\", ...}",
      "tokens": {
        "prompt_tokens": 200,
        "completion_tokens": 100
      }
    },
    {
      "name": "ForecastAgent",
      "status": "complete",
      "output": "Weather forecast for the next 5 days...",
      "tokens": {
        "prompt_tokens": 180,
        "completion_tokens": 90
      }
    },
    {
      "name": "WeatherHistoryAgent",
      "status": "complete",
      "output": "Historical weather analysis...",
      "tokens": {
        "prompt_tokens": 160,
        "completion_tokens": 80
      }
    },
    {
      "name": "SolutionAgent",
      "status": "complete",
      "output": "Based on the analysis, here are recommendations...",
      "tokens": {
        "prompt_tokens": 250,
        "completion_tokens": 150
      }
    },
    {
      "name": "ReviewerAgent",
      "status": "complete",
      "output": "The solution is complete and approved.",
      "tokens": {
        "prompt_tokens": 200,
        "completion_tokens": 100
      }
    }
  ],
  "final_answer": "Based on weather patterns in Siwan, I recommend...",
  "token_summary": {
    "total_prompt_tokens": 1140,
    "total_completion_tokens": 595,
    "total_cost_usd": 0.00891
  }
}
```

## Frontend Configuration

### API Endpoint (app.js)

```javascript
// Update this based on your backend location
const API_ENDPOINT = '/ask'; // Same domain
// OR
const API_ENDPOINT = 'http://localhost:8000/ask'; // Different domain
// OR
const API_ENDPOINT = 'https://api.khetsetu.com/ask'; // Production
```

### CORS Configuration

If your frontend and backend are on different domains, you need CORS:

**FastAPI:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourfrontend.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Flask:**
```python
from flask_cors import CORS
CORS(app, resources={r"/ask": {"origins": "*"}})
```

## Refactoring main.py for Web Integration

To make the frontend work smoothly, you may need to modify `main.py` to:

1. **Track agent responses separately** from the logging system
2. **Return structured data** instead of just printing to console
3. **Expose the agent execution logic** through a callable function

Here's a suggested refactor:

```python
# In main.py, add this method to KhetSetu class:

async def process_query_for_api(self, user_input: str) -> dict:
    """
    Process a query and return structured response for web API.
    
    Returns:
        dict: Structured response matching frontend expectations
    """
    agent_responses = []
    
    # [Run through the normal flow, but capture agent outputs]
    
    return {
        "status": "success",
        "agents": agent_responses,
        "final_answer": final_answer,
        "token_summary": {
            "total_prompt_tokens": self.token_tracker.total_prompt_tokens,
            "total_completion_tokens": self.token_tracker.total_completion_tokens,
            "total_cost_usd": cost
        }
    }
```

## Development Workflow

### 1. Local Testing

```bash
# Terminal 1: Run Python backend
cd /Users/pratik/Documents/ai-engineers-day
python -m http.server 5000
# OR start your Flask/FastAPI server

# Terminal 2: Serve frontend
cd /Users/pratik/Documents/ai-engineers-day
python -m http.server 8000

# Open browser to http://localhost:8000
```

### 2. Update API Endpoint

In `app.js`, change:
```javascript
const API_ENDPOINT = 'http://localhost:5000/ask';
```

### 3. Test Query

In the browser, type:
```
What crops should I plant in Siwan?
```

You should see agent responses flowing in real-time or all at once depending on your backend implementation.

## Advanced Features

### Streaming Responses (Optional)

For real-time streaming of agent responses, use Server-Sent Events (SSE):

```python
# Backend (FastAPI)
from fastapi.responses import StreamingResponse

@app.get("/ask/stream")
async def ask_stream(user_input: str):
    async def event_generator():
        khet_setu = KhetSetu()
        
        # Process agents and yield events
        async for agent_response in khet_setu.stream_agents(user_input):
            yield f"event: agent_update\ndata: {json.dumps(agent_response)}\n\n"
        
        yield f"event: complete\ndata: {json.dumps(final_result)}\n\n"
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

Uncomment `handleStreamingResponse()` in `app.js` to use this.

### Polling with Progress Updates

Instead of streaming, you can poll the backend:

```python
@app.get("/ask/status/{query_id}")
async def ask_status(query_id: str):
    """Get progress of ongoing query."""
    # Return: {"status": "running", "agents": [...]}
```

## Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support (iOS 13+)
- IE 11: ❌ Not supported (ES6 features used)

## Performance Considerations

1. **Token Usage Display**: Calculated client-side from agent responses
2. **Cost Calculation**: Uses standard GPT-4o pricing (configurable)
3. **Large Responses**: JSON output is prettified and syntax-highlighted
4. **Mobile**: Responsive design works on tablets and phones

## Troubleshooting

### "API endpoint not found"
- Check `API_ENDPOINT` in `app.js` matches your backend URL
- Verify backend server is running
- Check CORS headers if different domains

### "Undefined property errors"
- Backend response doesn't match expected format
- Check JSON structure matches API contract above
- Use browser DevTools Console to inspect response

### "Token values showing as '-'"
- Backend didn't include `token_summary` in response
- Make sure all agents include token counts
- Check `updateTokenDisplay()` in `app.js`

## Deployment

### Production Setup

1. **Build frontend** (optional minification):
   ```bash
   # Use build tools like webpack, rollup, or parcel
   ```

2. **Deploy backend** to production server

3. **Configure API endpoint** for production URL

4. **Enable CORS** appropriately

5. **Use HTTPS** in production

## File Sizes

- `index.html`: ~8 KB
- `styles.css`: ~15 KB
- `app.js`: ~12 KB
- **Total**: ~35 KB (minified ~18 KB)

## Future Enhancements

- [ ] Real-time streaming with WebSockets
- [ ] Chat history persistence (localStorage)
- [ ] Advanced data visualization for recommendations
- [ ] Multi-language UI
- [ ] Accessibility improvements (WCAG 2.1 AA)
- [ ] Dark mode toggle
- [ ] Export results as PDF
- [ ] User authentication
- [ ] Analytics integration

---

For questions or issues, refer to the code comments in `app.js` and `index.html`.
