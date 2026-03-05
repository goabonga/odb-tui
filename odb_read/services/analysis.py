"""Vehicle analysis: regen detection, EGR status, turbo analysis, gear estimation."""

from collections import deque
from typing import Optional, Tuple

from odb_read.models.presets import TIRE_PRESETS, GEARBOX_PRESETS


class AnalysisService:
    """Stateful analysis of live OBD data: regen, EGR, turbo, gear, and speed."""

    def __init__(self):
        self.egr_error_history = deque(maxlen=10)
        self.max_boost_observed = 0.0
        self.boost_rpm_history = deque(maxlen=120)
        self.max_speed = 0.0

    def detect_regen(self, pre_dpf_temp, post_dpf_temp, rpm, net_boost) -> str:
        """Detect DPF regeneration status from exhaust temps and RPM.

        Returns 'ACTIVE (HIGH CONF)', 'POSSIBLE', or 'INACTIVE'.
        """
        indicators = 0
        if post_dpf_temp is not None and post_dpf_temp > 550:
            indicators += 1
        if pre_dpf_temp is not None and pre_dpf_temp > 600:
            indicators += 1
        if rpm is not None and 850 <= rpm <= 1200 and (net_boost is None or net_boost < 20):
            indicators += 1
        if (pre_dpf_temp is not None and post_dpf_temp is not None
                and abs(pre_dpf_temp - post_dpf_temp) < 50):
            indicators += 1
        if indicators >= 2:
            return "ACTIVE (HIGH CONF)"
        elif indicators == 1:
            return "POSSIBLE"
        return "INACTIVE"

    def detect_egr_status(self, egr_commanded, egr_error) -> str:
        """Evaluate EGR valve health from commanded position and error history.

        Returns 'CLOSED', 'OK', 'WARN', 'BLOCKED', or 'STUCK OPEN'.
        """
        if egr_error is not None:
            self.egr_error_history.append(egr_error)
        if len(self.egr_error_history) == 0:
            return "--"
        avg_error = sum(self.egr_error_history) / len(self.egr_error_history)
        if egr_commanded is not None and egr_commanded == 0 and abs(avg_error) < 3:
            return "CLOSED"
        if abs(avg_error) < 5:
            return "OK"
        elif abs(avg_error) <= 15:
            return "WARN"
        elif avg_error < -15:
            return "BLOCKED"
        else:
            return "STUCK OPEN"

    def analyze_turbo(self, intake_pressure, baro_pressure, rpm) -> Tuple[Optional[float], str]:
        """Compute net boost (kPa) and turbo status ('OK' or 'LOW BOOST')."""
        if intake_pressure is None:
            return None, "--"
        atm = baro_pressure if baro_pressure is not None else 101.3
        net_boost = intake_pressure - atm
        if net_boost > self.max_boost_observed:
            self.max_boost_observed = net_boost
        self.boost_rpm_history.append((net_boost, rpm))
        turbo_status = "OK"
        if rpm is not None and rpm > 2500 and net_boost < 30:
            turbo_status = "LOW BOOST"
        return net_boost, turbo_status

    def estimate_gear(self, rpm, speed, tire_index: int, gearbox_index: int) -> Tuple[Optional[int], Optional[float]]:
        """Estimate current gear from RPM, speed, tire size, and gearbox ratios.

        Returns (gear_number, computed_ratio) or (None, ratio) if no match.
        """
        if rpm is None or speed is None or speed < 5 or rpm < 600:
            return None, None

        gb = GEARBOX_PRESETS[gearbox_index]
        tire_circ = TIRE_PRESETS[tire_index].circumference

        speed_m_per_min = speed * 1000.0 / 60.0
        wheel_rpm = speed_m_per_min / tire_circ
        overall_ratio = rpm / wheel_rpm
        gear_ratio = overall_ratio / gb.final_drive

        best_gear = None
        best_diff = float("inf")
        for gear, ratio in gb.ratios.items():
            diff = abs(gear_ratio - ratio)
            if diff < best_diff:
                best_diff = diff
                best_gear = gear
        if best_diff > 0.4:
            return None, gear_ratio
        return best_gear, gear_ratio

    def boost_averages(self) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        """Return average boost for low (<2000), mid (2000-3000), and high (>3000) RPM bands."""
        low, mid, high = [], [], []
        for boost, rpm in self.boost_rpm_history:
            if rpm is None:
                continue
            if rpm < 2000:
                low.append(boost)
            elif rpm <= 3000:
                mid.append(boost)
            else:
                high.append(boost)

        def avg(lst):
            return sum(lst) / len(lst) if lst else None

        return avg(low), avg(mid), avg(high)

    def update_max_speed(self, speed):
        """Track the highest observed speed during the session."""
        if speed is not None and speed > self.max_speed:
            self.max_speed = speed
