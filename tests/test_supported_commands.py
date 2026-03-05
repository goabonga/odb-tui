from odb_tui.models.supported_commands import CommandStatus, SupportedCommands


def test_command_status_defaults():
    cmd = CommandStatus(name="RPM", pid="0x0C", description="Engine RPM", supported=True)
    assert cmd.name == "RPM"
    assert cmd.pid == "0x0C"
    assert cmd.description == "Engine RPM"
    assert cmd.supported is True


def test_command_status_unsupported():
    cmd = CommandStatus(name="EGT", pid="0x78", description="Exhaust Gas Temp", supported=False)
    assert cmd.supported is False


def test_supported_commands_total():
    modes = {
        "Mode 01 — Live Data": [
            CommandStatus(name="RPM", pid="0x0C", description="Engine RPM", supported=True),
            CommandStatus(name="SPEED", pid="0x0D", description="Vehicle Speed", supported=False),
        ],
        "Mode 03 — DTCs": [
            CommandStatus(name="GET_DTC", pid="-", description="Get DTCs", supported=True),
        ],
    }
    sc = SupportedCommands(modes=modes)
    assert sc.total == 3


def test_supported_commands_supported_count():
    modes = {
        "Mode 01 — Live Data": [
            CommandStatus(name="RPM", pid="0x0C", description="Engine RPM", supported=True),
            CommandStatus(name="SPEED", pid="0x0D", description="Vehicle Speed", supported=False),
            CommandStatus(name="COOLANT_TEMP", pid="0x05", description="Coolant Temp", supported=True),
        ],
    }
    sc = SupportedCommands(modes=modes)
    assert sc.supported_count == 2


def test_supported_commands_empty():
    sc = SupportedCommands(modes={})
    assert sc.total == 0
    assert sc.supported_count == 0
