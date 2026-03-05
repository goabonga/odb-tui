"""CSV logging service for OBD data."""

import csv
import os
from datetime import datetime

from odb_read.models.log_config import LogConfig


CSV_HEADER = [
    "timestamp",
    # Engine
    "rpm", "engine_load_pct", "abs_load_pct",
    "coolant_temp_c", "oil_temp_c", "intake_temp_c", "ambient_temp_c",
    "maf_gs", "voltage_v", "timing_advance_deg", "run_time_s",
    # Fuel
    "rail_pressure_kpa", "fuel_rate_lh", "fuel_level_pct",
    "fuel_inject_timing_deg", "equiv_ratio",
    "short_fuel_trim_1_pct", "long_fuel_trim_1_pct",
    # Turbo / Air
    "intake_pressure_kpa", "baro_kpa", "net_boost_kpa",
    "max_boost_kpa", "turbo_status",
    "throttle_pct", "throttle_b_pct", "throttle_actuator_pct",
    "accel_d_pct", "accel_e_pct", "rel_accel_pct",
    # EGR / DPF
    "egr_cmd_pct", "egr_err_pct", "egr_status",
    "dpf_diff_kpa", "egt_pre_dpf_c", "egt_post_dpf_c",
    "egt_delta_c", "regen_status",
    # Gearbox
    "speed_kmh", "max_speed_kmh", "gear", "gear_ratio",
    "tire_size",
    # Diag
    "mil", "dtc_count", "fuel_type", "fuel_status",
    "dist_with_mil_km", "run_time_mil_s",
    "warmups_since_dtc_clear", "dist_since_dtc_clear_km",
    "time_since_dtc_clear_s",
    "dtc_codes",
]


class CSVLoggerService:
    """Writes live OBD sensor readings to a timestamped CSV file."""

    def __init__(self, log_config: LogConfig):
        self.log_config = log_config
        self.logging = False
        self._file = None
        self._writer = None

    def open(self):
        """Open a new CSV file and write the header row. No-op if CSV logging is disabled."""
        if not self.log_config.enable_csv:
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"obd_log_{ts}.csv"
        filepath = self.log_config.path(default_name, self.log_config.csv_filename)
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        self._file = open(filepath, "w", newline="")
        self._writer = csv.writer(self._file)
        self._writer.writerow(CSV_HEADER)
        self._file.flush()
        self.logging = True

    def close(self):
        """Flush and close the CSV file."""
        self.logging = False
        if self._file:
            try:
                self._file.close()
            except Exception:
                pass
            self._file = None
            self._writer = None

    def write_row(self, data):
        """Append one data row to the CSV and flush to disk."""
        if self.logging and self._writer:
            self._writer.writerow(data)
            self._file.flush()
