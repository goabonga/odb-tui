"""ELM327 serial transport layer (extracted from scan.py)."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List, Optional

import serial


def hex_bytes(s: str) -> str:
    """Normalize to uppercase hex without spaces."""
    return "".join(ch for ch in s.upper() if ch in "0123456789ABCDEF")


def chunks(s: str, n: int) -> List[str]:
    """Split string *s* into a list of substrings of length *n*."""
    return [s[i:i+n] for i in range(0, len(s), n)]


@dataclass
class ElmConfig:
    port: str
    baud: int = 38400
    timeout: float = 1.2
    write_delay: float = 0.05
    read_grace: float = 0.25
    init_delay: float = 1.0


class Elm327:
    """Minimal ELM327 wrapper reading until '>' prompt."""

    def __init__(self, cfg: ElmConfig):
        self.cfg = cfg
        self.ser = serial.Serial(cfg.port, cfg.baud, timeout=cfg.timeout)
        time.sleep(cfg.init_delay)

    def close(self):
        """Close the underlying serial port, ignoring errors."""
        try:
            self.ser.close()
        except Exception:
            pass

    def _read_until_prompt(self) -> str:
        """Read serial data until the '>' ELM prompt or timeout."""
        buf = b""
        deadline = time.time() + self.cfg.timeout + 1.5
        while time.time() < deadline:
            b = self.ser.read(1024)
            if b:
                buf += b
                if b">" in buf:
                    break
            else:
                time.sleep(0.02)
        return buf.decode(errors="replace")

    def cmd(self, cmd: str, *, wait: Optional[float] = None) -> str:
        """Send an AT command (no extra formatting)."""
        cmd = cmd.strip()
        if not cmd:
            return ""
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self.ser.write((cmd + "\r").encode("ascii", errors="ignore"))
        self.ser.flush()
        time.sleep(wait if wait is not None else self.cfg.read_grace)
        return self._read_until_prompt()

    def send_hex(self, payload_hex: str, *, wait: Optional[float] = None) -> str:
        """Send hex payload like '22F190' or '10 03' (spaces allowed)."""
        payload_hex = hex_bytes(payload_hex)
        if len(payload_hex) % 2 != 0:
            raise ValueError(f"Odd hex length: {payload_hex}")
        spaced = " ".join(chunks(payload_hex, 2))
        return self.cmd(spaced, wait=wait)

    @staticmethod
    def parse_lines(raw: str) -> List[str]:
        """Normalize ELM output: remove prompt, split lines, strip echoes."""
        raw = raw.replace(">", "")
        lines = []
        for ln in raw.splitlines():
            ln = ln.strip()
            if not ln:
                continue
            if ln.upper() in ("OK", "STOPPED", "NO DATA", "?", "SEARCHING..."):
                lines.append(ln.upper())
                continue
            h = hex_bytes(ln)
            if h:
                lines.append(h)
        return lines


def elm_init(elm: Elm327, req_id: str, resp_id: str, protocol: str = "6"):
    """Initialize ELM327 for UDS communication on given CAN IDs."""
    elm.cmd("ATZ", wait=1.2)       # Reset ELM327
    elm.cmd("ATE0")                 # Echo off
    elm.cmd("ATL0")                 # Linefeeds off
    elm.cmd("ATS0")                 # Spaces off in responses
    elm.cmd("ATH1")                 # Headers on (show CAN IDs)
    elm.cmd("ATCAF1")               # CAN auto-formatting on
    elm.cmd("ATAL")                 # Allow long (>7 byte) messages
    elm.cmd("ATST0A")               # Set timeout (~40 ms per retry)
    elm.cmd("ATAT1")                # Adaptive timing on
    elm.cmd(f"ATSP{protocol}")      # Set protocol (e.g. 6 = ISO 15765-4 CAN 11-bit 500k)
    elm.cmd(f"ATSH {req_id}")       # Set CAN request header (e.g. 7E0)
    elm.cmd("ATCRA " + resp_id)     # Set CAN receive address filter (e.g. 7E8)
