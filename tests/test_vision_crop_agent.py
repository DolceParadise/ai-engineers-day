"""
Smoke test for VisionCropAgent image analysis functionality.

This script demonstrates how to use the image-based crop analysis feature
with both base64-encoded images and image URLs.

Installation:
    pip install pillow requests

Usage:
    python tests/test_vision_crop_agent.py
"""

import asyncio
import json
import base64
import sys
import os
from pathlib import Path
from typing import Optional, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def encode_image_to_base64(image_path: str) -> str:
    """
    Encode a local image file to base64.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64-encoded image string (without data: prefix)
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


async def test_analyze_crop_image_kernel_function() -> None:
    """Test the analyze_crop_image kernel function directly."""
    print("\n" + "="*70)
    print("TEST 1: Direct Kernel Function Test (analyze_crop_image)")
    print("="*70)
    
    try:
        from kernel_functions import analyze_crop_image
        
        # Test with missing image (should return error gracefully)
        print("\nTest 1a: Call with no image (should handle gracefully)...")
        result = await analyze_crop_image(query="What is wrong with this plant?")
        result_json = json.loads(result)
        
        print(f"Status: {'✓ PASS' if 'answer' in result_json else '✗ FAIL'}")
        print(f"Response: {result_json.get('answer', 'N/A')[:100]}...")
        
    except Exception as e:
        print(f"✗ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_vision_crop_agent_creation() -> None:
    """Test creating VisionCropAgent instance."""
    print("\n" + "="*70)
    print("TEST 2: VisionCropAgent Creation")
    print("="*70)
    
    try:
        from src.config import KernelConfig
        from src.agents import VisionCropAgent
        
        # Create kernel
        kernel = KernelConfig.create_kernel()
        print("✓ Kernel created successfully")
        
        # Create agent
        vision_agent = VisionCropAgent.create(kernel)
        print(f"✓ VisionCropAgent created successfully")
        print(f"  - Agent name: {vision_agent.name}")
        print(f"  - Instructions length: {len(vision_agent.instructions)} chars")
        
    except Exception as e:
        print(f"✗ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_backend_api_request_model() -> None:
    """Test the backend API request model with image fields."""
    print("\n" + "="*70)
    print("TEST 3: Backend API Request Model")
    print("="*70)
    
    try:
        from backend_api import QueryRequest
        
        # Test 1: Request with only user_input (backwards compatibility)
        print("\nTest 3a: Backwards compatible request (user_input only)...")
        req1 = QueryRequest(user_input="What crops should I plant?")
        print(f"✓ PASS: Created request with user_input only")
        print(f"  - user_input: {req1.user_input[:50]}...")
        print(f"  - image_base64: {req1.image_base64}")
        print(f"  - image_url: {req1.image_url}")
        
        # Test 2: Request with image_base64
        print("\nTest 3b: Request with image_base64...")
        dummy_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        req2 = QueryRequest(
            user_input="Is this plant diseased?",
            image_base64=dummy_base64
        )
        print(f"✓ PASS: Created request with image_base64")
        print(f"  - Has image_base64: {bool(req2.image_base64)}")
        
        # Test 3: Request with image_url
        print("\nTest 3c: Request with image_url...")
        req3 = QueryRequest(
            user_input="Analyze this crop",
            image_url="https://example.com/crop.jpg"
        )
        print(f"✓ PASS: Created request with image_url")
        print(f"  - image_url: {req3.image_url}")
        
    except Exception as e:
        print(f"✗ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_parse_agent_image_intent() -> None:
    """Test that ParseAgent recognizes image-related intents."""
    print("\n" + "="*70)
    print("TEST 4: ParseAgent Image Intent Detection")
    print("="*70)
    
    try:
        from src.config import KernelConfig
        from src.agents import ParseAgent
        
        kernel = KernelConfig.create_kernel()
        parse_agent = ParseAgent.create(kernel)
        
        print(f"✓ ParseAgent created successfully")
        print(f"  - Agent name: {parse_agent.name}")
        
        # Check instructions contain image-related keywords
        instructions = parse_agent.instructions
        keywords = ["diagnose_from_image", "image_qna", "has_image"]
        
        for keyword in keywords:
            if keyword in instructions:
                print(f"  ✓ Found keyword: {keyword}")
            else:
                print(f"  ✗ Missing keyword: {keyword}")
                
    except Exception as e:
        print(f"✗ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_agent_manager_includes_vision_agent() -> None:
    """Test that AgentManager includes VisionCropAgent."""
    print("\n" + "="*70)
    print("TEST 5: AgentManager Configuration")
    print("="*70)
    
    try:
        from src.config import KernelConfig
        from src.agent_manager import AgentManager
        
        kernel = KernelConfig.create_kernel()
        agent_group = AgentManager.create_agent_group_chat(kernel)
        
        print(f"✓ AgentGroupChat created successfully")
        
        # Check agents list
        agent_names = [agent.name for agent in agent_group.agents]
        print(f"  - Total agents: {len(agent_names)}")
        
        expected_agents = [
            "PromptAgent", "ParseAgent", "ForecastAgent",
            "WeatherHistoryAgent", "SolutionAgent", 
            "VisionCropAgent", "ReviewerAgent"
        ]
        
        for agent_name in expected_agents:
            if agent_name in agent_names:
                print(f"    ✓ {agent_name}")
            else:
                print(f"    ✗ {agent_name} (MISSING)")
                
    except Exception as e:
        print(f"✗ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_khet_setu_with_image_parameters() -> None:
    """Test KhetSetu.process_web_query with image parameters."""
    print("\n" + "="*70)
    print("TEST 6: KhetSetu Web Query with Image Parameters")
    print("="*70)
    
    try:
        from main import KhetSetu
        
        print("\nTest 6a: Creating KhetSetu instance...")
        khet_setu = KhetSetu()
        print("✓ KhetSetu instance created")
        
        # Test that method signature accepts image parameters
        import inspect
        sig = inspect.signature(khet_setu.process_web_query)
        params = list(sig.parameters.keys())
        
        print(f"\nTest 6b: Checking process_web_query signature...")
        print(f"  - Parameters: {params}")
        
        required_params = ["user_input", "image_base64", "image_url"]
        for param in required_params:
            if param in params:
                print(f"    ✓ {param}")
            else:
                print(f"    ✗ {param} (MISSING)")
        
    except Exception as e:
        print(f"✗ FAIL: {str(e)}")
        import traceback
        traceback.print_exc()


def test_image_encoding() -> None:
    """Test image encoding utilities."""
    print("\n" + "="*70)
    print("TEST 7: Image Encoding Utilities")
    print("="*70)
    
    try:
        # Test base64 encoding of dummy image
        dummy_image = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01'
        encoded = base64.b64encode(dummy_image).decode('utf-8')
        
        print(f"✓ Successfully encoded {len(dummy_image)} bytes to base64")
        print(f"  - Encoded length: {len(encoded)} chars")
        print(f"  - First 50 chars: {encoded[:50]}...")
        
    except Exception as e:
        print(f"✗ FAIL: {str(e)}")


async def run_all_tests() -> None:
    """Run all smoke tests."""
    print("\n" + "="*70)
    print("VISION CROP AGENT - SMOKE TEST SUITE")
    print("="*70)
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check for required environment variables
    required_env_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"\n⚠ WARNING: Missing environment variables: {missing_vars}")
        print("  - Some tests may be skipped or fail")
        print("  - Set these in .env file to enable full testing")
    
    # Run tests
    try:
        await test_vision_crop_agent_creation()
        await test_backend_api_request_model()
        await test_parse_agent_image_intent()
        await test_agent_manager_includes_vision_agent()
        await test_khet_setu_with_image_parameters()
        test_image_encoding()
        
        # These tests require API keys
        if os.getenv("OPENAI_API_KEY"):
            await test_analyze_crop_image_kernel_function()
        else:
            print("\n" + "="*70)
            print("SKIPPED: Direct kernel function test (requires OPENAI_API_KEY)")
            print("="*70)
            
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*70)
    print("SMOKE TEST SUITE COMPLETE")
    print("="*70)


if __name__ == "__main__":
    # Run async tests
    asyncio.run(run_all_tests())
    
    # Print instructions
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("""
1. Verify all tests pass (green checkmarks)

2. Test with actual image:
   - Provide a real crop/field image
   - Encode to base64: python -c "import base64; print(base64.b64encode(open('image.jpg','rb').read()).decode())"
   - Send to /ask endpoint with image_base64 field

3. Example curl request:
   curl -X POST http://localhost:5001/ask \\
     -H "Content-Type: application/json" \\
     -d '{
       "user_input": "What disease is affecting my crop?",
       "image_base64": "<base64_encoded_image_here>"
     }'

4. Monitor logs for:
   - VisionCropAgent responses
   - Image analysis results
   - Token usage

5. For production:
   - Add rate limiting
   - Implement image size limits (max 20MB recommended)
   - Add request authentication
   - Cache vision analysis results
   - Monitor OpenAI vision API costs
""")
