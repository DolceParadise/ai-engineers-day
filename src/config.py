"""Configuration module for kernel and cost calculations."""

import os
from openai import AsyncOpenAI
from semantic_kernel.kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from kernel_functions import get_NASA_data, get_adaptations, get_forecast, analyze_crop_image


class KernelConfig:
    """Configuration and setup for Semantic Kernel."""

    @staticmethod
    def create_kernel() -> Kernel:
        """
        Create and configure a Semantic Kernel instance with OpenAI chat completion.
        
        Returns:
            Configured Kernel instance with climate tools
        """
        kernel = Kernel()

        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        kernel.add_service(
            OpenAIChatCompletion(
                ai_model_id="gpt-4o",
                async_client=client,
            )
        )

        # Add climate tools
        kernel.add_function(
            plugin_name="climate_tools",
            function_name="get_NASA_data",
            function=get_NASA_data
        )

        kernel.add_function(
            plugin_name="climate_tools",
            function_name="get_forecast",
            function=get_forecast
        )

        kernel.add_function(
            plugin_name="climate_tools",
            function_name="get_adaptations",
            function=get_adaptations
        )

        # Add vision tools
        kernel.add_function(
            plugin_name="vision_tools",
            function_name="analyze_crop_image",
            function=analyze_crop_image
        )

        return kernel


class CostCalculator:
    """Calculate costs for OpenAI API usage."""

    @staticmethod
    def calculate_cost(prompt_tokens: int, completion_tokens: int) -> float:
        """
        Calculate cost for GPT-4o usage.
        
        Pricing:
        - Input: $2.50 per 1M tokens
        - Output: $10.00 per 1M tokens
        
        Args:
            prompt_tokens: Number of prompt tokens used
            completion_tokens: Number of completion tokens generated
            
        Returns:
            Total cost in USD
        """
        input_cost = (prompt_tokens / 1_000_000) * 2.50
        output_cost = (completion_tokens / 1_000_000) * 10.00
        return input_cost + output_cost
