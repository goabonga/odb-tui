from odb_tui.models.vehicle import VehicleState


def test_vehicle_state_defaults():
    state = VehicleState()
    assert state.rpm is None
    assert state.speed is None
    assert state.coolant_temp is None
    assert state.engine_load is None
    assert state.net_boost is None
    assert state.status_raw is None
    assert state.connection_status == "DISCONNECTED"


def test_vehicle_state_dtc_lists_default():
    state = VehicleState()
    assert state.dtc_list == []
    assert state.current_dtc_list == []


def test_vehicle_state_with_values():
    state = VehicleState(rpm=3000.0, speed=120.0, coolant_temp=90.0)
    assert state.rpm == 3000.0
    assert state.speed == 120.0
    assert state.coolant_temp == 90.0
