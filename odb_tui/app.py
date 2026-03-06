"""Textual TUI application for OBD-II diagnostics."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Static, TabbedContent, TabPane

from odb_tui.controllers.app_controller import AppController
from odb_tui.models.vehicle import VehicleState
from odb_tui.views.panels.diag import build_diag_panel
from odb_tui.views.panels.egr import build_egr_panel
from odb_tui.views.panels.engine import build_engine_panel
from odb_tui.views.panels.errors import build_errors_panel
from odb_tui.views.panels.pids import build_pids_panel
from odb_tui.views.panels.turbo import build_turbo_panel

TAB_ORDER: list[tuple[str, str]] = [
    ("engine", "Engine"),
    ("turbo", "Turbo"),
    ("egr", "EGR"),
    ("diag", "Diag"),
    ("errors", "Errors"),
    ("pids", "PIDs"),
]

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
    TabbedContent { background: black; }
    TabPane { background: black; color: green; }
    Tabs { background: black; color: green; }
    Tab { background: black; color: green; }
    Tab.-active { background: green; color: black; }
    """

    BINDINGS = [
        Binding("c", "connect", "Connect"),
        Binding("d", "disconnect", "Disconnect"),
        Binding("1", "switch_tab('engine')", "Engine"),
        Binding("2", "switch_tab('turbo')", "Turbo"),
        Binding("3", "switch_tab('egr')", "EGR"),
        Binding("4", "switch_tab('diag')", "Diag"),
        Binding("5", "switch_tab('errors')", "Errors"),
        Binding("p", "switch_tab('pids')", "PIDs"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="engine", id="tabs"):
            for tab_id, title in TAB_ORDER:
                with TabPane(title, id=tab_id):
                    yield Static("", id=f"panel-{tab_id}")
        self.status_bar = Static("DISCONNECTED  |  -  |  -:-", id="status-bar")
        yield self.status_bar
        yield Footer()

    async def on_mount(self) -> None:
        self.ctrl = AppController()
        self._state = VehicleState()
        self._refresh_active_panel()
        self._poll_timer = self.set_interval(1.0, self._poll_sensors, pause=True)

    def _refresh_status(self) -> None:
        self.status_bar.update(f"{self.ctrl.status}  |  {self.ctrl.port}  |  {self.ctrl.vid}:{self.ctrl.pid}")

    def _refresh_active_panel(self) -> None:
        self._state.connection_status = self.ctrl.status
        tabs = self.query_one("#tabs", TabbedContent)
        active = tabs.active
        if active == "pids":
            content = build_pids_panel(self.ctrl.supported_commands)
        else:
            builder = PANEL_BUILDERS.get(active, build_engine_panel)
            content = builder(self._state)
        panel = self.query_one(f"#panel-{active}", Static)
        panel.update(content)

    def on_tabbed_content_tab_activated(self, event: TabbedContent.TabActivated) -> None:
        self._refresh_active_panel()

    def _poll_sensors(self) -> None:
        self.ctrl.update_state(self._state)
        self._state.connection_status = self.ctrl.status
        self._refresh_active_panel()

    async def action_connect(self) -> None:
        self.ctrl.connect()
        self._refresh_status()
        self._refresh_active_panel()
        if self.ctrl.status == "CONNECTED":
            self._poll_timer.resume()

    async def action_disconnect(self) -> None:
        self._poll_timer.pause()
        self.ctrl.disconnect()
        self._state = VehicleState()
        self._refresh_status()
        self._refresh_active_panel()

    async def action_switch_tab(self, name: str) -> None:
        tabs = self.query_one("#tabs", TabbedContent)
        tabs.active = name
