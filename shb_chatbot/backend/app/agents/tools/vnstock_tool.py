"""VNStock integration tool for real-time market data."""

import logging
from typing import Any
import pandas as pd

from vnstock.api.financial import Finance
from vnstock.api.quote import Quote
from vnstock import register_user
from app.core.config import settings

logger = logging.getLogger(__name__)

# Register VNStock API key globally if provided in settings
if settings.VNSTOCK_API_KEY:
    try:
        register_user(api_key=settings.VNSTOCK_API_KEY)
        logger.info("VNStock API key registered successfully.")
    except Exception as e:
        logger.warning(f"Could not register VNStock API key: {e}")

def calculate_rsi(data: pd.Series, window: int = 14) -> float:
    """Calculate Relative Strength Index (RSI)."""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])

def get_realtime_stock_data(symbol: str) -> dict[str, Any]:
    """Fetch real-time stock data, valuation ratios, and technicals using vnstock free tier.

    Args:
        symbol: The stock ticker (e.g., 'SHB').

    Returns:
        A dictionary with comprehensive real-time and financial data.
    """
    try:
        # 1. Price and Technicals
        q = Quote(symbol=symbol, source='vci')
        # Get enough history for RSI (14) and MA (20, 50)
        df = q.history(start='2025-01-01')

        if df is None or df.empty:
            return {"error": f"No market data found for {symbol}"}

        latest_row = df.iloc[-1]
        close_prices = df['close']

        ma20 = float(close_prices.rolling(window=20).mean().iloc[-1]) if len(close_prices) >= 20 else None
        ma50 = float(close_prices.rolling(window=50).mean().iloc[-1]) if len(close_prices) >= 50 else None
        rsi = calculate_rsi(close_prices) if len(close_prices) >= 15 else None

        # 2. Financials (Income Statement & Balance Sheet)
        f = Finance(symbol=symbol, source='vci')
        income_df = f.income_statement(period='quarter', count=1)
        balance_df = f.balance_sheet(period='quarter', count=1)

        pbt = "N/A"
        p_b = "N/A"
        dividend_yield = "N/A" # Would need more complex logic/data

        if income_df is not None and not income_df.empty:
            latest_col = income_df.columns[-1]
            pbt_row = income_df[income_df['item'].str.contains('lợi nhuận/lỗ trước thuế', na=False, case=False)]
            if not pbt_row.empty:
                pbt_val = pbt_row[latest_col].values[0]
                pbt = f"{pbt_val:,.0f} VND"

        if balance_df is not None and not balance_df.empty:
            latest_col = balance_df.columns[-1]
            equity_row = balance_df[balance_df['item'].str.contains('VỐN CHỦ SỞ HỮU', na=False, case=False)]
            assets_row = balance_df[balance_df['item'].str.contains('TỔNG TÀI SẢN', na=False, case=False)]

            if not equity_row.empty:
                equity = equity_row[latest_col].values[0]
                # Mock shares outstanding or get from elsewhere if possible
                # For SHB, approx 3.6B shares
                shares = 3662908500 if symbol == 'SHB' else 1000000000 # Placeholder
                bvps = equity / shares
                latest_price = float(latest_row.get('close', 0))
                p_b = round(latest_price / bvps, 2) if bvps > 0 else "N/A"

        return {
            "symbol": symbol,
            "latest_price": float(latest_row.get('close', 0)),
            "trading_date": str(latest_row.get('time', 'N/A')),
            "volume": int(latest_row.get('volume', 0)),
            "technicals": {
                "ma20": ma20,
                "ma50": ma50,
                "rsi": rsi,
                "trend": "Tích cực" if (ma20 and latest_row.get('close', 0) > ma20) else "Cần theo dõi"
            },
            "financials": {
                "pbt_latest_quarter": pbt,
                "p_b_ratio": p_b,
            },
            "source": "VNStock API (VCI) + Internal Calculations"
        }
    except Exception as e:
        logger.error(f"VNStock API Error for {symbol}: {e}")
        return {"error": str(e)}

def compare_banking_stocks(symbols: list[str]) -> list[dict[str, Any]]:
    """Compare multiple banking stocks."""
    results = []
    for symbol in symbols:
        data = get_realtime_stock_data(symbol)
        if "error" not in data:
            results.append(data)
    return results

def screen_shb_peers() -> list[str]:
    """Get a list of banking industry peers for comparison."""
    return ["ACB", "VPB", "HDB", "MBB", "TCB"]
