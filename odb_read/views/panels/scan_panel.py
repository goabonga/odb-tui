"""Scan results panel builder."""

from odb_read.services.uds import ascii_from_hex
from odb_read.services.scanner import ScanProgress


def build_scan_panel(progress: ScanProgress) -> str:
    """Build the UDS scan panel text: live progress, results, and raw ELM log."""
    scan_lines = []

    if progress.scanning:
        scan_lines += [
            f"SCAN EN COURS  |  Hits: {progress.hits}",
            f"{progress.phase}  |  {progress.status}",
            "",
            "RAW LOG",
            "-" * 56,
        ]
        scan_lines.extend(progress.raw_log)
    elif progress.results:
        scan_lines += [
            f"SCAN TERMINE  |  {len(progress.results)} reponses  |  [S] re-scanner",
            "",
            "RESULTATS",
            "-" * 56,
        ]
        for svc_did, desc, data_hex, data_len in progress.results:
            scan_lines.append(f"  {svc_did:<10} {desc}  [{data_len}B]")
            scan_lines.append(f"    -> {data_hex}  ({ascii_from_hex(data_hex)})")
            try:
                bts = bytes.fromhex(data_hex)
                if len(bts) >= 2:
                    raw16 = (bts[0] << 8) | bts[1]
                    scan_lines.append(
                        f"       uint16={raw16}  "
                        f"temp={raw16/10.0-40:.1f}°C  "
                        f"press={raw16/10.0:.1f}kPa"
                    )
            except Exception:
                pass
        if progress.raw_log:
            scan_lines += ["", "", "RAW LOG", "-" * 56]
            scan_lines.extend(progress.raw_log)
    elif progress.raw_log:
        scan_lines += [
            "DERNIER SCAN  |  0 reponses  |  [S] re-scanner",
            "",
            "RAW LOG",
            "-" * 56,
        ]
        scan_lines.extend(progress.raw_log)

    return "\n".join(scan_lines)
