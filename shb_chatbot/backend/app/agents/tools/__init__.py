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
from app.agents.tools.shb_report_search import search_shb_report
from app.agents.tools.shb_stock_tool import analyze_shb_stock
from app.agents.tools.vnstock_tool import get_realtime_stock_data

__all__ = [
    "analyze_macro_economy",
    "analyze_shb_risks",
    "analyze_shb_stock",
    "analyze_shb_stock_deep",
    "forecast_shb_price",
    "get_current_datetime",
    "search_shb_report",
    "get_realtime_stock_data",
]
