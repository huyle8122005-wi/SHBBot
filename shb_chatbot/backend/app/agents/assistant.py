"""Assistant agent with PydanticAI.

The main conversational agent that can be extended with custom tools.
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from pydantic_ai import Agent, RunContext
from pydantic_ai.capabilities import WebFetch, WebSearch
from pydantic_ai.messages import (
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    TextPart,
    UserPromptPart,
)
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.models.openai import OpenAIResponsesModel
from pydantic_ai.providers.google import GoogleProvider
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.settings import ModelSettings

from app.agents.prompts import DEFAULT_SYSTEM_PROMPT
from app.agents.tools import (
    analyze_macro_economy,
    analyze_shb_risks,
    analyze_shb_stock,
    analyze_shb_stock_deep,
    forecast_shb_price,
    get_current_datetime,
)
from app.agents.tools.vnstock_tool import (
    compare_banking_stocks,
    get_realtime_stock_data,
    screen_shb_peers,
)
from app.agents.tools.web_search_tool import get_latest_shb_interest_rates, search_web
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class Deps:
    """Dependencies for the assistant agent.

    These are passed to tools via RunContext.
    """

    user_id: str | None = None
    user_name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class AssistantAgent:
    """Assistant agent wrapper for conversational AI.

    Encapsulates agent creation and execution with tool support.
    """

    def __init__(
        self,
        model_name: str | None = None,
        temperature: float | None = None,
        system_prompt: str | None = None,
    ):
        self.model_name = model_name or settings.AI_MODEL
        self.temperature = temperature or settings.AI_TEMPERATURE
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        self._agent: Agent[Deps, str] | None = None

    def _create_agent(self) -> Agent[Deps, str]:
        """Create and configure the PydanticAI agent."""
        # Force Gemini if OpenAI key is missing but Gemini key is present
        is_google = "gemini" in self.model_name.lower() or (
            not settings.OPENAI_API_KEY and settings.GEMINI_API_KEY
        )

        if is_google:
            actual_model = (
                self.model_name if "gemini" in self.model_name.lower() else settings.AI_MODEL
            )
            model = GoogleModel(
                actual_model, provider=GoogleProvider(api_key=settings.GEMINI_API_KEY)
            )
        else:
            model = OpenAIResponsesModel(
                self.model_name,
                provider=OpenAIProvider(api_key=settings.OPENAI_API_KEY),
            )

        # Google does not support mixing built-in tools (capabilities) and function tools
        capabilities: list[Any] = []
        if not is_google:
            capabilities = [
                WebSearch(),
                WebFetch(),
            ]

        # Use the customized system prompt
        from app.agents.prompts import DEFAULT_SYSTEM_PROMPT

        agent = Agent[Deps, str](
            model=model,
            model_settings=ModelSettings(temperature=self.temperature),
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            capabilities=capabilities,
        )

        self._register_tools(agent)

        return agent

    def _register_tools(self, agent: Agent[Deps, str]) -> None:
        """Register all tools on the agent."""

        @agent.tool
        async def current_datetime(ctx: RunContext[Deps]) -> str:
            """Get the current date and time.

            Use this tool when you need to know the current date or time.
            """
            return get_current_datetime()

        @agent.tool
        async def shb_stock_analysis(ctx: RunContext[Deps]) -> dict[str, Any]:
            """Analyze SHB stock (Ngân hàng TMCP Sài Gòn - Hà Nội).

            Use this tool when the user asks about SHB stock price, technical analysis, or market sentiment.
            """
            return analyze_shb_stock()

        @agent.tool
        async def shb_deep_analysis(ctx: RunContext[Deps]) -> dict[str, Any]:
            """Provide deep financial analysis for SHB investment.

            Use this tool for complex questions about SHB's valuation, growth drivers, competitive advantages, or long-term investment potential.
            """
            return analyze_shb_stock_deep()

        @agent.tool
        async def macro_economic_analysis(ctx: RunContext[Deps]) -> dict[str, Any]:
            """Analyze the macro-economic environment in Vietnam.

            Use this tool to provide context on how the overall economy affects the banking sector and SHB.
            """
            return analyze_macro_economy()

        @agent.tool
        async def shb_price_forecast(ctx: RunContext[Deps]) -> dict[str, Any]:
            """Provide price forecasting for SHB stock.

            Use this tool when users ask for price targets or future projections for SHB stock.
            """
            return forecast_shb_price()

        @agent.tool
        async def shb_risk_assessment(ctx: RunContext[Deps]) -> dict[str, Any]:
            """Analyze potential investment risks for SHB.

            Use this tool to provide a balanced view of the risks and mitigation strategies for investing in SHB.
            """
            return analyze_shb_risks()

        @agent.tool
        async def search_shb_report_tool(ctx: RunContext[Deps], query: str) -> str:
            """Search for specific information in the SHB 2025 analysis report PDF.

            Use this tool to get in-depth data, tables, or specific details from the official SHB report.
            """
            from app.agents.tools.shb_report_search import search_shb_report
            return search_shb_report(query)

        @agent.tool
        async def real_time_market_data(ctx: RunContext[Deps], symbol: str) -> dict[str, Any]:
            """Get real-time market data for a stock using VNStock API.

            Use this tool when the user asks for the current price or real-time financial metrics.
            """
            return get_realtime_stock_data(symbol)

        @agent.tool
        async def banking_peers(ctx: RunContext[Deps]) -> list[str]:
            """Get a list of common banking peers for SHB comparison.

            Use this tool to find which other banks (like TCB, ACB, VPB) to compare SHB with.
            """
            return screen_shb_peers()

        @agent.tool
        async def compare_stocks(ctx: RunContext[Deps], symbols: list[str]) -> list[dict[str, Any]]:
            """Compare multiple stocks (especially banking stocks).

            Use this tool when the user asks to compare SHB with other banks like TCB, ACB, VPB, etc.
            """
            return compare_banking_stocks(symbols)

        @agent.tool
        async def web_search(ctx: RunContext[Deps], query: str) -> list[dict[str, Any]]:
            """Search the web for general information, news, or latest banking rates.

            Use this tool when the information is not available in the SHB report or VNStock API.
            """
            return search_web(query)

        @agent.tool
        async def get_shb_interest_rates(ctx: RunContext[Deps]) -> str:
            """Get the latest interest rates for SHB bank.

            Use this tool specifically when the user asks about SHB's current interest rates.
            """
            return get_latest_shb_interest_rates()

    @property
    def agent(self) -> Agent[Deps, str]:
        """Get or create the agent instance."""
        if self._agent is None:
            self._agent = self._create_agent()
        return self._agent

    async def run(
        self,
        user_input: str,
        history: list[dict[str, str]] | None = None,
        deps: Deps | None = None,
    ) -> tuple[str, list[Any], Deps]:
        """Run agent and return the output along with tool call events.

        Args:
            user_input: User's message.
            history: Conversation history as list of {"role": "...", "content": "..."}.
            deps: Optional dependencies. If not provided, a new Deps will be created.

        Returns:
            Tuple of (output_text, tool_events, deps).
        """
        model_history: list[ModelRequest | ModelResponse] = []

        for msg in history or []:
            if msg["role"] == "user":
                model_history.append(ModelRequest(parts=[UserPromptPart(content=msg["content"])]))
            elif msg["role"] == "assistant":
                model_history.append(ModelResponse(parts=[TextPart(content=msg["content"])]))
            elif msg["role"] == "system":
                model_history.append(ModelRequest(parts=[SystemPromptPart(content=msg["content"])]))

        agent_deps = deps if deps is not None else Deps()

        logger.info(f"Running agent with user input: {user_input[:100]}...")
        result = await self.agent.run(user_input, deps=agent_deps, message_history=model_history)

        tool_events: list[Any] = []
        for message in result.all_messages():
            if hasattr(message, "parts"):
                for part in message.parts:
                    if hasattr(part, "tool_name"):
                        tool_events.append(part)

        logger.info(f"Agent run complete. Output length: {len(result.output)} chars")

        return result.output, tool_events, agent_deps

    async def iter(
        self,
        user_input: str,
        history: list[dict[str, str]] | None = None,
        deps: Deps | None = None,
    ) -> Any:
        """Stream agent execution with full event access.

        Args:
            user_input: User's message.
            history: Conversation history.
            deps: Optional dependencies.

        Yields:
            Agent events for streaming responses.
        """
        model_history: list[ModelRequest | ModelResponse] = []

        for msg in history or []:
            if msg["role"] == "user":
                model_history.append(ModelRequest(parts=[UserPromptPart(content=msg["content"])]))
            elif msg["role"] == "assistant":
                model_history.append(ModelResponse(parts=[TextPart(content=msg["content"])]))
            elif msg["role"] == "system":
                model_history.append(ModelRequest(parts=[SystemPromptPart(content=msg["content"])]))

        agent_deps = deps if deps is not None else Deps()

        async with self.agent.iter(
            user_input,
            deps=agent_deps,
            message_history=model_history,
        ) as run:
            async for event in run:
                yield event


def get_agent(model_name: str | None = None) -> AssistantAgent:
    """Factory function to create an AssistantAgent.

    Args:
        model_name: Override the default AI model.

    Returns:
        Configured AssistantAgent instance.
    """
    return AssistantAgent(model_name=model_name)


async def run_agent(
    user_input: str,
    history: list[dict[str, str]],
    deps: Deps | None = None,
) -> tuple[str, list[Any], Deps]:
    """Run agent and return the output along with tool call events.

    This is a convenience function for backwards compatibility.

    Args:
        user_input: User's message.
        history: Conversation history.
        deps: Optional dependencies.

    Returns:
        Tuple of (output_text, tool_events, deps).
    """
    agent = get_agent()
    return await agent.run(user_input, history, deps)
