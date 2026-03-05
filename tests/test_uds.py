"""Tests for UDS helpers."""

from odb_read.services.uds import decode_negative, extract_positive_62, ascii_from_hex


class TestDecodeNegative:
    """Tests for decode_negative() -- UDS negative response parser."""

    def test_valid_negative_response(self):
        """Decode a standard 7F negative response with NRC 0x31."""
        result = decode_negative("7F2231")
        assert result == (0x7F, 0x22, 0x31)

    def test_too_short(self):
        """Return None when hex string is too short for a negative response."""
        assert decode_negative("7F22") is None

    def test_not_7f(self):
        """Return None when response does not start with 7F."""
        assert decode_negative("622231") is None

    def test_empty(self):
        """Return None for empty input."""
        assert decode_negative("") is None

    def test_other_nrc(self):
        """Decode a negative response with a different NRC code."""
        result = decode_negative("7F2211")
        assert result == (0x7F, 0x22, 0x11)

    def test_longer_response(self):
        """Decode correctly even when extra bytes follow the NRC."""
        # Extra bytes after NRC should still work
        result = decode_negative("7F221100")
        assert result == (0x7F, 0x22, 0x11)


class TestExtractPositive62:
    """Tests for extract_positive_62() -- UDS positive response (SID 0x62) parser."""

    def test_valid_positive(self):
        """Extract DID and data from a standard positive response."""
        result = extract_positive_62("62F190414243")
        assert result == (0x62, 0xF190, "414243")

    def test_too_short(self):
        """Return None when hex string is too short."""
        assert extract_positive_62("62F1") is None

    def test_not_62(self):
        """Return None when SID is not 0x62."""
        assert extract_positive_62("7FF190414243") is None

    def test_empty(self):
        """Return None for empty input."""
        assert extract_positive_62("") is None

    def test_minimal_data(self):
        """Extract a single data byte after the DID."""
        result = extract_positive_62("62F19041")
        assert result == (0x62, 0xF190, "41")

    def test_no_data_after_did(self):
        """Handle a response with DID bytes but no additional data."""
        # Exactly 8 chars: "62" + "F190" + "" → data is ""
        result = extract_positive_62("62F19000")
        assert result is not None
        assert result[1] == 0xF190


class TestAsciiFromHex:
    """Tests for ascii_from_hex() -- hex string to ASCII with dot replacement."""

    def test_hello(self):
        """Decode a fully printable ASCII hex string."""
        assert ascii_from_hex("48656C6C6F") == "Hello"

    def test_non_printable(self):
        """Replace a non-printable byte with a dot."""
        assert ascii_from_hex("01") == "."

    def test_mixed(self):
        """Replace non-printable bytes while keeping printable ones."""
        # "A" = 0x41, NUL = 0x00, "B" = 0x42
        assert ascii_from_hex("410042") == "A.B"

    def test_empty(self):
        """Return empty string for empty input."""
        assert ascii_from_hex("") == ""

    def test_space(self):
        """Decode a space character (0x20) as printable."""
        assert ascii_from_hex("20") == " "

    def test_tilde(self):
        """Decode the last printable ASCII character (0x7E tilde)."""
        # 0x7E = '~' (last printable ASCII)
        assert ascii_from_hex("7E") == "~"

    def test_del_non_printable(self):
        """Replace the DEL character (0x7F) with a dot."""
        # 0x7F = DEL, not printable
        assert ascii_from_hex("7F") == "."
