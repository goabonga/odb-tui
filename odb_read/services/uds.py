"""UDS helpers (extracted from scan.py)."""

from __future__ import annotations

import time
from typing import Optional, Tuple

from odb_read.services.elm_transport import Elm327, chunks


def now_iso() -> str:
    """Return the current local time as an ISO 8601 string."""
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())


NRC = {
    0x10: "General Reject",
    0x11: "Service Not Supported",
    0x12: "Sub-Function Not Supported",
    0x13: "Incorrect Message Length / Invalid Format",
    0x22: "Conditions Not Correct",
    0x31: "Request Out Of Range",
    0x33: "Security Access Denied",
    0x35: "Invalid Key",
    0x36: "Exceeded Number of Attempts",
    0x37: "Required Time Delay Not Expired",
    0x7E: "Sub-Function Not Supported In Active Session",
    0x78: "Response Pending",
}


def decode_negative(resp_hex: str) -> Optional[Tuple[int, int, int]]:
    """Return (0x7F, service, nrc) if it's a negative response."""
    if len(resp_hex) >= 6 and resp_hex.startswith("7F"):
        try:
            srv = int(resp_hex[2:4], 16)
            nrc = int(resp_hex[4:6], 16)
            return (0x7F, srv, nrc)
        except ValueError:
            return None
    return None


def extract_positive_62(resp_hex: str) -> Optional[Tuple[int, int, str]]:
    """For ReadDataByIdentifier positive response: 62 <DIDhi><DIDlo> <data...>"""
    if len(resp_hex) >= 8 and resp_hex.startswith("62"):
        try:
            did = int(resp_hex[2:6], 16)
            data = resp_hex[6:]
            return (0x62, did, data)
        except ValueError:
            return None
    return None


def ascii_from_hex(data_hex: str) -> str:
    """Convert hex string to printable ASCII, replacing non-printable bytes with '.'."""
    out = []
    for b in chunks(data_hex, 2):
        try:
            v = int(b, 16)
            if 32 <= v <= 126:
                out.append(chr(v))
            else:
                out.append(".")
        except ValueError:
            out.append("?")
    return "".join(out)


def uds_session_extended(elm: Elm327) -> dict:
    """Request UDS DiagnosticSessionControl extended session (10 03).

    Returns dict with 'ok' bool and parsed response lines.
    """
    raw = elm.send_hex("1003", wait=0.35)
    lines = Elm327.parse_lines(raw)
    ok = any(ln.startswith("5003") for ln in lines)
    neg = next((decode_negative(ln) for ln in lines if decode_negative(ln)), None)
    return {"ts": now_iso(), "op": "session_extended", "ok": ok, "lines": lines, "neg": neg}


def uds_read_vin(elm: Elm327) -> dict:
    """Read VIN via UDS ReadDataByIdentifier (22 F1 90).

    Returns dict with 'vin' string (or None) and raw response data.
    """
    raw = elm.send_hex("22F190", wait=0.5)
    lines = Elm327.parse_lines(raw)

    pos = None
    for ln in lines:
        p = extract_positive_62(ln)
        if p and p[1] == 0xF190:
            pos = p
            break

    neg = next((decode_negative(ln) for ln in lines if decode_negative(ln)), None)
    vin = None
    if pos:
        vin_ascii = ascii_from_hex(pos[2]).strip(".")
        vin = vin_ascii

    return {
        "ts": now_iso(),
        "op": "read_vin",
        "vin": vin,
        "lines": lines,
        "neg": ({"service": neg[1], "nrc": neg[2], "nrc_label": NRC.get(neg[2])} if neg else None),
    }


def uds_read_did(elm: Elm327, did: int, *, wait: float = 0.25) -> dict:
    """Read a single DID via UDS Service $22. Handles NRC 78 (response pending).

    Returns dict with 'positive' and/or 'negative' response details.
    """
    did_hex = f"{did:04X}"
    raw = elm.send_hex("22" + did_hex, wait=wait)
    lines = Elm327.parse_lines(raw)

    got_pending = any(
        (neg := decode_negative(ln)) is not None and neg[2] == 0x78
        for ln in lines
    )
    pos = None
    neg = None

    for ln in lines:
        p = extract_positive_62(ln)
        if p and p[1] == did:
            pos = p
        n = decode_negative(ln)
        if n:
            neg = n

    if got_pending and not pos:
        raw2 = elm.cmd("", wait=0.45)
        lines2 = Elm327.parse_lines(raw2)
        lines.extend(lines2)
        for ln in lines2:
            p = extract_positive_62(ln)
            if p and p[1] == did:
                pos = p
                break
            n = decode_negative(ln)
            if n:
                neg = n

    out = {
        "ts": now_iso(),
        "op": "read_did",
        "did": did,
        "did_hex": did_hex,
        "lines": lines,
        "positive": None,
        "negative": None,
    }
    if pos:
        data_hex = pos[2]
        out["positive"] = {
            "sid": "62",
            "data_hex": data_hex,
            "data_ascii_hint": ascii_from_hex(data_hex),
            "len_bytes": len(data_hex) // 2,
        }
    if neg:
        out["negative"] = {
            "sid": "7F",
            "service": f"{neg[1]:02X}",
            "nrc": f"{neg[2]:02X}",
            "nrc_label": NRC.get(neg[2]),
        }
    return out
