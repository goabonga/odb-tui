# odb-read

OBD-II diagnostic TUI with UDS scanning, CSV logging, and real-time analysis.

## Installation

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

For development (linting, tests, type-checking):

```bash
pip install -e ".[dev]"
```

For graph generation:

```bash
pip install -e ".[graph]"
```

## Usage

```bash
# Launch the TUI (no file logging by default)
odb-read

# Enable all file logs
odb-read --log-all

# Write logs to a dedicated directory
odb-read --log-all --log-dir ./logs

# Enable specific logs only
odb-read --elm-log --csv-log
odb-read --dtc-log --scan-log

# Custom filenames
odb-read --csv-log --csv-filename data.csv --log-dir ./logs

# Generate graphs from a CSV file
odb-graph
```

### CLI Options

| Option | Description |
|--------|-------------|
| `--log-dir DIR` | Output directory for log files (default: `.`) |
| `--log-all` | Enable all file logs |
| `--elm-log` | Enable ELM327 debug log |
| `--csv-log` | Enable CSV data log |
| `--pids-log` | Enable supported PIDs log |
| `--dtc-log` | Enable DTC report log |
| `--scan-log` | Enable UDS scan log |
| `--elm-filename` | Custom filename for ELM log |
| `--csv-filename` | Custom filename for CSV log |
| `--pids-filename` | Custom filename for PIDs log |
| `--dtc-filename` | Custom filename for DTC log |
| `--scan-filename` | Custom filename for scan log |

### Keyboard Shortcuts (TUI)

| Key | Action |
|-----|--------|
| `c` | Connect to OBD adapter |
| `r` | Reconnect |
| `d` | Disconnect |
| `g` | Toggle CSV logging |
| `t` | Cycle tire preset |
| `v` | Cycle gearbox preset |
| `s` | Start/stop UDS scan |
| `q` | Quit |

## Development

```bash
make check    # lint + typecheck + tests
make test     # tests only
make lint     # ruff check
make format   # ruff format
```

## Architecture

```
odb_read/
├── models/          # Dataclasses (VehicleState, LogConfig, presets, etc.)
├── views/           # Textual TUI (app, widgets, panels/)
├── controllers/     # AppController, UpdateController
└── services/        # OBD connection, CSV, UDS scanner, ELM transport
```
