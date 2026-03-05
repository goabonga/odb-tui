"""Diag panel builder."""

from odb_read.models.vehicle import VehicleState
from odb_read.views.formatters import fmti, fmt_time, fmt_str


def build_diag_panel(state: VehicleState) -> str:
    """Build the diagnostics panel text: MIL, DTCs, counters, calibration, and Mode 06 monitors."""
    mil_str = "--"
    dtc_count_str = "--"
    ign_type_str = "--"
    if state.status_raw is not None:
        try:
            mil_str = "ON" if state.status_raw.MIL else "OFF"  # type: ignore[attr-defined]
            dtc_count_str = str(state.status_raw.DTC_count)  # type: ignore[attr-defined]
            ign_type_str = state.status_raw.ignition_type  # type: ignore[attr-defined]
        except Exception:
            pass

    lines = [
        "ETAT MOTEUR",
        "",
        f"  MIL (VOYANT)     {mil_str}",
        f"  NB DTC           {dtc_count_str}",
        f"  ALLUMAGE         {ign_type_str}",
    ]
    if state.obd_comp is not None:
        lines.append(f"  NORME OBD        {fmt_str(state.obd_comp)}")
    if state.fuel_type is not None:
        lines.append(f"  TYPE CARBURANT   {fmt_str(state.fuel_type)}")
    if state.fuel_status is not None:
        lines.append(f"  FUEL STATUS      {fmt_str(state.fuel_status)}")

    lines += ["", "COMPTEURS", ""]
    lines.append(f"  DIST AVEC MIL km {fmti(state.dist_mil)}")
    if state.run_time_mil is not None:
        lines.append(f"  TEMPS AVEC MIL   {fmt_time(state.run_time_mil)}")
    lines.append(f"  WARMUPS DTC CLR  {fmti(state.warmups)}")
    lines.append(f"  DIST DTC CLR  km {fmti(state.dist_dtc)}")
    if state.time_dtc is not None:
        lines.append(f"  TEMPS DTC CLR    {fmt_time(state.time_dtc)}")

    lines += ["", "DTC MEMORISES", ""]
    if state.dtc_list:
        for code, desc in state.dtc_list:
            lines.append(f"  {code}  {desc}")
    else:
        lines.append("  Aucun DTC")

    if state.current_dtc_list:
        lines += ["", "DTC CYCLE EN COURS", ""]
        for code, desc in state.current_dtc_list:
            lines.append(f"  {code}  {desc}")

    # Calibration info
    if state.cal_id is not None or state.cvn is not None:
        lines += ["", "CALIBRATION ECU", ""]
        if state.cal_id is not None:
            lines.append(f"  CAL ID           {fmt_str(state.cal_id)}")
        if state.cvn is not None:
            lines.append(f"  CVN              {fmt_str(state.cvn)}")

    # Mode 06 monitors
    def fmt_monitor(mon, name):
        """Format a Mode 06 monitor's test results into display lines."""
        lines_out = []
        try:
            for test in mon:
                tid = getattr(test, 'tid', '?')
                val = getattr(test, 'value', None)
                lim_min = getattr(test, 'min', None)
                lim_max = getattr(test, 'max', None)
                passed = getattr(test, 'passed', None)
                status_m = "OK" if passed else "FAIL" if passed is not None else "?"
                lines_out.append(
                    f"  {name} T{tid}: {val}  "
                    f"[{lim_min}-{lim_max}] {status_m}"
                )
        except Exception:
            lines_out.append(f"  {name:<18} {str(mon)[:50]}")
        return lines_out

    monitors = []
    if state.mon_o2_b1s1 is not None:
        monitors.extend(fmt_monitor(state.mon_o2_b1s1, "O2 B1S1"))
    if state.mon_o2_b1s2 is not None:
        monitors.extend(fmt_monitor(state.mon_o2_b1s2, "O2 B1S2"))
    if state.mon_nox is not None:
        monitors.extend(fmt_monitor(state.mon_nox, "NOx ABSORBER"))
    if monitors:
        lines += ["", "MONITORS (Mode 06)", ""]
        lines.extend(monitors)

    return "\n".join(lines)
