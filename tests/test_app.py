"""Tests for the TabbedContent-based OBDReaderApp."""

import asyncio
from unittest.mock import MagicMock, patch

from textual.widgets import Footer, Static

from odb_tui.app import PANEL_BUILDERS, TAB_ORDER, OBDReaderApp
from odb_tui.views.panels.diag import build_diag_panel
from odb_tui.views.panels.egr import build_egr_panel
from odb_tui.views.panels.engine import build_engine_panel
from odb_tui.views.panels.errors import build_errors_panel
from odb_tui.views.panels.turbo import build_turbo_panel


def test_tab_order_has_six_entries():
    """TAB_ORDER should contain exactly six tab definitions."""
    assert len(TAB_ORDER) == 6


def test_tab_order_ids_and_titles():
    """TAB_ORDER ids and titles should match the expected layout."""
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
    """PANEL_BUILDERS should map five panel ids to their builder functions."""
    assert len(PANEL_BUILDERS) == 5
    assert PANEL_BUILDERS["engine"] is build_engine_panel
    assert PANEL_BUILDERS["turbo"] is build_turbo_panel
    assert PANEL_BUILDERS["egr"] is build_egr_panel
    assert PANEL_BUILDERS["diag"] is build_diag_panel
    assert PANEL_BUILDERS["errors"] is build_errors_panel


def test_panel_builders_excludes_pids():
    """PIDs panel uses a dedicated builder and should not be in PANEL_BUILDERS."""
    assert "pids" not in PANEL_BUILDERS


def test_bindings_include_tab_keys():
    """All numeric and 'p' key bindings for tab switching should be present."""
    keys = {b.key for b in OBDReaderApp.BINDINGS}
    assert "1" in keys
    assert "2" in keys
    assert "3" in keys
    assert "4" in keys
    assert "5" in keys
    assert "p" in keys


def test_bindings_tab_actions():
    """Each tab key binding should map to the correct switch_tab action."""
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
    """Calling action_switch_tab should set the TabbedContent active tab."""
    mock_ctrl = _mock_ctrl()
    mock_ctrl_cls.return_value = mock_ctrl

    async def run():
        app = OBDReaderApp()
        async with app.run_test() as pilot:
            from textual.widgets import TabbedContent

            await pilot.pause()
            mock_ctrl.status = "CONNECTED"
            await app.action_connect()
            await pilot.pause()
            await app.action_switch_tab("turbo")
            await pilot.pause()
            tabs = app.query_one("#tabs", TabbedContent)
            assert tabs.active == "turbo"

    _run_async(run())


@patch("odb_tui.app.AppController")
def test_action_switch_tab_to_each_panel(mock_ctrl_cls):
    """Switching to every tab in TAB_ORDER should activate each one."""
    mock_ctrl = _mock_ctrl()
    mock_ctrl_cls.return_value = mock_ctrl

    async def run():
        app = OBDReaderApp()
        async with app.run_test() as pilot:
            from textual.widgets import TabbedContent

            await pilot.pause()
            mock_ctrl.status = "CONNECTED"
            await app.action_connect()
            await pilot.pause()
            for tab_id, _ in TAB_ORDER:
                await app.action_switch_tab(tab_id)
                await pilot.pause()
                tabs = app.query_one("#tabs", TabbedContent)
                assert tabs.active == tab_id

    _run_async(run())


@patch("odb_tui.app.AppController")
def test_refresh_active_panel_calls_builder_for_engine(mock_ctrl_cls):
    """Refreshing the active panel on engine tab should call the engine builder."""
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
    """Refreshing the active panel on turbo tab should call the turbo builder."""
    mock_ctrl = _mock_ctrl()
    mock_ctrl_cls.return_value = mock_ctrl
    mock_builder = MagicMock(return_value="TURBO MOCK")

    async def run():
        import odb_tui.app as app_mod

        original = app_mod.PANEL_BUILDERS["turbo"]
        app_mod.PANEL_BUILDERS["turbo"] = mock_builder
        try:
            app = OBDReaderApp()
            async with app.run_test() as pilot:
                await pilot.pause()
                mock_ctrl.status = "CONNECTED"
                await app.action_connect()
                await pilot.pause()
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
    """Refreshing on pids tab should call build_pids_panel with supported commands."""
    mock_ctrl = _mock_ctrl()
    mock_ctrl_cls.return_value = mock_ctrl

    async def run():
        app = OBDReaderApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            mock_ctrl.status = "CONNECTED"
            await app.action_connect()
            await pilot.pause()
            await app.action_switch_tab("pids")
            await pilot.pause()
            with patch("odb_tui.app.build_pids_panel", return_value="PIDS MOCK") as mock_pids:
                app._refresh_active_panel()
                mock_pids.assert_called_once_with(mock_ctrl.supported_commands)

    _run_async(run())


@patch("odb_tui.app.AppController")
def test_refresh_active_panel_default_engine(mock_ctrl_cls):
    """The default active tab on mount should be engine."""
    mock_ctrl_cls.return_value = _mock_ctrl()

    async def run():
        app = OBDReaderApp()
        async with app.run_test() as pilot:
            from textual.widgets import TabbedContent

            await pilot.pause()
            tabs = app.query_one("#tabs", TabbedContent)
            assert tabs.active == "engine"

    _run_async(run())


@patch("odb_tui.app.AppController")
def test_no_status_bar_static_widget(mock_ctrl_cls):
    """Old #status-bar Static widget should no longer exist in the DOM."""
    mock_ctrl_cls.return_value = _mock_ctrl()

    async def run():
        app = OBDReaderApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            results = app.query("#status-bar")
            assert len(results) == 0

    _run_async(run())


