"""Tool to search through the SHB 2025 analysis report PDF."""

import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

def search_shb_report(query: str) -> str:
    """Search for specific information in the SHB_2025_12_11_BuiToVietAnh.pdf report.

    Use this tool when you need detailed information about SHB bank that is not covered
    by the basic stock analysis tools, such as detailed financial tables, specific
    risk warnings, or in-depth analysis of M&A deals.

    Args:
        query: The search query or keywords to look for in the report.

    Returns:
        A string containing relevant excerpts from the report.
    """
    try:
        import pymupdf

        pdf_path = Path("SHB_2025_12_11_BuiToVietAnh.pdf")
        # Search in parents until found or reached root
        current = Path.cwd()
        found = False
        for _ in range(3):
            if (current / "SHB_2025_12_11_BuiToVietAnh.pdf").exists():
                pdf_path = current / "SHB_2025_12_11_BuiToVietAnh.pdf"
                found = True
                break
            current = current.parent

        if not found:
            return "Error: Report PDF file not found."

        doc: Any = pymupdf.open(pdf_path)
        relevant_content = []

        query_words = query.lower().split()

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()

            # Simple keyword matching for relevance
            match_count = sum(1 for word in query_words if word in text.lower())

            if match_count > 0:
                relevant_content.append(f"--- Page {page_num + 1} ---\n{text.strip()}")

            # Limit results to avoid token overflow
            if len(relevant_content) >= 3:
                break

        doc.close()

        if not relevant_content:
            return f"No specific information found for '{query}' in the report."

        return "\n\n".join(relevant_content)

    except Exception as e:
        logger.error(f"Error searching report: {e}")
        return f"An error occurred while searching the report: {e!s}"
