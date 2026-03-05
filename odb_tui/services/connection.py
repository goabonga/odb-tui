"""OBD-II connection management service."""

from __future__ import annotations

import obd

from odb_tui.models.supported_commands import CommandStatus, SupportedCommands

MODE_NAMES: dict[int, str] = {
    1: "Mode 01 — Live Data",
    2: "Mode 02 — Freeze Frame",
    3: "Mode 03 — DTCs",
    4: "Mode 04 — Clear DTCs",
    6: "Mode 06 — Test Results",
    7: "Mode 07 — Pending DTCs",
    9: "Mode 09 — Vehicle Info",
}


class OBDConnectionService:
    """Wrap python-obd to manage a single OBD-II connection."""

    def __init__(self) -> None:
        self.connection: obd.OBD | None = None

    @property
    def is_connected(self) -> bool:
        return self.connection is not None and self.connection.is_connected()

    def connect(self, port: str) -> bool:
        try:
            self.connection = obd.OBD(port, fast=False)
            return bool(self.connection.is_connected())
        except Exception:
            self.connection = None
            return False

    def disconnect(self) -> None:
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
        self.connection = None

    def discover_supported_commands(self) -> SupportedCommands:
        """Scan all OBD modes and return which commands are supported by the vehicle."""
        if not self.is_connected or self.connection is None:
            return SupportedCommands()

        modes: dict[str, list[CommandStatus]] = {}

        for mode_num in (1, 2, 3, 4, 6, 7, 9):
            mode_name = MODE_NAMES.get(mode_num, f"Mode {mode_num:02d}")
            cmds: list[CommandStatus] = []
            try:
                mode_commands = obd.commands[mode_num]
            except (KeyError, IndexError):
                continue
            for cmd in mode_commands:
                if cmd is None:
                    continue
                pid_hex = f"0x{cmd.pid:02X}" if hasattr(cmd, "pid") and cmd.pid is not None else "-"
                supported = bool(self.connection.supports(cmd))
                cmds.append(CommandStatus(
                    name=str(cmd.name),
                    pid=pid_hex,
                    description=str(cmd.desc),
                    supported=supported,
                ))
            if cmds:
                modes[mode_name] = cmds

        # ELM adapter commands
        elm_cmds: list[CommandStatus] = []
        for elm_name in ("ELM_VERSION", "ELM_VOLTAGE"):
            cmd = getattr(obd.commands, elm_name, None)
            if cmd is not None:
                supported = bool(self.connection.supports(cmd))
                elm_cmds.append(CommandStatus(
                    name=str(cmd.name),
                    pid="-",
                    description=str(cmd.desc),
                    supported=supported,
                ))
        if elm_cmds:
            modes["ELM — Adapter"] = elm_cmds

        return SupportedCommands(modes=modes)
