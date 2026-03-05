"""Log configuration dataclass for controlling all file outputs."""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class LogConfig:
    """Configuration for all log file outputs.

    Attributes:
        log_dir: Répertoire de base pour tous les fichiers de log.
        enable_elm: Activer le log des échanges ELM327 bruts.
        enable_csv: Activer l'enregistrement CSV des données capteurs.
        enable_pids: Activer le log des PIDs supportés.
        enable_dtc: Activer le log des codes défaut (DTC).
        enable_scan: Activer le log du scan UDS.
        *_filename: Nom de fichier personnalisé (sinon nom par défaut).
    """

    log_dir: str = "."
    enable_elm: bool = False
    enable_csv: bool = False
    enable_pids: bool = False
    enable_dtc: bool = False
    enable_scan: bool = False
    elm_filename: Optional[str] = None
    csv_filename: Optional[str] = None
    pids_filename: Optional[str] = None
    dtc_filename: Optional[str] = None
    scan_filename: Optional[str] = None

    def path(self, default_name: str, override: Optional[str] = None) -> str:
        """Build full path: log_dir / (override or default_name).

        Args:
            default_name: Nom de fichier par défaut si aucun override.
            override: Nom de fichier personnalisé (prioritaire).
        """
        name = override if override else default_name
        return os.path.join(self.log_dir, name)
