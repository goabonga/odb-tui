"""Model for OBD-II supported commands discovery results."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CommandStatus:
    """Status of a single OBD command."""

    name: str
    pid: str
    description: str
    supported: bool


@dataclass
class SupportedCommands:
    """All OBD commands grouped by mode with support status."""

    modes: dict[str, list[CommandStatus]] = field(default_factory=dict)

    @property
    def total(self) -> int:
        """Total number of commands across all modes."""
        return sum(len(cmds) for cmds in self.modes.values())

    @property
    def supported_count(self) -> int:
        """Number of supported commands across all modes."""
        return sum(1 for cmds in self.modes.values() for cmd in cmds if cmd.supported)
