"""Gearbox panel builder."""

from odb_read.models.vehicle import VehicleState
from odb_read.views.formatters import fmt, fmti
from odb_read.views.widgets import bar


def build_gearbox_panel(state: VehicleState) -> str:
    """Build the gearbox panel text: speed, gear indicator, ratios, and tire info."""
    gear_display = f"  {state.gear}" if state.gear is not None else "  N"
    ratio_display = f"{state.gear_ratio:.3f}" if state.gear_ratio is not None else "--"

    gear_indicator = ""
    for g in range(1, state.gb_count + 1):
        if g == state.gear:
            gear_indicator += f" [{g}]"
        else:
            gear_indicator += f"  {g} "

    lines = [
        "VITESSE / REGIME",
        "",
        f"  VITESSE  km/h  {fmti(state.speed)}  {bar(state.speed, 200)}",
        f"  RPM            {fmti(state.rpm)}  {bar(state.rpm, 5000)}",
        f"  PAPILLON   %   {fmt(state.throttle)}  {bar(state.throttle, 100)}",
        f"  MAX      km/h  {fmti(state.max_speed)}",
        "",
        "RAPPORT ENGAGE",
        "",
        f"  RAPPORT        {gear_display}",
        f"  RATIO          {ratio_display:>6}",
        f"  INDICATEUR     {gear_indicator}",
        "",
        f"BOITE: {state.gb_label}  [V] changer",
        "",
    ]

    for g in sorted(state.gb_ratios.keys()):
        marker = " <<" if g == state.gear else ""
        lines.append(f"  {g}e  {state.gb_ratios[g]:.3f}{marker}")

    lines += [
        "",
        f"  Pont: {state.gb_final}",
        f"  PNEU: {state.tire_label} ({state.tire_circ:.3f}m)  [T] changer",
    ]

    return "\n".join(lines)
