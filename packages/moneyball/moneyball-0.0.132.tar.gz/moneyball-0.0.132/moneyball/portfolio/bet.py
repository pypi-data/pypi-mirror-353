"""The bet dictionary format."""

from typing import TypedDict

from .team import Team

Bet = TypedDict(
    "Bet",
    {
        "strategy": str,
        "league": str,
        "kelly": float,
        "weight": float,
        "teams": list[Team],
        "dt": str,
    },
)
