"""Generate a full OBD-II dashboard PNG from an obd_log_*.csv file."""

import sys
import glob as globmod
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# ── Dark theme ───────────────────────────────────────────────
C = {
    "bg":     "#0d1117",
    "panel":  "#161b22",
    "grid":   "#21262d",
    "text":   "#c9d1d9",
    "muted":  "#8b949e",
    "accent": "#58a6ff",
    "green":  "#3fb950",
    "orange": "#d29922",
    "red":    "#f85149",
    "cyan":   "#39d2e0",
    "purple": "#bc8cff",
    "yellow": "#e3b341",
    "pink":   "#f778ba",
    "lime":   "#a5d63a",
}


def load_csv(path: str) -> pd.DataFrame:
    """Load an OBD CSV log, drop rows without RPM, and add elapsed time columns."""
    df = pd.read_csv(path, parse_dates=["timestamp"])
    df = df.dropna(subset=["rpm"])
    df = df.reset_index(drop=True)
    df["elapsed_s"] = (df["timestamp"] - df["timestamp"].iloc[0]).dt.total_seconds()
    df["elapsed_min"] = df["elapsed_s"] / 60.0
    return df


def setup_ax(ax):
    """Apply the dark theme styling (colors, grid, spines) to a matplotlib Axes."""
    ax.set_facecolor(C["panel"])
    ax.tick_params(colors=C["text"], labelsize=6)
    ax.grid(True, color=C["grid"], linewidth=0.4, alpha=0.5)
    for spine in ax.spines.values():
        spine.set_color(C["grid"])
    ax.xaxis.label.set_color(C["text"])
    ax.yaxis.label.set_color(C["text"])


def has_data(df, col):
    """Return True if *col* exists in the DataFrame and has at least 2 non-null values."""
    return col in df.columns and df[col].dropna().shape[0] > 1


def plot_line(ax, df, col, label, unit, color, ylim=None, fill=True):
    """Plot a single time-series line with optional fill and min/moy/max stats overlay."""
    setup_ax(ax)
    data = df[col].dropna()
    if data.empty:
        ax.text(0.5, 0.5, "Pas de donnees", transform=ax.transAxes,
                ha="center", va="center", color=C["muted"], fontsize=9)
        ax.set_title(label, color=C["text"], fontsize=8, fontweight="bold", loc="left")
        return
    x = df.loc[data.index, "elapsed_min"]
    ax.plot(x, data, color=color, linewidth=1.0, alpha=0.9)
    if fill:
        ax.fill_between(x, data, alpha=0.12, color=color)
    vmin, vmax, vmean = data.min(), data.max(), data.mean()
    stats = f"min {vmin:.1f}  moy {vmean:.1f}  max {vmax:.1f}"
    ax.text(0.98, 0.93, stats, transform=ax.transAxes, ha="right", va="top",
            fontsize=5.5, color=C["text"], alpha=0.7,
            bbox=dict(boxstyle="round,pad=0.25", facecolor=C["bg"], edgecolor=C["grid"], alpha=0.8))
    ax.set_title(f"{label} ({unit})", color=C["text"], fontsize=8, fontweight="bold", loc="left")
    if ylim:
        ax.set_ylim(ylim)


def plot_dual(ax, df, col1, col2, label1, label2, title, unit, c1, c2, ylim=None):
    """Plot two overlaid time-series lines on the same Axes with a shared legend."""
    setup_ax(ax)
    for col, lbl, color in [(col1, label1, c1), (col2, label2, c2)]:
        data = df[col].dropna()
        if data.empty:
            continue
        x = df.loc[data.index, "elapsed_min"]
        ax.plot(x, data, color=color, linewidth=1.0, alpha=0.85, label=lbl)
        ax.fill_between(x, data, alpha=0.08, color=color)
    ax.legend(fontsize=5.5, loc="upper left", facecolor=C["panel"], edgecolor=C["grid"],
              labelcolor=C["text"], framealpha=0.9)
    ax.set_title(f"{title} ({unit})", color=C["text"], fontsize=8, fontweight="bold", loc="left")
    if ylim:
        ax.set_ylim(ylim)


