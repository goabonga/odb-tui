from odb_tui.models.vehicle import VehicleState
from odb_tui.views.panels.diag import build_diag_panel
from odb_tui.views.panels.egr import build_egr_panel
from odb_tui.views.panels.engine import build_engine_panel
from odb_tui.views.panels.errors import build_errors_panel
from odb_tui.views.panels.turbo import build_turbo_panel


def test_engine_panel_empty_state():
    result = build_engine_panel(VehicleState())
    assert "ENGINE" in result


def test_engine_panel_with_data():
    state = VehicleState(rpm=3000.0, coolant_temp=90.0, fuel_level=75.0)
    result = build_engine_panel(state)
    assert "3000" in result
    assert "COOLANT" in result
    assert "LEVEL" in result


def test_turbo_panel_empty_state():
    result = build_turbo_panel(VehicleState())
    assert "TURBO" in result


def test_turbo_panel_with_boost():
    state = VehicleState(intake_press=200.0, baro=101.0, net_boost=99.0)
    result = build_turbo_panel(state)
    assert "INTAKE" in result
    assert "NET BOOST" in result


def test_egr_panel_empty_state():
    result = build_egr_panel(VehicleState())
    assert "EGR" in result
    assert "No EGR data" in result


def test_egr_panel_with_data():
    state = VehicleState(egr_cmd=25.0, egr_err=-3.5)
    result = build_egr_panel(state)
    assert "COMMANDED" in result
    assert "3.5% below" in result


def test_diag_panel_empty_state():
    result = build_diag_panel(VehicleState())
    assert "DIAGNOSTICS" in result
    assert "MIL" in result


def test_diag_panel_with_dtcs():
    state = VehicleState(dtc_list=[("P0420", "Catalyst efficiency below threshold")])
    result = build_diag_panel(state)
    assert "P0420" in result
    assert "Catalyst" in result


def test_errors_panel_not_connected():
    state = VehicleState(connection_status="DISCONNECTED")
    result = build_errors_panel(state)
    assert "--" in result


def test_errors_panel_no_errors():
    state = VehicleState(connection_status="CONNECTED")
    result = build_errors_panel(state)
    assert "No errors" in result


def test_errors_panel_with_dtcs():
    state = VehicleState(
        connection_status="CONNECTED",
        dtc_list=[("P0300", "Random misfire detected")],
    )
    result = build_errors_panel(state)
    assert "P0300" in result
    assert "misfire" in result
