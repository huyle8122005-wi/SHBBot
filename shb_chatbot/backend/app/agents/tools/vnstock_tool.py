"""VNStock integration tool for real-time market data."""

import logging
from typing import Any

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

def get_realtime_stock_data(symbol: str) -> dict[str, Any]:
    """Fetch real-time (latest) stock data and financial flow using vnstock.

    Args:
        symbol: The stock ticker (e.g., 'SHB').

    Returns:
        A dictionary with real-time price and financial flow summary.
    """
    try:
        # Use vci as a reliable source for SHB
        q = Quote(symbol=symbol, source='vci')
        # Get history to find the latest price
        df = q.history(start='2025-01-01')

        if df is None or df.empty:
            return {"error": f"No market data found for {symbol}"}

        latest_row = df.iloc[-1]

        # Get financial flow (income statement)
        f = Finance(symbol=symbol, source='vci')
        income_df = f.income_statement(period='quarter', count=1)

        pbt = "N/A"
        if income_df is not None and not income_df.empty:
            # Find the row for PBT (Tổng lợi nhuận/lỗ trước thuế)
            # The column name for the latest quarter might be dynamic (e.g., '2025-Q2')
            latest_col = income_df.columns[-1]
            pbt_row = income_df[income_df['item'].str.contains('lợi nhuận/lỗ trước thuế', na=False, case=False)]
            if not pbt_row.empty:
                pbt_val = pbt_row[latest_col].values[0]
                pbt = f"{pbt_val:,.0f} VND"

        return {
            "symbol": symbol,
            "latest_price": float(latest_row.get('close', 0)),
            "trading_date": str(latest_row.get('time', 'N/A')),
            "volume": int(latest_row.get('volume', 0)),
            "pbt_latest_quarter": pbt,
            "source": "VNStock API (VCI)"
        }
    except Exception as e:
        logger.error(f"VNStock API Error: {e}")
        return {"error": str(e)}

def screen_shb_peers() -> list[str]:
    """Get a list of banking industry peers for comparison."""
    # Pre-defined banking peers as listing_companies API can be heavy/unreliable without full account
    return ["ACB", "VPB", "HDB", "MBB", "TCB"]
