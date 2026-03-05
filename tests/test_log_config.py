"""Tests for LogConfig dataclass."""

import os

from odb_read.models.log_config import LogConfig


class TestLogConfigDefaults:
    """Tests for LogConfig default field values."""

    def test_all_disabled_by_default(self):
        """All logging enable flags default to False."""
        cfg = LogConfig()
        assert cfg.enable_elm is False
        assert cfg.enable_csv is False
        assert cfg.enable_pids is False
        assert cfg.enable_dtc is False
        assert cfg.enable_scan is False

    def test_default_log_dir(self):
        """Default log directory is the current directory."""
        cfg = LogConfig()
        assert cfg.log_dir == "."

    def test_all_filenames_none(self):
        """All optional filename overrides default to None."""
        cfg = LogConfig()
        assert cfg.elm_filename is None
        assert cfg.csv_filename is None
        assert cfg.pids_filename is None
        assert cfg.dtc_filename is None
        assert cfg.scan_filename is None


class TestLogConfigPath:
    """Tests for LogConfig.path() -- log file path resolution."""

    def test_default_dir_default_name(self):
        """Build a path using the default directory and given filename."""
        cfg = LogConfig()
        assert cfg.path("test.log") == os.path.join(".", "test.log")

    def test_custom_dir(self):
        """Build a path using a custom log directory."""
        cfg = LogConfig(log_dir="/tmp/logs")
        assert cfg.path("test.log") == "/tmp/logs/test.log"

    def test_override_filename(self):
        """Use an override filename instead of the default."""
        cfg = LogConfig(log_dir="/tmp/logs")
        assert cfg.path("test.log", "custom.log") == "/tmp/logs/custom.log"

    def test_override_none_uses_default(self):
        """Fall back to the default filename when override is None."""
        cfg = LogConfig(log_dir="/tmp/logs")
        assert cfg.path("test.log", None) == "/tmp/logs/test.log"
