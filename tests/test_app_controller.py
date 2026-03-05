"""Tests for app controller."""

from unittest.mock import MagicMock, patch

from odb_read.controllers.app_controller import AppController
from odb_read.models.log_config import LogConfig
from odb_read.models.presets import TIRE_PRESETS, GEARBOX_PRESETS


class TestCycleTire:
    """Tests for cycle_tire() -- tire preset rotation."""

    def test_increments(self):
        """Advance tire index by one."""
        ctrl = AppController()
        initial = ctrl.tire_index
        ctrl.cycle_tire()
        assert ctrl.tire_index == (initial + 1) % len(TIRE_PRESETS)

    def test_wraps_around(self):
        """Wrap tire index back to zero at the end of the list."""
        ctrl = AppController()
        ctrl.tire_index = len(TIRE_PRESETS) - 1
        ctrl.cycle_tire()
        assert ctrl.tire_index == 0


class TestCycleGearbox:
    """Tests for cycle_gearbox() -- gearbox preset rotation."""

    def test_increments(self):
        """Advance gearbox index by one."""
        ctrl = AppController()
        initial = ctrl.gearbox_index
        ctrl.cycle_gearbox()
        assert ctrl.gearbox_index == (initial + 1) % len(GEARBOX_PRESETS)

    def test_wraps_around(self):
        """Wrap gearbox index back to zero at the end of the list."""
        ctrl = AppController()
        ctrl.gearbox_index = len(GEARBOX_PRESETS) - 1
        ctrl.cycle_gearbox()
        assert ctrl.gearbox_index == 0


class TestToggleCsv:
    """Tests for toggle_csv() -- CSV logging on/off toggle."""

    def test_off_on_off(self, tmp_path, monkeypatch):
        """Toggle CSV logging from off to on and back to off."""
        monkeypatch.chdir(tmp_path)
        cfg = LogConfig(enable_csv=True)
        ctrl = AppController(log_config=cfg)
        assert ctrl.csv_logger.logging is False
        ctrl.toggle_csv()
        assert ctrl.csv_logger.logging is True
        ctrl.toggle_csv()
        assert ctrl.csv_logger.logging is False


class TestLogConfig:
    """Tests for AppController log configuration defaults and overrides."""

    def test_default_log_config(self):
        """All logging flags are disabled by default."""
        ctrl = AppController()
        assert ctrl.log_config.enable_elm is False
        assert ctrl.log_config.enable_csv is False
        assert ctrl.log_config.enable_pids is False
        assert ctrl.log_config.enable_dtc is False
        assert ctrl.log_config.enable_scan is False

    def test_explicit_log_config(self):
        """Pass an explicit LogConfig to override defaults."""
        cfg = LogConfig(enable_pids=True, enable_dtc=True)
        ctrl = AppController(log_config=cfg)
        assert ctrl.log_config.enable_pids is True
        assert ctrl.log_config.enable_dtc is True


class TestConnect:
    """Tests for connect() -- device detection and OBD connection."""

    @patch("odb_read.controllers.app_controller.save_supported_pids")
    @patch("odb_read.controllers.app_controller.detect_obd_device")
    def test_no_device(self, mock_detect, mock_save):
        """Return False and set status to NO DEVICE when no adapter is found."""
        mock_detect.return_value = (None, None, None)
        ctrl = AppController()
        result = ctrl.connect()
        assert result is False
        assert ctrl.status == "NO DEVICE"

    @patch("odb_read.controllers.app_controller.save_supported_pids")
    @patch("odb_read.controllers.app_controller.detect_obd_device")
    def test_connect_success(self, mock_detect, mock_save):
        """Return True and store vehicle name on successful connection."""
        mock_detect.return_value = ("/dev/ttyUSB0", "0403", "6015")
        ctrl = AppController()
        ctrl.conn = MagicMock()
        ctrl.conn.connect.return_value = True
        ctrl.conn.read_vehicle_name.return_value = "BMW (VIN: WBA123)"

        result = ctrl.connect()
        assert result is True
        assert ctrl.status == "CONNECTED"
        assert ctrl.vehicle_name == "BMW (VIN: WBA123)"

    @patch("odb_read.controllers.app_controller.save_supported_pids")
    @patch("odb_read.controllers.app_controller.detect_obd_device")
    def test_connect_no_file_logging_by_default(self, mock_detect, mock_save):
        """Call save_supported_pids even when file logging is disabled by default."""
        mock_detect.return_value = ("/dev/ttyUSB0", "0403", "6015")
        ctrl = AppController()
        ctrl.conn = MagicMock()
        ctrl.conn.connect.return_value = True
        ctrl.conn.read_vehicle_name.return_value = "BMW"

        ctrl.connect()
        # save_supported_pids is always called, but enable_pids=False by default
        # so the function returns early
        mock_save.assert_called_once()

    @patch("odb_read.controllers.app_controller.save_supported_pids")
    @patch("odb_read.controllers.app_controller.detect_obd_device")
    def test_connect_with_pids_logging(self, mock_detect, mock_save):
        """Call save_supported_pids when PID logging is enabled."""
        mock_detect.return_value = ("/dev/ttyUSB0", "0403", "6015")
        cfg = LogConfig(enable_pids=True)
        ctrl = AppController(log_config=cfg)
        ctrl.conn = MagicMock()
        ctrl.conn.connect.return_value = True
        ctrl.conn.read_vehicle_name.return_value = "BMW"

        ctrl.connect()
        mock_save.assert_called_once()

    @patch("odb_read.controllers.app_controller.save_supported_pids")
    @patch("odb_read.controllers.app_controller.detect_obd_device")
    def test_connect_failed(self, mock_detect, mock_save):
        """Return False and set status to FAILED when connection fails."""
        mock_detect.return_value = ("/dev/ttyUSB0", "0403", "6015")
        ctrl = AppController()
        ctrl.conn = MagicMock()
        ctrl.conn.connect.return_value = False

        result = ctrl.connect()
        assert result is False
        assert ctrl.status == "FAILED"


class TestDisconnect:
    """Tests for disconnect() -- cleanup on disconnection."""

    def test_sets_disconnected(self):
        """Set status to DISCONNECTED and close logger and connection."""
        ctrl = AppController()
        ctrl.csv_logger = MagicMock()
        ctrl.conn = MagicMock()
        ctrl.disconnect()
        assert ctrl.status == "DISCONNECTED"
        ctrl.csv_logger.close.assert_called_once()
        ctrl.conn.disconnect.assert_called_once()
