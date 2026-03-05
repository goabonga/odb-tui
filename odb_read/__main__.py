"""Allow running with ``python -m odb_read``."""

import argparse

from odb_read.models.log_config import LogConfig
from odb_read.views.app import OBDReaderApp


def main():
    """Parse CLI arguments, build LogConfig, and launch the Textual TUI app."""
    parser = argparse.ArgumentParser(description="OBD-II vehicle diagnostic TUI")
    parser.add_argument("--log-dir", default=".", help="Répertoire de sortie pour les logs")
    parser.add_argument("--log-all", action="store_true", help="Activer tous les logs fichier")
    parser.add_argument("--elm-log", action="store_true", help="Activer le log ELM327")
    parser.add_argument("--csv-log", action="store_true", help="Activer le log CSV")
    parser.add_argument("--pids-log", action="store_true", help="Activer le log PIDs supportés")
    parser.add_argument("--dtc-log", action="store_true", help="Activer le log DTC")
    parser.add_argument("--scan-log", action="store_true", help="Activer le log scan UDS")
    parser.add_argument("--elm-filename", default=None, help="Nom du fichier ELM log")
    parser.add_argument("--csv-filename", default=None, help="Nom du fichier CSV")
    parser.add_argument("--pids-filename", default=None, help="Nom du fichier PIDs")
    parser.add_argument("--dtc-filename", default=None, help="Nom du fichier DTC")
    parser.add_argument("--scan-filename", default=None, help="Nom du fichier scan")
    args = parser.parse_args()

    cfg = LogConfig(
        log_dir=args.log_dir,
        enable_elm=args.log_all or args.elm_log,
        enable_csv=args.log_all or args.csv_log,
        enable_pids=args.log_all or args.pids_log,
        enable_dtc=args.log_all or args.dtc_log,
        enable_scan=args.log_all or args.scan_log,
        elm_filename=args.elm_filename,
        csv_filename=args.csv_filename,
        pids_filename=args.pids_filename,
        dtc_filename=args.dtc_filename,
        scan_filename=args.scan_filename,
    )
    OBDReaderApp(log_config=cfg).run()


if __name__ == "__main__":
    main()
