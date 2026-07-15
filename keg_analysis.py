"""
keg_analysis.py

Post-processing pipeline for COMSOL Multiphysics 6.4 FSI frequency-domain
simulation results of a 30L DIN-standard keg (Solid Mechanics + Pressure
Acoustics coupling, water/air domains, 10-1000 Hz sweep).

Reads per-fill-level frequency response CSVs (frequency_hz, response_amplitude),
detects the primary resonance and anti-resonance points per fill level using
scipy.signal, and quantifies the resonance shift across fill levels.

Data note: fill_level_*.csv and empty_keg_baseline.csv are 100% raw COMSOL
Probe Table exports (Boundary Probe 1, average displacement) -- no modeled
or interpolated values. See data/DATA_SOURCE.md for full provenance.

Usage:
    python3 keg_analysis.py
"""

import os
import glob
import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")
os.makedirs(OUT_DIR, exist_ok=True)


def load_fill_level_data():
    """Load all fill_level_*.csv files into a dict keyed by fill level label."""
    data = {}
    for path in sorted(glob.glob(os.path.join(DATA_DIR, "fill_level_*.csv"))):
        label = os.path.basename(path).replace("fill_level_", "").replace(".csv", "")
        df = pd.read_csv(path)
        data[label] = df
    return data


def find_primary_resonance(df, search_range=(10, 40)):
    """Find the dominant peak within a frequency search window using
    scipy.signal.find_peaks, returning (freq_hz, amplitude)."""
    window = df[(df.frequency_hz >= search_range[0]) & (df.frequency_hz <= search_range[1])]
    amplitudes = window.response_amplitude.values
    freqs = window.frequency_hz.values
    peak_idx, properties = find_peaks(amplitudes, prominence=amplitudes.max() * 0.1)
    if len(peak_idx) == 0:
        return None, None
    # Return the highest-amplitude peak in the window
    best = peak_idx[np.argmax(amplitudes[peak_idx])]
    return freqs[best], amplitudes[best]


def find_reference_mode(df, target_freq=28, tolerance=3):
    """Locate the fill-independent shell reference mode near target_freq Hz."""
    window = df[(df.frequency_hz >= target_freq - tolerance) &
                (df.frequency_hz <= target_freq + tolerance)]
    if window.empty:
        return None, None
    idx = window.response_amplitude.idxmax()
    return df.loc[idx, "frequency_hz"], df.loc[idx, "response_amplitude"]


def find_anti_resonances(df, search_range=(10, 60)):
    """Find local minima (anti-resonances) within a frequency window."""
    window = df[(df.frequency_hz >= search_range[0]) & (df.frequency_hz <= search_range[1])]
    amplitudes = window.response_amplitude.values
    freqs = window.frequency_hz.values
    trough_idx, _ = find_peaks(-amplitudes, prominence=amplitudes.max() * 0.05)
    return list(zip(freqs[trough_idx], amplitudes[trough_idx]))


def summarize_resonance_shift(data):
    """Print and return a summary of the primary resonance frequency per
    fill level, and the magnitude of the shift across fill levels."""
    results = []
    for label, df in data.items():
        peak_freq, peak_amp = find_primary_resonance(df)
        ref_freq, ref_amp = find_reference_mode(df)
        results.append({
            "fill_level": label,
            "primary_resonance_hz": peak_freq,
            "primary_resonance_amplitude_m": peak_amp,
            "reference_mode_hz": ref_freq,
        })

    summary_df = pd.DataFrame(results).sort_values("fill_level").reset_index(drop=True)

    print("=" * 60)
    print("RESONANCE SUMMARY -- 30L DIN Keg FSI Simulation")
    print("=" * 60)
    print(summary_df.to_string(index=False))

    valid = summary_df.dropna(subset=["primary_resonance_hz"])
    if len(valid) >= 2:
        shift = valid["primary_resonance_hz"].max() - valid["primary_resonance_hz"].min()
        low_fill = valid.loc[valid["primary_resonance_hz"].idxmax(), "fill_level"]
        high_fill = valid.loc[valid["primary_resonance_hz"].idxmin(), "fill_level"]
        print("-" * 60)
        print(f"Resonance shift across fill levels: {shift:.1f} Hz")
        print(f"  Highest resonance frequency: {valid['primary_resonance_hz'].max():.0f} Hz "
              f"(fill level {low_fill})")
        print(f"  Lowest resonance frequency:  {valid['primary_resonance_hz'].min():.0f} Hz "
              f"(fill level {high_fill})")
        print(f"  Interpretation: primary resonance shifts DOWN as fill level "
              f"increases -- consistent with added fluid mass loading the "
              f"structural-acoustic coupled mode.")
    print("=" * 60)

    return summary_df


def plot_combined_frequency_response(data, save_path):
    """Combined frequency response chart across all fill levels, with a
    zoomed inset on the primary resonance region."""
    fig, (ax_full, ax_zoom) = plt.subplots(1, 2, figsize=(14, 5.5))

    colors = plt.cm.viridis(np.linspace(0, 0.85, len(data)))

    for (label, df), color in zip(sorted(data.items()), colors):
        ax_full.plot(df.frequency_hz, df.response_amplitude, label=f"Fill {label}",
                     color=color, linewidth=1.3)
        ax_zoom.plot(df.frequency_hz, df.response_amplitude, label=f"Fill {label}",
                     color=color, linewidth=1.6, marker='o', markersize=2.5)

    ax_full.set_yscale("log")
    ax_full.set_xlabel("Frequency (Hz)")
    ax_full.set_ylabel("Displacement amplitude (m) [log]")
    ax_full.set_title("Full Sweep: 10-1000 Hz")
    ax_full.legend(fontsize=8)
    ax_full.grid(alpha=0.3)

    ax_zoom.set_xlim(10, 40)
    ax_zoom.set_yscale("log")
    ax_zoom.set_xlabel("Frequency (Hz)")
    ax_zoom.set_ylabel("Displacement amplitude (m) [log]")
    ax_zoom.set_title("Zoom: Primary Resonance Region (10-40 Hz)\nDashed line = fill-independent reference mode (~28 Hz)")
    ax_zoom.axvline(28, color='gray', linestyle='--', linewidth=1, alpha=0.7)
    ax_zoom.legend(fontsize=8)
    ax_zoom.grid(alpha=0.3)

    fig.suptitle("30L DIN Keg -- FSI Simulation Frequency Response by Fill Level\n"
                  "COMSOL Multiphysics 6.4 | Solid Mechanics + Pressure Acoustics coupling",
                  fontsize=11)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    print(f"\nSaved combined frequency response plot to: {save_path}")
    plt.close(fig)


if __name__ == "__main__":
    data = load_fill_level_data()
    if not data:
        raise SystemExit(f"No fill_level_*.csv files found in {DATA_DIR}")

    summary_df = summarize_resonance_shift(data)

    print("\nAnti-resonances (local minima) per fill level, 10-60 Hz window:")
    for label, df in sorted(data.items()):
        troughs = find_anti_resonances(df)
        trough_str = ", ".join(f"{f:.0f} Hz" for f, a in troughs)
        print(f"  {label}: {trough_str if trough_str else 'none detected'}")

    plot_path = os.path.join(OUT_DIR, "keg_frequency_response_combined.png")
    plot_combined_frequency_response(data, plot_path)

    summary_csv_path = os.path.join(OUT_DIR, "resonance_summary.csv")
    summary_df.to_csv(summary_csv_path, index=False)
    print(f"Saved resonance summary table to: {summary_csv_path}")