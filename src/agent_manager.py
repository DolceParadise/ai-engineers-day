"""Agent Manager - Orchestrates multi-agent interactions."""

from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.agents.strategies import (
    KernelFunctionSelectionStrategy,
    KernelFunctionTerminationStrategy
)
from semantic_kernel.functions import KernelFunctionFromPrompt
from semantic_kernel.prompt_template.prompt_template_config import PromptTemplateConfig
from semantic_kernel.kernel import Kernel
from src.agents import (
    PromptAgent,
    ParseAgent,
    ForecastAgent,
    WeatherHistoryAgent,
    SolutionAgent,
    ReviewerAgent,
)


class AgentManager:
    """
    Manages agent interactions and orchestrates the multi-agent conversation flow.
    
    Handles agent selection, conversation termination, and chat management.
    """

    @staticmethod
    def create_agent_group_chat(kernel: Kernel) -> AgentGroupChat:
        """
        Create an AgentGroupChat with all agents and strategies.
        
        Args:
            kernel: Semantic Kernel instance with configured services
            
        Returns:
            Configured AgentGroupChat instance
        """
        # Create all agents
        prompt_agent = PromptAgent.create(kernel)
        parse_agent = ParseAgent.create(kernel)
        forecast_agent = ForecastAgent.create(kernel)
        history_agent = WeatherHistoryAgent.create(kernel)
        solution_agent = SolutionAgent.create(kernel)
        reviewer_agent = ReviewerAgent.create(kernel)

        # Create termination strategy
        termination_function = KernelFunctionFromPrompt(
            function_name="termination",
            prompt_template_config=PromptTemplateConfig(
                template="""
        Determine if the conversation is complete.

        Criteria:
        1. The SolutionReviewerAgent has stated explicitly "This solution is completely approved." and has no further recommendations or concerns.
        Do not count messages that include phrases like "not approved," "needs improvement," "almost approved," or "would be approved if...".
        2. The most recent message must be from PromptAgent. The PromptAgent must have said "This conversation is complete."

        If both conditions are met, return: yes
        Otherwise, return: no

        History:
        {{$history}}
        """,
                allow_dangerously_set_content=True
            )
        )

        # Create selection strategy
        selection_function = KernelFunctionFromPrompt(
            function_name="selection",
            prompt_template_config=PromptTemplateConfig(
                template="""
        Determine which participant takes the next turn in a conversation based on the most recent messages in the conversation history.
        State only the name of the participant to take the next turn.
        If the conversation is complete, respond with exactly "none".
        No participant should take more than one turn in a row.

        Always follow these rules, and ensure the conversation includes at least 4 turns before it can end:

        General Flow:
        - After the user input, PromptAgent always speaks first.
        - Another agent MUST speak after PromptAgent speaks first.
        When choosing the agent to speak next, follow one of the 3 branches below depending on user intent.

        1. If the user's intent is to get a weather forecast:
        - After PromptAgent replies, ForecastAgent responds.
        - After ForecastAgent replies, ReviewerAgent provides feedback.
        - If the ReviewerAgent says "This solution is completely approved.", PromptAgent responds and ends the conversation.
        - Otherwise, ForecastAgent replies again with revisions, and ReviewerAgent must review again.
        - Repeat this cycle until ReviewerAgent approves the solution.
        - Then PromptAgent replies with "This conversation is complete.", and only then respond with "none".

        2. If the user's intent is to get weather history:
        - Same as above, but use WeatherHistoryAgent instead of ForecastAgent.

        3. If the user's intent is to get a solution:
        - Same pattern using SolutionAgent instead of ForecastAgent.

        Additional Enforcement Rules:
        1. Choose only from these participants:
        - PromptAgent
        - WeatherHistoryAgent (only choose this if the user's intent is weather history)
        - ForecastAgent (only choose this if the user's intent is weather forecast)
        - SolutionAgent (only choose this if the user's intent is to get a solution to a problem)
        - ReviewerAgent

        2. NEVER select the same agent twice in a row.
        3. The conversation only ends when PromptAgent replies with "This conversation is complete.".
        4. Do not return "none" unless the very last speaker was PromptAgent and they explicitly said "This conversation is complete."
        5. Do NOT call or execute any kernel functions.
        6. Only output the name of the next agent or "none".

        History:
        {{{{ $history }}}}
        """,
                allow_dangerously_set_content=True
            )
        )

        # Create and configure AgentGroupChat
        agent_group_chat = AgentGroupChat(
            agents=[
                prompt_agent,
                parse_agent,
                forecast_agent,
                history_agent,
                solution_agent,
                reviewer_agent
            ],
            termination_strategy=KernelFunctionTerminationStrategy(
                agents=[reviewer_agent],
                function=termination_function,
                kernel=kernel,
                result_parser=lambda result: str(result.value).strip().lower() == "yes",
                history_variable_name="history",
                maximum_iterations=6,
            ),
            selection_strategy=KernelFunctionSelectionStrategy(
                function=selection_function,
                kernel=kernel,
                result_parser=lambda result: (
                    None if str(result.value).strip().lower() == "none" else
                    str(result.value[0]) if result.value and len(result.value) > 0 else None
                ),
                agent_variable_name="agents",
                history_variable_name="history",
            )
        )

        return agent_group_chat
