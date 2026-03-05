"""OBD connection management and safe query helpers."""

import obd

from odb_read.models.dtc import manufacturer_from_vin


class OBDConnectionService:
    """Manages the python-obd connection and provides safe query helpers.

    Wraps connection lifecycle (connect/disconnect) and offers safe_*()
    methods that silently return None on unsupported PIDs or errors.
    """

    def __init__(self):
        self.connection = None
        self._unsupported_custom = set()  # cache for custom PIDs that returned null

    @property
    def is_connected(self) -> bool:
        return self.connection is not None and self.connection.is_connected()

    def connect(self, port: str) -> bool:
        """Connect to OBD adapter. Returns True on success."""
        self._unsupported_custom = set()
        try:
            self.connection = obd.OBD(port, fast=False)
            return self.connection.is_connected()
        except Exception:
            return False

    def disconnect(self):
        """Close the OBD connection and reset internal state."""
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
        self.connection = None
        self._unsupported_custom = set()

    def read_vehicle_name(self) -> str:
        """Read VIN and return 'Manufacturer (VIN: ...)' or '-'."""
        try:
            r = self.connection.query(obd.commands.VIN)
            if r.is_null():
                return "-"
            raw = r.value
            if isinstance(raw, (bytes, bytearray)):
                vin = raw.decode('ascii', errors='ignore')
            else:
                vin = str(raw)
            vin = vin.strip().strip('\x00')
            if len(vin) < 3:
                return "-"
            manufacturer = manufacturer_from_vin(vin)
            return f"{manufacturer} (VIN: {vin})"
        except Exception:
            return "-"

    def get_baud_rate(self) -> int:
        """Get current serial baud rate from connection."""
        try:
            return self.connection.interface._ELM327__port.baudrate
        except Exception:
            return 38400

    def protocol_name(self) -> str:
        """Return the active OBD protocol name (e.g. 'ISO 15765-4'), or '?' on error."""
        try:
            return self.connection.protocol_name()
        except Exception:
            return "?"

    def supports(self, cmd) -> bool:
        """Check whether the connected ECU supports the given OBD command."""
        if not self.is_connected:
            return False
        return self.connection.supports(cmd)

    # -- Safe query helpers --

    def safe(self, cmd):
        """Read a standard OBD PID, return numeric magnitude or None."""
        if not self.is_connected:
            return None
        if not self.connection.supports(cmd):
            return None
        try:
            r = self.connection.query(cmd)
            return None if r.is_null() else r.value.magnitude
        except Exception:
            return None

    def safe_raw(self, cmd):
        """Read a standard OBD PID, return raw value (for non-numeric)."""
        if not self.is_connected:
            return None
        if not self.connection.supports(cmd):
            return None
        try:
            r = self.connection.query(cmd)
            return None if r.is_null() else r.value
        except Exception:
            return None

    def safe_first(self, *cmds):
        """Try multiple OBD commands, return first supported value."""
        for cmd in cmds:
            val = self.safe(cmd)
            if val is not None:
                return val
        return None

    def safe_custom(self, cmd):
        """Read a custom OBD command with force=True, cache failures."""
        if not self.is_connected:
            return None
        if cmd in self._unsupported_custom:
            return None
        try:
            r = self.connection.query(cmd, force=True)
            if r.is_null():
                self._unsupported_custom.add(cmd)
                return None
            return r.value
        except Exception:
            self._unsupported_custom.add(cmd)
            return None
