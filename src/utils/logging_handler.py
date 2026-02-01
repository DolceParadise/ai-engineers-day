"""Logging and data handling utilities."""

import os
import pandas as pd


class DataLogger:
    """Handle CSV logging for agent inputs and outputs."""

    def __init__(self, logs_dir: str = "./logs"):
        """
        Initialize the data logger.
        
        Args:
            logs_dir: Directory path for log files
        """
        self.logs_dir = logs_dir
        self.input_csv_path = os.path.join(logs_dir, "input.csv")
        self.output_csv_path = os.path.join(logs_dir, "output.csv")
        self.tokens_txt_path = os.path.join(logs_dir, "tokens.txt")
        self._initialize_directories()

    def _initialize_directories(self) -> None:
        """Create logs directory if it doesn't exist."""
        os.makedirs(self.logs_dir, exist_ok=True)

    def get_next_input_id(self) -> int:
        """
        Get the next input ID based on existing logs.
        
        Returns:
            Next input ID to use
        """
        if not os.path.exists(self.input_csv_path):
            pd.DataFrame(columns=['InputID', 'Statement']).to_csv(
                self.input_csv_path, index=False
            )
            return 1

        input_df = pd.read_csv(self.input_csv_path)
        if input_df.empty:
            return 1
        return input_df['InputID'].astype(int).max() + 1

    def log_input(self, input_id: int, statement: str) -> None:
        """
        Log user input to CSV.
        
        Args:
            input_id: Unique input identifier
            statement: User's input statement
        """
        input_df = pd.DataFrame({
            'InputID': [input_id],
            'Statement': [statement]
        })
        input_df.to_csv(
            self.input_csv_path, index=False, mode='a', header=False
        )

    def log_output(self, output_df: pd.DataFrame) -> None:
        """
        Log agent outputs to CSV.
        
        Args:
            output_df: DataFrame containing output entries
        """
        output_df.to_csv(
            self.output_csv_path, index=False, mode='a'
        )

    def add_output_record(
        self,
        output_df: pd.DataFrame,
        input_id: int,
        sequence_number: int,
        agent_name: str,
        output_content: str
    ) -> pd.DataFrame:
        """
        Add a single output record to the dataframe.
        
        Args:
            output_df: Existing output dataframe
            input_id: Unique input identifier
            sequence_number: Sequence number in conversation
            agent_name: Name of the agent
            output_content: Content of the output
            
        Returns:
            Updated dataframe
        """
        new_record = pd.DataFrame({
            'InputID': [input_id],
            'SequenceNumber': [sequence_number],
            'AgentName': [agent_name],
            'Output': [output_content]
        })
        return pd.concat([output_df, new_record], ignore_index=True)

    def log_token_usage(
        self,
        input_id: int,
        prompt_agent_tokens: int,
        parse_tokens: int,
        forecast_tokens: int,
        history_tokens: int,
        solution_tokens: int,
        reviewer_tokens: int,
        total_tokens: int,
        total_prompt_tokens: int,
        total_completion_tokens: int,
        total_cost: float
    ) -> None:
        """
        Log token usage and cost information.
        
        Args:
            input_id: Unique input identifier
            prompt_agent_tokens: Tokens used by PromptAgent
            parse_tokens: Tokens used by ParseAgent
            forecast_tokens: Tokens used by ForecastAgent
            history_tokens: Tokens used by WeatherHistoryAgent
            solution_tokens: Tokens used by SolutionAgent
            reviewer_tokens: Tokens used by ReviewerAgent
            total_tokens: Total tokens used
            total_prompt_tokens: Total prompt tokens
            total_completion_tokens: Total completion tokens
            total_cost: Total cost in USD
        """
        token_data = f"""
Input: {input_id}
PromptAgent tokens: {prompt_agent_tokens}
ParseAgent tokens: {parse_tokens}
ForecastAgent tokens: {forecast_tokens}
WeatherHistoryAgent tokens: {history_tokens}
SolutionAgent tokens: {solution_tokens}
ReviewerAgent tokens: {reviewer_tokens}
Total tokens: {total_tokens}
Total prompt tokens: {total_prompt_tokens}
Total completion tokens: {total_completion_tokens}
Total cost (USD): ${total_cost:.6f}
"""
        with open(self.tokens_txt_path, "a") as file:
            file.write(token_data)


class TokenTracker:
    """Track token usage across agents."""

    def __init__(self):
        """Initialize token tracking."""
        self.prompt_agent_tokens = 0
        self.parse_tokens = 0
        self.forecast_tokens = 0
        self.history_tokens = 0
        self.solution_tokens = 0
        self.reviewer_tokens = 0
        self.total_tokens = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0

    def update_agent_tokens(
        self,
        agent_name: str,
        prompt_tokens: int,
        completion_tokens: int
    ) -> None:
        """
        Update token counts for a specific agent.
        
        Args:
            agent_name: Name of the agent
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
        """
        total_tokens = prompt_tokens + completion_tokens

        if agent_name == "PromptAgent":
            self.prompt_agent_tokens += total_tokens
        elif agent_name == "ParseAgent":
            self.parse_tokens += total_tokens
        elif agent_name == "ForecastAgent":
            self.forecast_tokens += total_tokens
        elif agent_name == "WeatherHistoryAgent":
            self.history_tokens += total_tokens
        elif agent_name == "SolutionAgent":
            self.solution_tokens += total_tokens
        elif agent_name == "ReviewerAgent":
            self.reviewer_tokens += total_tokens

        self.total_tokens += total_tokens
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens

    def get_summary(self) -> dict:
        """
        Get a summary of token usage.
        
        Returns:
            Dictionary containing token counts and totals
        """
        return {
            'prompt_agent_tokens': self.prompt_agent_tokens,
            'parse_tokens': self.parse_tokens,
            'forecast_tokens': self.forecast_tokens,
            'history_tokens': self.history_tokens,
            'solution_tokens': self.solution_tokens,
            'reviewer_tokens': self.reviewer_tokens,
            'total_tokens': self.total_tokens,
            'total_prompt_tokens': self.total_prompt_tokens,
            'total_completion_tokens': self.total_completion_tokens
        }
