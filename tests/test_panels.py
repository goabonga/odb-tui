from odb_tui.models.vehicle import VehicleState
from odb_tui.views.panels.diag import build_diag_panel
from odb_tui.views.panels.egr import build_egr_panel
from odb_tui.views.panels.engine import build_engine_panel
from odb_tui.views.panels.errors import build_errors_panel
from odb_tui.views.panels.turbo import build_turbo_panel

# --- Engine panel ---


def test_engine_panel_no_title():
    result = build_engine_panel(VehicleState())
    first_line = result.split("\n")[0]
    assert first_line != "ENGINE"


def test_engine_panel_no_title_separator():
    result = build_engine_panel(VehicleState())
    lines = result.split("\n")
    assert lines[0] != "─" * 60
    if len(lines) > 1:
        assert lines[1] != "─" * 60


def test_engine_panel_with_data():
    state = VehicleState(rpm=3000.0, coolant_temp=90.0, fuel_level=75.0)
    result = build_engine_panel(state)
    assert "3000" in result
    assert "COOLANT" in result
    assert "LEVEL" in result


def test_engine_panel_temperatures_subsection():
    state = VehicleState(coolant_temp=90.0)
    result = build_engine_panel(state)
    assert "TEMPERATURES" in result


def test_engine_panel_fuel_subsection():
    state = VehicleState(fuel_level=75.0)
    result = build_engine_panel(state)
    assert "FUEL" in result


def test_engine_panel_o2_subsection():
    state = VehicleState(o2_s1_wr=1.0)
    result = build_engine_panel(state)
    assert "O2 SENSORS" in result


# --- Turbo panel ---


def test_turbo_panel_no_title():
    result = build_turbo_panel(VehicleState())
    first_line = result.split("\n")[0]
    assert first_line != "TURBO / AIR"


def test_turbo_panel_no_title_separator():
    result = build_turbo_panel(VehicleState())
    lines = result.split("\n")
    assert lines[0] != "─" * 60
    if len(lines) > 1:
        assert lines[1] != "─" * 60


def test_turbo_panel_with_boost():
    state = VehicleState(intake_press=200.0, baro=101.0, net_boost=99.0)
    result = build_turbo_panel(state)
    assert "INTAKE" in result
    assert "NET BOOST" in result


def test_turbo_panel_throttle_subsection():
    state = VehicleState(throttle=50.0)
    result = build_turbo_panel(state)
    assert "THROTTLE" in result


def test_turbo_panel_accelerator_subsection():
    state = VehicleState(accel_d=30.0)
    result = build_turbo_panel(state)
    assert "ACCELERATOR" in result


# --- EGR panel ---


def test_egr_panel_no_title():
    result = build_egr_panel(VehicleState())
    first_line = result.split("\n")[0]
    assert first_line != "EGR"


def test_egr_panel_no_title_separator():
    result = build_egr_panel(VehicleState())
    lines = result.split("\n")
    assert lines[0] != "─" * 60
    if len(lines) > 1:
        assert lines[1] != "─" * 60


def test_egr_panel_with_data():
    state = VehicleState(egr_cmd=25.0, egr_err=-3.5)
    result = build_egr_panel(state)
    assert "COMMANDED" in result
    assert "3.5% below" in result


# --- Diag panel ---


def test_diag_panel_no_title():
    result = build_diag_panel(VehicleState())
    first_line = result.split("\n")[0]
    assert first_line != "DIAGNOSTICS"


def test_diag_panel_no_title_separator():
    result = build_diag_panel(VehicleState())
    lines = result.split("\n")
    assert lines[0] != "─" * 60
    if len(lines) > 1:
        assert lines[1] != "─" * 60


def test_diag_panel_mil_present():
    result = build_diag_panel(VehicleState())
    assert "MIL" in result


def test_diag_panel_with_dtcs():
    state = VehicleState(dtc_list=[("P0420", "Catalyst efficiency below threshold")])
    result = build_diag_panel(state)
    assert "P0420" in result
    assert "Catalyst" in result


def test_diag_panel_counters_subsection():
    state = VehicleState(dist_mil=100.0)
    result = build_diag_panel(state)
    assert "COUNTERS" in result


def test_diag_panel_calibration_subsection():
    state = VehicleState(cal_id="CAL123")
    result = build_diag_panel(state)
    assert "CALIBRATION" in result


def test_diag_panel_stored_dtcs_subsection():
    state = VehicleState(dtc_list=[("P0420", "Catalyst efficiency")])
    result = build_diag_panel(state)
    assert "STORED DTCs" in result


def test_diag_panel_current_dtcs_subsection():
    state = VehicleState(current_dtc_list=[("P0300", "Random misfire")])
    result = build_diag_panel(state)
    assert "CURRENT DTCs" in result


# --- Errors panel ---


def test_errors_panel_no_title():
    state = VehicleState(connection_status="CONNECTED")
    result = build_errors_panel(state)
    first_line = result.split("\n")[0]
    assert first_line != "ERRORS"


def test_errors_panel_no_title_separator():
    state = VehicleState(connection_status="CONNECTED")
    result = build_errors_panel(state)
    lines = result.split("\n")
    assert lines[0] != "─" * 60
    if len(lines) > 1:
        assert lines[1] != "─" * 60


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
