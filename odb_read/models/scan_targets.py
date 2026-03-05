"""UDS Service $22 DID candidates and scan ranges.

Defines known DIDs to probe first (S22_DID_CANDIDATES), extended address
ranges for broader discovery (S22_SCAN_RANGES), and CAN header pairs for
multi-ECU scanning (CAN_HEADERS).
"""

# Candidate DIDs for diesel ECUs (Bosch EDC17, Denso, Marelli)
S22_DID_CANDIDATES = [
    # EGT / Exhaust temperatures
    ("180E", "EGT Pre-DPF"),
    ("180F", "EGT Post-DPF"),
    ("1018", "EGT Upstream Turbo"),
    ("1024", "DPF Temp Inlet"),
    ("1025", "DPF Temp Outlet"),
    ("1026", "EGT Sensor 1"),
    ("1027", "EGT Sensor 2"),
    ("2033", "EGT Pre-Cat"),
    ("2034", "EGT Post-Cat"),
    ("F478", "EGT Bank1 Alt"),
    ("F479", "EGT Bank1 S2 Alt"),
    ("F40E", "EGT Pre-Turbo Alt"),
    ("F40F", "EGT Post-Turbo Alt"),
    # DPF / FAP pressure & status
    ("1028", "DPF Diff Pressure"),
    ("1810", "DPF Diff Pressure Alt"),
    ("2032", "DPF Pressure"),
    ("F416", "DPF Pressure Alt"),
    ("F47A", "DPF Pressure Alt2"),
    ("100C", "DPF Soot Loading"),
    ("100D", "DPF Regen Status"),
    ("1934", "FAP Soot Quantity"),
    ("1935", "FAP Regen Distance"),
    ("F40A", "Regen Status Alt"),
    ("F417", "DPF Status Alt"),
    ("F428", "DPF Soot Alt"),
    # Engine extras
    ("100A", "Oil Temperature"),
    ("100B", "Fuel Temperature"),
    ("1001", "Engine Torque"),
    ("1002", "Turbo Boost Actual"),
    ("1003", "Turbo Boost Target"),
    ("1014", "Injection Quantity"),
    ("1015", "Injection Timing"),
]

# Extended scan ranges for broader discovery
S22_SCAN_RANGES = [
    (0xF100, 0xF1FF),  # UDS Identification DIDs
    (0xF400, 0xF4FF),  # Extended ECU data
    (0x1000, 0x1060),
    (0x1800, 0x1840),
    (0x1900, 0x1950),
    (0x2000, 0x2060),
]

# CAN headers to probe: (request_id, response_id, description)
CAN_HEADERS = [
    ("7E0", "7E8", "Engine ECU"),
    ("7E2", "7EA", "ECU alt 1"),
    ("7C0", "7C8", "ECU mfr 1"),
]
