"""Formatting utilities for panel display."""

from __future__ import annotations

from typing import Any, Callable


def fmt(v: float | None) -> str:
    """Format float with 1 decimal, or '--' if None."""
    return f"{v:>8.1f}" if v is not None else "      --"


def fmti(v: int | float | None) -> str:
    """Format as integer, or '--' if None."""
    return f"{int(v):>8d}" if v is not None else "      --"


def fmt2(v: float | None) -> str:
    """Format float with 2 decimals, or '--' if None."""
    return f"{v:>8.2f}" if v is not None else "      --"


def fmt_time(secs: float | None) -> str:
    """Format seconds as HH:MM:SS, or '--' if None."""
    if secs is None:
        return "      --"
    s = int(secs)
    return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"


def fmt_str(v: Any | None) -> str:
    """Format as string, or '--' if None."""
    return str(v) if v is not None else "--"


def add_if(
    lines: list[str],
    label: str,
    val: Any | None,
    fmt_fn: Callable[..., str] = fmt,
    bar_fn: Callable[..., str] | None = None,
    bar_max: float = 100,
) -> None:
    """Append a formatted line only if val is not None."""
    if val is None:
        return
    line = f"  {label:<18} {fmt_fn(val)}"
    if bar_fn is not None:
        line += f"  {bar_fn(val, bar_max)}"
    lines.append(line)
