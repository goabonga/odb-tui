"""Text-based widgets for panel display."""

from __future__ import annotations


def bar(value: float | None, max_value: float, width: int = 28) -> str:
    """Render a text gauge bar using block characters."""
    if value is None or max_value <= 0:
        return "░" * width
    ratio = max(0.0, min(1.0, value / max_value))
    filled = int(ratio * width)
    return "█" * filled + "░" * (width - filled)
