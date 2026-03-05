"""Tests for CSV logger service."""

import csv

from odb_read.models.log_config import LogConfig
from odb_read.services.csv_logger import CSVLoggerService, CSV_HEADER


class TestCSVLoggerService:
    """Tests for CSVLoggerService -- open, write, close lifecycle."""

    def test_open_creates_file(self, tmp_path):
        """Create a CSV file on disk when open() is called."""
        cfg = LogConfig(log_dir=str(tmp_path), enable_csv=True)
        svc = CSVLoggerService(cfg)
        svc.open()
        assert svc.logging is True
        csv_files = list(tmp_path.glob("obd_log_*.csv"))
        assert len(csv_files) == 1
        svc.close()

    def test_open_writes_header(self, tmp_path):
        """Write the CSV header row immediately on open."""
        cfg = LogConfig(log_dir=str(tmp_path), enable_csv=True)
        svc = CSVLoggerService(cfg)
        svc.open()
        svc.close()

        csv_file = list(tmp_path.glob("obd_log_*.csv"))[0]
        with open(csv_file) as f:
            reader = csv.reader(f)
            header = next(reader)
        assert header == CSV_HEADER

    def test_write_row(self, tmp_path):
        """Write a data row that appears after the header."""
        cfg = LogConfig(log_dir=str(tmp_path), enable_csv=True)
        svc = CSVLoggerService(cfg)
        svc.open()
        svc.write_row(["2024-01-01", 3000, 75.0])
        svc.close()

        csv_file = list(tmp_path.glob("obd_log_*.csv"))[0]
        with open(csv_file) as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            row = next(reader)
        assert row[0] == "2024-01-01"
        assert row[1] == "3000"
        assert row[2] == "75.0"

    def test_close_sets_logging_false(self, tmp_path):
        """Set logging flag to False after close."""
        cfg = LogConfig(log_dir=str(tmp_path), enable_csv=True)
        svc = CSVLoggerService(cfg)
        svc.open()
        assert svc.logging is True
        svc.close()
        assert svc.logging is False

    def test_write_row_after_close_no_error(self, tmp_path):
        """Silently ignore write_row calls after close."""
        cfg = LogConfig(log_dir=str(tmp_path), enable_csv=True)
        svc = CSVLoggerService(cfg)
        svc.open()
        svc.close()
        # Should not raise
        svc.write_row(["data"])

    def test_close_without_open(self):
        """Handle close gracefully when open was never called."""
        cfg = LogConfig(enable_csv=True)
        svc = CSVLoggerService(cfg)
        # Should not raise
        svc.close()
        assert svc.logging is False

    def test_open_disabled_does_nothing(self, tmp_path):
        """Skip file creation when enable_csv is False."""
        cfg = LogConfig(log_dir=str(tmp_path), enable_csv=False)
        svc = CSVLoggerService(cfg)
        svc.open()
        assert svc.logging is False
        csv_files = list(tmp_path.glob("obd_log_*.csv"))
        assert len(csv_files) == 0

    def test_custom_filename(self, tmp_path):
        """Use a custom filename instead of the timestamped default."""
        cfg = LogConfig(log_dir=str(tmp_path), enable_csv=True, csv_filename="custom.csv")
        svc = CSVLoggerService(cfg)
        svc.open()
        assert svc.logging is True
        assert (tmp_path / "custom.csv").exists()
        svc.close()
