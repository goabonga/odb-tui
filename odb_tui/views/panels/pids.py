"""Panel builder for supported OBD commands display."""

from __future__ import annotations

from odb_tui.models.supported_commands import SupportedCommands


def build_pids_panel(supported_commands: SupportedCommands | None) -> str:
    """Build a text panel listing all OBD commands grouped by mode with support checkboxes."""
    if supported_commands is None:
        return "Not connected"

    lines: list[str] = []
    lines.append(f"  Total: {supported_commands.supported_count} / {supported_commands.total} supported")
    lines.append("")

    for mode_name, cmds in supported_commands.modes.items():
        mode_supported = sum(1 for c in cmds if c.supported)
        lines.append(f"{mode_name} ({mode_supported} / {len(cmds)})")
        lines.append("─" * 60)
        for cmd in cmds:
            check = "[x]" if cmd.supported else "[ ]"
            lines.append(f"  {check}  {cmd.pid:<6}  {cmd.name:<25} {cmd.description}")
        lines.append("")

    return "\n".join(lines)
