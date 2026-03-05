"""Engine dashboard panel builder."""

from __future__ import annotations

from odb_tui.models.vehicle import VehicleState
from odb_tui.views.formatters import add_if, fmt, fmt2, fmt_str, fmt_time, fmti
from odb_tui.views.widgets import bar


def build_engine_panel(state: VehicleState) -> str:
    """Build the engine panel displaying RPM, load, temps, fuel, and O2 data."""
    lines: list[str] = ["ENGINE"]
    lines.append("─" * 60)

    add_if(lines, "RPM", state.rpm, fmti, bar, 7000)
    add_if(lines, "LOAD %", state.engine_load, fmt, bar, 100)
    add_if(lines, "ABS LOAD %", state.abs_load, fmt, bar, 100)
    add_if(lines, "TIMING °", state.timing, fmt)
    add_if(lines, "RUN TIME", state.run_time, fmt_time)

    # Temperatures
    temps = [state.coolant_temp, state.oil_temp, state.intake_temp, state.ambient_temp]
    if any(t is not None for t in temps):
        lines.append("")
        lines.append("TEMPERATURES")
        lines.append("─" * 60)
        add_if(lines, "COOLANT °C", state.coolant_temp, fmt, bar, 130)
        add_if(lines, "OIL °C", state.oil_temp, fmt, bar, 150)
        add_if(lines, "INTAKE °C", state.intake_temp, fmt, bar, 80)
        add_if(lines, "AMBIENT °C", state.ambient_temp, fmt)

    # Fuel
    fuels = [state.fuel_rail, state.fuel_rate, state.fuel_level, state.fuel_inject,
             state.equiv_ratio, state.short_ft1, state.long_ft1]
    if any(f is not None for f in fuels):
        lines.append("")
        lines.append("FUEL")
        lines.append("─" * 60)
        add_if(lines, "RAIL kPa", state.fuel_rail, fmt)
        add_if(lines, "RATE L/h", state.fuel_rate, fmt)
        add_if(lines, "LEVEL %", state.fuel_level, fmt, bar, 100)
        add_if(lines, "INJECT °", state.fuel_inject, fmt)
        add_if(lines, "EQUIV RATIO", state.equiv_ratio, fmt2)
        add_if(lines, "SHORT FT1 %", state.short_ft1, fmt)
        add_if(lines, "LONG FT1 %", state.long_ft1, fmt)

    # MAF / Voltage
    add_if(lines, "MAF g/s", state.maf, fmt)
    add_if(lines, "VOLTAGE V", state.voltage, fmt)

    # O2
    if state.o2_sensors is not None or state.o2_s1_wr is not None or state.o2_s2_wr is not None:
        lines.append("")
        lines.append("O2 SENSORS")
        lines.append("─" * 60)
        if state.o2_sensors is not None:
            lines.append(f"  SENSORS          {fmt_str(state.o2_sensors)}")
        add_if(lines, "S1 LAMBDA", state.o2_s1_wr, fmt2)
        add_if(lines, "S2 LAMBDA", state.o2_s2_wr, fmt2)

    return "\n".join(lines)
