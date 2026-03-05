import serial.tools.list_ports as list_ports


def detect_obd_device() -> tuple[str | None, str | None, str | None]:
    ports = list_ports.comports()
    for port in ports:
        vid = f"{port.vid:04x}" if port.vid else None
        pid = f"{port.pid:04x}" if port.pid else None
        if (
            (vid == "0403" and pid == "6015")
            or "vLinker" in (port.product or "")
            or "vgatemall" in (port.manufacturer or "")
        ):
            return port.device, vid, pid
    return None, None, None
