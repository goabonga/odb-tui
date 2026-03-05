"""Tests for widgets.bar()."""

from odb_read.views.widgets import bar


class TestBar:
    """Tests for bar() -- Unicode block-character progress bar."""

    def test_none_value(self):
        """Render an empty bar when value is None."""
        result = bar(None, 100)
        assert result == "░" * 28

    def test_none_custom_width(self):
        """Render an empty bar at custom width when value is None."""
        result = bar(None, 100, 10)
        assert result == "░" * 10

    def test_half(self):
        """Render a half-filled bar."""
        result = bar(50, 100, 10)
        assert result == "█" * 5 + "░" * 5

    def test_full(self):
        """Render a fully filled bar."""
        result = bar(100, 100, 10)
        assert result == "█" * 10

    def test_empty(self):
        """Render a completely empty bar for zero value."""
        result = bar(0, 100, 10)
        assert result == "░" * 10

    def test_overflow_clamped(self):
        """Clamp value exceeding max to a full bar."""
        result = bar(200, 100, 10)
        # min(200/100, 1.0) = 1.0 → full bar
        assert result == "█" * 10

    def test_default_width(self):
        """Use the default bar width of 28 characters."""
        result = bar(50, 100)
        assert len(result) == 28
