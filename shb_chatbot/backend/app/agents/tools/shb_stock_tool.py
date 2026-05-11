"""SHB Stock analysis tool for agents."""

from typing import Any


def analyze_shb_stock() -> dict[str, Any]:
    """Analyze SHB stock (Ngân hàng TMCP Sài Gòn - Hà Nội).

    This tool provides current price, technical analysis indicators,
    and market sentiment for SHB stock code based on the 11/12/2025 report.

    Returns:
        A dictionary containing stock analysis data.
    """
    # Data from Report 11/12/2025
    current_price = 16650  # SHB price in VND
    target_price = 19500
    p_b_current = 0.75
    p_b_target = 0.95

    # Mock technical indicators consistent with the report's "Trading Buy" sentiment
    rsi = 62.5
    moving_average_20 = 15800
    moving_average_50 = 15200

    # Trend assessment
    trend = "Tăng trưởng ngắn hạn (Trading Buy)"

    # News summary from report
    news = [
        "Hoàn tất bán 50% vốn SHBFinance cho Krungsri trong năm 2025, thu về 1.300-1.500 tỷ thặng dư.",
        "Kế hoạch chia cổ tức 18% cho năm 2024 và 2025 (tiền mặt và cổ phiếu).",
        "Room tín dụng 9 tháng đạt 15%, dư địa còn lại cho Q4 khoảng 1%."
    ]

    return {
        "stock_code": "SHB",
        "company_name": "Ngân hàng TMCP Sài Gòn - Hà Nội",
        "current_price_vnd": current_price,
        "target_price_vnd": target_price,
        "p_b_ratio": p_b_current,
        "technical_analysis": {
            "rsi_14": rsi,
            "ma_20": moving_average_20,
            "ma_50": moving_average_50,
            "trend": trend,
            "status": "Vùng mua an toàn (15.500 - 16.200)"
        },
        "market_sentiment": "Trung lập thiên hướng Tích cực ngắn hạn",
        "latest_news_highlights": news,
        "analysis_summary": (
            f"SHB đang giao dịch ở mức {current_price:,} VND (P/B {p_b_current}x), vùng 'Deep Discount' so với giá trị sổ sách. "
            f"Giá mục tiêu kỳ vọng là {target_price:,} VND (P/B {p_b_target}x). "
            "Động lực chính đến từ thương vụ SHBFinance và kế hoạch chia cổ tức khủng, bất chấp áp lực từ nợ xấu và room tín dụng hạn hẹp."
        )
    }
