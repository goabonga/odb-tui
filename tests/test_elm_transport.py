"""Tests for ELM327 transport layer utilities."""

from odb_read.services.elm_transport import hex_bytes, chunks, ElmConfig, Elm327


class TestHexBytes:
    """Tests for hex_bytes() -- raw string to clean uppercase hex."""

    def test_basic(self):
        """Strip spaces and uppercase hex characters."""
        assert hex_bytes("1a 2B") == "1A2B"

    def test_invalid_chars_filtered(self):
        """Filter out non-hex characters."""
        assert hex_bytes("1A-XX-2B") == "1A2B"

    def test_empty(self):
        """Return empty string for empty input."""
        assert hex_bytes("") == ""

    def test_all_invalid(self):
        """Return empty string when all characters are invalid hex."""
        assert hex_bytes("xyz") == ""

    def test_no_spaces(self):
        """Handle input that has no spaces."""
        assert hex_bytes("aabb") == "AABB"

    def test_mixed(self):
        """Handle a typical multi-byte hex response with spaces."""
        assert hex_bytes("62 F1 90 48 65") == "62F1904865"


class TestChunks:
    """Tests for chunks() -- split string into fixed-size pieces."""

    def test_basic(self):
        """Split an evenly divisible string into chunks."""
        assert chunks("AABBCC", 2) == ["AA", "BB", "CC"]

    def test_odd_length(self):
        """Handle a string that does not divide evenly."""
        assert chunks("AABBC", 2) == ["AA", "BB", "C"]

    def test_empty(self):
        """Return empty list for empty input."""
        assert chunks("", 2) == []

    def test_single_chunk(self):
        """Return one chunk when input is shorter than chunk size."""
        assert chunks("AB", 4) == ["AB"]


class TestElmConfig:
    """Tests for ElmConfig dataclass defaults and overrides."""

    def test_defaults(self):
        """Verify all default timing and baud values."""
        cfg = ElmConfig(port="/dev/ttyUSB0")
        assert cfg.port == "/dev/ttyUSB0"
        assert cfg.baud == 38400
        assert cfg.timeout == 1.2
        assert cfg.write_delay == 0.05
        assert cfg.read_grace == 0.25
        assert cfg.init_delay == 1.0

    def test_custom(self):
        """Override baud and timeout with custom values."""
        cfg = ElmConfig(port="/dev/ttyS0", baud=115200, timeout=2.0)
        assert cfg.baud == 115200
        assert cfg.timeout == 2.0


class TestElm327ParseLines:
    """Tests for Elm327.parse_lines() -- raw serial output parsing."""

    def test_prompt_removed(self):
        """Strip the '>' prompt character from output."""
        lines = Elm327.parse_lines(">OK\r\n>")
        assert "OK" in lines

    def test_ok(self):
        """Parse a simple OK response."""
        lines = Elm327.parse_lines("OK\r\n>")
        assert lines == ["OK"]

    def test_no_data(self):
        """Parse a NO DATA response."""
        lines = Elm327.parse_lines("NO DATA\r\n>")
        assert lines == ["NO DATA"]

    def test_hex_valid(self):
        """Parse a hex data response into a clean hex string."""
        lines = Elm327.parse_lines("62 F1 90 41 42 43\r\n>")
        assert "62F19041424" in lines[0] or lines[0] == "62F190414243"

    def test_empty_lines_skipped(self):
        """Skip blank lines in the output."""
        lines = Elm327.parse_lines("\r\n\r\n>")
        assert lines == []

    def test_stopped(self):
        """Parse a STOPPED response."""
        lines = Elm327.parse_lines("STOPPED\r\n>")
        assert lines == ["STOPPED"]

    def test_searching(self):
        """Parse a SEARCHING... response."""
        lines = Elm327.parse_lines("SEARCHING...\r\n>")
        assert lines == ["SEARCHING..."]

    def test_mixed(self):
        """Parse a response containing both hex data and OK."""
        raw = "62F190414243\r\nOK\r\n>"
        lines = Elm327.parse_lines(raw)
        assert "62F190414243" in lines
        assert "OK" in lines
