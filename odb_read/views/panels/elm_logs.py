"""ELM logs panel builder."""

from odb_read.views.logging_setup import OBDLogHandler


def build_elm_log_panel(log_handler: OBDLogHandler, elm_log_file: str) -> str:
    """Build the ELM log panel text showing the last 20 captured log messages."""
    lines = ["ELM LOGS", f"File: {elm_log_file}", ""]
    if log_handler.logs:
        for line in log_handler.logs[-20:]:
            lines.append(line)
    else:
        lines.append("No logs yet")
    return "\n".join(lines)
