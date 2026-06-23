"""
utils.py
Shared utility functions for the FIFA Scout Assistant.
"""

import re


EXAMPLE_QUERIES = [
    "Show me top 10 players",
    "Compare Messi and Ronaldo",
    "Best players under 23",
    "Best strikers with pace above 85",
    "Highest rated clubs",
    "Best value players",
    "Players with potential above 90",
    "Top 5 goalkeepers",
    "Spanish players with overall above 85",
    "Best midfielders under 25",
]


def sanitize_query(query: str) -> str:
    """Strip leading/trailing whitespace and collapse internal spaces."""
    return re.sub(r"\s+", " ", query.strip())


def format_number(n: float | int) -> str:
    """Human-readable large numbers."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.0f}K"
    return str(int(n))
