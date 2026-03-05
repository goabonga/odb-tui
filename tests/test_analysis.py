"""Tests for analysis service."""

import pytest


class TestDetectRegen:
    """Tests for detect_regen() -- DPF regeneration status detection."""

    def test_all_none_inactive(self, analysis):
        """Return INACTIVE when all sensor inputs are None."""
        assert analysis.detect_regen(None, None, None, None) == "INACTIVE"

    def test_one_indicator_possible(self, analysis):
        """Return POSSIBLE when only one indicator (post_dpf > 550) is met."""
        # post_dpf > 550
        assert analysis.detect_regen(None, 600, None, None) == "POSSIBLE"

    def test_two_indicators_active(self, analysis):
        """Return ACTIVE (HIGH CONF) when two indicators are met."""
        # post_dpf > 550 AND pre_dpf > 600
        assert analysis.detect_regen(650, 600, None, None) == "ACTIVE (HIGH CONF)"

    def test_rpm_indicator(self, analysis):
        """Detect POSSIBLE regen from elevated idle RPM with low boost."""
        # rpm in [850, 1200] with low boost
        assert analysis.detect_regen(None, None, 1000, 10) == "POSSIBLE"

    def test_three_indicators(self, analysis):
        """Return ACTIVE (HIGH CONF) when three indicators are met."""
        # pre > 600, post > 550, rpm in range + low boost
        result = analysis.detect_regen(650, 600, 1000, 5)
        assert result == "ACTIVE (HIGH CONF)"

    def test_small_delta_indicator(self, analysis):
        """Detect regen when pre/post DPF temperatures are close together."""
        # pre and post close together AND post > 550
        result = analysis.detect_regen(580, 560, None, None)
        assert result == "ACTIVE (HIGH CONF)"


class TestDetectEgrStatus:
    """Tests for detect_egr_status() -- EGR valve health classification."""

    def test_no_history(self, analysis):
        """Return '--' when both inputs are None."""
        assert analysis.detect_egr_status(None, None) == "--"

    def test_small_error_ok(self, analysis):
        """Return OK for a small EGR error at normal commanded position."""
        assert analysis.detect_egr_status(50.0, 2.0) == "OK"

    def test_small_error_closed(self, analysis):
        """Return CLOSED when commanded position is zero."""
        assert analysis.detect_egr_status(0, 1.0) == "CLOSED"

    def test_warn(self, analysis):
        """Return WARN for a moderate EGR error."""
        # avg_error between 5 and 15
        assert analysis.detect_egr_status(50.0, 10.0) == "WARN"

    def test_blocked(self, analysis):
        """Return BLOCKED for a large negative error."""
        # Large negative error
        assert analysis.detect_egr_status(50.0, -20.0) == "BLOCKED"

    def test_stuck_open(self, analysis):
        """Return STUCK OPEN for a large positive error."""
        # Large positive error
        assert analysis.detect_egr_status(50.0, 20.0) == "STUCK OPEN"

    def test_history_averaging(self, analysis):
        """Average multiple samples so a single spike stays within OK range."""
        # Push small errors, then one bigger → average may still be OK
        for _ in range(5):
            analysis.detect_egr_status(50.0, 2.0)
        # Average of 5x2.0 = 2.0, then one 10.0 → avg = (10+10)/6 ≈ 3.33
        result = analysis.detect_egr_status(50.0, 10.0)
        # avg = (2*5 + 10) / 6 = 20/6 ≈ 3.33 → < 5 → OK
        assert result == "OK"


