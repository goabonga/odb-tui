"""Diagnostics dashboard panel builder."""

from __future__ import annotations

from odb_tui.models.vehicle import VehicleState
from odb_tui.views.formatters import add_if, fmt, fmt_str, fmt_time, fmti


def build_diag_panel(state: VehicleState) -> str:
    """Build the diagnostics panel displaying MIL, DTCs, compliance, and counters."""
    lines: list[str] = []

    # Status (MIL, DTC count, ignition type)
    mil_str = "--"
    dtc_count_str = "--"
    ign_str = "--"
    if state.status_raw is not None:
        try:
            mil_str = "ON" if state.status_raw.MIL else "OFF"
            dtc_count_str = str(state.status_raw.DTC_count)
            ign_str = str(state.status_raw.ignition_type)
        except (AttributeError, TypeError):
            pass
    lines.append(f"  {'MIL':<18} {mil_str:>8}")
    lines.append(f"  {'DTC COUNT':<18} {dtc_count_str:>8}")
    lines.append(f"  {'IGNITION':<18} {ign_str:>8}")

    # OBD info
    if state.obd_comp is not None:
        lines.append(f"  {'OBD STANDARD':<18} {fmt_str(state.obd_comp)}")
    if state.fuel_type is not None:
        lines.append(f"  {'FUEL TYPE':<18} {fmt_str(state.fuel_type)}")
    if state.fuel_status is not None:
        lines.append(f"  {'FUEL STATUS':<18} {fmt_str(state.fuel_status)}")

    # Counters
    counters = [state.dist_mil, state.run_time_mil, state.warmups, state.dist_dtc, state.time_dtc]
    if any(c is not None for c in counters):
        lines.append("")
        lines.append("COUNTERS")
        lines.append("─" * 60)
        add_if(lines, "DIST MIL km", state.dist_mil, fmti)
        add_if(lines, "TIME MIL", state.run_time_mil, fmt_time)
        add_if(lines, "WARMUPS", state.warmups, fmti)
        add_if(lines, "DIST DTC km", state.dist_dtc, fmti)
        add_if(lines, "TIME DTC min", state.time_dtc, fmt)

    # Calibration
    if state.cal_id is not None or state.cvn is not None:
        lines.append("")
        lines.append("CALIBRATION")
        lines.append("─" * 60)
        if state.cal_id is not None:
            lines.append(f"  {'CAL ID':<18} {fmt_str(state.cal_id)}")
        if state.cvn is not None:
            lines.append(f"  {'CVN':<18} {fmt_str(state.cvn)}")

    # DTCs
    if state.dtc_list:
        lines.append("")
        lines.append("STORED DTCs")
        lines.append("─" * 60)
        for code, desc in state.dtc_list:
            lines.append(f"  {code}  {desc}")

    if state.current_dtc_list:
        lines.append("")
        lines.append("CURRENT DTCs")
        lines.append("─" * 60)
        for code, desc in state.current_dtc_list:
            lines.append(f"  {code}  {desc}")

    return "\n".join(lines)
