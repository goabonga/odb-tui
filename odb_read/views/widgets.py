"""Reusable TUI widgets."""

from textual.widgets import Static


class Panel(Static):
    """Static widget wrapper used as a named display area for panel text."""

    def update_content(self, text):
        self.update(text)


def bar(value, max_value, width=28):
    """Return a text-based bar gauge (filled/empty blocks) scaled to max_value."""
    if value is None:
        return "░" * width
    ratio = min(float(value) / max_value, 1.0)
    filled = int(ratio * width)
    return "█" * filled + "░" * (width - filled)