class TestAnalyzeTurbo:
    """Tests for analyze_turbo() -- boost pressure calculation and status."""

    def test_none_intake(self, analysis):
        """Return None boost and '--' status when intake is None."""
        boost, status = analysis.analyze_turbo(None, None, None)
        assert boost is None
        assert status == "--"

    def test_normal_boost(self, analysis):
        """Calculate boost as intake minus baro and return OK status."""
        boost, status = analysis.analyze_turbo(150.0, 101.3, 2000)
        assert boost == pytest.approx(48.7, rel=0.01)
        assert status == "OK"

    def test_low_boost_high_rpm(self, analysis):
        """Return LOW BOOST status when boost is insufficient at high RPM."""
        boost, status = analysis.analyze_turbo(120.0, 101.3, 3000)
        assert boost == pytest.approx(18.7, rel=0.01)
        assert status == "LOW BOOST"

    def test_no_baro_defaults_to_101_3(self, analysis):
        """Default barometric pressure to 101.3 kPa when not available."""
        boost, status = analysis.analyze_turbo(150.0, None, 2000)
        assert boost == pytest.approx(48.7, rel=0.01)

    def test_max_boost_tracked(self, analysis):
        """Track the maximum observed boost and never decrease it."""
        analysis.analyze_turbo(200.0, 101.3, 2000)
        assert analysis.max_boost_observed == pytest.approx(98.7, rel=0.01)
        analysis.analyze_turbo(150.0, 101.3, 2000)
        # Should not decrease
        assert analysis.max_boost_observed == pytest.approx(98.7, rel=0.01)


class TestEstimateGear:
    """Tests for estimate_gear() -- gear detection from RPM and speed."""

    def test_speed_too_low(self, analysis):
        """Return None gear and ratio when speed is too low to estimate."""
        gear, ratio = analysis.estimate_gear(2000, 3, 0, 0)
        assert gear is None
        assert ratio is None

    def test_rpm_too_low(self, analysis):
        """Return None gear when RPM is below the minimum threshold."""
        gear, ratio = analysis.estimate_gear(400, 60, 0, 0)
        assert gear is None

    def test_highway_speed_gear5(self, analysis):
        """Estimate 5th gear at typical highway RPM and speed."""
        # ~120 km/h at ~3000 rpm in a 5-speed gearbox → gear 5
        gear, ratio = analysis.estimate_gear(3000, 120, 0, 0)
        assert gear == 5

    def test_out_of_range(self, analysis):
        """Return None gear but still compute ratio for abnormal values."""
        # Very abnormal ratio
        gear, ratio = analysis.estimate_gear(7000, 10, 0, 0)
        assert gear is None
        assert ratio is not None


class TestBoostAverages:
    """Tests for boost_averages() -- RPM-band boost averaging."""

    def test_empty(self, analysis):
        """Return all None when no boost samples have been recorded."""
        low, mid, high = analysis.boost_averages()
        assert low is None
        assert mid is None
        assert high is None

    def test_with_data(self, analysis):
        """Compute separate averages for low, mid, and high RPM bands."""
        # Low RPM samples
        analysis.boost_rpm_history.append((10.0, 1500))
        analysis.boost_rpm_history.append((20.0, 1800))
        # Mid RPM
        analysis.boost_rpm_history.append((30.0, 2500))
        # High RPM
        analysis.boost_rpm_history.append((50.0, 3500))

        low, mid, high = analysis.boost_averages()
        assert low == pytest.approx(15.0)
        assert mid == pytest.approx(30.0)
        assert high == pytest.approx(50.0)

    def test_none_rpm_skipped(self, analysis):
        """Skip samples where RPM is None."""
        analysis.boost_rpm_history.append((10.0, None))
        low, mid, high = analysis.boost_averages()
        assert low is None
        assert mid is None
        assert high is None


class TestUpdateMaxSpeed:
    """Tests for update_max_speed() -- maximum speed tracking."""

    def test_increases(self, analysis):
        """Update max speed when a higher value is provided."""
        analysis.update_max_speed(100)
        assert analysis.max_speed == 100

    def test_does_not_regress(self, analysis):
        """Keep the existing max when a lower value is provided."""
        analysis.update_max_speed(100)
        analysis.update_max_speed(80)
        assert analysis.max_speed == 100

    def test_none_ignored(self, analysis):
        """Ignore None values without changing the current max."""
        analysis.update_max_speed(100)
        analysis.update_max_speed(None)
        assert analysis.max_speed == 100
