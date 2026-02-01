"""
FastAPI backend API for KhetSetu Web UI
This connects the frontend to the main.py logic.

Installation:
    pip install fastapi uvicorn python-multipart

Usage:
    uvicorn backend_api:app --host 127.0.0.1 --port 5001 --reload
    
Then update app.js to use:
    const API_ENDPOINT = 'http://localhost:5001/ask';
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import asyncio
import json
import sys
from datetime import datetime
from typing import Optional, List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# NOTE: Import KhetSetu only when needed to avoid startup errors
# from main import KhetSetu

app = FastAPI(title="KhetSetu Backend API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Request/Response Models
# ============================================================================

class QueryRequest(BaseModel):
    user_input: str = Field(..., min_length=1, description="User's agricultural query")

class TokenInfo(BaseModel):
    prompt_tokens: int
    completion_tokens: int

class AgentResponse(BaseModel):
    name: str
    status: str
    output: str
    tokens: TokenInfo

class TokenSummary(BaseModel):
    total_prompt_tokens: int
    total_completion_tokens: int
    total_cost_usd: float

class QueryResponse(BaseModel):
    status: str
    agents: List[AgentResponse]
    final_answer: str
    token_summary: TokenSummary
    message: Optional[str] = None

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str

# ============================================================================
# API Endpoints
# ============================================================================

@app.get('/health', response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="KhetSetu Backend API",
        timestamp=datetime.now().isoformat()
    )


@app.post('/ask', response_model=QueryResponse)
async def ask_query(request: QueryRequest):
    """
    Main endpoint to process agricultural queries.
    
    Request:
    {
        "user_input": "What crops should I plant in Kenya?"
    }
    
    Response:
    {
        "status": "success",
        "agents": [
            {
                "name": "PromptAgent",
                "status": "complete",
                "output": "...",
                "tokens": {"prompt_tokens": 150, "completion_tokens": 75}
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
        user_input = request.user_input.strip()
        
        if not user_input:
            raise HTTPException(status_code=400, detail="user_input field is required")
        
        # Process the query
        # Note: This is a simplified example. In production, you should:
        # 1. Run this in a task queue (Celery, RQ, etc.)
        # 2. Add timeout handling
        # 3. Persist results to database
        # 4. Add rate limiting
        
        response = await process_query_async(user_input)
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing query: {e}")
        import traceback
        traceback.print_exc()
        
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post('/ask-async')
async def ask_query_async_endpoint():
    """
    Async endpoint (returns immediately, results available via /results/{task_id})
    
    Requires task queue like Celery in production.
    This is a placeholder for advanced implementations.
    """
    raise HTTPException(
        status_code=501,
        detail="Async endpoint not yet implemented. Use /ask instead."
    )


# ============================================================================
# Helper Functions
# ============================================================================

async def process_query_async(user_input: str) -> QueryResponse:
    """
    Process a query asynchronously and return structured response.
    
    Integrates with the real KhetSetu system from main.py
    
    Args:
        user_input (str): The user's agricultural query
        
    Returns:
        QueryResponse: Structured response matching frontend API contract
    """
    try:
        # Import here to avoid startup issues if dependencies are missing
        from main import KhetSetu
        
        # Create KhetSetu instance and process query
        khet_setu_system = KhetSetu()
        
        # Run the async main method
        result = await khet_setu_system.process_web_query(user_input)
        
        return QueryResponse(**result)
        
    except Exception as e:
        print(f"Error in process_query_async: {e}")
        import traceback
        traceback.print_exc()
        
        # Return error response
        return QueryResponse(
            status="error",
            message=f"Failed to process query: {str(e)}",
            agents=[],
            final_answer="Sorry, I encountered an error processing your request. Please try again.",
            token_summary=TokenSummary(
                total_prompt_tokens=0,
                total_completion_tokens=0,
                total_cost_usd=0.0
            )
        )


# ============================================================================
# Integration Helper
# ============================================================================

def integrate_with_main_py():
    """
    Instructions for integrating with the actual main.py logic.
    
    To use the real KhetSetu system instead of mock responses:
    
    1. Modify main.py to expose agent tracking:
    
        class KhetSetu:
            def __init__(self):
                ...
                self.agent_responses_for_api = []  # Add this
            
            async def main(self):
                ...
                # Before calling AgentGroupChatManager.invoke():
                
                async for content in AgentGroupChatManager.invoke():
                    # Capture agent response
                    self.agent_responses_for_api.append({
                        "name": content.name,
                        "status": "complete",
                        "output": content.content,
                        "tokens": {
                            "prompt_tokens": content.metadata["usage"].prompt_tokens,
                            "completion_tokens": content.metadata["usage"].completion_tokens
                        }
                    })
    
    2. Create an async wrapper:
    
        def process_query_sync(user_input: str) -> dict:
            khet_setu = KhetSetu()
            
            # Run async main in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(khet_setu.main())
            finally:
                loop.close()
            
            # Return captured responses
            return {
                "status": "success",
                "agents": khet_setu.agent_responses_for_api,
                "final_answer": khet_setu.final_answer,  # Add to KhetSetu
                "token_summary": khet_setu.token_tracker.get_summary()
            }
    """
    pass


# ============================================================================
# Run Server
# ============================================================================

if __name__ == '__main__':
    import uvicorn
    
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║          KhetSetu Backend API Server                   ║
    ║                  (FastAPI)                             ║
    ║                                                        ║
    ║  API Endpoint:  http://localhost:5001/ask             ║
    ║  Health Check:  http://localhost:5001/health          ║
    ║  API Docs:      http://localhost:5001/docs            ║
    ║                                                        ║
    ║  Frontend should use:                                 ║
    ║  const API_ENDPOINT = 'http://localhost:5001/ask'     ║
    ╚════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host='127.0.0.1',
        port=5001,
        log_level='info'
    )
