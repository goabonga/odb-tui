"""Textual TUI application for OBD-II diagnostics."""

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Static

from odb_tui.controllers.app_controller import AppController


class OBDReaderApp(App[None]):
    """Minimal Textual app rendering an OBD-II dashboard."""

    CSS = """
    Screen { background: black; color: green; }
    #status-bar { height: 1; text-align: right; color: green; }
    """

    BINDINGS = [
        Binding("c", "connect", "Connect"),
        Binding("d", "disconnect", "Disconnect"),
        Binding("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Build the widget tree: header, main content, status bar, footer."""
        yield Header(show_clock=True)
        yield Static("OBD-II Reader", id="main")
        self.status_bar = Static("DISCONNECTED  |  -  |  -:-", id="status-bar")
        yield self.status_bar
        yield Footer()

    async def on_mount(self) -> None:
        """Initialize the controller."""
        self.ctrl = AppController()

    def _refresh_status(self) -> None:
        self.status_bar.update(f"{self.ctrl.status}  |  {self.ctrl.port}  |  {self.ctrl.vid}:{self.ctrl.pid}")

    async def action_connect(self) -> None:
        """Handle 'c' key: connect to the OBD adapter."""
        self.ctrl.connect()
        self._refresh_status()

    async def action_disconnect(self) -> None:
        """Handle 'd' key: disconnect from the OBD adapter."""
        self.ctrl.disconnect()
        self._refresh_status()
