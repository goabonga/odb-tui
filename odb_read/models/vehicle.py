"""Snapshot of all vehicle sensor readings at a given instant."""

from dataclasses import dataclass, field
from typing import Optional, List, Tuple


@dataclass
class VehicleState:
    """Instantaneous snapshot of all vehicle sensor readings.

    Populated by UpdateController on each OBD polling cycle, then consumed
    by panel builders (views) and the CSV logger.  Every field defaults to
    None (or a safe neutral value) so that a freshly-created instance is
    always valid.
    """

    # --- Engine core: RPM, loads, temperatures, MAF, voltage, timing ---
    rpm: Optional[float] = None
    engine_load: Optional[float] = None
    abs_load: Optional[float] = None
    coolant_temp: Optional[float] = None
    oil_temp: Optional[float] = None
    intake_temp: Optional[float] = None
    ambient_temp: Optional[float] = None
    maf: Optional[float] = None
    voltage: Optional[float] = None
    timing: Optional[float] = None
    run_time: Optional[float] = None

    # --- Fuel system: rail pressure, consumption, fuel trims ---
    rail: Optional[float] = None
    fuel_rate: Optional[float] = None
    fuel_level: Optional[float] = None
    fuel_inject: Optional[float] = None
    equiv_ratio: Optional[float] = None
    short_ft1: Optional[float] = None
    long_ft1: Optional[float] = None

    # --- Turbo / Air: boost, throttle positions, accelerator pedal ---
    intake_press: Optional[float] = None
    baro: Optional[float] = None
    net_boost: Optional[float] = None
    max_boost_observed: float = 0.0
    turbo_status: str = "--"
    throttle: Optional[float] = None
    throttle_b: Optional[float] = None
    throttle_act: Optional[float] = None
    accel_d: Optional[float] = None
    accel_e: Optional[float] = None
    rel_accel: Optional[float] = None

    # --- O2 / Lambda: wide-band oxygen sensors ---
    o2_sensors: object = None
    o2_s1_wr: Optional[float] = None
    o2_s2_wr: Optional[float] = None

    # --- EGR / DPF (FAP): exhaust gas recirculation and particulate filter ---
    egr_cmd: Optional[float] = None
    egr_err: Optional[float] = None
    egr_status: str = "--"
    dpf_diff: Optional[float] = None
    pre_dpf: Optional[float] = None
    post_dpf: Optional[float] = None
    regen_status: str = "INACTIVE"

    # --- Speed / Gearbox: vitesse, rapport estimé ---
    speed: Optional[float] = None
    max_speed: float = 0.0
    gear: Optional[int] = None
    gear_ratio: Optional[float] = None

    # --- Diagnostics: OBD readiness, fuel type, MIL counters, calibration ---
    status_raw: object = None
    obd_comp: object = None
    fuel_type: object = None
    fuel_status: object = None
    dist_mil: Optional[float] = None
    run_time_mil: Optional[float] = None
    warmups: Optional[float] = None
    dist_dtc: Optional[float] = None
    time_dtc: Optional[float] = None
    cal_id: object = None
    cvn: object = None
    mon_o2_b1s1: object = None
    mon_o2_b1s2: object = None
    mon_nox: object = None

    # --- DTCs: stored and current diagnostic trouble codes ---
    dtc_list: List[Tuple[str, str]] = field(default_factory=list)
    current_dtc_list: List[Tuple[str, str]] = field(default_factory=list)

    # --- Boost averages: moyennes de pression par plage de régime ---
    boost_low: Optional[float] = None
    boost_mid: Optional[float] = None
    boost_high: Optional[float] = None
    boost_samples: int = 0

    # --- RPM / speed history: ring buffers for sparkline graphs ---
    rpm_history: List[float] = field(default_factory=list)
    speed_history: List[float] = field(default_factory=list)

    # --- Vehicle info: identity, port, connection state ---
    vehicle_name: str = "-"
    port: str = "-"
    vid: str = "-"
    pid: str = "-"
    connection_status: str = "DISCONNECTED"

    # --- Gearbox / tire config: préréglages actifs (affichage) ---
    gb_label: str = ""
    gb_count: int = 0
    gb_final: float = 0.0
    gb_ratios: dict = field(default_factory=dict)
    tire_label: str = ""
    tire_circ: float = 0.0

    # --- CSV logging state ---
    csv_logging: bool = False

    # --- Scan state: UDS Service $22 discovery progress ---
    scanning: bool = False
    scan_phase: str = ""
    scan_status: str = ""
    scan_hits: int = 0
    scan_raw_log: list = field(default_factory=list)
    s22_results: list = field(default_factory=list)
