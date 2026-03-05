# odb-tui

Terminal-based OBD-II diagnostic dashboard for real-time vehicle data.

## Installation

```bash
pip install odb-tui
```

## Usage

```bash
# Launch the TUI
odb-tui

# Show version
odb-tui --version
```

## What it does

- Auto-detect OBD-II USB adapters (vLinker, VID 0403/PID 6015) and connect via python-obd
- Discover all supported OBD commands (modes 01-09 + ELM) and display them grouped by mode with support checkboxes
- Dashboard panels with conditional display — only shows data for commands supported by the vehicle:
  - **Engine** (1): RPM, load, temperatures, fuel, O2 sensors
  - **Turbo/Air** (2): intake pressure, boost, throttle, accelerator
  - **EGR** (3): commanded EGR, error interpretation
  - **Diagnostics** (4): MIL status, DTCs, OBD compliance, counters, calibration
  - **Errors** (5): active diagnostic trouble codes
  - **Supported PIDs** (p): full OBD command list with availability checkboxes
- Keybindings: `c` connect, `d` disconnect, `1`-`5` switch panels, `p` PIDs, `q` quit

## Development

### Prerequisites

- Python 3.13+

### Setup

```bash
make install-dev
```

### Code Quality

```bash
# Run linter (ruff)
make lint

# Format code
make format

# Run type checker (mypy)
make typecheck

# Run all checks (lint + typecheck + tests)
make check
```

### Testing

```bash
# Run tests
make test
```

### Conventional Commits

This project uses [Conventional Commits](https://www.conventionalcommits.org/) for commit messages:

```bash
# Interactive commit
cz commit

# Or use git with conventional format
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug"
```

Commit types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.

### Release

Releases are triggered by commits with the `chore(release):` prefix on `main` branch:

```bash
# Standard release (version bumped automatically based on conventional commits)
git commit --allow-empty -m "chore(release): release a new version"

# Stable release (bumps major version, e.g. 0.x.x -> 1.0.0)
git commit --allow-empty -m "chore(release): release a stable version"
```

The release workflow:
1. Checks if commit matches `chore(release): ...`
2. Detects `stable` keyword for major version bump
3. Waits for CI to pass
4. Bumps version with commitizen (major bump if stable)
5. Generates changelog
6. Publishes package to PyPI
7. Creates GitHub release

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

[MIT](LICENSE)
