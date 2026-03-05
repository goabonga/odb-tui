"""Format helpers for panel display."""


def fmt(v):
    """Format a float with one decimal place, right-aligned, or '--' if None."""
    return f"{v:>6.1f}" if v is not None else "    --"


def fmti(v):
    """Format a number as an integer, right-aligned, or '--' if None."""
    return f"{v:>6.0f}" if v is not None else "    --"


def fmt2(v):
    """Format a float with two decimal places, right-aligned, or '--' if None."""
    return f"{v:>6.2f}" if v is not None else "    --"


def fmt_time(secs):
    """Format seconds as HH:MM:SS, or '--' if None."""
    if secs is None:
        return "      --"
    s = int(secs)
    return f"  {s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"


def fmt_str(v):
    """Convert value to string, or '--' if None."""
    return str(v) if v is not None else "--"


def add_if(lines, label, val, fmt_fn=None, bar_fn=None, bar_max=None):
    """Only add line if value is not None."""
    if val is None:
        return
    if fmt_fn is None:
        fmt_fn = fmt
    line = f"  {label} {fmt_fn(val)}"
    if bar_fn and bar_max:
        line += f"  {bar_fn(val, bar_max)}"
    lines.append(line)
