"""Application controller orchestrating OBD services."""

from __future__ import annotations

from odb_tui.models.supported_commands import SupportedCommands
from odb_tui.services.connection import OBDConnectionService
from odb_tui.services.device import detect_obd_device


class AppController:
    """Coordinate device detection and connection lifecycle."""

    def __init__(self) -> None:
        self.conn = OBDConnectionService()
        self.status = "DISCONNECTED"
        self.port = "-"
        self.vid = "-"
        self.pid = "-"
        self.supported_commands: SupportedCommands | None = None

    def connect(self) -> None:
        self.status = "CONNECTING..."
        device, vid, pid = detect_obd_device()
        if not device:
            self.status = "NO DEVICE"
            return
        self.port = device
        self.vid = vid or "-"
        self.pid = pid or "-"
        if self.conn.connect(device):
            self.status = "CONNECTED"
            self.supported_commands = self.conn.discover_supported_commands()
        else:
            self.status = "FAILED"

    def disconnect(self) -> None:
        self.conn.disconnect()
        self.status = "DISCONNECTED"
        self.supported_commands = None
