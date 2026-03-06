"""EGR dashboard panel builder."""

from __future__ import annotations

from odb_tui.models.vehicle import VehicleState
from odb_tui.views.formatters import add_if, fmt
from odb_tui.views.widgets import bar


def build_egr_panel(state: VehicleState) -> str:
    """Build the EGR panel displaying commanded EGR and error interpretation."""
    lines: list[str] = []

    if state.egr_cmd is None and state.egr_err is None:
        lines.append("  No EGR data available")
        return "\n".join(lines)

    add_if(lines, "COMMANDED %", state.egr_cmd, fmt, bar, 100)

    if state.egr_err is not None:
        if state.egr_err < 0:
            interpretation = f"({abs(state.egr_err):.1f}% below commanded)"
        elif state.egr_err > 0:
            interpretation = f"({state.egr_err:.1f}% above commanded)"
        else:
            interpretation = "(perfect)"
        lines.append(f"  {'ERROR %':<18} {fmt(state.egr_err)}  {interpretation}")

    return "\n".join(lines)
