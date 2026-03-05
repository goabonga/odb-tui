"""Tests for OBD connection service."""

from unittest.mock import MagicMock, patch

from odb_read.services.connection import OBDConnectionService


def _make_response(value=None, is_null=False):
    """Create a mock OBD response with the given value and null state."""
    resp = MagicMock()
    resp.is_null.return_value = is_null
    resp.value = value
    return resp


class TestSafe:
    """Tests for safe() -- guarded OBD query returning magnitude."""

    def test_connected_supported_returns_magnitude(self):
        """Return the magnitude when connected and command is supported."""
        svc = OBDConnectionService()
        svc.connection = MagicMock()
        svc.connection.is_connected.return_value = True
        svc.connection.supports.return_value = True

        val = MagicMock()
        val.magnitude = 42.0
        svc.connection.query.return_value = _make_response(value=val)

        cmd = MagicMock()
        assert svc.safe(cmd) == 42.0

    def test_disconnected_returns_none(self):
        """Return None when there is no active connection."""
        svc = OBDConnectionService()
        svc.connection = None
        assert svc.safe(MagicMock()) is None

    def test_not_supported_returns_none(self):
        """Return None when the command is not supported by the ECU."""
        svc = OBDConnectionService()
        svc.connection = MagicMock()
        svc.connection.is_connected.return_value = True
        svc.connection.supports.return_value = False
        assert svc.safe(MagicMock()) is None

    def test_exception_returns_none(self):
        """Return None when the query raises an exception."""
        svc = OBDConnectionService()
        svc.connection = MagicMock()
        svc.connection.is_connected.return_value = True
        svc.connection.supports.return_value = True
        svc.connection.query.side_effect = Exception("timeout")
        assert svc.safe(MagicMock()) is None

    def test_null_response_returns_none(self):
        """Return None when the OBD response is null."""
        svc = OBDConnectionService()
        svc.connection = MagicMock()
        svc.connection.is_connected.return_value = True
        svc.connection.supports.return_value = True
        svc.connection.query.return_value = _make_response(is_null=True)
        assert svc.safe(MagicMock()) is None


class TestSafeRaw:
    """Tests for safe_raw() -- guarded OBD query returning raw value."""

    def test_returns_raw_value(self):
        """Return the raw response value without extracting magnitude."""
        svc = OBDConnectionService()
        svc.connection = MagicMock()
        svc.connection.is_connected.return_value = True
        svc.connection.supports.return_value = True
        svc.connection.query.return_value = _make_response(value="raw_data")
        assert svc.safe_raw(MagicMock()) == "raw_data"

    def test_disconnected_returns_none(self):
        """Return None when there is no active connection."""
        svc = OBDConnectionService()
        svc.connection = None
        assert svc.safe_raw(MagicMock()) is None


class TestSafeFirst:
    """Tests for safe_first() -- try multiple commands, return first supported."""

    def test_first_supported(self):
        """Return the result from the first supported command."""
        svc = OBDConnectionService()
        svc.connection = MagicMock()
        svc.connection.is_connected.return_value = True
        svc.connection.supports.side_effect = [False, True]

        val = MagicMock()
        val.magnitude = 99.0
        svc.connection.query.return_value = _make_response(value=val)

        cmd1, cmd2 = MagicMock(), MagicMock()
        assert svc.safe_first(cmd1, cmd2) == 99.0

    def test_none_supported(self):
        """Return None when no commands are supported."""
        svc = OBDConnectionService()
        svc.connection = MagicMock()
        svc.connection.is_connected.return_value = True
        svc.connection.supports.return_value = False
        assert svc.safe_first(MagicMock(), MagicMock()) is None


class TestSafeCustom:
    """Tests for safe_custom() -- forced query with null-response caching."""

    def test_force_true_ok(self):
        """Return the value when query succeeds with force=True."""
        svc = OBDConnectionService()
        svc.connection = MagicMock()
        svc.connection.is_connected.return_value = True
        svc.connection.query.return_value = _make_response(value={"s1": 450.0})

        cmd = MagicMock()
        result = svc.safe_custom(cmd)
        assert result == {"s1": 450.0}
        svc.connection.query.assert_called_once_with(cmd, force=True)

    def test_null_caches_and_returns_none(self):
        """Cache a null response so subsequent calls skip the query."""
        svc = OBDConnectionService()
        svc.connection = MagicMock()
        svc.connection.is_connected.return_value = True
        svc.connection.query.return_value = _make_response(is_null=True)

        cmd = MagicMock()
        assert svc.safe_custom(cmd) is None
        # Second call should be cached
        assert svc.safe_custom(cmd) is None
        # query only called once due to cache
        assert svc.connection.query.call_count == 1

    def test_disconnected_returns_none(self):
        """Return None when there is no active connection."""
        svc = OBDConnectionService()
        svc.connection = None
        assert svc.safe_custom(MagicMock()) is None


class TestReadVehicleName:
    """Tests for read_vehicle_name() -- VIN query and manufacturer lookup."""

    @patch("odb_read.services.connection.obd")
    def test_vin_found(self, mock_obd):
        """Return manufacturer and VIN when query succeeds."""
        svc = OBDConnectionService()
        svc.connection = MagicMock()

        resp = MagicMock()
        resp.is_null.return_value = False
        resp.value = "WBA12345678901234"
        svc.connection.query.return_value = resp

        result = svc.read_vehicle_name()
        assert "BMW" in result
        assert "WBA12345678901234" in result

    @patch("odb_read.services.connection.obd")
    def test_null_vin(self, mock_obd):
        """Return '-' when the VIN response is null."""
        svc = OBDConnectionService()
        svc.connection = MagicMock()

        resp = MagicMock()
        resp.is_null.return_value = True
        svc.connection.query.return_value = resp

        assert svc.read_vehicle_name() == "-"

    @patch("odb_read.services.connection.obd")
    def test_exception(self, mock_obd):
        """Return '-' when the VIN query raises an exception."""
        svc = OBDConnectionService()
        svc.connection = MagicMock()
        svc.connection.query.side_effect = Exception("fail")
        assert svc.read_vehicle_name() == "-"
