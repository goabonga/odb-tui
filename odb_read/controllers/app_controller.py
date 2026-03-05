"""AppController orchestrates services for the TUI app."""

import threading
import time
from datetime import datetime

from odb_read.models.log_config import LogConfig
from odb_read.models.presets import (
    TIRE_PRESETS, GEARBOX_PRESETS,
    DEFAULT_TIRE_INDEX, DEFAULT_GEARBOX_INDEX,
)
from odb_read.services.device import detect_obd_device
from odb_read.services.connection import OBDConnectionService
from odb_read.services.analysis import AnalysisService
from odb_read.services.csv_logger import CSVLoggerService
from odb_read.services.file_logger import save_supported_pids, save_dtc_to_file
from odb_read.services.scanner import ScanService
from odb_read.controllers.update_controller import UpdateController


class AppController:
    """Central controller that wires services together and exposes high-level actions to the TUI."""

    def __init__(self, log_config: LogConfig | None = None):
        self.log_config = log_config or LogConfig()
        self.conn = OBDConnectionService()
        self.analysis = AnalysisService()
        self.csv_logger = CSVLoggerService(self.log_config)
        self.scan_service = ScanService()
        self.updater = UpdateController(self.conn, self.analysis)

        self.status = "DISCONNECTED"
        self.port = "-"
        self.vid = "-"
        self.pid = "-"
        self.vehicle_name = "-"

        self.tire_index = DEFAULT_TIRE_INDEX
        self.gearbox_index = DEFAULT_GEARBOX_INDEX

        self._last_dtc_set: set[str] = set()

    @property
    def scanning(self):
        return self.scan_service.progress.scanning

    @property
    def scan_progress(self):
        return self.scan_service.progress

    def connect(self):
        """Detect the OBD device, open a connection, and save supported PIDs."""
        self.status = "CONNECTING..."
        self.port, self.vid, self.pid = detect_obd_device()

        if not self.port:
            self.status = "NO DEVICE"
            return False

        if self.conn.connect(self.port):
            self.status = "CONNECTED"
            self.vehicle_name = self.conn.read_vehicle_name()
            save_supported_pids(
                self.conn, self.vehicle_name, self.port,
                self.vid, self.pid, self.log_config,
            )
            return True
        else:
            self.status = "FAILED"
            return False

    def disconnect(self):
        """Close CSV logger and OBD connection, reset status to DISCONNECTED."""
        self.csv_logger.close()
        self.conn.disconnect()
        self.status = "DISCONNECTED"

    def reconnect(self):
        """Disconnect then reconnect to the OBD adapter."""
        self.disconnect()
        self.connect()

    def toggle_csv(self):
        """Start or stop CSV data logging."""
        if self.csv_logger.logging:
            self.csv_logger.close()
        else:
            self.csv_logger.open()

    def cycle_tire(self):
        """Cycle to the next tire preset for gear-ratio calculation."""
        self.tire_index = (self.tire_index + 1) % len(TIRE_PRESETS)

    def cycle_gearbox(self):
        """Cycle to the next gearbox preset for gear-ratio calculation."""
        self.gearbox_index = (self.gearbox_index + 1) % len(GEARBOX_PRESETS)

    def start_scan(self):
        """Start UDS scan in a background thread. Returns False if not possible."""
        if self.scanning:
            self.scan_service.request_stop()
            return False
        if not self.conn.is_connected:
            return False

        port_path = self.port
        baud = self.conn.get_baud_rate()

        # Close python-obd to release serial port
        self.scan_service.progress.status = "Deconnexion OBD..."
        try:
            self.conn.connection.close()
        except Exception:
            pass
        self.conn.connection = None
        self.status = "SCANNING"
        time.sleep(0.5)

        def _run_scan():
            self.scan_service.do_scan(
                port_path, baud, self.vehicle_name, self.port,
                log_config=self.log_config,
            )
            # Reconnect python-obd
            self.scan_service.progress.status = "Reconnexion OBD..."
            time.sleep(0.5)
            if self.conn.connect(port_path):
                self.status = "CONNECTED"
                self.vehicle_name = self.conn.read_vehicle_name()
            else:
                self.status = "RECONNECT FAILED"

        thread = threading.Thread(target=_run_scan, daemon=True)
        thread.start()
        return True

    def read_state(self):
        """Read all sensors and return a VehicleState."""
        state = self.updater.read_state(self.tire_index, self.gearbox_index)
        state.vehicle_name = self.vehicle_name
        state.port = self.port
        state.vid = self.vid
        state.pid = self.pid
        state.connection_status = self.status
        state.csv_logging = self.csv_logger.logging
        state.scanning = self.scanning
        state.scan_phase = self.scan_progress.phase
        state.scan_status = self.scan_progress.status
        state.scan_hits = self.scan_progress.hits
        state.scan_raw_log = self.scan_progress.raw_log
        state.s22_results = self.scan_progress.results

        # Save DTCs if new
        if state.dtc_list or state.current_dtc_list:
            self._last_dtc_set = save_dtc_to_file(
                state.dtc_list, state.current_dtc_list,
                self.vehicle_name, self.port, self._last_dtc_set,
                self.log_config,
            )

        return state

    def write_csv_row(self, state):
        """Write a CSV row from state."""
        if not self.csv_logger.logging:
            return
        egt_delta = (abs(state.pre_dpf - state.post_dpf)
                     if state.pre_dpf is not None and state.post_dpf is not None
                     else None)

        mil_val = None
        dtc_count_val = None
        if state.status_raw is not None:
            try:
                mil_val = state.status_raw.MIL
                dtc_count_val = state.status_raw.DTC_count
            except Exception:
                pass
        dtc_codes_str = ";".join(code for code, _ in state.dtc_list) if state.dtc_list else ""

        self.csv_logger.write_row([
            datetime.now().isoformat(),
            # Engine
            state.rpm, state.engine_load, state.abs_load,
            state.coolant_temp, state.oil_temp, state.intake_temp, state.ambient_temp,
            state.maf, state.voltage, state.timing, state.run_time,
            # Fuel
            state.rail, state.fuel_rate, state.fuel_level, state.fuel_inject,
            state.equiv_ratio, state.short_ft1, state.long_ft1,
            # Turbo / Air
            state.intake_press, state.baro, state.net_boost,
            state.max_boost_observed, state.turbo_status,
            state.throttle, state.throttle_b, state.throttle_act,
            state.accel_d, state.accel_e, state.rel_accel,
            # EGR / DPF
            state.egr_cmd, state.egr_err, state.egr_status,
            state.dpf_diff, state.pre_dpf, state.post_dpf, egt_delta, state.regen_status,
            # Gearbox
            state.speed, state.max_speed, state.gear, state.gear_ratio,
            state.tire_label,
            # Diag
            mil_val, dtc_count_val,
            str(state.fuel_type) if state.fuel_type else None,
            str(state.fuel_status) if state.fuel_status else None,
            state.dist_mil, state.run_time_mil,
            state.warmups, state.dist_dtc, state.time_dtc,
            dtc_codes_str,
        ])
