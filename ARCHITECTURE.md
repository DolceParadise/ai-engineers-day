"""Project structure and architecture documentation."""

# AgroAskAI - Refactored Architecture

## Overview
The AgroAskAI project has been refactored to follow industry-standard Python coding practices and best practices for software architecture. The codebase is now organized into modular, maintainable components with clear separation of concerns.

## Project Structure

```
ai-engineers-day/
├── main.py                           # Entry point for the application
├── kernel_functions.py               # Semantic Kernel function definitions
├── requirements.txt                  # Project dependencies
├── README.md                         # Project documentation
│
└── src/                              # Main source code package
    ├── __init__.py                   # Package initialization
    ├── config.py                     # Configuration classes
    ├── agent_manager.py              # Agent orchestration
    │
    ├── agents/                       # Individual agent implementations
    │   ├── __init__.py              
    │   ├── prompt_agent.py           # User-facing communication agent
    │   ├── parse_agent.py            # Input parsing agent
    │   ├── forecast_agent.py         # Weather forecast agent
    │   ├── weather_history_agent.py  # Historical weather agent
    │   ├── solution_agent.py         # Solution recommendation agent
    │   └── reviewer_agent.py         # Solution review and approval agent
    │
    └── utils/                        # Utility modules
        ├── __init__.py
        ├── language_detection.py     # Multi-language support utilities
        └── logging_handler.py        # Data logging and tracking utilities
```

## Key Components

### 1. **Main Module** (`main.py`)
The entry point for the application containing the `AgroAskAI` class that orchestrates the entire system:
- Manages agent initialization and interaction
- Handles user input/output
- Coordinates weather data retrieval
- Tracks costs and token usage
- Implements comprehensive error handling

**Key Methods:**
- `parse_user_input()`: Extracts structured data from natural language
- `get_weather_context()`: Retrieves weather and forecast data
- `run_agent_group_chat()`: Manages the multi-agent conversation loop
- `main()`: Main execution flow

### 2. **Configuration Module** (`src/config.py`)
Centralized configuration and setup:
- `KernelConfig`: Creates and configures the Semantic Kernel with OpenAI services
- `CostCalculator`: Calculates API usage costs

### 3. **Agent Manager** (`src/agent_manager.py`)
Orchestrates multi-agent interactions:
- Creates all agent instances
- Sets up selection strategies
- Configures termination conditions
- Manages agent conversation flow

### 4. **Individual Agents** (`src/agents/`)

Each agent is a standalone module following the same pattern for maintainability:

- **PromptAgent**: User-facing communication agent
  - Greets users at the start
  - Delivers approved solutions at the end
  - Never performs analysis or decision-making

- **ParseAgent**: Extracts structured information
  - Converts natural language to JSON format
  - Identifies user intent, location, dates
  - Validates and re-requests missing information

- **ForecastAgent**: Provides weather forecasts
  - Calls `get_forecast()` kernel function
  - Summarizes forecast data
  - Responds in user's language

- **WeatherHistoryAgent**: Provides historical weather data
  - Calls `get_NASA_data()` kernel function
  - Analyzes long-term climate patterns
  - Spans requested time ranges

- **SolutionAgent**: Generates agricultural solutions
  - Creates actionable recommendations
  - References weather context
  - Suggests sustainable practices

- **ReviewerAgent**: Validates and approves solutions
  - Checks completeness and accuracy
  - Ensures practical implementation
  - Provides improvement suggestions

### 5. **Utility Modules** (`src/utils/`)

- **Language Detection** (`language_detection.py`)
  - Multi-language detection with special Hinglish support
  - Three detection methods:
    - Devanagari script detection (Hindi)
    - Romanized Hinglish pattern matching
    - Fallback to langdetect library

- **Logging Handler** (`logging_handler.py`)
  - `DataLogger`: Manages CSV logging for inputs/outputs
  - `TokenTracker`: Tracks token usage per agent
  - Cost tracking and reporting

## Design Principles Applied

### 1. **Single Responsibility Principle**
- Each module has one clear purpose
- Agents focus on specific tasks
- Utilities handle cross-cutting concerns

### 2. **Open/Closed Principle**
- Easy to extend with new agents
- Configuration-driven behavior
- Minimal changes to existing code when adding features

### 3. **Dependency Injection**
- Kernel passed to agent creators
- Loose coupling between components
- Easy to test and mock

### 4. **DRY (Don't Repeat Yourself)**
- Extracted common logging logic
- Centralized kernel configuration
- Reusable language detection functions

### 5. **Clear Documentation**
- Comprehensive docstrings (Google style)
- Type hints throughout
- README and inline comments

## Code Quality Features

### Type Hints
All functions include type hints for better IDE support and documentation:
```python
async def parse_user_input(
    self,
    parse_agent,
    user_input: str
) -> Optional[Dict[str, Any]]:
```

### Error Handling
Comprehensive try-except blocks with meaningful error messages:
- ServiceResponseException (token limits)
- FunctionExecutionException (rate limits)
- JSONDecodeError (parsing errors)

### Async/Await Pattern
Proper asynchronous programming with:
- Async functions for I/O operations
- Proper await usage
- Event loop management

### Configuration Management
- Environment variables via `.env`
- Centralized kernel setup
- Extensible configuration classes

## Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Adding New Agents

1. Create a new file in `src/agents/` (e.g., `new_agent.py`)
2. Define a class with `NAME`, `INSTRUCTIONS`, and a `create()` method
3. Add to `src/agents/__init__.py`
4. Register in `AgentManager.create_agent_group_chat()`

Example:
```python
class NewAgent:
    NAME = "NewAgent"
    INSTRUCTIONS = "..."
    
    @staticmethod
    def create(kernel: Kernel) -> ChatCompletionAgent:
        return ChatCompletionAgent(
            kernel=kernel,
            name=NewAgent.NAME,
            instructions=NewAgent.INSTRUCTIONS
        )
```

## Dependencies

See `requirements.txt` for complete list:
- `semantic-kernel`: AI orchestration framework
- `openai`: OpenAI API client
- `python-dotenv`: Environment variable management
- `pandas`: Data handling and CSV operations
- `langdetect`: Language detection library

## Logging and Monitoring

Token usage and costs are logged to `logs/`:
- `input.csv`: User queries
- `output.csv`: Agent responses
- `tokens.txt`: Token usage breakdown per agent

Example token tracking output:
```
Input: 1
PromptAgent tokens: 245
ParseAgent tokens: 189
ForecastAgent tokens: 512
WeatherHistoryAgent tokens: 428
SolutionAgent tokens: 1024
ReviewerAgent tokens: 356
Total tokens: 2754
Total prompt tokens: 1842
Total completion tokens: 912
Total cost (USD): $0.011234
```

## Best Practices Implemented

1. **Modular Architecture**: Clear separation of concerns
2. **Type Safety**: Comprehensive type hints
3. **Error Handling**: Robust exception handling
4. **Documentation**: Clear docstrings and comments
5. **Configuration**: Centralized and environment-aware
6. **Logging**: Comprehensive data tracking
7. **Testing**: Organized for easy unit testing
8. **Performance**: Efficient token management
9. **Scalability**: Easy to add agents or modify behavior
10. **Maintenance**: Clear code structure and naming conventions

## Future Enhancements

- Add unit tests for each component
- Implement caching for frequently requested data
- Add more sophisticated language models
- Implement persistent conversation history
- Add metrics and monitoring dashboard
- Support for additional languages
- Database integration for data persistence

---

For more information, see the main README.md file.
