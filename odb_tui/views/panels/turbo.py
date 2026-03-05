"""Turbo/Air dashboard panel builder."""

from __future__ import annotations

from odb_tui.models.vehicle import VehicleState
from odb_tui.views.formatters import add_if, fmt
from odb_tui.views.widgets import bar


def build_turbo_panel(state: VehicleState) -> str:
    """Build the turbo panel displaying pressure, boost, throttle, and accelerator data."""
    lines: list[str] = ["TURBO / AIR"]
    lines.append("─" * 60)

    add_if(lines, "INTAKE kPa", state.intake_press, fmt, bar, 300)
    add_if(lines, "BARO kPa", state.baro, fmt)

    if state.net_boost is not None:
        boost_bar = bar(state.net_boost, 200) if state.net_boost > 0 else ""
        lines.append(f"  {'NET BOOST kPa':<18} {fmt(state.net_boost)}  {boost_bar}")

    # Throttle
    throttles = [state.throttle, state.throttle_b, state.throttle_act]
    if any(t is not None for t in throttles):
        lines.append("")
        lines.append("THROTTLE")
        lines.append("─" * 60)
        add_if(lines, "POSITION %", state.throttle, fmt, bar, 100)
        add_if(lines, "POSITION B %", state.throttle_b, fmt, bar, 100)
        add_if(lines, "ACTUATOR %", state.throttle_act, fmt, bar, 100)

    # Accelerator
    accels = [state.accel_d, state.accel_e, state.rel_accel]
    if any(a is not None for a in accels):
        lines.append("")
        lines.append("ACCELERATOR")
        lines.append("─" * 60)
        add_if(lines, "POSITION D %", state.accel_d, fmt, bar, 100)
        add_if(lines, "POSITION E %", state.accel_e, fmt, bar, 100)
        add_if(lines, "RELATIVE %", state.rel_accel, fmt, bar, 100)

    return "\n".join(lines)
