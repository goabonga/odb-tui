"""Custom OBD commands for DPF and EGT sensors."""

from obd import OBDCommand
from obd.protocols import ECU


def dpf_diff_pressure_decoder(messages):
    """Decode DPF differential pressure (PID 7A) in kPa.

    Raw bytes [2..3] form a 16-bit value divided by 10 to give kPa.
    Returns None if the response is too short.
    """
    d = messages[0].data
    if len(d) < 4:
        return None
    return ((d[2] * 256) + d[3]) / 10.0


# Custom OBDCommand: pression différentielle FAP (PID $7A, Mode 01)
DPF_DIFF_PRESSURE = OBDCommand(
    "DPF_DIFF_PRESSURE", "DPF Differential Pressure Bank 1",
    b"017A", 4, dpf_diff_pressure_decoder, ECU.ENGINE, True,
)


def egt_bank1_decoder(messages):
    """Decode exhaust gas temperatures for Bank 1 (PID 78).

    Returns a dict with keys 's1' and/or 's2' representing sensor 1
    (pre-DPF) and sensor 2 (post-DPF) temperatures in degrees Celsius.
    Formula: (raw_16bit / 10) - 40.
    """
    d = messages[0].data
    result = {}
    if len(d) >= 5:
        result['s1'] = ((d[3] * 256) + d[4]) / 10.0 - 40.0
    if len(d) >= 7:
        result['s2'] = ((d[5] * 256) + d[6]) / 10.0 - 40.0
    return result


# Custom OBDCommand: températures d'échappement banc 1 (PID $78, Mode 01)
EGT_BANK1 = OBDCommand(
    "EGT_BANK1", "Exhaust Gas Temp Bank 1",
    b"0178", 7, egt_bank1_decoder, ECU.ENGINE, True,
)
