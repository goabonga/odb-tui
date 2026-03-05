"""Tests for OBD device detection."""

from unittest.mock import MagicMock, patch

from odb_read.services.device import detect_obd_device


def _make_port(device="/dev/ttyUSB0", vid=None, pid=None, product=None, manufacturer=None):
    """Create a mock serial port with the given attributes."""
    port = MagicMock()
    port.device = device
    port.vid = vid
    port.pid = pid
    port.product = product
    port.manufacturer = manufacturer
    return port


class TestDetectObdDevice:
    """Tests for detect_obd_device() -- serial port auto-detection."""

    @patch("odb_read.services.device.serial.tools.list_ports.comports")
    def test_vid_pid_match(self, mock_comports):
        """Detect a device by matching VID/PID."""
        mock_comports.return_value = [_make_port(vid=0x0403, pid=0x6015)]
        device, vid, pid = detect_obd_device()
        assert device == "/dev/ttyUSB0"
        assert vid == "0403"
        assert pid == "6015"

    @patch("odb_read.services.device.serial.tools.list_ports.comports")
    def test_product_vlinker(self, mock_comports):
        """Detect a device by product name containing 'vLinker'."""
        mock_comports.return_value = [_make_port(product="vLinker FS")]
        device, vid, pid = detect_obd_device()
        assert device == "/dev/ttyUSB0"

    @patch("odb_read.services.device.serial.tools.list_ports.comports")
    def test_manufacturer_vgatemall(self, mock_comports):
        """Detect a device by manufacturer name 'vgatemall'."""
        mock_comports.return_value = [_make_port(manufacturer="vgatemall")]
        device, vid, pid = detect_obd_device()
        assert device == "/dev/ttyUSB0"

    @patch("odb_read.services.device.serial.tools.list_ports.comports")
    def test_no_match(self, mock_comports):
        """Return None when no ports match known OBD adapters."""
        mock_comports.return_value = [_make_port(vid=0x1234, pid=0x5678, product="Other", manufacturer="Other")]
        device, vid, pid = detect_obd_device()
        assert device is None
        assert vid is None
        assert pid is None

    @patch("odb_read.services.device.serial.tools.list_ports.comports")
    def test_empty_ports(self, mock_comports):
        """Return None when no serial ports are available."""
        mock_comports.return_value = []
        device, vid, pid = detect_obd_device()
        assert device is None
        assert vid is None
        assert pid is None
