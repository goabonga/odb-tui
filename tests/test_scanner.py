"""Tests for scanner service."""

from odb_read.services.scanner import ScanProgress, ScanService


class TestScanProgress:
    """Tests for ScanProgress dataclass defaults."""

    def test_defaults(self):
        """Verify all default field values on a fresh ScanProgress."""
        p = ScanProgress()
        assert p.scanning is False
        assert p.stop_requested is False
        assert p.status == ""
        assert p.phase == ""
        assert p.hits == 0
        assert p.raw_log == []
        assert p.results == []


class TestScanService:
    """Tests for ScanService stop-request mechanism."""

    def test_request_stop(self):
        """Set stop_requested flag and update status on request_stop()."""
        svc = ScanService()
        assert svc.progress.stop_requested is False
        svc.request_stop()
        assert svc.progress.stop_requested is True
        assert "ARRET" in svc.progress.status
