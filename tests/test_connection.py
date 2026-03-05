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


def test_discover_supported_commands(mocker):
    mock_cmd1 = MagicMock()
    mock_cmd1.name = "RPM"
    mock_cmd1.pid = 0x0C
    mock_cmd1.desc = "Engine RPM"
    mock_cmd2 = MagicMock()
    mock_cmd2.name = "SPEED"
    mock_cmd2.pid = 0x0D
    mock_cmd2.desc = "Vehicle Speed"
    mock_conn = MagicMock()
    mock_conn.is_connected.return_value = True
    mock_conn.supports.side_effect = lambda cmd: cmd.name == "RPM"
    mocker.patch("odb_tui.services.connection.obd.OBD", return_value=mock_conn)
    mocker.patch("odb_tui.services.connection.obd.commands.__getitem__", return_value=[mock_cmd1, mock_cmd2])
    svc = OBDConnectionService()
    svc.connect("/dev/ttyUSB0")
    result = svc.discover_supported_commands()
    assert result.total >= 2
    assert result.supported_count >= 1


def test_discover_supported_commands_not_connected():
    svc = OBDConnectionService()
    result = svc.discover_supported_commands()
    assert result.total == 0
