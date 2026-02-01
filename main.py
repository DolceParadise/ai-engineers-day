"""
KhetSetu - Main entry point for the multi-agent agricultural assistance system.

This module orchestrates the multi-agent system that handles agricultural queries
through language detection, weather data retrieval, and AI-powered recommendations.
"""

import asyncio
import json
import os
from typing import Optional, Dict, Any

import pandas as pd
from dotenv import load_dotenv
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents import AuthorRole, ChatMessageContent
from semantic_kernel.exceptions.service_exceptions import ServiceResponseException
from semantic_kernel.exceptions.function_exceptions import FunctionExecutionException

from src.config import KernelConfig, CostCalculator
from src.agent_manager import AgentManager
from src.utils.language_detection import detect_user_language
from src.utils.logging_handler import DataLogger, TokenTracker

# Load environment variables
load_dotenv()


class KhetSetu:
    """
    Main orchestrator for the KhetSetu multi-agent system.
    
    Manages agent interactions, data logging, and cost tracking for agricultural
    query processing.
    """

    def __init__(self):
        """Initialize KhetSetu system."""
        self.kernel = KernelConfig.create_kernel()
        self.agent_group_chat = AgentManager.create_agent_group_chat(self.kernel)
        self.data_logger = DataLogger()
        self.token_tracker = TokenTracker()
        self.cost_calculator = CostCalculator()
        self.agent_outputs = []  # Store agent outputs for web API

    async def parse_user_input(
        self,
        parse_agent,
        user_input: str
    ) -> Optional[Dict[str, Any]]:
        """
        Parse user input to extract structured data.
        
        Args:
            parse_agent: The ParseAgent instance
            user_input: Raw user input text
            
        Returns:
            Dictionary with parsed intent, location, and date info, or None on error
        """
        responses = []
        try:
            async for response in parse_agent.invoke(messages=user_input):
                responses.append(response)
                if hasattr(response, "metadata"):
                    usage = response.metadata.get("usage")
                    if usage:
                        self.token_tracker.update_agent_tokens(
                            "ParseAgent",
                            usage.prompt_tokens if hasattr(usage, 'prompt_tokens') else 0,
                            usage.completion_tokens if hasattr(usage, 'completion_tokens') else 0
                        )
        except json.JSONDecodeError as e:
            print("Error: Failed to parse response. Please restart and try again.")
            return None

        if not responses:
            return None

        try:
            parsed = json.loads(responses[0].content.content)
            return parsed
        except (json.JSONDecodeError, KeyError, AttributeError):
            print("Error: Failed to parse JSON response.")
            return None

    async def request_missing_value(
        self,
        field_name: str,
        parse_agent,
        validation_fn=None
    ) -> Optional[str]:
        """
        Request a missing or invalid value from the user.
        
        Args:
            field_name: Name of the field being requested
            parse_agent: The ParseAgent instance
            validation_fn: Optional function to validate the response
            
        Returns:
            User's input or None if invalid
        """
        prompts = {
            'intent': "KhetSetu answers agriculture-related questions. Try asking about farming, weather forecasts, or past climate trends: ",
            'location': 'Please enter a location (e.g., city, state, or country): '
        }

        user_message = input(prompts.get(field_name, f"Please provide {field_name}: "))

        await self.agent_group_chat.add_chat_message(ChatMessageContent(
            role=AuthorRole.USER,
            content=user_message
        ))

        parsed = await self.parse_user_input(parse_agent, user_message)

        if parsed is None:
            return None

        if validation_fn:
            return validation_fn(parsed)
        return parsed.get(field_name)

    async def get_weather_context(self, location: str, start_year: int, end_year: int, forecast_date: int) -> tuple:
        """
        Retrieve weather history and forecast data.
        
        Args:
            location: Location for weather data
            start_year: Start year for historical data
            end_year: End year for historical data
            forecast_date: Forecast date parameter
            
        Returns:
            Tuple of (historical_summary, forecast_summary)
        """
        history_args = KernelArguments(
            location=location,
            start_year=start_year,
            end_year=end_year
        )

        forecast_args = KernelArguments(
            location=location,
            forecast_date=forecast_date
        )

        try:
            historical_summary = await self.kernel.invoke(
                plugin_name="climate_tools",
                function_name="get_NASA_data",
                arguments=history_args
            )

            forecast_summary = await self.kernel.invoke(
                plugin_name="climate_tools",
                function_name="get_forecast",
                arguments=forecast_args
            )

            return historical_summary, forecast_summary
        except Exception as e:
            print(f"Warning: Could not retrieve weather data: {e}")
            return "", ""

    async def run_agent_group_chat(
        self,
        user_intent: str,
        location: str,
        user_language: str,
        context: str,
        input_id: int
    ) -> pd.DataFrame:
        """
        Run the agent group chat conversation.
        
        Args:
            user_intent: Parsed user intent
            location: Target location
            user_language: Detected user language
            context: Context information for agents
            input_id: Unique input identifier
            
        Returns:
            DataFrame with conversation outputs
        """
        output_df = pd.DataFrame(columns=['InputID', 'SequenceNumber', 'AgentName', 'Output'])
        sequence_number = 1

        try:
            async for content in self.agent_group_chat.invoke():
                output_df = self.data_logger.add_output_record(
                    output_df,
                    input_id,
                    sequence_number,
                    content.name,
                    content.content
                )
                sequence_number += 1

                # Track tokens
                if hasattr(content, 'metadata'):
                    usage = content.metadata.get("usage")
                    if usage:
                        self.token_tracker.update_agent_tokens(
                            content.name,
                            usage.prompt_tokens if hasattr(usage, 'prompt_tokens') else 0,
                            usage.completion_tokens if hasattr(usage, 'completion_tokens') else 0
                        )

                # Reduce history if too many tokens
                summary = self.token_tracker.get_summary()
                if summary['total_tokens'] > 7000:
                    await self.agent_group_chat.reduce_history()

                print(f"==={content.name or '*'}===: '{content.content}\n'")

                # Check if conversation is complete
                if ("This conversation is complete." in content.content and 
                    content.name == "PromptAgent"):
                    self.agent_group_chat.is_complete = True
                    break

        except ServiceResponseException as e:
            if "tokens_limit_reached" in str(e):
                print("Conversation ended: Token limit reached")
                output_df = self.data_logger.add_output_record(
                    output_df, input_id, sequence_number, "System",
                    "Conversation ended due to token limit."
                )
        except FunctionExecutionException as e:
            print("Error: Rate limit exceeded. Please wait 24 hours before retrying.")
            output_df = self.data_logger.add_output_record(
                output_df, input_id, sequence_number, "System",
                "Rate limit exceeded."
            )
        except json.JSONDecodeError as e:
            print("Error: Failed to parse response. Please restart and try again.")
            output_df = self.data_logger.add_output_record(
                output_df, input_id, sequence_number, "System",
                "JSON parsing error."
            )

        return output_df

    async def main(self) -> None:
        """Main execution function for KhetSetu."""
        # Get next input ID
        input_id = self.data_logger.get_next_input_id()

        # Get user input
        user_input = input("User Prompt: ")
        self.data_logger.log_input(input_id, user_input)

        # Detect user language
        detected_code, user_language = detect_user_language(user_input)
        language_context = (
            f"The user's language is {user_language}. "
            f"Please respond appropriately in that language."
        )

        # Add context messages
        await self.agent_group_chat.add_chat_message(ChatMessageContent(
            role=AuthorRole.USER,
            content=language_context
        ))

        await self.agent_group_chat.add_chat_message(ChatMessageContent(
            role=AuthorRole.USER,
            content=user_input
        ))

        # Create parse agent for extraction
        from src.agents import ParseAgent
        parse_agent = ParseAgent.create(self.kernel)

        # Parse user input
        parsed = await self.parse_user_input(parse_agent, user_input)

        if parsed is None:
            print("Error: Could not parse user input.")
            return

        user_intent = parsed.get("user_intent")
        location = parsed.get("location")
        start_year = parsed.get("start_year", 2015)
        end_year = parsed.get("end_year", 2025)
        forecast_date = parsed.get("forecast_date", 0)

        # Request missing values
        while user_intent not in ["get_solution", "weather_forecast", "weather_history"]:
            user_intent = await self.request_missing_value(
                'intent',
                parse_agent,
                lambda p: p.get("user_intent")
            )
            if user_intent:
                print(f"Updated user intent: {user_intent}")

        while not location:
            location = await self.request_missing_value(
                'location',
                parse_agent,
                lambda p: p.get("location")
            )
            if location:
                print(f"Updated location: {location}")

        # Get weather data
        historical_summary, forecast_summary = await self.get_weather_context(
            location, start_year, end_year, forecast_date
        )

        # Build context for agents
        context = (
            f"The location is {location}. The user intent is {user_intent}. "
            f"The user's question is {user_input}. The user's language is {user_language}. "
            f"The weather forecast is {forecast_summary} and the weather history is {historical_summary}"
        )

        await self.agent_group_chat.add_chat_message(ChatMessageContent(
            role=AuthorRole.USER,
            content=context
        ))

        # Run agent group chat
        output_df = await self.run_agent_group_chat(
            user_intent, location, user_language, context, input_id
        )

        # Log outputs
        if not output_df.empty:
            self.data_logger.log_output(output_df)

        # Calculate and log costs
        summary = self.token_tracker.get_summary()
        total_cost = self.cost_calculator.calculate_cost(
            summary['total_prompt_tokens'],
            summary['total_completion_tokens']
        )

        self.data_logger.log_token_usage(
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

        # Print cost summary
        print(f"\n{'='*50}")
        print(f"Cost Summary for Input #{input_id}")
        print(f"{'='*50}")
        print(f"Prompt tokens: {summary['total_prompt_tokens']:,}")
        print(f"Completion tokens: {summary['total_completion_tokens']:,}")
        print(f"Total tokens: {summary['total_tokens']:,}")
        print(f"Total cost: ${total_cost:.6f}")
        print(f"{'='*50}\n")

    async def process_web_query(self, user_input: str) -> dict:
        """
        Process a user query and return structured response for web API.
        
        Args:
            user_input: The user's agricultural query
            
        Returns:
            Dictionary with agent outputs, final answer, and token summary
        """
        self.agent_outputs = []
        self.token_tracker = TokenTracker()  # Reset token tracker
        
        try:
            # Detect language - returns tuple (code, language_name)
            detected_code, user_language = detect_user_language(user_input)
            
            # Add language context
            language_context = (
                f"The user's language is {user_language}. "
                f"Please respond appropriately in that language."
            )
            
            await self.agent_group_chat.add_chat_message(ChatMessageContent(
                role=AuthorRole.USER,
                content=language_context
            ))
            
            await self.agent_group_chat.add_chat_message(ChatMessageContent(
                role=AuthorRole.USER,
                content=user_input
            ))
            
            # Get parse agent
            from src.agents import ParseAgent
            parse_agent = ParseAgent.create(self.kernel)
            
            # Parse user input
            parsed_data = await self.parse_user_input(parse_agent, user_input)
            if not parsed_data:
                # Return partial results if we have any agent outputs
                summary = self.token_tracker.get_summary()
                total_cost = self.cost_calculator.calculate_cost(
                    summary['total_prompt_tokens'],
                    summary['total_completion_tokens']
                )
                return {
                    "status": "error",
                    "message": "Failed to parse input",
                    "agents": self.agent_outputs,
                    "final_answer": "Sorry, I couldn't understand your query. Please try rephrasing.",
                    "token_summary": {
                        "total_prompt_tokens": summary['total_prompt_tokens'],
                        "total_completion_tokens": summary['total_completion_tokens'],
                        "total_cost_usd": round(total_cost, 6)
                    }
                }
            
            user_intent = parsed_data.get("user_intent", "weather_forecast")
            location = parsed_data.get("location", "Unknown")
            start_year = parsed_data.get("start_year", 2015)
            end_year = parsed_data.get("end_year", 2025)
            forecast_date = parsed_data.get("forecast_date", 0)
            
            # Get weather data
            historical_summary, forecast_summary = await self.get_weather_context(
                location, start_year, end_year, forecast_date
            )
            
            # Build context
            context = (
                f"The location is {location}. The user intent is {user_intent}. "
                f"The user's question is {user_input}. The user's language is {user_language}. "
                f"The weather forecast is {forecast_summary} and the weather history is {historical_summary}"
            )
            
            await self.agent_group_chat.add_chat_message(ChatMessageContent(
                role=AuthorRole.USER,
                content=context
            ))
            
            # Run agent group chat and capture outputs
            final_answer = None
            try:
                async for response in self.agent_group_chat.invoke():
                    agent_name = response.name if hasattr(response, 'name') else "Unknown"
                    output = response.content if hasattr(response, 'content') else str(response)
                    
                    # Track tokens if available
                    if hasattr(response, "metadata"):
                        usage = response.metadata.get("usage")
                        if usage:
                            prompt_tokens = usage.prompt_tokens if hasattr(usage, 'prompt_tokens') else 0
                            completion_tokens = usage.completion_tokens if hasattr(usage, 'completion_tokens') else 0
                            self.token_tracker.update_agent_tokens(agent_name, prompt_tokens, completion_tokens)
                            
                            self.agent_outputs.append({
                                "name": agent_name,
                                "status": "complete",
                                "output": output,
                                "tokens": {
                                    "prompt_tokens": prompt_tokens,
                                    "completion_tokens": completion_tokens
                                }
                            })
                        else:
                            self.agent_outputs.append({
                                "name": agent_name,
                                "status": "complete",
                                "output": output,
                                "tokens": {"prompt_tokens": 0, "completion_tokens": 0}
                            })
                    else:
                        self.agent_outputs.append({
                            "name": agent_name,
                            "status": "complete",
                            "output": output,
                            "tokens": {"prompt_tokens": 0, "completion_tokens": 0}
                        })
                    
                    # Capture the final answer (last PromptAgent output)
                    if agent_name == "PromptAgent":
                        final_answer = output
                    
                    # Check for completion signal
                    if "This conversation is complete." in output and agent_name == "PromptAgent":
                        break
                        
            except Exception as invoke_error:
                # Log but continue to return partial results
                print(f"Error during agent invocation: {invoke_error}")
                import traceback
                traceback.print_exc()
            
            # Extract final answer from the last PromptAgent response
            # Remove the completion marker if present
            if final_answer and "This conversation is complete." in final_answer:
                final_answer = final_answer.replace("This conversation is complete.", "").strip()
            
            # If no final answer, try to get the last approved response
            if not final_answer and self.agent_outputs:
                # Look for the last agent output (excluding ReviewerAgent)
                for agent_output in reversed(self.agent_outputs):
                    if agent_output["name"] not in ["ReviewerAgent", "ParseAgent"]:
                        final_answer = agent_output["output"]
                        if "This conversation is complete." in final_answer:
                            final_answer = final_answer.replace("This conversation is complete.", "").strip()
                        break
            
            # Calculate summary
            summary = self.token_tracker.get_summary()
            total_cost = self.cost_calculator.calculate_cost(
                summary['total_prompt_tokens'],
                summary['total_completion_tokens']
            )
            
            return {
                "status": "success",
                "agents": self.agent_outputs,
                "final_answer": final_answer or "No response generated",
                "token_summary": {
                    "total_prompt_tokens": summary['total_prompt_tokens'],
                    "total_completion_tokens": summary['total_completion_tokens'],
                    "total_cost_usd": round(total_cost, 6)
                }
            }
            
        except Exception as e:
            print(f"Error in process_web_query: {e}")
            import traceback
            traceback.print_exc()
            
            # Calculate summary even on error
            summary = self.token_tracker.get_summary()
            total_cost = self.cost_calculator.calculate_cost(
                summary['total_prompt_tokens'],
                summary['total_completion_tokens']
            )
            
            return {
                "status": "error",
                "message": str(e),
                "agents": self.agent_outputs,
                "final_answer": f"Sorry, I encountered an error: {str(e)}",
                "token_summary": {
                    "total_prompt_tokens": summary['total_prompt_tokens'],
                    "total_completion_tokens": summary['total_completion_tokens'],
                    "total_cost_usd": round(total_cost, 6)
                }
            }


def main():
    """Entry point for the application."""
    try:
        khet_setu = KhetSetu()
        asyncio.run(khet_setu.main())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    except Exception as e:
        print(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
