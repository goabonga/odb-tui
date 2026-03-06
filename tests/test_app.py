import asyncio
from unittest.mock import MagicMock, patch

from odb_tui.app import PANEL_BUILDERS, TAB_ORDER, OBDReaderApp
from odb_tui.views.panels.diag import build_diag_panel
from odb_tui.views.panels.egr import build_egr_panel
from odb_tui.views.panels.engine import build_engine_panel
from odb_tui.views.panels.errors import build_errors_panel
from odb_tui.views.panels.turbo import build_turbo_panel


def test_tab_order_has_six_entries():
    assert len(TAB_ORDER) == 6


def test_tab_order_ids_and_titles():
    expected = [
        ("engine", "Engine"),
        ("turbo", "Turbo"),
        ("egr", "EGR"),
        ("diag", "Diag"),
        ("errors", "Errors"),
        ("pids", "PIDs"),
    ]
    assert TAB_ORDER == expected


def test_panel_builders_maps_five_panels():
    assert len(PANEL_BUILDERS) == 5
    assert PANEL_BUILDERS["engine"] is build_engine_panel
    assert PANEL_BUILDERS["turbo"] is build_turbo_panel
    assert PANEL_BUILDERS["egr"] is build_egr_panel
    assert PANEL_BUILDERS["diag"] is build_diag_panel
    assert PANEL_BUILDERS["errors"] is build_errors_panel


def test_panel_builders_excludes_pids():
    assert "pids" not in PANEL_BUILDERS


def test_bindings_include_tab_keys():
    keys = {b.key for b in OBDReaderApp.BINDINGS}
    assert "1" in keys
    assert "2" in keys
    assert "3" in keys
    assert "4" in keys
    assert "5" in keys
    assert "p" in keys


def test_bindings_tab_actions():
    action_map = {b.key: b.action for b in OBDReaderApp.BINDINGS}
    assert action_map["1"] == "switch_tab('engine')"
    assert action_map["2"] == "switch_tab('turbo')"
    assert action_map["3"] == "switch_tab('egr')"
    assert action_map["4"] == "switch_tab('diag')"
    assert action_map["5"] == "switch_tab('errors')"
    assert action_map["p"] == "switch_tab('pids')"


def _mock_ctrl():
    ctrl = MagicMock()
    ctrl.status = "DISCONNECTED"
    ctrl.port = "-"
    ctrl.vid = "-"
    ctrl.pid = "-"
    ctrl.supported_commands = None
    return ctrl


def _run_async(coro):
    asyncio.run(coro)


@patch("odb_tui.app.AppController")
def test_action_switch_tab_sets_active(mock_ctrl_cls):
    mock_ctrl_cls.return_value = _mock_ctrl()

    async def run():
        app = OBDReaderApp()
        async with app.run_test() as pilot:
            from textual.widgets import TabbedContent

            await app.action_switch_tab("turbo")
            await pilot.pause()
            tabs = app.query_one("#tabs", TabbedContent)
            assert tabs.active == "turbo"

    _run_async(run())


@patch("odb_tui.app.AppController")
def test_action_switch_tab_to_each_panel(mock_ctrl_cls):
    mock_ctrl_cls.return_value = _mock_ctrl()

    async def run():
        app = OBDReaderApp()
        async with app.run_test() as pilot:
            from textual.widgets import TabbedContent

            for tab_id, _ in TAB_ORDER:
                await app.action_switch_tab(tab_id)
                await pilot.pause()
                tabs = app.query_one("#tabs", TabbedContent)
                assert tabs.active == tab_id

    _run_async(run())


@patch("odb_tui.app.AppController")
def test_refresh_active_panel_calls_builder_for_engine(mock_ctrl_cls):
    mock_ctrl_cls.return_value = _mock_ctrl()
    mock_builder = MagicMock(return_value="ENGINE MOCK")

    async def run():
        import odb_tui.app as app_mod

        original = app_mod.PANEL_BUILDERS["engine"]
        app_mod.PANEL_BUILDERS["engine"] = mock_builder
        try:
            app = OBDReaderApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                mock_builder.reset_mock()
                app._refresh_active_panel()
                mock_builder.assert_called_once()
        finally:
            app_mod.PANEL_BUILDERS["engine"] = original

    _run_async(run())


@patch("odb_tui.app.AppController")
def test_refresh_active_panel_calls_builder_for_turbo(mock_ctrl_cls):
    mock_ctrl_cls.return_value = _mock_ctrl()
    mock_builder = MagicMock(return_value="TURBO MOCK")

    async def run():
        import odb_tui.app as app_mod

        original = app_mod.PANEL_BUILDERS["turbo"]
        app_mod.PANEL_BUILDERS["turbo"] = mock_builder
        try:
            app = OBDReaderApp()
            async with app.run_test() as pilot:
                await app.action_switch_tab("turbo")
                await pilot.pause()
                mock_builder.reset_mock()
                app._refresh_active_panel()
                mock_builder.assert_called_once()
        finally:
            app_mod.PANEL_BUILDERS["turbo"] = original

    _run_async(run())


@patch("odb_tui.app.AppController")
def test_refresh_active_panel_calls_pids_builder(mock_ctrl_cls):
    mock_ctrl = _mock_ctrl()
    mock_ctrl_cls.return_value = mock_ctrl

    async def run():
        app = OBDReaderApp()
        async with app.run_test() as pilot:
            await app.action_switch_tab("pids")
            await pilot.pause()
            with patch("odb_tui.app.build_pids_panel", return_value="PIDS MOCK") as mock_pids:
                app._refresh_active_panel()
                mock_pids.assert_called_once_with(mock_ctrl.supported_commands)

    _run_async(run())


@patch("odb_tui.app.AppController")
def test_refresh_active_panel_default_engine(mock_ctrl_cls):
    mock_ctrl_cls.return_value = _mock_ctrl()

    async def run():
        app = OBDReaderApp()
        async with app.run_test() as pilot:
            from textual.widgets import TabbedContent

            await pilot.pause()
            tabs = app.query_one("#tabs", TabbedContent)
            assert tabs.active == "engine"

    _run_async(run())
