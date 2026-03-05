"""Textual TUI application for OBD-II diagnostics."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Static

from odb_tui.controllers.app_controller import AppController
from odb_tui.models.vehicle import VehicleState
from odb_tui.views.panels.diag import build_diag_panel
from odb_tui.views.panels.egr import build_egr_panel
from odb_tui.views.panels.engine import build_engine_panel
from odb_tui.views.panels.errors import build_errors_panel
from odb_tui.views.panels.pids import build_pids_panel
from odb_tui.views.panels.turbo import build_turbo_panel

PANEL_BUILDERS = {
    "engine": build_engine_panel,
    "turbo": build_turbo_panel,
    "egr": build_egr_panel,
    "diag": build_diag_panel,
    "errors": build_errors_panel,
}


class OBDReaderApp(App[None]):
    """Minimal Textual app rendering an OBD-II dashboard."""

    CSS = """
    Screen { background: black; color: green; }
    #status-bar { height: 1; text-align: right; color: green; }
    #dashboard { display: block; }
    #pids-panel { display: none; }
    .show-pids #dashboard { display: none; }
    .show-pids #pids-panel { display: block; }
    """

    BINDINGS = [
        Binding("c", "connect", "Connect"),
        Binding("d", "disconnect", "Disconnect"),
        Binding("1", "panel('engine')", "Engine"),
        Binding("2", "panel('turbo')", "Turbo"),
        Binding("3", "panel('egr')", "EGR"),
        Binding("4", "panel('diag')", "Diag"),
        Binding("5", "panel('errors')", "Errors"),
        Binding("p", "toggle_pids", "PIDs"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Build the widget tree: header, dashboard, pids panel, status bar, footer."""
        yield Header(show_clock=True)
        yield Static("", id="dashboard")
        yield Static("", id="pids-panel")
        self.status_bar = Static("DISCONNECTED  |  -  |  -:-", id="status-bar")
        yield self.status_bar
        yield Footer()

    async def on_mount(self) -> None:
        """Initialize the controller and default panel."""
        self.ctrl = AppController()
        self._current_panel = "engine"
        self._state = VehicleState()
        self._refresh_dashboard()

    def _refresh_status(self) -> None:
        self.status_bar.update(f"{self.ctrl.status}  |  {self.ctrl.port}  |  {self.ctrl.vid}:{self.ctrl.pid}")

    def _refresh_dashboard(self) -> None:
        self._state.connection_status = self.ctrl.status
        builder = PANEL_BUILDERS.get(self._current_panel, build_engine_panel)
        dashboard = self.query_one("#dashboard", Static)
        dashboard.update(builder(self._state))

    async def action_connect(self) -> None:
        """Handle 'c' key: connect to the OBD adapter."""
        self.ctrl.connect()
        self._refresh_status()
        self._refresh_dashboard()

    async def action_disconnect(self) -> None:
        """Handle 'd' key: disconnect from the OBD adapter."""
        self.ctrl.disconnect()
        self._state = VehicleState()
        self._refresh_status()
        self._refresh_dashboard()

    async def action_panel(self, name: str) -> None:
        """Handle 1-5 keys: switch active dashboard panel."""
        self.screen.remove_class("show-pids")
        self._current_panel = name
        self._refresh_dashboard()

    async def action_toggle_pids(self) -> None:
        """Handle 'p' key: toggle the supported PIDs panel."""
        self.screen.toggle_class("show-pids")
        panel = self.query_one("#pids-panel", Static)
        panel.update(build_pids_panel(self.ctrl.supported_commands))
