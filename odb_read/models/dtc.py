"""VIN / WMI manufacturer lookup.

Maps World Manufacturer Identifier (WMI) codes -- the first 3 characters
of a VIN -- to human-readable manufacturer names.
"""

# Full 3-character WMI codes for precise manufacturer identification
WMI_MAP = {
    "JSA": "Suzuki", "JS1": "Suzuki", "JS2": "Suzuki",
    "JS3": "Suzuki", "JS4": "Suzuki", "TSM": "Suzuki",
    "VF1": "Renault", "VF3": "Peugeot", "VF7": "Citroën",
    "WBA": "BMW", "WBS": "BMW M", "WDB": "Mercedes",
    "WDD": "Mercedes", "WF0": "Ford EU", "WVW": "VW",
    "WAU": "Audi", "ZAR": "Alfa Romeo", "ZFA": "Fiat",
    "1G1": "Chevrolet", "1GC": "Chevrolet", "2T1": "Toyota",
    "JTD": "Toyota", "JHM": "Honda", "JN1": "Nissan",
    "KMH": "Hyundai", "KNA": "Kia",
}

# Fallback 2-character prefix map when the full WMI is not found
WMI2_MAP = {
    "JS": "Suzuki", "VF": "Renault/PSA", "WB": "BMW",
    "WD": "Mercedes", "WF": "Ford EU", "WV": "VW",
    "WA": "Audi", "ZA": "Alfa/Fiat", "JT": "Toyota",
    "JH": "Honda", "JN": "Nissan", "KM": "Hyundai",
    "KN": "Kia",
}


def manufacturer_from_vin(vin: str) -> str:
    """Return the manufacturer name from a VIN string.

    Looks up the first 3 characters (WMI) in WMI_MAP, then falls back
    to the first 2 characters in WMI2_MAP.  Returns the raw WMI prefix
    if no match is found.
    """
    if len(vin) < 3:
        return vin
    wmi = vin[:3].upper()
    return WMI_MAP.get(wmi, WMI2_MAP.get(wmi[:2], vin[:3]))
