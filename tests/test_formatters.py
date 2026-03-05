from odb_tui.views.formatters import add_if, fmt, fmt2, fmt_str, fmt_time, fmti
from odb_tui.views.widgets import bar


def test_fmt_value():
    assert fmt(123.456) == "   123.5"


def test_fmt_none():
    assert fmt(None) == "      --"


def test_fmti_value():
    assert fmti(3000) == "    3000"


def test_fmti_none():
    assert fmti(None) == "      --"


def test_fmt2_value():
    assert fmt2(1.005) == "    1.00" or fmt2(1.005) == "    1.01"


def test_fmt_time_value():
    assert fmt_time(3661.0) == "01:01:01"


def test_fmt_time_none():
    assert fmt_time(None) == "      --"


def test_fmt_str_value():
    assert fmt_str("hello") == "hello"


def test_fmt_str_none():
    assert fmt_str(None) == "--"


def test_add_if_with_value():
    lines: list[str] = []
    add_if(lines, "RPM", 3000.0, fmti)
    assert len(lines) == 1
    assert "RPM" in lines[0]
    assert "3000" in lines[0]


def test_add_if_with_none():
    lines: list[str] = []
    add_if(lines, "RPM", None, fmti)
    assert len(lines) == 0


def test_bar_value():
    result = bar(50.0, 100.0, width=10)
    assert "█" in result
    assert "░" in result
    assert len(result) == 10


def test_bar_none():
    result = bar(None, 100.0, width=10)
    assert result == "░" * 10
