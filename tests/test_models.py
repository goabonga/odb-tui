"""Tests for model modules: dtc, presets, scan_targets, vehicle, obd_commands."""

from odb_read.models.dtc import manufacturer_from_vin
from odb_read.models.vehicle import VehicleState
from odb_read.models.presets import (
    TirePreset, GearboxPreset,
    TIRE_PRESETS, GEARBOX_PRESETS,
    DEFAULT_TIRE_INDEX, DEFAULT_GEARBOX_INDEX,
)
from odb_read.models.scan_targets import S22_DID_CANDIDATES, CAN_HEADERS
from odb_read.models.obd_commands import DPF_DIFF_PRESSURE, EGT_BANK1


# --- manufacturer_from_vin ---

class TestManufacturerFromVin:
    """Tests for VIN-to-manufacturer lookup logic."""

    def test_wmi3_match(self):
        """Match a known 3-char WMI prefix (BMW)."""
        assert manufacturer_from_vin("WBA12345678901234") == "BMW"

    def test_wmi3_match_other(self):
        """Match a different 3-char WMI prefix (Renault)."""
        assert manufacturer_from_vin("VF1ABCDEF1234") == "Renault"

    def test_wmi2_fallback(self):
        """Fall back to 2-char WMI when 3-char is unknown."""
        assert manufacturer_from_vin("WVX12345678901234") == "VW"

    def test_unknown_returns_first3(self):
        """Return first 3 characters when no WMI matches."""
        assert manufacturer_from_vin("XXX12345678901234") == "XXX"

    def test_short_vin(self):
        """Handle a VIN shorter than 3 characters."""
        assert manufacturer_from_vin("AB") == "AB"

    def test_empty_vin(self):
        """Return empty string for an empty VIN."""
        assert manufacturer_from_vin("") == ""

    def test_case_insensitive(self):
        """Match WMI regardless of letter case."""
        assert manufacturer_from_vin("wba12345678901234") == "BMW"


# --- VehicleState ---

class TestVehicleState:
    """Tests for VehicleState dataclass defaults and construction."""

    def test_defaults(self):
        """Verify all default field values on a fresh VehicleState."""
        s = VehicleState()
        assert s.rpm is None
        assert s.speed is None
        assert s.max_speed == 0.0
        assert s.regen_status == "INACTIVE"
        assert s.egr_status == "--"
        assert s.turbo_status == "--"
        assert s.vehicle_name == "-"
        assert s.connection_status == "DISCONNECTED"
        assert s.csv_logging is False
        assert s.dtc_list == []
        assert s.rpm_history == []
        assert s.boost_samples == 0

    def test_custom_fields(self):
        """Construct VehicleState with explicit field values."""
        s = VehicleState(rpm=3000, speed=120.5, vehicle_name="BMW")
        assert s.rpm == 3000
        assert s.speed == 120.5
        assert s.vehicle_name == "BMW"


# --- Presets ---

class TestPresets:
    """Tests for TirePreset and GearboxPreset construction and built-in lists."""

    def test_tire_preset_construction(self):
        """Create a TirePreset and verify its fields."""
        t = TirePreset("205/55R16", 1.976)
        assert t.label == "205/55R16"
        assert t.circumference == 1.976

    def test_gearbox_preset_construction(self):
        """Create a GearboxPreset and verify its fields."""
        g = GearboxPreset("5 vitesses", 5, 3.938, {1: 3.583, 2: 1.952})
        assert g.label == "5 vitesses"
        assert g.nb_gears == 5
        assert g.final_drive == 3.938
        assert g.ratios[1] == 3.583

    def test_tire_presets_not_empty(self):
        """Ensure the built-in TIRE_PRESETS list is populated."""
        assert len(TIRE_PRESETS) > 0

    def test_gearbox_presets_not_empty(self):
        """Ensure the built-in GEARBOX_PRESETS list is populated."""
        assert len(GEARBOX_PRESETS) > 0

    def test_default_tire_index_valid(self):
        """Ensure the default tire index is within bounds."""
        assert 0 <= DEFAULT_TIRE_INDEX < len(TIRE_PRESETS)

    def test_default_gearbox_index_valid(self):
        """Ensure the default gearbox index is within bounds."""
        assert 0 <= DEFAULT_GEARBOX_INDEX < len(GEARBOX_PRESETS)


# --- Scan targets ---

class TestScanTargets:
    """Tests for scan target constant lists (S22 DIDs and CAN headers)."""

    def test_s22_did_candidates_not_empty(self):
        """Ensure S22 DID candidates list is populated."""
        assert len(S22_DID_CANDIDATES) > 0

    def test_s22_did_candidates_format(self):
        """Validate each S22 DID entry is a (hex_string, description) pair."""
        for item in S22_DID_CANDIDATES:
            assert len(item) == 2
            hex_str, desc = item
            assert isinstance(hex_str, str)
            assert isinstance(desc, str)
            # Verify hex_str is valid hex
            int(hex_str, 16)

    def test_can_headers_format(self):
        """Validate each CAN header entry is a (request, response, description) triple."""
        assert len(CAN_HEADERS) > 0
        for item in CAN_HEADERS:
            assert len(item) == 3
            req, resp, desc = item
            assert isinstance(req, str)
            assert isinstance(resp, str)
            assert isinstance(desc, str)


# --- OBD Commands ---

class TestOBDCommands:
    """Tests for custom OBD command definitions."""

    def test_dpf_diff_pressure_is_obd_command(self):
        """Verify DPF_DIFF_PRESSURE is a valid OBDCommand instance."""
        from obd import OBDCommand
        assert isinstance(DPF_DIFF_PRESSURE, OBDCommand)

    def test_egt_bank1_is_obd_command(self):
        """Verify EGT_BANK1 is a valid OBDCommand instance."""
        from obd import OBDCommand
        assert isinstance(EGT_BANK1, OBDCommand)