def plot_scatter(ax, df, xcol, ycol, xlabel, ylabel, title, color):
    """Draw a scatter plot colored by elapsed time (cool colormap)."""
    setup_ax(ax)
    mask = df[xcol].notna() & df[ycol].notna()
    if mask.sum() < 2:
        ax.text(0.5, 0.5, "Pas de donnees", transform=ax.transAxes,
                ha="center", va="center", color=C["muted"], fontsize=9)
        ax.set_title(title, color=C["text"], fontsize=8, fontweight="bold", loc="left")
        return
    x, y = df.loc[mask, xcol], df.loc[mask, ycol]
    t = df.loc[mask, "elapsed_min"]
    sc = ax.scatter(x, y, c=t, cmap="cool", s=12, alpha=0.7, edgecolors="none")
    cbar = plt.colorbar(sc, ax=ax, pad=0.02)
    cbar.set_label("min", fontsize=5, color=C["muted"])
    cbar.ax.tick_params(labelsize=5, colors=C["muted"])
    ax.set_xlabel(xlabel, fontsize=6)
    ax.set_ylabel(ylabel, fontsize=6)
    ax.set_title(title, color=C["text"], fontsize=8, fontweight="bold", loc="left")


def plot_bar_status(ax, df, col, title, palette=None):
    """Draw a horizontal bar chart of status value counts (e.g. EGR/regen status)."""
    setup_ax(ax)
    data = df[col].dropna()
    if data.empty:
        ax.text(0.5, 0.5, "Pas de donnees", transform=ax.transAxes,
                ha="center", va="center", color=C["muted"], fontsize=9)
        ax.set_title(title, color=C["text"], fontsize=8, fontweight="bold", loc="left")
        return
    counts = data.value_counts()
    if palette is None:
        palette = {"OK": C["green"], "CLOSED": C["accent"], "WARN": C["orange"],
                   "BLOCKED": C["red"], "STUCK OPEN": C["red"],
                   "INACTIVE": C["muted"], "POSSIBLE": C["yellow"],
                   "ACTIVE (HIGH CONF)": C["red"], "LOW BOOST": C["orange"]}
    colors = [palette.get(v, C["purple"]) for v in counts.index]
    ax.barh(range(len(counts)), counts.values, color=colors, alpha=0.85, height=0.6)
    ax.set_yticks(range(len(counts)))
    ax.set_yticklabels(counts.index, fontsize=6)
    for i, v in enumerate(counts.values):
        pct = v / len(data) * 100
        ax.text(v + 0.3, i, f"{v} ({pct:.0f}%)", va="center", fontsize=5.5, color=C["text"])
    ax.set_title(title, color=C["text"], fontsize=8, fontweight="bold", loc="left")
    ax.invert_yaxis()


def plot_histogram(ax, df, col, label, unit, color, bins=25):
    """Draw a histogram with a dashed mean line."""
    setup_ax(ax)
    data = df[col].dropna()
    if data.empty:
        ax.text(0.5, 0.5, "Pas de donnees", transform=ax.transAxes,
                ha="center", va="center", color=C["muted"], fontsize=9)
        ax.set_title(label, color=C["text"], fontsize=8, fontweight="bold", loc="left")
        return
    ax.hist(data, bins=bins, color=color, alpha=0.7, edgecolor=C["grid"], linewidth=0.5)
    ax.axvline(data.mean(), color=C["red"], linewidth=1, linestyle="--", alpha=0.8, label=f"moy {data.mean():.1f}")
    ax.legend(fontsize=5.5, loc="upper right", facecolor=C["panel"], edgecolor=C["grid"],
              labelcolor=C["text"], framealpha=0.9)
    ax.set_title(f"{label} - Distribution ({unit})", color=C["text"], fontsize=8, fontweight="bold", loc="left")
    ax.set_xlabel(unit, fontsize=6)
    ax.set_ylabel("Nb", fontsize=6)


