from odb_tui.models.supported_commands import CommandStatus, SupportedCommands
from odb_tui.views.panels.pids import build_pids_panel


def _make_supported_commands() -> SupportedCommands:
    modes = {
        "Mode 01 — Live Data": [
            CommandStatus(name="RPM", pid="0x0C", description="Engine RPM", supported=True),
            CommandStatus(name="SPEED", pid="0x0D", description="Vehicle Speed", supported=False),
        ],
    }
    return SupportedCommands(modes=modes)


def test_build_pids_panel_not_connected():
    result = build_pids_panel(None)
    assert "Not connected" in result


def test_build_pids_panel_no_title():
    sc = _make_supported_commands()
    result = build_pids_panel(sc)
    first_line = result.split("\n")[0]
    assert first_line != "SUPPORTED OBD COMMANDS"


def test_build_pids_panel_with_commands():
    sc = _make_supported_commands()
    result = build_pids_panel(sc)
    assert "1 / 2 supported" in result
    assert "Mode 01" in result
    assert "RPM" in result
    assert "SPEED" in result


def test_build_pids_panel_checkbox_format():
    sc = _make_supported_commands()
    result = build_pids_panel(sc)
    lines = result.split("\n")
    rpm_line = [line for line in lines if "RPM" in line][0]
    egt_lines = [line for line in lines if "SPEED" in line]
    speed_line = egt_lines[0]
    assert "[x]" in rpm_line
    assert "[ ]" in speed_line


def test_build_pids_panel_mode_headers_present():
    sc = _make_supported_commands()
    result = build_pids_panel(sc)
    assert "Mode 01 — Live Data" in result
