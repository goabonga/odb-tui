"""File logging: save supported PIDs and DTC reports."""

import os
from datetime import datetime

import obd

from odb_read.models.log_config import LogConfig


def save_supported_pids(connection_service, vehicle_name: str, port: str,
                        vid: str, pid: str, log_config: LogConfig):
    """Save supported PIDs list to file on connect."""
    if not log_config.enable_pids:
        return
    try:
        conn = connection_service.connection
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"pids_supported_{ts}.log"
        filepath = log_config.path(default_name, log_config.pids_filename)
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w") as f:
            f.write(f"Supported PIDs - {datetime.now().isoformat()}\n")
            f.write(f"Vehicle: {vehicle_name}\n")
            f.write(f"Port: {port}  VID:PID: {vid}:{pid}\n")
            f.write(f"Protocol: {connection_service.protocol_name()}\n")
            f.write("\n")

            for mode in range(1, 10):
                try:
                    cmds = obd.commands[mode]
                except (IndexError, KeyError):
                    continue
                supported = []
                for cmd in cmds:
                    if cmd and conn.supports(cmd):
                        supported.append(cmd)
                if not supported:
                    continue
                f.write(f"MODE {mode:02d} ({len(supported)} PIDs)\n")
                f.write("-" * 60 + "\n")
                for cmd in supported:
                    pid_hex = cmd.command.decode() if isinstance(cmd.command, bytes) else str(cmd.command)
                    f.write(f"  {pid_hex:<8} {cmd.name:<35} {cmd.desc}\n")
                f.write("\n")
    except Exception:
        pass


def save_dtc_to_file(dtc_list, current_dtc_list, vehicle_name: str,
                     port: str, last_dtc_set: set, log_config: LogConfig) -> set:
    """Save DTCs to file when new codes are detected. Returns updated last_dtc_set."""
    if not log_config.enable_dtc:
        return last_dtc_set
    current_set = {code for code, _ in dtc_list}
    current_set.update(code for code, _ in current_dtc_list)
    if not current_set or current_set == last_dtc_set:
        return last_dtc_set
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    default_name = f"dtc_{ts}.log"
    filepath = log_config.path(default_name, log_config.dtc_filename)
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w") as f:
        f.write(f"DTC Report - {datetime.now().isoformat()}\n")
        f.write(f"Vehicle: {vehicle_name}\n")
        f.write(f"Port: {port}\n\n")
        if dtc_list:
            f.write("STORED DTCs:\n")
            for code, desc in dtc_list:
                f.write(f"  {code}  {desc}\n")
        if current_dtc_list:
            f.write("\nCURRENT CYCLE DTCs:\n")
            for code, desc in current_dtc_list:
                f.write(f"  {code}  {desc}\n")
    return current_set
