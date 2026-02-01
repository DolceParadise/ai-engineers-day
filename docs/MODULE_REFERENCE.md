# Module Reference

## Quick Import Guide

This document shows how to import and use the main components of the refactored KhetSetu system.

## src.config

**Purpose**: Kernel setup and cost calculation

```python
from src.config import KernelConfig, CostCalculator

# Create kernel with all services and tools
kernel = KernelConfig.create_kernel()

# Calculate costs
calculator = CostCalculator()
cost = calculator.calculate_cost(
    prompt_tokens=1000,
    completion_tokens=500
)  # Returns float (USD)
```

### Classes
- **KernelConfig**: Static methods for kernel setup
  - `create_kernel() -> Kernel`: Creates and configures the Semantic Kernel
  
- **CostCalculator**: Cost calculation utilities
  - `calculate_cost(prompt_tokens: int, completion_tokens: int) -> float`

---

## src.agent_manager

**Purpose**: Multi-agent orchestration and conversation management

```python
from src.agent_manager import AgentManager

# Create agent group chat with all agents and strategies
agent_group_chat = AgentManager.create_agent_group_chat(kernel)
```

### Classes
- **AgentManager**: Static methods for agent creation and orchestration
  - `create_agent_group_chat(kernel: Kernel) -> AgentGroupChat`: Creates configured agent group chat

---

## src.agents

**Purpose**: Individual agent definitions

```python
from src.agents import (
    PromptAgent,
    ParseAgent,
    ForecastAgent,
    WeatherHistoryAgent,
    SolutionAgent,
    ReviewerAgent,
)

# Each agent follows the same pattern:
# 1. Has a NAME attribute
# 2. Has INSTRUCTIONS attribute
# 3. Has a create() static method

agent = PromptAgent.create(kernel)
```

### Available Agents

#### PromptAgent
User-facing communication agent
```python
agent = PromptAgent.create(kernel)
# NAME = "PromptAgent"
```

#### ParseAgent
Extracts structured data from user input
```python
agent = ParseAgent.create(kernel)
# NAME = "ParseAgent"
# Returns JSON with: user_intent, location, start_year, end_year, forecast_date
```

#### ForecastAgent
Provides weather forecasts
```python
agent = ForecastAgent.create(kernel)
# NAME = "ForecastAgent"
```

#### WeatherHistoryAgent
Provides historical weather data
```python
agent = WeatherHistoryAgent.create(kernel)
# NAME = "WeatherHistoryAgent"
```

#### SolutionAgent
Generates agricultural solutions
```python
agent = SolutionAgent.create(kernel)
# NAME = "SolutionAgent"
```

#### ReviewerAgent
Reviews and validates solutions
```python
agent = ReviewerAgent.create(kernel)
# NAME = "ReviewerAgent"
```

---

## src.utils.language_detection

**Purpose**: Multi-language detection with special Hinglish support

```python
from src.utils.language_detection import (
    detect_user_language,
    is_hinglish,
    is_romanized_hinglish,
)

# Detect user language
code, name = detect_user_language("Hello, how are you?")
# Returns: ("en", "English")

code, name = detect_user_language("Namaste, kaise ho?")
# Returns: ("hi-en", "Hinglish (Hindi and English)")

# Check if text is Hinglish
is_hinglish("नमस्ते hello")  # Returns: True

# Check if romanized Hinglish
is_romanized_hinglish("mein kal jana chahta hoon")  # Returns: True
```

### Functions
- **detect_user_language(text: str) -> Tuple[str, str]**
  - Returns: (language_code, language_name)
  - Special handling for Hinglish and romanized Hinglish
  
- **is_hinglish(text: str) -> bool**
  - Detects mix of Devanagari and Latin scripts
  
- **is_romanized_hinglish(text: str) -> bool**
  - Detects Hindi written in Latin script mixed with English

---

## src.utils.logging_handler

**Purpose**: Data logging and token tracking

