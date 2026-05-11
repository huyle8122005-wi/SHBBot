import pytest

from app.agents.tools.financial_analysis_tools import analyze_shb_risks, forecast_shb_price
from app.agents.tools.shb_deep_analysis_tool import analyze_shb_stock_deep
from app.agents.tools.shb_report_search import search_shb_report
from app.agents.tools.shb_stock_tool import analyze_shb_stock


def test_analyze_shb_stock_real_data():
    """Verify shb_stock_tool returns updated 2025 data."""
    data = analyze_shb_stock()
    assert data["stock_code"] == "SHB"
    assert data["current_price_vnd"] == 16650
    assert data["target_price_vnd"] == 19500
    assert "SHBFinance" in data["latest_news_highlights"][0]

def test_analyze_shb_stock_deep_real_data():
    """Verify shb_deep_analysis_tool returns updated 9M2025 data."""
    data = analyze_shb_stock_deep()
    assert data["financial_health_9M2025"]["pbt_vnd"] == "12.307 tỷ (+36% YoY)"
    assert data["financial_health_9M2025"]["npl_ratio"] == "3.06% (Vượt ngưỡng tâm lý 3%)"
    assert "SHBFinance" in data["growth_drivers"][0]

def test_forecast_shb_price_real_data():
    """Verify forecast tool returns updated targets."""
    data = forecast_shb_price()
    assert data["target_price"] == "19.500 VND (P/B ~0.95x)"
    assert data["buy_zone"] == "15.500 - 16.200 VND (P/B ~0.75x)"

def test_analyze_shb_risks_real_data():
    """Verify risk tool returns updated warnings."""
    data = analyze_shb_risks()
    assert "3.06%" in data["asset_quality"]
    assert "LLR < 60%" in data["provision_buffer"]

def test_search_shb_report_integration():
    """Verify PDF search tool can find content in the actual file."""
    # Search for a unique term from the PDF we OCR'd
    result = search_shb_report("Krungsri")
    assert "SHBFinance" in result
    assert "Krungsri" in result
    assert "Page" in result

@pytest.mark.anyio
async def test_assistant_agent_tool_registration():
    """Verify AssistantAgent has the new search tool registered."""
    from app.agents.assistant import AssistantAgent
    agent_wrapper = AssistantAgent()
    agent = agent_wrapper.agent

    # Check the synchronous tools dictionary
    tool_names = list(agent._function_toolset.tools.keys())

    assert "search_shb_report_tool" in tool_names
    assert "shb_stock_analysis" in tool_names
