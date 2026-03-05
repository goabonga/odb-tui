"""Tests for file logger functions."""

from unittest.mock import MagicMock, patch

from odb_read.models.log_config import LogConfig
from odb_read.services.file_logger import save_dtc_to_file, save_supported_pids


class TestSaveDtcToFile:
    """Tests for save_dtc_to_file() -- DTC log file creation."""

    def test_new_dtcs_creates_file(self, tmp_path):
        """Create a DTC log file when new codes are detected."""
        cfg = LogConfig(log_dir=str(tmp_path), enable_dtc=True)
        dtc_list = [("P0420", "Catalyst Efficiency Below Threshold")]
        current_dtc_list = []
        last_set = set()

        new_set = save_dtc_to_file(dtc_list, current_dtc_list, "BMW", "/dev/ttyUSB0", last_set, cfg)

        assert "P0420" in new_set
        dtc_files = list(tmp_path.glob("dtc_*.log"))
        assert len(dtc_files) == 1

        content = dtc_files[0].read_text()
        assert "P0420" in content
        assert "BMW" in content

    def test_same_set_no_file(self, tmp_path):
        """Skip file creation when DTC set has not changed."""
        cfg = LogConfig(log_dir=str(tmp_path), enable_dtc=True)
        dtc_list = [("P0420", "desc")]
        last_set = {"P0420"}

        new_set = save_dtc_to_file(dtc_list, [], "BMW", "/dev/ttyUSB0", last_set, cfg)
        assert new_set == last_set
        dtc_files = list(tmp_path.glob("dtc_*.log"))
        assert len(dtc_files) == 0

    def test_empty_dtcs_no_file(self, tmp_path):
        """Skip file creation when there are no DTCs."""
        cfg = LogConfig(log_dir=str(tmp_path), enable_dtc=True)
        new_set = save_dtc_to_file([], [], "BMW", "/dev/ttyUSB0", set(), cfg)
        assert new_set == set()
        dtc_files = list(tmp_path.glob("dtc_*.log"))
        assert len(dtc_files) == 0

    def test_current_dtcs_included(self, tmp_path):
        """Include current (active) DTCs in the log file."""
        cfg = LogConfig(log_dir=str(tmp_path), enable_dtc=True)
        new_set = save_dtc_to_file(
            [], [("P0300", "Random Misfire")], "Test", "/dev/ttyUSB0", set(), cfg
        )
        assert "P0300" in new_set
        dtc_files = list(tmp_path.glob("dtc_*.log"))
        assert len(dtc_files) == 1
        content = dtc_files[0].read_text()
        assert "P0300" in content

    def test_disabled_no_file(self, tmp_path):
        """Skip file creation when enable_dtc is False."""
        cfg = LogConfig(log_dir=str(tmp_path), enable_dtc=False)
        dtc_list = [("P0420", "desc")]
        last_set = set()

        new_set = save_dtc_to_file(dtc_list, [], "BMW", "/dev/ttyUSB0", last_set, cfg)
        assert new_set == last_set
        dtc_files = list(tmp_path.glob("dtc_*.log"))
        assert len(dtc_files) == 0

    def test_custom_filename(self, tmp_path):
        """Use a custom filename for the DTC log."""
        cfg = LogConfig(log_dir=str(tmp_path), enable_dtc=True, dtc_filename="my_dtc.log")
        dtc_list = [("P0420", "desc")]
        save_dtc_to_file(dtc_list, [], "BMW", "/dev/ttyUSB0", set(), cfg)
        assert (tmp_path / "my_dtc.log").exists()


class TestSaveSupportedPids:
    """Tests for save_supported_pids() -- supported PID log file creation."""

    def test_creates_file(self, tmp_path):
        """Create a PID log file listing supported commands."""
        cfg = LogConfig(log_dir=str(tmp_path), enable_pids=True)

        mock_conn_svc = MagicMock()
        mock_conn_svc.protocol_name.return_value = "ISO 15765-4 (CAN 11/500)"

        mock_conn = MagicMock()
        mock_conn_svc.connection = mock_conn
        mock_conn.supports.return_value = False

        with patch("odb_read.services.file_logger.obd") as mock_obd:
            mock_cmd = MagicMock()
            mock_cmd.command = b"0100"
            mock_cmd.name = "PIDS_A"
            mock_cmd.desc = "Supported PIDs [01-20]"
            mock_conn.supports.side_effect = lambda c: c == mock_cmd

            mock_obd.commands.__getitem__ = MagicMock(side_effect=KeyError)
            def getitem(mode):
                if mode == 1:
                    return [mock_cmd]
                raise KeyError
            mock_obd.commands.__getitem__ = getitem

            save_supported_pids(mock_conn_svc, "Test Car", "/dev/ttyUSB0", "0403", "6015", cfg)

        pid_files = list(tmp_path.glob("pids_supported_*.log"))
        assert len(pid_files) == 1
        content = pid_files[0].read_text()
        assert "Test Car" in content

    def test_disabled_no_file(self, tmp_path):
        """Skip file creation when enable_pids is False."""
        cfg = LogConfig(log_dir=str(tmp_path), enable_pids=False)
        mock_conn_svc = MagicMock()
        save_supported_pids(mock_conn_svc, "Test Car", "/dev/ttyUSB0", "0403", "6015", cfg)
        pid_files = list(tmp_path.glob("pids_supported_*.log"))
        assert len(pid_files) == 0