```python
from src.utils.logging_handler import DataLogger, TokenTracker

# Initialize logging
logger = DataLogger(logs_dir="./logs")

# Get next input ID
input_id = logger.get_next_input_id()

# Log user input
logger.log_input(input_id, "What should I plant?")

# Track tokens
tracker = TokenTracker()
tracker.update_agent_tokens(
    agent_name="PromptAgent",
    prompt_tokens=150,
    completion_tokens=75
)

# Get summary
summary = tracker.get_summary()

# Log token usage
logger.log_token_usage(
    input_id=1,
    prompt_agent_tokens=150,
    parse_tokens=120,
    forecast_tokens=200,
    history_tokens=180,
    solution_tokens=300,
    reviewer_tokens=250,
    total_tokens=1200,
    total_prompt_tokens=800,
    total_completion_tokens=400,
    total_cost=0.0045
)
```

### Classes

#### DataLogger
Manages CSV logging for inputs/outputs

**Methods:**
- `__init__(logs_dir: str = "./logs")`
- `get_next_input_id() -> int`
- `log_input(input_id: int, statement: str) -> None`
- `log_output(output_df: pd.DataFrame) -> None`
- `add_output_record(output_df, input_id, sequence_number, agent_name, output_content) -> pd.DataFrame`
- `log_token_usage(input_id, prompt_agent_tokens, ..., total_cost) -> None`

#### TokenTracker
Tracks token usage across agents

**Methods:**
- `__init__()`
- `update_agent_tokens(agent_name: str, prompt_tokens: int, completion_tokens: int) -> None`
- `get_summary() -> dict`: Returns token counts for all agents

---

## Complete Usage Example

```python
import asyncio
from src.config import KernelConfig, CostCalculator
from src.agent_manager import AgentManager
from src.utils.language_detection import detect_user_language
from src.utils.logging_handler import DataLogger, TokenTracker

async def main():
    # Setup
    kernel = KernelConfig.create_kernel()
    agent_group_chat = AgentManager.create_agent_group_chat(kernel)
    logger = DataLogger()
    tracker = TokenTracker()
    calculator = CostCalculator()
    
    # Get user input
    user_input = input("Your query: ")
    
    # Detect language
    code, language = detect_user_language(user_input)
    print(f"Detected language: {language}")
    
    # Log input
    input_id = logger.get_next_input_id()
    logger.log_input(input_id, user_input)
    
    # Add message to chat
    from semantic_kernel.contents import AuthorRole, ChatMessageContent
    await agent_group_chat.add_chat_message(ChatMessageContent(
        role=AuthorRole.USER,
        content=user_input
    ))
    
    # Process through agents
    sequence_number = 1
    async for content in agent_group_chat.invoke():
        print(f"{content.name}: {content.content}\n")
        
        # Track tokens
        if hasattr(content, 'metadata'):
            usage = content.metadata.get("usage", {})
            tracker.update_agent_tokens(
                content.name,
                usage.get("prompt_tokens", 0),
                usage.get("completion_tokens", 0)
            )
        
        sequence_number += 1
    
    # Calculate and log costs
    summary = tracker.get_summary()
    total_cost = calculator.calculate_cost(
        summary['total_prompt_tokens'],
        summary['total_completion_tokens']
    )
    
    logger.log_token_usage(
        input_id,
        summary['prompt_agent_tokens'],
        summary['parse_tokens'],
        summary['forecast_tokens'],
        summary['history_tokens'],
        summary['solution_tokens'],
        summary['reviewer_tokens'],
        summary['total_tokens'],
        summary['total_prompt_tokens'],
        summary['total_completion_tokens'],
        total_cost
    )
    
    print(f"Total cost: ${total_cost:.6f}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Environment Variables

Create a `.env` file with:
```
OPENAI_API_KEY=your_key_here
GEO_API_KEY=your_geo_key_here
OPEN_WEATHER_API_KEY=your_weather_key_here
```

---

## CSV Output Format

### input.csv
```
InputID,Statement
1,"What crops should I plant in Kenya?"
2,"What is the weather forecast for tomorrow?"
```

### output.csv
```
InputID,SequenceNumber,AgentName,Output
1,1,PromptAgent,"Hello! I'm here to assist..."
1,2,ParseAgent,"{...json...}"
1,3,ForecastAgent,"The forecast for Kenya..."
...
```

### tokens.txt
```
Input: 1
PromptAgent tokens: 245
ParseAgent tokens: 189
ForecastAgent tokens: 512
...
Total cost (USD): $0.011234
```

---

For more details, see:
- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed architecture documentation
- [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) - Summary of changes
