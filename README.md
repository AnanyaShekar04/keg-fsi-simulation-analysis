# Keg FSI Simulation - Frequency Response Analysis Pipeline

**Author:** Ananya Shekar
**Institution:** ifak Institut für Automation und Kommunikation e.V., Magdeburg, Germany (Studentische Hilfskraft, Oct 2025 – May 2026)
**Simulation Tool:** COMSOL Multiphysics 6.4
**Analysis Tool:** Python 3
**Project Type:** Research internship — non-invasive fill level detection

## Table of Contents

1. [Project Overview](#project-overview)
2. [Real World Application](#real-world-application)
3. [Physics Background](#physics-background)
4. [COMSOL Simulation Setup](#comsol-simulation-setup)
5. [Geometry and Parametrization](#geometry-and-parametrization)
6. [Physics Interfaces](#physics-interfaces)
7. [Multiphysics Coupling](#multiphysics-coupling)
8. [Mesh Configuration](#mesh-configuration)
9. [Virtual Sensor Setup](#virtual-sensor-setup)
10. [Fill Levels Simulated](#fill-levels-simulated)
11. [Python Analysis Pipeline](#python-analysis-pipeline)
12. [How to Run](#how-to-run)
13. [Key Findings](#key-findings)
14. [Data Provenance](#data-provenance)
15. [Tech Stack](#tech-stack)
16. [Repository Structure](#repository-structure)

## Project Overview

This project develops a high-fidelity Fluid-Structure Interaction (FSI) simulation of a 30L DIN-standard keg to analyze how varying fluid fill levels affect the structural-acoustic frequency response of the keg shell.

The simulation couples Solid Mechanics, Pressure Acoustics (Water), and Pressure Acoustics (Air) in COMSOL Multiphysics 6.4 to model the physical behavior of a partially filled pressurized vessel under harmonic excitation across 10–1000 Hz.

A Python post-processing pipeline (`keg_analysis.py`) automates peak and anti-resonance detection across fill levels, quantifies the resonance shift, and generates a combined frequency response plot.

**Headline result:** the primary structural-acoustic resonance shifts monotonically **from 22 Hz (low fill) to 18 Hz (high fill)** as fill level increases, with a **fill-independent reference mode at 28 Hz** that stays fixed across all fill levels — providing a calibration anchor for sensor-based fill classification.

## Real World Application

In the beverage and industrial vessel industries, knowing how full a keg or tank is without opening it is a critical operational requirement. Traditional methods rely on weight measurement or invasive sensors. This project investigates a non-invasive approach using vibration sensing:

- Attach a piezoelectric vibration sensor to the outer surface of the keg
- Apply a frequency sweep excitation
- Measure the structural displacement response
- Infer fill level from where the resonance peak sits, using the fixed 28 Hz mode as a calibration reference

**Why simulate first:** COMSOL allows systematic study of all fill levels before physical prototyping, identifies optimal sensor placement, and predicts which frequency ranges are most sensitive to fill-level change — reducing experimental cost and time.

Applications: beverage industry keg monitoring, chemical/food industry tank level monitoring, oil & gas non-invasive fluid level sensing.

## Physics Background

**Fluid-Structure Interaction (FSI):** describes the two-way interaction between a deformable solid structure and an enclosed fluid. When the keg shell vibrates, it compresses and expands the fluid inside; the fluid exerts pressure back on the shell, modifying its vibrational behavior.

**Structural Mechanics** - the keg shell is modeled as linear elastic steel (AISI 4340), governed by:

```
M·ü + C·u̇ + K·u = F(t)
```

**Pressure Acoustics** - the fluid domains (water and air) are modeled with the frequency-domain Helmholtz equation:

```
∇²p + (ω/c)²·p = 0
```

**Why two acoustic domains:** water/beer at the bottom (density 1000 kg/m³, speed of sound 1481 m/s) and air at the top (density 1.2 kg/m³, speed of sound 343 m/s) have fundamentally different acoustic properties and are modeled separately, coupled at the fill-level interface.

**Resonance and anti-resonance:** resonance peaks occur when excitation frequency matches a natural frequency of the coupled system (displacement maximized). Anti-resonances occur when structural and acoustic responses cancel out of phase (displacement minimized). Both shift with fill level as fluid mass loading changes — this shift is the physical basis for the fill-detection concept.

## COMSOL Simulation Setup

- COMSOL Multiphysics 6.4.0.378
- Structural Mechanics Module, Acoustics Module, Multiphysics coupling
- Study type: Frequency Domain
- Frequency range: 10–1000 Hz

## Geometry and Parametrization

Keg geometry imported from a DIN-standard 30L keg CAD file (hollow-shell STEP format). Interior fluid domains (water and air) were manually constructed as parametric cylinders since they aren't present in the shell-only CAD import:

| Parameter | Expression | Description |
|---|---|---|
| `h_water` | variable | Height of water domain |
| `h_air` | `h_total - h_water` | Height of air domain (auto-updates) |
| `h_total` | 0.229 m | Total internal keg height |

Form Assembly (not Form Union) was used to handle the disconnected solid (steel shell) and fluid (water + air) components, with identity pairs created at the fluid-solid interfaces. This was a required workaround for a COMSOL geometry limitation: two separate fluid domains cannot be created without identity pairs when built this way.

## Physics Interfaces

**Solid Mechanics (`solid2`)** — steel shell domains. Material: Steel AISI 4340 (density 7850 kg/m³, Young's modulus 205 GPa, Poisson's ratio 0.28).

**Pressure Acoustics — Water (`acpr`)** — water cylinder domain. Density 1000 kg/m³, speed of sound 1481 m/s.

**Pressure Acoustics — Air (`acpr2`)** — air cylinder domain. Density 1.2 kg/m³, speed of sound 343 m/s.

## Multiphysics Coupling

- **Acoustic-Structure boundary pair:** steel shell ↔ fluid domains, at all inner walls where fluid contacts steel. Two-way FSI coupling.
- **Acoustic-Acoustic boundary pair:** water domain ↔ air domain, at the fill-level interface.

## Mesh Configuration

- Physics-controlled mesh, fine element size
- ~142,805 elements, 835,636 degrees of freedom
- ~45 seconds average solution time per frequency step

## Virtual Sensor Setup

A Domain Point Probe on the outer steel shell simulates a piezoelectric vibration sensor:

| Parameter | Value |
|---|---|
| Probe location | (0.064057, 0.022963, 0.16969) m |
| Expression | `solid2.disp` |
| Unit | mm |

## Fill Levels Simulated

Seven fill configurations were run across the project: empty keg (baseline), quarter fill (0.066 m), half fill (0.133 m), and four fill heights — 0.14 m, 0.16 m, 0.18 m, 0.20 m.

The four core fill levels (0.14–0.20 m) and the empty-keg baseline have full raw COMSOL exports in this repository — 1 Hz resolution across the full 10–1000 Hz sweep for the four fill levels, and 10 Hz resolution for the empty-keg baseline. Quarter and half fill were run later in the project, specifically to characterize the high-frequency shell modes (600–1000 Hz) after the primary resonance behavior was already established from the four fill levels above — no low-frequency data exists for those two. See [Data Provenance](#data-provenance) for the exact breakdown.

## Python Analysis Pipeline

`keg_analysis.py`:

1. **`load_fill_level_data()`** — reads all `data/fill_level_*.csv` files into a dict keyed by fill level.
2. **`find_primary_resonance()`** — uses `scipy.signal.find_peaks` to locate the dominant resonance in a search window.
3. **`find_reference_mode()`** — locates the fill-independent shell mode near 28 Hz.
4. **`find_anti_resonances()`** — finds local minima (anti-resonance dips) via `find_peaks` on the inverted signal.
5. **`summarize_resonance_shift()`** — builds and prints the resonance summary table, quantifies the shift magnitude across fill levels.
6. **`plot_combined_frequency_response()`** — generates the combined full-sweep + zoomed-resonance plot.

## How to Run

```bash
git clone https://github.com/AnanyaShekar04/keg-fsi-simulation-analysis.git
cd keg-fsi-simulation-analysis
pip install pandas matplotlib scipy numpy
python3 keg_analysis.py
```

Adding a new fill level: drop a new `fill_level_<label>.csv` (columns: `frequency_hz`, `response_amplitude`) into `data/`, matching the existing format. The script auto-discovers all `fill_level_*.csv` files — no code changes needed.

## Key Findings

| Fill Level | Primary Resonance (Hz) | Reference Mode (Hz) |
|---|---|---|
| 0.14 m | 22 | 28 |
| 0.16 m | 20 | 28 |
| 0.18 m | 20 | 28 |
| 0.20 m | 18 | 28 |

- **Resonance shift: 22 Hz → 18 Hz** as fill level increases, consistent with added fluid mass loading the structural-acoustic coupled mode downward.
- **28 Hz reference mode is fill-independent** across all tested levels — a calibration anchor for classification.
- High-frequency modes (600–1000 Hz region, per the April baseline run at 50 Hz resolution: peaks near 110/510/760 Hz) are shell-dominated and do not shift with fill level, confirming the low-frequency region is where fill-level information actually lives.

## Data Provenance

- **`fill_level_0.14m.csv`, `0.16m.csv`, `0.18m.csv`, `0.20m.csv`:** 100% raw COMSOL Probe Table exports, full 10–1000 Hz sweep at 1 Hz resolution (991 points each). No modeled or interpolated values.
- **`empty_keg_baseline.csv`:** raw export, 10 Hz resolution, 10–180 Hz.
- **`quarter_half_600_1000hz.csv`:** raw export for quarter (0.066 m) and half (0.133 m) fill, but only 600–1000 Hz at 10 Hz resolution — units are micrometers (µm), not meters, unlike the other CSVs. No low-frequency data for these two levels.

Every `data_source` column reads `comsol_raw` — there is no modeled or synthetic data in this repository. See `data/DATA_SOURCE.md` for the full breakdown.

## Tech Stack

| Tool | Purpose |
|---|---|
| COMSOL Multiphysics 6.4 | Multiphysics FSI simulation |
| Python 3 | Data processing and visualization |
| pandas | Data manipulation and CSV I/O |
| matplotlib | Plotting |
| scipy | Peak / anti-resonance detection |
| numpy | Numerical operations |
| Git / GitHub | Version control |

## Repository Structure

```
keg-fsi-simulation-analysis/
├── keg_analysis.py               # Main analysis script
├── README.md                     # This file
├── data/
│   ├── DATA_SOURCE.md
│   ├── empty_keg_baseline.csv
│   ├── fill_level_0.14m.csv
│   ├── fill_level_0.16m.csv
│   ├── fill_level_0.18m.csv
│   ├── fill_level_0.20m.csv
│   └── quarter_half_600_1000hz.csv
└── outputs/
    ├── keg_frequency_response_combined.png
    └── resonance_summary.csv
```

## Contact

**Ananya Shekar**
M.Sc. Electrical Engineering & Information Technology, Otto von Guericke University Magdeburg
ananyashekar4210@gmail.com | [LinkedIn](https://www.linkedin.com/in/ananya-shekar-04ee) | [GitHub](https://github.com/AnanyaShekar04)

This project was completed as part of a research internship (Studentische Hilfskraft) at ifak Institut für Automation und Kommunikation e.V., Magdeburg, Germany, Oct 2025 – May 2026.
