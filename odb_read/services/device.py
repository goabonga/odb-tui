"""OBD device auto-detection."""

import serial.tools.list_ports


def detect_obd_device():
    """Detect a known OBD-II adapter (vLinker etc.) and return (device, vid, pid)."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        vid = f"{port.vid:04x}" if port.vid else "----"
        pid = f"{port.pid:04x}" if port.pid else "----"
        if (
            (vid == "0403" and pid == "6015")
            or "vLinker" in (port.product or "")
            or "vgatemall" in (port.manufacturer or "")
        ):
            return port.device, vid, pid
    return None, None, None
