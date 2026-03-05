from odb_tui.models.supported_commands import CommandStatus, SupportedCommands
from odb_tui.views.panels.pids import build_pids_panel


def test_build_pids_panel_not_connected():
    result = build_pids_panel(None)
    assert "Not connected" in result


def test_build_pids_panel_with_commands():
    modes = {
        "Mode 01 — Live Data": [
            CommandStatus(name="RPM", pid="0x0C", description="Engine RPM", supported=True),
            CommandStatus(name="SPEED", pid="0x0D", description="Vehicle Speed", supported=False),
        ],
    }
    sc = SupportedCommands(modes=modes)
    result = build_pids_panel(sc)
    assert "SUPPORTED OBD COMMANDS" in result
    assert "1 / 2 supported" in result
    assert "Mode 01" in result
    assert "RPM" in result
    assert "SPEED" in result


def test_build_pids_panel_checkbox_format():
    modes = {
        "Mode 01 — Live Data": [
            CommandStatus(name="RPM", pid="0x0C", description="Engine RPM", supported=True),
            CommandStatus(name="EGT", pid="0x78", description="Exhaust Gas Temp", supported=False),
        ],
    }
    sc = SupportedCommands(modes=modes)
    result = build_pids_panel(sc)
    lines = result.split("\n")
    rpm_line = [line for line in lines if "RPM" in line][0]
    egt_line = [line for line in lines if "EGT" in line][0]
    assert "[x]" in rpm_line
    assert "[ ]" in egt_line
