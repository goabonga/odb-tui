from unittest.mock import MagicMock

from odb_tui.services.connection import OBDConnectionService


def test_initial_state():
    svc = OBDConnectionService()
    assert svc.is_connected is False
    assert svc.connection is None


def test_connect_success(mocker):
    mock_conn = MagicMock()
    mock_conn.is_connected.return_value = True
    mocker.patch("odb_tui.services.connection.obd.OBD", return_value=mock_conn)
    svc = OBDConnectionService()
    result = svc.connect("/dev/ttyUSB0")
    assert result is True
    assert svc.is_connected is True


def test_connect_failure(mocker):
    mocker.patch("odb_tui.services.connection.obd.OBD", side_effect=Exception("connection error"))
    svc = OBDConnectionService()
    result = svc.connect("/dev/ttyUSB0")
    assert result is False
    assert svc.is_connected is False


def test_disconnect(mocker):
    mock_conn = MagicMock()
    mock_conn.is_connected.return_value = True
    mocker.patch("odb_tui.services.connection.obd.OBD", return_value=mock_conn)
    svc = OBDConnectionService()
    svc.connect("/dev/ttyUSB0")
    svc.disconnect()
    assert svc.is_connected is False


def test_disconnect_when_not_connected():
    svc = OBDConnectionService()
    svc.disconnect()
    assert svc.is_connected is False
