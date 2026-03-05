"""Textual TUI application — delegates all logic to AppController."""

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, TabbedContent, TabPane, Sparkline
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.binding import Binding

from odb_read.controllers.app_controller import AppController
from odb_read.models.log_config import LogConfig
from odb_read.views.logging_setup import setup_logging
from odb_read.views.widgets import Panel
from odb_read.views.panels.engine import build_engine_panel
from odb_read.views.panels.turbo import build_turbo_panel
from odb_read.views.panels.dpf_egr import build_dpf_panel
from odb_read.views.panels.gearbox import build_gearbox_panel
from odb_read.views.panels.diag import build_diag_panel
from odb_read.views.panels.pids import build_pids_panel
from odb_read.views.panels.scan_panel import build_scan_panel
from odb_read.views.panels.elm_logs import build_elm_log_panel
from odb_read.views.panels.errors import build_error_panel


class OBDReaderApp(App):
    """Textual application that renders live OBD-II data in a tabbed dashboard."""

    def __init__(self, log_config: LogConfig | None = None, **kwargs):
        super().__init__(**kwargs)
        self._log_config = log_config or LogConfig()

    CSS = """
    Screen { background: black; color: green; }
    #main-area { height: 1fr; }
    #left  { width: 70%; border: solid green; }
    #right { color: red; width: 1fr; }
    #rpm-spark { height: 5; color: green; border-top: solid green; }
    TabbedContent { height: 1fr; }
    TabPane { height: 1fr; }
    .tab-scroll { height: 1fr; }
    #err-scroll { width: 30%; height: 1fr; border: solid red; }
    #status-bar { height: 1; }
    #status-right { width: 1fr; text-align: right; color: green; }
    """

    BINDINGS = [
        Binding("c", "connect", "Connect"),
        Binding("r", "reconnect", "Reconnect"),
        Binding("d", "disconnect", "Disconnect"),
        Binding("g", "toggle_csv", "CSV Log"),
        Binding("t", "cycle_tire", "Pneu"),
        Binding("v", "cycle_gearbox", "Boite"),
        Binding("s", "scan_dids", "Scan $22"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Build the widget tree: header, tabbed panels, error sidebar, status bar, footer."""
        yield Header(show_clock=True)
        with Horizontal(id="main-area"):
            with Vertical(id="left"):
                with TabbedContent():
                    with TabPane("Moteur", id="tab-engine"):
                        with VerticalScroll(classes="tab-scroll"):
                            self.engine_panel = Panel(id="engine-panel")
                            yield self.engine_panel
                    with TabPane("Turbo/Air", id="tab-turbo"):
                        with VerticalScroll(classes="tab-scroll"):
                            self.turbo_panel = Panel(id="turbo-panel")
                            yield self.turbo_panel
                    with TabPane("DPF/EGR", id="tab-dpf"):
                        with VerticalScroll(classes="tab-scroll"):
                            self.dpf_panel = Panel(id="dpf-panel")
                            yield self.dpf_panel
                    with TabPane("Boite", id="tab-gearbox"):
                        with VerticalScroll(classes="tab-scroll"):
                            self.gearbox_panel = Panel(id="gearbox-panel")
                            yield self.gearbox_panel
                    with TabPane("Diag", id="tab-diag"):
                        with VerticalScroll(classes="tab-scroll"):
                            self.diag_panel = Panel(id="diag-panel")
                            yield self.diag_panel
                    with TabPane("PIDs", id="tab-pids"):
                        with VerticalScroll(classes="tab-scroll"):
                            self.pids_panel = Panel(id="pids-panel")
                            yield self.pids_panel
                    with TabPane("Scan", id="tab-scan", disabled=True):
                        with VerticalScroll(classes="tab-scroll"):
                            self.scan_panel = Panel(id="scan-panel")
                            yield self.scan_panel
                    with TabPane("ELM Logs", id="tab-elm"):
                        with VerticalScroll(classes="tab-scroll"):
                            self.elm_log_panel = Panel(id="elm-log-panel")
                            yield self.elm_log_panel
                self.rpm_sparkline = Sparkline([], id="rpm-spark")
                yield self.rpm_sparkline
            with VerticalScroll(id="err-scroll"):
                self.errors = Panel(id="right")
                yield self.errors
        with Horizontal(id="status-bar"):
            self.status_widget = Static("", id="status-right")
            yield self.status_widget
        yield Footer()

    async def on_mount(self):
        """Initialize logging, create the controller, and start the 1-second refresh timer."""
        self.log_handler, self.elm_log_file = setup_logging(self._log_config)
        self.ctrl = AppController(log_config=self._log_config)
        self.set_interval(1, self.update_ui)

    # -- Actions --

    async def action_connect(self):
        """Handle 'c' key: connect to the OBD adapter."""
        self.ctrl.connect()

    async def action_reconnect(self):
        """Handle 'r' key: disconnect then reconnect."""
        self.ctrl.reconnect()

    async def action_disconnect(self):
        """Handle 'd' key: disconnect from the OBD adapter."""
        self.ctrl.disconnect()

    async def action_toggle_csv(self):
        """Handle 'g' key: toggle CSV data logging on/off."""
        self.ctrl.toggle_csv()

    async def action_cycle_tire(self):
        """Handle 't' key: cycle to the next tire preset."""
        self.ctrl.cycle_tire()

    async def action_cycle_gearbox(self):
        """Handle 'v' key: cycle to the next gearbox preset."""
        self.ctrl.cycle_gearbox()

    async def action_scan_dids(self):
        """Handle 's' key: start or stop a UDS DID scan."""
        if self.ctrl.scanning:
            self.ctrl.scan_service.request_stop()
            return
        if not self.ctrl.conn.is_connected:
            return
        # Clear panels during scan
        for panel in (self.engine_panel, self.turbo_panel, self.dpf_panel,
                      self.gearbox_panel, self.diag_panel, self.pids_panel, self.errors):
            panel.update_content("SCAN EN COURS...")
        # Enable and switch to Scan tab
        tab_pane = self.query_one("#tab-scan")
        tab_pane.disabled = False
        tc = self.query_one(TabbedContent)
        tc.active = "tab-scan"
        self.ctrl.start_scan()

    # -- Update loop --

    async def update_ui(self):
        """Periodic callback: read sensors, refresh all panels, write CSV row."""
        ctrl = self.ctrl

        # During scan, only update scan panel and status bar
        if ctrl.scanning:
            self.status_widget.update(
                f"SCANNING  |  {ctrl.scan_progress.phase}  |  "
                f"{ctrl.scan_progress.status}  |  Hits: {ctrl.scan_progress.hits}"
            )
            self.scan_panel.update_content(build_scan_panel(ctrl.scan_progress))
            return

        # Read all sensors
        state = ctrl.read_state()

        # Update panels
        self.engine_panel.update_content(build_engine_panel(state))
        self.turbo_panel.update_content(build_turbo_panel(state))
        self.dpf_panel.update_content(build_dpf_panel(state))
        self.gearbox_panel.update_content(build_gearbox_panel(state))
        self.diag_panel.update_content(build_diag_panel(state))
        self.pids_panel.update_content(build_pids_panel(ctrl.conn))
        self.errors.update_content(build_error_panel(state))

        # ELM logs
        self.elm_log_panel.update_content(
            build_elm_log_panel(self.log_handler, self.elm_log_file)
        )

        # Scan panel (if results exist)
        if ctrl.scan_progress.raw_log or ctrl.scan_progress.results:
            self.scan_panel.update_content(build_scan_panel(ctrl.scan_progress))

        # RPM sparkline
        self.rpm_sparkline.data = state.rpm_history

        # CSV logging
        ctrl.write_csv_row(state)

        # Status bar
        csv_state = "REC" if state.csv_logging else "OFF"
        self.status_widget.update(
            f"CSV: {csv_state}  |  {ctrl.status}  |  {state.port}"
            f"  |  {state.vid}:{state.pid}"
        )
