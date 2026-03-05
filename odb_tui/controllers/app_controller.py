from odb_tui.services.connection import OBDConnectionService
from odb_tui.services.device import detect_obd_device


class AppController:

    def __init__(self) -> None:
        self.conn = OBDConnectionService()
        self.status = "DISCONNECTED"
        self.port = "-"
        self.vid = "-"
        self.pid = "-"

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
        else:
            self.status = "FAILED"

    def disconnect(self) -> None:
        self.conn.disconnect()
        self.status = "DISCONNECTED"
