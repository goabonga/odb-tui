"""DPF/EGR panel builder."""

from odb_read.models.vehicle import VehicleState
from odb_read.views.formatters import fmt
from odb_read.views.widgets import bar


def build_dpf_panel(state: VehicleState) -> str:
    """Build the DPF/EGR panel text: EGR status, DPF pressure, EGT temps, regen status."""
    # EGR error interpretation
    if state.egr_err is not None:
        if state.egr_err < 0:
            egr_err_info = f"({abs(state.egr_err):.1f}% sous le cmd)"
        elif state.egr_err > 0:
            egr_err_info = f"({state.egr_err:.1f}% sur le cmd)"
        else:
            egr_err_info = "(parfait)"
    else:
        egr_err_info = ""

    lines = [
        "EGR (Recirculation Gaz Echappement)",
        "",
        f"  COMMANDE     % {fmt(state.egr_cmd)}  {bar(state.egr_cmd, 100)}",
        f"  ERREUR       % {fmt(state.egr_err)}  {egr_err_info}",
        f"  STATUS         {state.egr_status:>6}",
    ]

    if state.dpf_diff is not None or state.pre_dpf is not None or state.post_dpf is not None:
        lines += ["", "DPF / FAP", ""]
        if state.dpf_diff is not None:
            lines.append(f"  DELTA P   kPa  {fmt(state.dpf_diff)}  {bar(state.dpf_diff, 20)}")
        if state.pre_dpf is not None or state.post_dpf is not None:
            lines += ["", "TEMPERATURES ECHAPPEMENT (EGT)", ""]
            lines.append(f"  PRE-DPF   °C   {fmt(state.pre_dpf)}  {bar(state.pre_dpf, 800)}")
            lines.append(f"  POST-DPF  °C   {fmt(state.post_dpf)}  {bar(state.post_dpf, 800)}")
            if state.pre_dpf is not None and state.post_dpf is not None:
                delta = abs(state.pre_dpf - state.post_dpf)
                lines.append(f"  DELTA T   °C   {delta:>6.1f}")

    lines += [
        "",
        "REGENERATION",
        "",
        f"  STATUS: {state.regen_status}",
    ]

    return "\n".join(lines)
