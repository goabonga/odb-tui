from unittest.mock import MagicMock

from odb_tui.controllers.app_controller import AppController


def test_initial_state():
    ctrl = AppController()
    assert ctrl.status == "DISCONNECTED"
    assert ctrl.port == "-"
    assert ctrl.vid == "-"
    assert ctrl.pid == "-"


def test_connect_success(mocker):
    mocker.patch(
        "odb_tui.controllers.app_controller.detect_obd_device",
        return_value=("/dev/ttyUSB0", "0403", "6015"),
    )
    mock_conn = MagicMock()
    mock_conn.is_connected.return_value = True
    mocker.patch("odb_tui.services.connection.obd.OBD", return_value=mock_conn)
    ctrl = AppController()
    ctrl.connect()
    assert ctrl.status == "CONNECTED"
    assert ctrl.port == "/dev/ttyUSB0"
    assert ctrl.vid == "0403"
    assert ctrl.pid == "6015"


def test_connect_no_device(mocker):
    mocker.patch(
        "odb_tui.controllers.app_controller.detect_obd_device",
        return_value=(None, None, None),
    )
    ctrl = AppController()
    ctrl.connect()
    assert ctrl.status == "NO DEVICE"


def test_connect_failure(mocker):
    mocker.patch(
        "odb_tui.controllers.app_controller.detect_obd_device",
        return_value=("/dev/ttyUSB0", "0403", "6015"),
    )
    mocker.patch("odb_tui.services.connection.obd.OBD", side_effect=Exception("fail"))
    ctrl = AppController()
    ctrl.connect()
    assert ctrl.status == "FAILED"


def test_disconnect(mocker):
    mocker.patch(
        "odb_tui.controllers.app_controller.detect_obd_device",
        return_value=("/dev/ttyUSB0", "0403", "6015"),
    )
    mock_conn = MagicMock()
    mock_conn.is_connected.return_value = True
    mocker.patch("odb_tui.services.connection.obd.OBD", return_value=mock_conn)
    ctrl = AppController()
    ctrl.connect()
    ctrl.disconnect()
    assert ctrl.status == "DISCONNECTED"


def test_connect_discovers_commands(mocker):
    mocker.patch(
        "odb_tui.controllers.app_controller.detect_obd_device",
        return_value=("/dev/ttyUSB0", "0403", "6015"),
    )
    mock_conn = MagicMock()
    mock_conn.is_connected.return_value = True
    mock_conn.supports.return_value = False
    mocker.patch("odb_tui.services.connection.obd.OBD", return_value=mock_conn)
    mocker.patch("odb_tui.services.connection.obd.commands.__getitem__", return_value=[])
    ctrl = AppController()
    ctrl.connect()
    assert ctrl.supported_commands is not None


def test_disconnect_clears_commands(mocker):
    mocker.patch(
        "odb_tui.controllers.app_controller.detect_obd_device",
        return_value=("/dev/ttyUSB0", "0403", "6015"),
    )
    mock_conn = MagicMock()
    mock_conn.is_connected.return_value = True
    mock_conn.supports.return_value = False
    mocker.patch("odb_tui.services.connection.obd.OBD", return_value=mock_conn)
    mocker.patch("odb_tui.services.connection.obd.commands.__getitem__", return_value=[])
    ctrl = AppController()
    ctrl.connect()
    ctrl.disconnect()
    assert ctrl.supported_commands is None
