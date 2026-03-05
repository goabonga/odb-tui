"""Error panel builder (right sidebar)."""

from odb_read.models.vehicle import VehicleState


def build_error_panel(state: VehicleState) -> str:
    """Build the error sidebar text listing stored DTCs or 'No errors'."""
    lines = ["ERRORS\n"]

    if state.connection_status not in ("DISCONNECTED", "NO DEVICE", "FAILED"):
        if state.dtc_list:
            for code, desc in state.dtc_list:
                lines.append(code)
                lines.append(desc)
                lines.append("")
        else:
            lines.append("No errors")
    else:
        lines.append("--")

    return "\n".join(lines)
