"""SHB Deep Stock analysis tool for agents."""

from typing import Any


def analyze_shb_stock_deep() -> dict[str, Any]:
    """Provide deep financial analysis for SHB (Ngân hàng TMCP Sài Gòn - Hà Nội).

    Includes valuation metrics, growth potential, and strategic advantages
    based on the 9M2025 financial results.

    Returns:
        A dictionary containing deep analysis data.
    """
    return {
        "stock_code": "SHB",
        "financial_health_9M2025": {
            "pbt_vnd": "12.307 tỷ (+36% YoY)",
            "npl_ratio": "3.06% (Vượt ngưỡng tâm lý 3%)",
            "llr_ratio": "56.91% (Bộ đệm dự phòng mỏng)",
            "nim": "3.94% (Cải thiện so với 2024 nhưng đang chịu áp lực COF)"
        },
        "valuation": {
            "p_b_ratio": "0.75x (Tại thị giá 16.650 VND, vùng Deep Discount)",
            "bvps_est": "22.000 - 23.000 VND",
            "dividend_plan": "18% cho 2024-2025 (Tiền mặt và cổ phiếu)"
        },
        "growth_drivers": [
            "Thương vụ M&A SHBFinance: Hoàn tất bán 50% vốn còn lại, mang về 1.300-1.500 tỷ thặng dư.",
            "Lợi thế hệ sinh thái: Mối quan hệ với T&T Group hỗ trợ đầu ra tín dụng lãi suất cao (YOA 8.7%).",
            "Kỳ vọng phục hồi BĐS: SHB có độ nhạy (Beta) cao, sẽ hưởng lợi lớn khi thị trường BĐS ấm lại vào cuối 2025."
        ],
        "risks": [
            "Chất lượng tài sản suy giảm: Nợ nhóm 2 đang tăng trở lại.",
            "Rủi ro lãi giả - lỗ thật: Tỷ lệ lãi dự thu cao, dòng tiền thực (Cash flow) yếu.",
            "Áp lực vốn: Cần gia tăng Vốn cấp 2 để đảm bảo hệ số CAR theo Basel III."
        ],
        "investment_thesis": (
            "SHB là một cổ phiếu 'High Beta Play'. Khuyến nghị MUA GIAO DỊCH (Trading Buy) cho mục tiêu ngắn hạn. "
            "Dù chất lượng tài sản nội tại còn lo ngại, nhưng các sự kiện tài chính (Corporate Actions) và "
            "định giá cực rẻ (P/B 0.75x) tạo ra biên an toàn cho chiến lược Trading dựa trên tin tức."
        )
    }
