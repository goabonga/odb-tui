"""Turbo/Air panel builder."""

from odb_read.models.vehicle import VehicleState
from odb_read.views.formatters import fmt, add_if
from odb_read.views.widgets import bar


def build_turbo_panel(state: VehicleState) -> str:
    """Build the turbo/air panel text: boost pressure, throttle, and accelerator positions."""
    lines = [
        "PRESSION ADMISSION / TURBO",
        "",
        f"  INTAKE    kPa  {fmt(state.intake_press)}  {bar(state.intake_press, 300)}",
        f"  BARO      kPa  {fmt(state.baro)}",
        f"  NET BOOST kPa  {fmt(state.net_boost)}  "
        + (bar(state.net_boost, 200) if state.net_boost and state.net_boost > 0 else ""),
        f"  MAX BOOST kPa  {fmt(state.max_boost_observed)}",
        f"  STATUS         {state.turbo_status:>6}",
        "",
        "BOOST MOYEN PAR REGIME",
        "",
        f"  < 2000 RPM     {fmt(state.boost_low)}",
        f"  2000-3000      {fmt(state.boost_mid)}",
        f"  > 3000 RPM     {fmt(state.boost_high)}",
        f"  ECHANTILLONS   {state.boost_samples}/120",
        "",
        "PAPILLON",
        "",
    ]
    add_if(lines, "POSITION     %", state.throttle, bar_fn=bar, bar_max=100)
    add_if(lines, "POSITION B   %", state.throttle_b, bar_fn=bar, bar_max=100)
    add_if(lines, "ACTUATEUR    %", state.throttle_act, bar_fn=bar, bar_max=100)

    lines += ["", "ACCELERATEUR", ""]
    add_if(lines, "PEDALE D     %", state.accel_d, bar_fn=bar, bar_max=100)
    add_if(lines, "PEDALE E     %", state.accel_e, bar_fn=bar, bar_max=100)
    add_if(lines, "RELATIF      %", state.rel_accel, bar_fn=bar, bar_max=100)

    return "\n".join(lines)
