"""Errors dashboard panel builder."""

from __future__ import annotations

from odb_tui.models.vehicle import VehicleState


def build_errors_panel(state: VehicleState) -> str:
    """Build the errors panel displaying active DTCs."""
    lines: list[str] = ["ERRORS"]
    lines.append("─" * 60)

    if state.connection_status in ("DISCONNECTED", "NO DEVICE", "FAILED"):
        lines.append("  --")
        return "\n".join(lines)

    if state.dtc_list:
        for code, desc in state.dtc_list:
            lines.append(f"  {code}")
            lines.append(f"  {desc}")
            lines.append("")
    else:
        lines.append("  No errors")

    return "\n".join(lines)
