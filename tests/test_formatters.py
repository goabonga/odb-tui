"""Tests for view formatters."""

from odb_read.views.formatters import fmt, fmti, fmt2, fmt_time, fmt_str, add_if


class TestFmt:
    """Tests for fmt() -- one-decimal float formatter."""

    def test_float_value(self):
        """Format a typical float to one decimal place."""
        assert fmt(3.14) == "   3.1"

    def test_none(self):
        """Return placeholder for None input."""
        assert fmt(None) == "    --"

    def test_zero(self):
        """Format zero as '0.0'."""
        assert fmt(0) == "   0.0"

    def test_negative(self):
        """Format a negative number correctly."""
        assert fmt(-5.6) == "  -5.6"

    def test_large_value(self):
        """Format a large number without truncation."""
        result = fmt(12345.6)
        assert "12345.6" in result


class TestFmti:
    """Tests for fmti() -- integer formatter."""

    def test_int_value(self):
        """Format a regular integer value."""
        assert fmti(42) == "    42"

    def test_none(self):
        """Return placeholder for None input."""
        assert fmti(None) == "    --"

    def test_float_truncated(self):
        """Round a float to the nearest integer."""
        assert fmti(3.7) == "     4"

    def test_zero(self):
        """Format zero as an integer."""
        assert fmti(0) == "     0"


class TestFmt2:
    """Tests for fmt2() -- two-decimal float formatter."""

    def test_float_value(self):
        """Format a float to two decimal places."""
        assert fmt2(1.5) == "  1.50"

    def test_none(self):
        """Return placeholder for None input."""
        assert fmt2(None) == "    --"

    def test_zero(self):
        """Format zero with two decimal places."""
        assert fmt2(0) == "  0.00"


class TestFmtTime:
    """Tests for fmt_time() -- seconds-to-HH:MM:SS formatter."""

    def test_seconds(self):
        """Format seconds-only duration."""
        assert fmt_time(45) == "  00:00:45"

    def test_minutes(self):
        """Format a duration with minutes and seconds."""
        assert fmt_time(125) == "  00:02:05"

    def test_hours(self):
        """Format a duration with hours, minutes, and seconds."""
        assert fmt_time(3661) == "  01:01:01"

    def test_none(self):
        """Return placeholder for None input."""
        assert fmt_time(None) == "      --"

    def test_zero(self):
        """Format zero seconds as 00:00:00."""
        assert fmt_time(0) == "  00:00:00"


class TestFmtStr:
    """Tests for fmt_str() -- string formatter with None fallback."""

    def test_string(self):
        """Pass through a regular string unchanged."""
        assert fmt_str("hello") == "hello"

    def test_none(self):
        """Return '--' placeholder for None."""
        assert fmt_str(None) == "--"

    def test_number(self):
        """Convert a numeric value to its string representation."""
        assert fmt_str(42) == "42"


class TestAddIf:
    """Tests for add_if() -- conditional line appender."""

    def test_skip_none(self):
        """Do not append a line when value is None."""
        lines = []
        add_if(lines, "RPM", None)
        assert lines == []

    def test_add_value(self):
        """Append a formatted line for a non-None value."""
        lines = []
        add_if(lines, "RPM", 3000.0)
        assert len(lines) == 1
        assert "RPM" in lines[0]
        assert "3000.0" in lines[0]

    def test_with_bar_fn(self):
        """Append a line that includes a bar visualization."""
        lines = []
        def bar_fn(v, mx):
            return f"[{v}/{mx}]"

        add_if(lines, "LOAD", 50.0, bar_fn=bar_fn, bar_max=100)
        assert len(lines) == 1
        assert "[50.0/100]" in lines[0]

    def test_custom_fmt_fn(self):
        """Use a custom format function for the value."""
        lines = []
        add_if(lines, "GEAR", 3, fmt_fn=lambda v: str(v))
        assert len(lines) == 1
        assert "3" in lines[0]
