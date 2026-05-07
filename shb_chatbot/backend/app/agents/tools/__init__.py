"""Agent tools module.

This module contains utility functions that can be used as agent tools.
Tools are registered in the agent definition using @agent.tool decorator.
"""

from app.agents.tools.datetime_tool import get_current_datetime
from app.agents.tools.financial_analysis_tools import (
    analyze_macro_economy,
    analyze_shb_risks,
    forecast_shb_price,
)
from app.agents.tools.shb_deep_analysis_tool import analyze_shb_stock_deep
from app.agents.tools.shb_stock_tool import analyze_shb_stock

__all__ = [
    "analyze_macro_economy",
    "analyze_shb_risks",
    "analyze_shb_stock",
    "analyze_shb_stock_deep",
    "forecast_shb_price",
    "get_current_datetime",
]