def add_section_label(fig, gs_row, text):
    """Add a styled section header label spanning the full grid row."""
    ax = fig.add_subplot(gs_row)
    ax.set_facecolor(C["bg"])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.text(0.005, 0.3, f"  {text}  ", transform=ax.transAxes,
            fontsize=10, fontweight="bold", color=C["accent"], va="center",
            bbox=dict(boxstyle="round,pad=0.3", facecolor=C["bg"], edgecolor=C["accent"], alpha=0.9))


def generate_graph(csv_path: str):
    """Build the full multi-section OBD-II dashboard PNG from a CSV log file."""
    df = load_csv(csv_path)

    t_start = df["timestamp"].iloc[0].strftime("%Y-%m-%d %H:%M:%S")
    t_end = df["timestamp"].iloc[-1].strftime("%H:%M:%S")
    duration_s = df["elapsed_s"].iloc[-1]
    duration_str = f"{int(duration_s // 60)}m{int(duration_s % 60):02d}s"
    nb_samples = len(df)

    n_sections = 8
    height_ratios = []
    for _ in range(n_sections):
        height_ratios += [1, 12]

    fig = plt.figure(figsize=(24, 36))
    fig.set_facecolor(C["bg"])

    gs = gridspec.GridSpec(n_sections * 2, 4, figure=fig,
                           height_ratios=height_ratios,
                           hspace=0.25, wspace=0.30,
                           left=0.04, right=0.98, top=0.975, bottom=0.02)

    fig.suptitle(
        f"OBD-II Dashboard Complet  —  {t_start} > {t_end}  ({duration_str}, {nb_samples} samples)",
        color=C["accent"], fontsize=15, fontweight="bold", y=0.99,
    )

    # ROW 0 — MOTEUR
    add_section_label(fig, gs[0, :], "MOTEUR")
    r = 1
    ax = fig.add_subplot(gs[r, 0])
    plot_line(ax, df, "rpm", "Regime moteur", "tr/min", C["green"], ylim=(0, None))
    ax = fig.add_subplot(gs[r, 1])
    plot_line(ax, df, "engine_load_pct", "Charge moteur", "%", C["cyan"], ylim=(0, 100))
    ax = fig.add_subplot(gs[r, 2])
    if has_data(df, "abs_load_pct"):
        plot_line(ax, df, "abs_load_pct", "Charge absolue", "%", C["purple"])
    else:
        plot_histogram(ax, df, "rpm", "RPM", "tr/min", C["green"])
    ax = fig.add_subplot(gs[r, 3])
    plot_line(ax, df, "run_time_s", "Temps fonctionnement", "s", C["muted"])

    # ROW 1 — TEMPERATURES
    add_section_label(fig, gs[2, :], "TEMPERATURES")
    r = 3
    ax = fig.add_subplot(gs[r, 0])
    plot_line(ax, df, "coolant_temp_c", "Temp. liquide refroid.", "°C", C["orange"])
    ax = fig.add_subplot(gs[r, 1])
    if has_data(df, "oil_temp_c"):
        plot_line(ax, df, "oil_temp_c", "Temp. huile", "°C", C["red"])
    else:
        if has_data(df, "intake_temp_c"):
            plot_dual(ax, df, "coolant_temp_c", "intake_temp_c",
                      "Liquide", "Admission", "Temperatures", "°C", C["orange"], C["cyan"])
        else:
            plot_line(ax, df, "coolant_temp_c", "Temp. liquide (zoom)", "°C", C["orange"])
    ax = fig.add_subplot(gs[r, 2])
    plot_line(ax, df, "intake_temp_c", "Temp. admission", "°C", C["cyan"])
    ax = fig.add_subplot(gs[r, 3])
    if has_data(df, "ambient_temp_c"):
        plot_line(ax, df, "ambient_temp_c", "Temp. ambiante", "°C", C["yellow"])
    elif has_data(df, "egt_pre_dpf_c") and has_data(df, "egt_post_dpf_c"):
        plot_dual(ax, df, "egt_pre_dpf_c", "egt_post_dpf_c",
                  "Pre-DPF", "Post-DPF", "Temp. echappement (EGT)", "°C", C["red"], C["orange"])
    else:
        plot_histogram(ax, df, "coolant_temp_c", "Temp. liquide", "°C", C["orange"])

    # ROW 2 — TURBO / PRESSION
    add_section_label(fig, gs[4, :], "TURBO / PRESSION")
    r = 5
    ax = fig.add_subplot(gs[r, 0])
    plot_line(ax, df, "net_boost_kpa", "Boost net", "kPa", C["purple"])
    ax = fig.add_subplot(gs[r, 1])
    plot_line(ax, df, "max_boost_kpa", "Boost max observe", "kPa", C["pink"])
    ax = fig.add_subplot(gs[r, 2])
    plot_line(ax, df, "intake_pressure_kpa", "Pression admission", "kPa", C["accent"])
    ax = fig.add_subplot(gs[r, 3])
    if has_data(df, "baro_kpa"):
        plot_dual(ax, df, "intake_pressure_kpa", "baro_kpa",
                  "Admission", "Baro", "Admission vs Barometrique", "kPa", C["accent"], C["yellow"])
    else:
        plot_line(ax, df, "baro_kpa", "Pression barometrique", "kPa", C["yellow"])

    # ROW 3 — DEBIT AIR / PAPILLON
    add_section_label(fig, gs[6, :], "DEBIT AIR / PAPILLON")
    r = 7
    ax = fig.add_subplot(gs[r, 0])
    plot_line(ax, df, "maf_gs", "Debit air (MAF)", "g/s", C["cyan"])
    ax = fig.add_subplot(gs[r, 1])
    plot_line(ax, df, "throttle_pct", "Position papillon", "%", C["green"], ylim=(0, 100))
    ax = fig.add_subplot(gs[r, 2])
    plot_line(ax, df, "throttle_actuator_pct", "Actuateur papillon", "%", C["lime"], ylim=(0, 100))
    ax = fig.add_subplot(gs[r, 3])
    if has_data(df, "accel_d_pct") and has_data(df, "accel_e_pct"):
        plot_dual(ax, df, "accel_d_pct", "accel_e_pct",
                  "Pedale D", "Pedale E", "Pedales accelerateur", "%", C["orange"], C["yellow"], ylim=(0, 100))
    else:
        plot_line(ax, df, "accel_d_pct", "Pedale accel. D", "%", C["orange"], ylim=(0, 100))

    # ROW 4 — CARBURANT / ELECTRIQUE
    add_section_label(fig, gs[8, :], "CARBURANT / ELECTRIQUE")
    r = 9
    ax = fig.add_subplot(gs[r, 0])
    plot_line(ax, df, "rail_pressure_kpa", "Pression rampe", "kPa", C["red"])
    ax = fig.add_subplot(gs[r, 1])
    plot_line(ax, df, "fuel_level_pct", "Niveau carburant", "%", C["green"], ylim=(0, 100))
    ax = fig.add_subplot(gs[r, 2])
    plot_line(ax, df, "voltage_v", "Tension batterie", "V", C["yellow"])
    ax = fig.add_subplot(gs[r, 3])
    plot_histogram(ax, df, "voltage_v", "Tension batterie", "V", C["yellow"])

    # ROW 5 — EGR / DPF
    add_section_label(fig, gs[10, :], "EGR / DPF / ECHAPPEMENT")
    r = 11
    ax = fig.add_subplot(gs[r, 0])
    plot_line(ax, df, "egr_cmd_pct", "Commande EGR", "%", C["cyan"])
    ax = fig.add_subplot(gs[r, 1])
    plot_line(ax, df, "egr_err_pct", "Erreur EGR", "%", C["red"])
    ax = fig.add_subplot(gs[r, 2])
    if has_data(df, "egr_status"):
        plot_bar_status(ax, df, "egr_status", "Repartition EGR Status")
    elif has_data(df, "dpf_diff_kpa"):
        plot_line(ax, df, "dpf_diff_kpa", "DPF Delta Pression", "kPa", C["orange"])
    else:
        setup_ax(ax)
        plot_dual(ax, df, "egr_cmd_pct", "egr_err_pct",
                  "Commande", "Erreur", "EGR Cmd vs Erreur", "%", C["cyan"], C["red"])
    ax = fig.add_subplot(gs[r, 3])
    if has_data(df, "regen_status"):
        plot_bar_status(ax, df, "regen_status", "Repartition Regen Status")
    elif has_data(df, "dpf_diff_kpa"):
        plot_line(ax, df, "dpf_diff_kpa", "DPF Delta Pression", "kPa", C["orange"])
    else:
        plot_histogram(ax, df, "egr_err_pct", "Erreur EGR", "%", C["red"])

    # ROW 6 — VITESSE / BOITE
    add_section_label(fig, gs[12, :], "VITESSE / BOITE")
    r = 13
    ax = fig.add_subplot(gs[r, 0])
    plot_line(ax, df, "speed_kmh", "Vitesse vehicule", "km/h", C["accent"], ylim=(0, None))
    ax = fig.add_subplot(gs[r, 1])
    if has_data(df, "speed_kmh") and has_data(df, "rpm"):
        plot_dual(ax, df, "speed_kmh", "rpm",
                  "Vitesse", "RPM", "Vitesse vs RPM", "km/h | tr/min", C["accent"], C["green"])
        ax2 = ax.twinx()
        ax2.set_ylabel("RPM", fontsize=6, color=C["green"])
        ax2.tick_params(colors=C["green"], labelsize=5)
    else:
        plot_line(ax, df, "speed_kmh", "Vitesse", "km/h", C["accent"])
    ax = fig.add_subplot(gs[r, 2])
    if has_data(df, "turbo_status"):
        plot_bar_status(ax, df, "turbo_status", "Repartition Turbo Status")
    else:
        plot_histogram(ax, df, "net_boost_kpa", "Boost net", "kPa", C["purple"])
    ax = fig.add_subplot(gs[r, 3])
    if has_data(df, "gear") and df["gear"].dropna().shape[0] > 2:
        plot_line(ax, df, "gear", "Rapport engage", "N", C["lime"], fill=False)
    else:
        plot_histogram(ax, df, "engine_load_pct", "Charge moteur", "%", C["cyan"])

    # ROW 7 — ANALYSE / CORRELATIONS
    add_section_label(fig, gs[14, :], "ANALYSE / CORRELATIONS")
    r = 15
    ax = fig.add_subplot(gs[r, 0])
    plot_scatter(ax, df, "rpm", "engine_load_pct", "RPM", "Charge %",
                 "RPM vs Charge moteur", C["cyan"])
    ax = fig.add_subplot(gs[r, 1])
    plot_scatter(ax, df, "rpm", "net_boost_kpa", "RPM", "Boost kPa",
                 "RPM vs Boost net", C["purple"])
    ax = fig.add_subplot(gs[r, 2])
    plot_scatter(ax, df, "rpm", "maf_gs", "RPM", "MAF g/s",
                 "RPM vs Debit air", C["green"])
    ax = fig.add_subplot(gs[r, 3])
    plot_scatter(ax, df, "rpm", "voltage_v", "RPM", "Tension V",
                 "RPM vs Tension batterie", C["yellow"])

    # Save
    out_path = csv_path.replace(".csv", "_dashboard.png")
    fig.savefig(out_path, dpi=150, facecolor=C["bg"])
    plt.close(fig)
    print(f"Dashboard saved: {out_path}  ({Path(out_path).stat().st_size / 1024:.0f} KB)")
    return out_path


def main():
    """CLI entry point: generate dashboard from a CSV path argument or the most recent log."""
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        files = sorted(globmod.glob("obd_log_*.csv"))
        if not files:
            print("No obd_log_*.csv file found in current directory.")
            sys.exit(1)
        csv_path = files[-1]
        print(f"Using most recent file: {csv_path}")

    generate_graph(csv_path)


if __name__ == "__main__":
    main()
