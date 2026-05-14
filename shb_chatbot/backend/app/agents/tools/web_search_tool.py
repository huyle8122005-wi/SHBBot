"""Web search tool using DuckDuckGo."""

import logging
from typing import Any

from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

def search_web(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """Search the web for up-to-date information.

    Args:
        query: The search query.
        max_results: Maximum number of results to return.

    Returns:
        A list of search results with title, link, and snippet.
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            return results
    except Exception as e:
        logger.error(f"Web search error: {e}")
        return [{"error": str(e)}]

def get_latest_shb_interest_rates() -> str:
    """Find the latest interest rates for SHB bank by searching the web.

    Returns:
        A summary of the latest interest rates found.
    """
    query = "lãi suất tiền gửi SHB mới nhất 2026"
    results = search_web(query, max_results=3)

    if not results or "error" in results[0]:
        return "Không thể tìm thấy thông tin lãi suất mới nhất qua tìm kiếm web."

    summary = "Thông tin lãi suất SHB mới nhất từ web:\n"
    for res in results:
        summary += f"- {res.get('title')}: {res.get('body')}\n  Nguồn: {res.get('href')}\n"

    return summary
