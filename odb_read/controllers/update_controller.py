"""Reads all sensors and produces a VehicleState snapshot."""

from collections import deque

import obd

from odb_read.models.vehicle import VehicleState
from odb_read.models.obd_commands import DPF_DIFF_PRESSURE, EGT_BANK1
from odb_read.models.presets import TIRE_PRESETS, GEARBOX_PRESETS
from odb_read.services.connection import OBDConnectionService
from odb_read.services.analysis import AnalysisService


class UpdateController:
    """Queries all OBD-II sensors and assembles a VehicleState snapshot each cycle."""

    def __init__(self, connection: OBDConnectionService, analysis: AnalysisService):
        self.conn = connection
        self.analysis = analysis
        self.rpm_history: deque[float] = deque(maxlen=60)
        self.speed_history: deque[float] = deque(maxlen=60)

    def read_state(self, tire_index: int, gearbox_index: int) -> VehicleState:
        """Read all sensors and return a VehicleState snapshot."""
        c = self.conn

        # Engine core
        rpm = c.safe(obd.commands.RPM)
        engine_load = c.safe(obd.commands.ENGINE_LOAD)
        abs_load = c.safe(obd.commands.ABSOLUTE_LOAD)
        coolant_temp = c.safe(obd.commands.COOLANT_TEMP)
        oil_temp = c.safe(obd.commands.OIL_TEMP)
        intake_temp = c.safe(obd.commands.INTAKE_TEMP)
        ambient_temp = c.safe(obd.commands.AMBIANT_AIR_TEMP)
        maf = c.safe(obd.commands.MAF)
        voltage = c.safe(obd.commands.CONTROL_MODULE_VOLTAGE)
        timing = c.safe(obd.commands.TIMING_ADVANCE)
        run_time = c.safe(obd.commands.RUN_TIME)

        # Fuel system
        rail = c.safe_first(
            obd.commands.FUEL_RAIL_PRESSURE_DIRECT,
            obd.commands.FUEL_RAIL_PRESSURE_VAC,
        )
        fuel_rate = c.safe(obd.commands.FUEL_RATE)
        fuel_level = c.safe(obd.commands.FUEL_LEVEL)
        fuel_inject = c.safe(obd.commands.FUEL_INJECT_TIMING)
        equiv_ratio = c.safe(obd.commands.COMMANDED_EQUIV_RATIO)
        short_ft1 = c.safe(obd.commands.SHORT_FUEL_TRIM_1)
        long_ft1 = c.safe(obd.commands.LONG_FUEL_TRIM_1)

        # Turbo / Air
        intake_press = c.safe(obd.commands.INTAKE_PRESSURE)
        baro = c.safe(obd.commands.BAROMETRIC_PRESSURE)
        throttle = c.safe_first(
            obd.commands.THROTTLE_POS,
            obd.commands.RELATIVE_THROTTLE_POS,
            obd.commands.ACCELERATOR_POS_D,
        )
        throttle_b = c.safe(obd.commands.THROTTLE_POS_B)
        throttle_act = c.safe(obd.commands.THROTTLE_ACTUATOR)
        accel_d = c.safe(obd.commands.ACCELERATOR_POS_D)
        accel_e = c.safe(obd.commands.ACCELERATOR_POS_E)
        rel_accel = c.safe(obd.commands.RELATIVE_ACCEL_POS)

        # O2 / Lambda
        o2_sensors = c.safe_raw(obd.commands.O2_SENSORS)
        o2_s1_wr = c.safe(obd.commands.O2_S1_WR_CURRENT)
        o2_s2_wr = c.safe(obd.commands.O2_S2_WR_CURRENT)

        # EGR / DPF
        egr_cmd = c.safe(obd.commands.COMMANDED_EGR)
        egr_err = c.safe(obd.commands.EGR_ERROR)
        egt_data = c.safe_custom(EGT_BANK1)
        pre_dpf = egt_data.get('s1') if isinstance(egt_data, dict) else None
        post_dpf = egt_data.get('s2') if isinstance(egt_data, dict) else None
        dpf_diff = c.safe_custom(DPF_DIFF_PRESSURE)

        # Speed
        speed = c.safe(obd.commands.SPEED)

        # Analysis
        egr_status = self.analysis.detect_egr_status(egr_cmd, egr_err)
        net_boost, turbo_status = self.analysis.analyze_turbo(intake_press, baro, rpm)
        regen_status = self.analysis.detect_regen(pre_dpf, post_dpf, rpm, net_boost)
        gear, gear_ratio = self.analysis.estimate_gear(rpm, speed, tire_index, gearbox_index)
        self.analysis.update_max_speed(speed)
        boost_low, boost_mid, boost_high = self.analysis.boost_averages()

        # Histories
        self.rpm_history.append(rpm if rpm is not None else 0)
        self.speed_history.append(speed if speed is not None else 0)

        # DTCs
        dtc_list = []
        current_dtc_list = []
        if c.is_connected:
            try:
                dtc_r = c.connection.query(obd.commands.GET_DTC)
                if dtc_r.value:
                    dtc_list = dtc_r.value
            except Exception:
                pass
            try:
                cur_r = c.connection.query(obd.commands.GET_CURRENT_DTC)
                if cur_r.value:
                    current_dtc_list = cur_r.value
            except Exception:
                pass

        # Diag
        status_raw = c.safe_raw(obd.commands.STATUS)
        obd_comp = c.safe_raw(obd.commands.OBD_COMPLIANCE)
        fuel_type = c.safe_raw(obd.commands.FUEL_TYPE)
        fuel_status = c.safe_raw(obd.commands.FUEL_STATUS)
        dist_mil = c.safe(obd.commands.DISTANCE_W_MIL)
        run_time_mil = c.safe(obd.commands.RUN_TIME_MIL)
        warmups = c.safe(obd.commands.WARMUPS_SINCE_DTC_CLEAR)
        dist_dtc = c.safe(obd.commands.DISTANCE_SINCE_DTC_CLEAR)
        time_dtc = c.safe(obd.commands.TIME_SINCE_DTC_CLEARED)
        cal_id = c.safe_raw(obd.commands.CALIBRATION_ID)
        cvn = c.safe_raw(obd.commands.CVN)
        mon_o2_b1s1 = c.safe_raw(obd.commands.MONITOR_O2_B1S1)
        mon_o2_b1s2 = c.safe_raw(obd.commands.MONITOR_O2_B1S2)
        mon_nox = c.safe_raw(obd.commands.MONITOR_NOX_ABSORBER_B1)

        # Gearbox/tire config for display
        gb = GEARBOX_PRESETS[gearbox_index]
        tire = TIRE_PRESETS[tire_index]

        return VehicleState(
            rpm=rpm, engine_load=engine_load, abs_load=abs_load,
            coolant_temp=coolant_temp, oil_temp=oil_temp,
            intake_temp=intake_temp, ambient_temp=ambient_temp,
            maf=maf, voltage=voltage, timing=timing, run_time=run_time,
            rail=rail, fuel_rate=fuel_rate, fuel_level=fuel_level,
            fuel_inject=fuel_inject, equiv_ratio=equiv_ratio,
            short_ft1=short_ft1, long_ft1=long_ft1,
            intake_press=intake_press, baro=baro, net_boost=net_boost,
            max_boost_observed=self.analysis.max_boost_observed,
            turbo_status=turbo_status,
            throttle=throttle, throttle_b=throttle_b, throttle_act=throttle_act,
            accel_d=accel_d, accel_e=accel_e, rel_accel=rel_accel,
            o2_sensors=o2_sensors, o2_s1_wr=o2_s1_wr, o2_s2_wr=o2_s2_wr,
            egr_cmd=egr_cmd, egr_err=egr_err, egr_status=egr_status,
            dpf_diff=dpf_diff, pre_dpf=pre_dpf, post_dpf=post_dpf,
            regen_status=regen_status,
            speed=speed, max_speed=self.analysis.max_speed,
            gear=gear, gear_ratio=gear_ratio,
            status_raw=status_raw, obd_comp=obd_comp,
            fuel_type=fuel_type, fuel_status=fuel_status,
            dist_mil=dist_mil, run_time_mil=run_time_mil,
            warmups=warmups, dist_dtc=dist_dtc, time_dtc=time_dtc,
            cal_id=cal_id, cvn=cvn,
            mon_o2_b1s1=mon_o2_b1s1, mon_o2_b1s2=mon_o2_b1s2, mon_nox=mon_nox,
            dtc_list=dtc_list, current_dtc_list=current_dtc_list,
            boost_low=boost_low, boost_mid=boost_mid, boost_high=boost_high,
            boost_samples=len(self.analysis.boost_rpm_history),
            rpm_history=list(self.rpm_history),
            speed_history=list(self.speed_history),
            gb_label=gb.label, gb_count=gb.nb_gears,
            gb_final=gb.final_drive, gb_ratios=gb.ratios,
            tire_label=tire.label, tire_circ=tire.circumference,
        )
