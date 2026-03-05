"""UDS deep scan service ($22, $21, $19)."""

import os
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple

from odb_read.models.log_config import LogConfig
from odb_read.models.scan_targets import S22_DID_CANDIDATES, S22_SCAN_RANGES, CAN_HEADERS
from odb_read.services.elm_transport import Elm327, ElmConfig, elm_init
from odb_read.services.uds import (
    NRC, uds_session_extended, uds_read_did,
    decode_negative, ascii_from_hex,
)


@dataclass
class ScanProgress:
    """Mutable scan state shared between the background scan thread and the TUI.

    The UI reads these fields to display progress; the scan thread writes them.
    """
    scanning: bool = False
    stop_requested: bool = False
    status: str = ""
    phase: str = ""
    hits: int = 0
    raw_log: List[str] = field(default_factory=list)
    results: List[Tuple[str, str, str, int]] = field(default_factory=list)


class ScanService:
    """Runs a multi-phase UDS deep scan ($22, $21, $19) over ELM327."""

    def __init__(self):
        self.progress = ScanProgress()

    def request_stop(self):
        self.progress.stop_requested = True
        self.progress.status = "ARRET DEMANDE..."

    def do_scan(self, port_path: str, baud: int, vehicle_name: str, port_label: str,
                 *, log_config: LogConfig):
        """Run the full UDS scan. Call from a background thread."""
        progress = self.progress
        progress.scanning = True
        progress.stop_requested = False
        progress.status = "Demarrage..."
        progress.raw_log = []
        progress.hits = 0
        progress.phase = ""
        progress.results = []

        results = []
        raw_log = []

        def log(line):
            raw_log.append(line)
            progress.raw_log.append(line)

        def stopped():
            return progress.stop_requested

        elm = None
        try:
            progress.status = "Init ELM327..."
            cfg = ElmConfig(port=port_path, baud=baud)
            elm = Elm327(cfg)

            working_header = None

            # PHASE 0: Probe headers
            progress.phase = "PHASE 0: Probe headers"
            log("=" * 50)
            log("PHASE 0: PROBE HEADERS")
            log("=" * 50)
            for req_id, resp_id, hdr_desc in CAN_HEADERS:
                progress.status = f"Probe {req_id} ({hdr_desc})..."
                elm_init(elm, req_id=req_id, resp_id=resp_id, protocol="6")
                elm.cmd("ATH0")

                log(f"\n[{req_id}] {hdr_desc}")

                ev = uds_session_extended(elm)
                sess_ok = ev["ok"]
                log(
                    f"  Session 1003: "
                    f"{'OK' if sess_ok else 'FAIL'} {ev.get('lines', [])}"
                )

                for kwp_cmd, kwp_name in [
                    ("1081", "KWP Standard"),
                    ("1089", "KWP Development"),
                ]:
                    raw_kwp = elm.send_hex(kwp_cmd, wait=0.30)
                    lines_kwp = Elm327.parse_lines(raw_kwp)
                    kwp_ok = any(ln.startswith("50") for ln in lines_kwp)
                    neg_kwp = next(
                        (decode_negative(ln) for ln in lines_kwp if decode_negative(ln)),
                        None,
                    )
                    if kwp_ok:
                        log(f"  {kwp_name}: OK {lines_kwp}")
                        working_header = (req_id, resp_id)
                    elif neg_kwp:
                        log(
                            f"  {kwp_name}: NRC "
                            f"{neg_kwp[2]:02X} {NRC.get(neg_kwp[2], '')}"
                        )
                    else:
                        log(f"  {kwp_name}: {lines_kwp}")

                for test_did in [0xF190, 0xF478, 0x1024]:
                    ev = uds_read_did(elm, test_did, wait=0.30)
                    if ev["positive"]:
                        log(
                            f"  S22 {test_did:04X}: "
                            f"HIT data={ev['positive']['data_hex']}"
                        )
                        working_header = (req_id, resp_id)
                    elif ev["negative"]:
                        nrc_code = ev["negative"]["nrc"]
                        nrc_label = ev["negative"].get("nrc_label", "")
                        log(f"  S22 {test_did:04X}: NRC {nrc_code} {nrc_label}")
                    else:
                        log(
                            f"  S22 {test_did:04X}: "
                            f"NO RESPONSE {ev.get('lines', [])}"
                        )

                raw21 = elm.send_hex("2101", wait=0.30)
                lines21 = Elm327.parse_lines(raw21)
                for ln in lines21:
                    if ln.startswith("61"):
                        log(f"  S21 01: HIT {ln}")
                        working_header = (req_id, resp_id)
                        break
                else:
                    neg21 = next(
                        (decode_negative(ln) for ln in lines21 if decode_negative(ln)),
                        None,
                    )
                    if neg21:
                        log(
                            f"  S21 01: NRC "
                            f"{neg21[2]:02X} {NRC.get(neg21[2], '')}"
                        )
                    else:
                        log(f"  S21 01: {lines21}")

                if working_header:
                    break

            # PHASE 1: Full scan on best header
            req_id, resp_id = working_header or ("7E0", "7E8")
            progress.phase = f"PHASE 1: Service $22 sur {req_id}"
            log("")
            log("=" * 50)
            log(f"PHASE 1: SERVICE $22 sur {req_id}")
            log("=" * 50)
            progress.status = f"Scan sur {req_id}..."
            elm_init(elm, req_id=req_id, resp_id=resp_id, protocol="6")
            elm.cmd("ATH0")

            for sess_cmd in ["1081", "1089", "1003"]:
                raw_s = elm.send_hex(sess_cmd, wait=0.30)
                lines_s = Elm327.parse_lines(raw_s)
                if any(ln.startswith("50") for ln in lines_s):
                    log(f"  Active session: {sess_cmd} on {req_id}")
                    break

            progress.status = "Test Service $22..."
            ev_test = uds_read_did(elm, 0xF190, wait=0.30)
            s22_supported = True
            if ev_test["negative"] and ev_test["negative"]["nrc"] == "11":
                log("  Service $22: NRC 11 (serviceNotSupported) -- SKIP")
                s22_supported = False

            if s22_supported:
                # Phase 1a: targeted known DIDs
                total = len(S22_DID_CANDIDATES)
                for i, (did_hex, desc) in enumerate(S22_DID_CANDIDATES):
                    if stopped():
                        log("  >> ARRET DEMANDE")
                        break
                    did_int = int(did_hex, 16)
                    progress.status = f"S22 cibles {i+1}/{total}: {did_hex}"
                    ev = uds_read_did(elm, did_int, wait=0.25)
                    if ev["positive"]:
                        d = ev["positive"]
                        results.append((
                            f"22:{did_hex}", desc,
                            d["data_hex"], d["len_bytes"],
                        ))
                        progress.hits += 1
                        log(
                            f"  [+] S22 {did_hex} ({desc}): "
                            f"[{d['len_bytes']}B] {d['data_hex']} "
                            f"ascii={d['data_ascii_hint']}"
                        )
                    time.sleep(0.03)

                # Phase 1b: extended range scan
                all_dids = []
                targeted_set = {int(d, 16) for d, _ in S22_DID_CANDIDATES}
                for start, end in S22_SCAN_RANGES:
                    for did in range(start, end + 1):
                        if did not in targeted_set:
                            all_dids.append(did)

                total2 = len(all_dids)
                for i, did_int in enumerate(all_dids):
                    if stopped():
                        log("  >> ARRET DEMANDE")
                        break
                    did_hex = f"{did_int:04X}"
                    progress.status = f"S22 range {i+1}/{total2}: {did_hex}"
                    ev = uds_read_did(elm, did_int, wait=0.25)
                    if ev["positive"]:
                        d = ev["positive"]
                        results.append((
                            f"22:{did_hex}", "Discovered",
                            d["data_hex"], d["len_bytes"],
                        ))
                        progress.hits += 1
                        log(
                            f"  [+] S22 {did_hex}: "
                            f"[{d['len_bytes']}B] {d['data_hex']} "
                            f"ascii={d['data_ascii_hint']}"
                        )
                    time.sleep(0.03)
            else:
                log("  (scan $22 saute)")

            # PHASE 2: Service $21 (KWP2000)
            if stopped():
                log("\n>> SCAN ARRETE PAR L'UTILISATEUR")
                raise StopIteration
            progress.phase = f"PHASE 2: Service $21 sur {req_id}"
            log("")
            log("=" * 50)
            log(f"PHASE 2: SERVICE $21 (KWP2000) 00-FF sur {req_id}")
            log("=" * 50)
            for did in range(0x00, 0x100):
                if stopped():
                    log("  >> ARRET DEMANDE")
                    break
                did_hex = f"{did:02X}"
                progress.status = f"S21 {did_hex} ({did}/255)"
                raw = elm.send_hex(f"21{did_hex}", wait=0.25)
                lines = Elm327.parse_lines(raw)
                hit = False
                for ln in lines:
                    if ln.startswith("61"):
                        data = ln[4:]
                        results.append((
                            f"21:{did_hex}", f"KWP DID {did_hex}",
                            data, len(data) // 2,
                        ))
                        progress.hits += 1
                        log(
                            f"  [+] S21 {did_hex}: "
                            f"[{len(data)//2}B] {data} "
                            f"ascii={ascii_from_hex(data)}"
                        )
                        hit = True
                        break
                if not hit:
                    neg = next(
                        (decode_negative(ln) for ln in lines if decode_negative(ln)),
                        None,
                    )
                    if neg:
                        nrc_val = neg[2]
                        if nrc_val == 0x11:
                            log("  S21: NRC 11 (serviceNotSupported) -- STOP")
                            break
                        if nrc_val not in (0x31, 0x12):
                            log(
                                f"  S21 {did_hex}: NRC "
                                f"{nrc_val:02X} {NRC.get(nrc_val, '')}"
                            )
                time.sleep(0.03)

            # PHASE 3: Service $19 (UDS DTC info)
            if stopped():
                log("\n>> SCAN ARRETE PAR L'UTILISATEUR")
                raise StopIteration
            progress.phase = "PHASE 3: Service $19"
            log("")
            log("=" * 50)
            log("PHASE 3: SERVICE $19 (DTC INFO)")
            log("=" * 50)
            for sub_hex in ["0102", "02FF", "0AFF", "06FF"]:
                progress.status = f"S19 {sub_hex}"
                raw = elm.send_hex(f"19{sub_hex}", wait=0.35)
                lines = Elm327.parse_lines(raw)
                for ln in lines:
                    if ln.startswith("59"):
                        results.append((
                            f"19:{sub_hex}", "DTC Info",
                            ln, len(ln) // 2,
                        ))
                        progress.hits += 1
                        log(f"  [+] S19 {sub_hex}: {ln}")
                        break
                else:
                    neg = next(
                        (decode_negative(ln) for ln in lines if decode_negative(ln)),
                        None,
                    )
                    if neg:
                        log(
                            f"  S19 {sub_hex}: NRC "
                            f"{neg[2]:02X} {NRC.get(neg[2], '')}"
                        )
                    else:
                        log(f"  S19 {sub_hex}: {lines}")

            # Cleanup: return ECU to default session
            progress.status = "Retour session par defaut..."
            elm.send_hex("1001", wait=0.25)
            log("")
            log("=" * 50)
            log(f"SCAN TERMINE: {len(results)} reponses positives")
            log("=" * 50)
            log("Retour session par defaut (10 01)")

        except StopIteration:
            pass
        except Exception as e:
            log(f"\nEXCEPTION: {e}")
            log(traceback.format_exc())
        finally:
            if elm:
                try:
                    elm.send_hex("1001", wait=0.15)
                except Exception:
                    pass
                elm.close()

        progress.results = results
        if log_config.enable_scan:
            self._save_results(results, raw_log, vehicle_name, port_label, log_config)

        n = len(results)
        progress.status = f"TERMINE: {n} DIDs trouves"
        progress.scanning = False

    def _save_results(self, results, raw_log, vehicle_name: str,
                      port_label: str, log_config: LogConfig):
        """Write scan results and the raw probe log to a timestamped file."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"s22_scan_{ts}.log"
        filepath = log_config.path(default_name, log_config.scan_filename)
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w") as f:
            f.write(f"UDS Deep Scan - {datetime.now().isoformat()}\n")
            f.write(f"Vehicle: {vehicle_name}\n")
            f.write(f"Port: {port_label}\n\n")

            f.write("=" * 60 + "\n")
            f.write("RAW PROBE LOG\n")
            f.write("=" * 60 + "\n\n")
            if raw_log:
                for line in raw_log:
                    f.write(line + "\n")
            f.write("\n")

            f.write("=" * 60 + "\n")
            f.write(f"POSITIVE RESPONSES: {len(results)}\n")
            f.write("=" * 60 + "\n\n")

            if results:
                for svc_did, desc, data_hex, data_len in results:
                    f.write(
                        f"  {svc_did:<10}  {desc:<28}  "
                        f"[{data_len:2d}B]  {data_hex}\n"
                    )
                    f.write(
                        f"              ascii: {ascii_from_hex(data_hex)}\n"
                    )
                    try:
                        bts = bytes.fromhex(data_hex)
                        if len(bts) >= 2:
                            raw16 = (bts[0] << 8) | bts[1]
                            f.write(
                                f"              uint16={raw16}  "
                                f"temp(÷10-40)={raw16/10.0-40:.1f}°C  "
                                f"press(÷10)={raw16/10.0:.1f}kPa\n"
                            )
                        if len(bts) == 1:
                            f.write(
                                f"              uint8={bts[0]}  "
                                f"temp(-40)={bts[0]-40}°C\n"
                            )
                    except Exception:
                        pass
            else:
                f.write("  Aucune reponse positive.\n\n")
                f.write("  L'ECU ne supporte probablement pas Service $22/$21\n")
                f.write("  via le port OBD-II standard.\n\n")
                f.write("  Consulter le RAW PROBE LOG ci-dessus pour\n")
                f.write("  comprendre les codes d'erreur NRC retournes.\n")
