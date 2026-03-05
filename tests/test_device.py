from unittest.mock import MagicMock

from odb_tui.services.device import detect_obd_device


def _make_port(device="/dev/ttyUSB0", vid=None, pid=None, product=None, manufacturer=None):
    port = MagicMock()
    port.device = device
    port.vid = vid
    port.pid = pid
    port.product = product
    port.manufacturer = manufacturer
    return port


def test_detect_known_device(mocker):
    port = _make_port(device="/dev/ttyUSB0", product="vLinker FS USB")
    mocker.patch("odb_tui.services.device.list_ports.comports", return_value=[port])
    device, vid, pid = detect_obd_device()
    assert device == "/dev/ttyUSB0"


def test_detect_no_device(mocker):
    mocker.patch("odb_tui.services.device.list_ports.comports", return_value=[])
    device, vid, pid = detect_obd_device()
    assert device is None
    assert vid is None
    assert pid is None


def test_detect_by_vid_pid(mocker):
    port = _make_port(device="/dev/ttyUSB1", vid=0x0403, pid=0x6015)
    mocker.patch("odb_tui.services.device.list_ports.comports", return_value=[port])
    device, vid, pid = detect_obd_device()
    assert device == "/dev/ttyUSB1"
    assert vid == "0403"
    assert pid == "6015"
