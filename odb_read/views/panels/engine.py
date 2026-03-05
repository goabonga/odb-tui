"""Engine panel builder."""

from odb_read.models.vehicle import VehicleState
from odb_read.views.formatters import fmt, fmti, fmt2, fmt_time, fmt_str, add_if
from odb_read.views.widgets import bar


def build_engine_panel(state: VehicleState) -> str:
    """Build the engine panel text: RPM, load, temps, fuel, MAF, and O2 data."""
    lines = [
        state.vehicle_name,
        "",
        "REGIME / CHARGE",
        "",
        f"  RPM            {fmti(state.rpm)}  {bar(state.rpm, 5000)}",
        f"  CHARGE       % {fmt(state.engine_load)}  {bar(state.engine_load, 100)}",
    ]
    add_if(lines, "CHARGE ABS   %", state.abs_load)
    add_if(lines, "AVANCE       °", state.timing)
    lines.append(f"  FONCTIONNEMENT {fmt_time(state.run_time)}")

    lines += ["", "TEMPERATURES", ""]
    lines.append(f"  LIQUIDE   °C   {fmt(state.coolant_temp)}  {bar(state.coolant_temp, 120)}")
    add_if(lines, "HUILE     °C  ", state.oil_temp, bar_fn=bar, bar_max=150)
    lines.append(f"  ADMISSION °C   {fmt(state.intake_temp)}  {bar(state.intake_temp, 80)}")
    add_if(lines, "AMBIANTE  °C  ", state.ambient_temp)

    lines += ["", "ALIMENTATION", ""]
    lines.append(f"  RAMPE    kPa   {fmti(state.rail)}  {bar(state.rail, 200000)}")
    add_if(lines, "DEBIT    L/h  ", state.fuel_rate, fmt_fn=fmt2)
    lines.append(f"  NIVEAU     %   {fmt(state.fuel_level)}  {bar(state.fuel_level, 100)}")
    add_if(lines, "INJECT     °  ", state.fuel_inject)
    add_if(lines, "LAMBDA        ", state.equiv_ratio, fmt_fn=fmt2)
    add_if(lines, "TRIM CT    %  ", state.short_ft1)
    add_if(lines, "TRIM LT    %  ", state.long_ft1)

    lines += ["", "DEBITMETRE / ELECTRIQUE", ""]
    lines.append(f"  MAF      g/s   {fmt(state.maf)}  {bar(state.maf, 200)}")
    lines.append(f"  TENSION    V   {fmt(state.voltage)}")

    # O2 / Lambda
    if state.o2_sensors is not None or state.o2_s1_wr is not None or state.o2_s2_wr is not None:
        lines += ["", "SONDES O2 / LAMBDA", ""]
        if state.o2_sensors is not None:
            lines.append(f"  SONDES O2        {fmt_str(state.o2_sensors)}")
        add_if(lines, "S1 LAMBDA  mA   ", state.o2_s1_wr)
        add_if(lines, "S2 LAMBDA  mA   ", state.o2_s2_wr)

    return "\n".join(lines)
