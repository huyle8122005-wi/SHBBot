"""SHB Stock analysis tool for agents."""

from typing import Any


def analyze_shb_stock() -> dict[str, Any]:
    """Analyze SHB stock (Ngân hàng TMCP Sài Gòn - Hà Nội).

    This tool provides current price, technical analysis indicators,
    and market sentiment for SHB stock code.

    Returns:
        A dictionary containing stock analysis data.
    """
    # In a real application, this would fetch data from a financial API
    current_price = 12450  # SHB price in VND
    change_pct = 1.25      # Mock percentage change

    # Mock technical indicators
    rsi = 58.4             # Relative Strength Index
    moving_average_20 = 12100
    moving_average_50 = 11850

    # Trend assessment
    trend = "Bullish" if current_price > moving_average_50 else "Sideways"

    # Mock sentiment and news summary
    news = [
        "SHB reports strong Q1 profit growth.",
        "Positive credit growth targets for the year.",
        "Foreign investors increasing stake in SHB."
    ]

    return {
        "stock_code": "SHB",
        "company_name": "Ngân hàng TMCP Sài Gòn - Hà Nội",
        "current_price_vnd": current_price,
        "change_percentage": change_pct,
        "technical_analysis": {
            "rsi_14": rsi,
            "ma_20": moving_average_20,
            "ma_50": moving_average_50,
            "trend": trend,
            "status": "Neutral to Positive" if 40 < rsi < 70 else "Overbought/Oversold"
        },
        "market_sentiment": "Positive",
        "latest_news_highlights": news,
        "analysis_summary": (
            f"SHB stock is currently trading at {current_price:,} VND, showing a {change_pct}% increase today. "
            f"Technical indicators suggest a {trend.lower()} trend with an RSI of {rsi}, which is in the healthy zone. "
            "Market sentiment remains positive due to strong fundamental growth and attractive valuation."
        )
    }