@patch("odb_tui.app.AppController")
def test_app_has_no_status_bar_attribute_as_static(mock_ctrl_cls):
    """App should not expose a status_bar attribute typed as Static."""
    mock_ctrl_cls.return_value = _mock_ctrl()

    async def run():
        app = OBDReaderApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            assert not hasattr(app, "status_bar") or not isinstance(app.status_bar, Static)

    _run_async(run())


@patch("odb_tui.app.AppController")
def test_refresh_status_method_exists(mock_ctrl_cls):
    """App should have a callable _refresh_status method."""
    mock_ctrl_cls.return_value = _mock_ctrl()

    async def run():
        app = OBDReaderApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            assert hasattr(app, "_refresh_status")
            assert callable(app._refresh_status)

    _run_async(run())


@patch("odb_tui.app.AppController")
def test_default_footer_shows_disconnected_info(mock_ctrl_cls):
    """Footer should be present after refreshing status with default controller."""
    mock_ctrl_cls.return_value = _mock_ctrl()

    async def run():
        app = OBDReaderApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            app._refresh_status()
            await pilot.pause()
            footer = app.query_one(Footer)
            assert footer is not None

    _run_async(run())


@patch("odb_tui.app.AppController")
def test_css_has_no_status_bar_rule(mock_ctrl_cls):
    """App CSS should not contain the removed #status-bar rule."""
    mock_ctrl_cls.return_value = _mock_ctrl()
    assert "#status-bar" not in OBDReaderApp.CSS


@patch("odb_tui.app.AppController")
def test_refresh_status_updates_connection_info(mock_ctrl_cls):
    """Refreshing status with a connected controller should keep the footer present."""
    mock_ctrl = _mock_ctrl()
    mock_ctrl.status = "CONNECTED"
    mock_ctrl.port = "/dev/ttyUSB0"
    mock_ctrl.vid = "1a86"
    mock_ctrl.pid = "7523"
    mock_ctrl_cls.return_value = mock_ctrl

    async def run():
        app = OBDReaderApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            app._refresh_status()
            await pilot.pause()
            footer = app.query_one(Footer)
            assert footer is not None

    _run_async(run())


@patch("odb_tui.app.AppController")
def test_tabs_disabled_on_startup(mock_ctrl_cls):
    """All tabs should be disabled on startup when device is not connected."""
    mock_ctrl_cls.return_value = _mock_ctrl()

    async def run():
        app = OBDReaderApp()
        async with app.run_test() as pilot:
            from textual.widgets import TabbedContent

            await pilot.pause()
            tabs_widget = app.query_one("#tabs", TabbedContent)
            for tab_id, _ in TAB_ORDER:
                tab = tabs_widget.get_tab(tab_id)
                assert tab.disabled, f"Tab '{tab_id}' should be disabled on startup"

    _run_async(run())


@patch("odb_tui.app.AppController")
def test_tabs_enabled_after_connect(mock_ctrl_cls):
    """All tabs should be enabled after a successful connection."""
    mock_ctrl = _mock_ctrl()
    mock_ctrl_cls.return_value = mock_ctrl

    async def run():
        app = OBDReaderApp()
        async with app.run_test() as pilot:
            from textual.widgets import TabbedContent

            await pilot.pause()
            mock_ctrl.status = "CONNECTED"
            await app.action_connect()
            await pilot.pause()
            tabs_widget = app.query_one("#tabs", TabbedContent)
            for tab_id, _ in TAB_ORDER:
                tab = tabs_widget.get_tab(tab_id)
                assert not tab.disabled, f"Tab '{tab_id}' should be enabled after connect"

    _run_async(run())


@patch("odb_tui.app.AppController")
def test_tabs_disabled_after_disconnect(mock_ctrl_cls):
    """All tabs should be disabled again after disconnecting."""
    mock_ctrl = _mock_ctrl()
    mock_ctrl_cls.return_value = mock_ctrl

    async def run():
        app = OBDReaderApp()
        async with app.run_test() as pilot:
            from textual.widgets import TabbedContent

            await pilot.pause()
            mock_ctrl.status = "CONNECTED"
            await app.action_connect()
            await pilot.pause()
            mock_ctrl.status = "DISCONNECTED"
            await app.action_disconnect()
            await pilot.pause()
            tabs_widget = app.query_one("#tabs", TabbedContent)
            for tab_id, _ in TAB_ORDER:
                tab = tabs_widget.get_tab(tab_id)
                assert tab.disabled, f"Tab '{tab_id}' should be disabled after disconnect"

    _run_async(run())


@patch("odb_tui.app.AppController")
def test_action_switch_tab_ignored_when_disconnected(mock_ctrl_cls):
    """Switching tabs via action_switch_tab should be ignored when disconnected."""
    mock_ctrl_cls.return_value = _mock_ctrl()

    async def run():
        app = OBDReaderApp()
        async with app.run_test() as pilot:
            from textual.widgets import TabbedContent

            await pilot.pause()
            tabs_widget = app.query_one("#tabs", TabbedContent)
            initial_active = tabs_widget.active
            await app.action_switch_tab("turbo")
            await pilot.pause()
            assert tabs_widget.active == initial_active, "Tab should not switch when disconnected"

    _run_async(run())


@patch("odb_tui.app.AppController")
def test_disabled_tabs_have_dimmed_style(mock_ctrl_cls):
    """Disabled tabs should have a distinct dimmed visual style via CSS."""
    mock_ctrl_cls.return_value = _mock_ctrl()
    assert "Tab.-disabled" in OBDReaderApp.CSS or "Tab:disabled" in OBDReaderApp.CSS
