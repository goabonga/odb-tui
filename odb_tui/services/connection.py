import obd


class OBDConnectionService:

    def __init__(self) -> None:
        self.connection: obd.OBD | None = None

    @property
    def is_connected(self) -> bool:
        return self.connection is not None and self.connection.is_connected()

    def connect(self, port: str) -> bool:
        try:
            self.connection = obd.OBD(port, fast=False)
            return bool(self.connection.is_connected())
        except Exception:
            self.connection = None
            return False

    def disconnect(self) -> None:
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
        self.connection = None
