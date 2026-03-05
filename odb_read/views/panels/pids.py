"""Supported PIDs panel builder."""

import obd

from odb_read.services.connection import OBDConnectionService


def build_pids_panel(connection: OBDConnectionService) -> str:
    """Build the supported-PIDs panel text listing all OBD commands the ECU supports."""
    lines = ["COMMANDES OBD SUPPORTEES", ""]
    if connection.is_connected:
        total_supported = 0
        for mode_idx in range(1, len(obd.commands)):
            try:
                mode_cmds = obd.commands[mode_idx]
            except (IndexError, KeyError):
                continue
            if not mode_cmds:
                continue
            supported = []
            for cmd in mode_cmds:
                if cmd and connection.supports(cmd):
                    supported.append(cmd)
            if not supported:
                continue
            total_supported += len(supported)
            lines.append(f"MODE {mode_idx:02d} ({len(supported)} PIDs)")
            lines.append("-" * 56)
            for cmd in supported:
                pid_hex = cmd.command.decode() if isinstance(cmd.command, bytes) else str(cmd.command)
                lines.append(f"  {pid_hex:>6}  {cmd.name:<30}  {cmd.desc}")
            lines.append("")
        lines.insert(2, f"  Total: {total_supported} PIDs supportes")
        lines.insert(3, "")
    else:
        lines.append("  Connecter le vehicule pour scanner les PIDs")

    return "\n".join(lines)
