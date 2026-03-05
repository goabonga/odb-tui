"""Vehicle state model for standard OBD-II sensor data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VehicleState:
    """Snapshot of all standard OBD-II sensor readings.

    All fields default to None — a None value means the command
    is not supported or has not been read yet.
    """

    # Engine
    rpm: float | None = None
    engine_load: float | None = None
    abs_load: float | None = None
    coolant_temp: float | None = None
    oil_temp: float | None = None
    intake_temp: float | None = None
    ambient_temp: float | None = None
    maf: float | None = None
    voltage: float | None = None
    timing: float | None = None
    run_time: float | None = None

    # Fuel
    fuel_rail: float | None = None
    fuel_rate: float | None = None
    fuel_level: float | None = None
    fuel_inject: float | None = None
    equiv_ratio: float | None = None
    short_ft1: float | None = None
    long_ft1: float | None = None

    # Turbo / Air
    intake_press: float | None = None
    baro: float | None = None
    throttle: float | None = None
    throttle_b: float | None = None
    throttle_act: float | None = None
    accel_d: float | None = None
    accel_e: float | None = None
    rel_accel: float | None = None

    # O2
    o2_sensors: Any | None = None
    o2_s1_wr: float | None = None
    o2_s2_wr: float | None = None

    # EGR
    egr_cmd: float | None = None
    egr_err: float | None = None

    # Speed
    speed: float | None = None

    # Computed
    net_boost: float | None = None

    # Diagnostics
    status_raw: Any | None = None
    obd_comp: Any | None = None
    fuel_type: Any | None = None
    fuel_status: Any | None = None
    dist_mil: float | None = None
    run_time_mil: float | None = None
    warmups: float | None = None
    dist_dtc: float | None = None
    time_dtc: float | None = None
    cal_id: Any | None = None
    cvn: Any | None = None

    # DTCs
    dtc_list: list[tuple[str, str]] = field(default_factory=list)
    current_dtc_list: list[tuple[str, str]] = field(default_factory=list)

    # Connection info
    connection_status: str = "DISCONNECTED"
