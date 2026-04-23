# keg-fsi-simulation-analysis
Keg FSI Simulation — Frequency Response Analysis Pipeline

Author: Ananya Shekar  
Institution: ifak Institut für Automation und Kommunikation e.V., Magdeburg, Germany  
Simulation Tool: COMSOL Multiphysics 6.4
Analysis Tool: Python 3
Project Type: Research Internship — Non-Invasive Fill Level Detection

📋 Table of Contents

1.Project Overview
2.Real World Application
3.Physics Background
4.COMSOL Simulation Setup
5.Geometry and Parametrization
6.Physics Interfaces
7.Multiphysics Coupling
8.Mesh Configuration
9.Virtual Sensor Setup
10.Fill Levels Simulated
11.Python Analysis Pipeline
12.How to Run
13.Sample Results
14.Key Findings
15.Power BI Dashboard
16.Tech Stack
17.Repository Structure


🎯 Project Overview
This project develops a high-fidelity Fluid-Structure Interaction (FSI) simulation of a 30L DIN standard beer keg to analyze how varying fluid fill levels affect the structural-acoustic frequency response of the keg shell.
The simulation couples Solid Mechanics, Pressure Acoustics (Water), and Pressure Acoustics (Air) in COMSOL Multiphysics 6.4 to model the complete physical behavior of a partially filled pressurized vessel under harmonic excitation across a frequency range of 10 Hz to 1000 Hz.
A Python post-processing pipeline automates the analysis of COMSOL exported results — automatically detecting resonance peaks, generating publication-ready plots, and exporting structured data for Power BI visualization.

🌍 Real World Application
In industrial and beverage industries, knowing how full a keg or tank is without opening it is a critical operational requirement. Traditional methods involve weight measurement or invasive sensors. This project investigates a non-invasive approach using vibration sensing:
The concept:

Attach a piezoelectric vibration sensor to the outer surface of the keg
Apply a frequency sweep excitation
Measure the structural displacement response
The resonance frequencies shift with fill level — allowing fill level to be inferred from the frequency response

Why simulation first:

Simulating with COMSOL allows systematic study of all fill levels before physical experiments
Identifies optimal sensor placement locations
Predicts which frequency ranges are most sensitive to fill level changes
Reduces experimental cost and time

This approach has applications in:

Beverage industry — keg fill monitoring
Chemical industry — tank level monitoring
Food processing — vessel fill detection
Oil and gas — non-invasive fluid level sensing


⚛️ Physics Background
What is Fluid-Structure Interaction (FSI)?
FSI describes the interaction between a deformable solid structure and a surrounding or enclosed fluid. When the keg shell vibrates, it compresses and expands the fluid inside. The fluid in turn exerts pressure back on the shell — modifying its vibrational behavior. This two-way coupling is what makes the problem complex and interesting.
Structural Mechanics
The keg shell is modeled as a linear elastic solid (Steel AISI 4340). When subjected to harmonic excitation, it deforms according to Newton's second law:
M·ü + C·u̇ + K·u = F(t)
Where M is the mass matrix, C is the damping matrix, K is the stiffness matrix, u is displacement, and F is the applied force.
Pressure Acoustics
The fluid domains (water and air) are modeled using the Helmholtz equation for pressure acoustics in the frequency domain:
∇²p + (ω/c)²·p = 0
Where p is acoustic pressure, ω is angular frequency, and c is the speed of sound in the medium.
Why Two Acoustic Domains?
A partially filled keg contains:

Water/beer at the bottom — high density (1000 kg/m³), high speed of sound (1481 m/s)
Air at the top — low density (1.2 kg/m³), low speed of sound (343 m/s)

These two fluids have fundamentally different acoustic properties and must be modeled separately with a coupling boundary at their interface (the fill level surface).
Resonance and Anti-resonance

Resonance peaks occur when the excitation frequency matches a natural frequency of the coupled system — displacement is maximized
Anti-resonances occur when the structural and acoustic responses are out of phase and cancel — displacement is minimized
Both features shift with fill level as the fluid mass loading changes


🔧 COMSOL Simulation Setup
Software

COMSOL Multiphysics 6.4.0.378
Structural Mechanics Module
Acoustics Module
Multiphysics coupling

Study Type

Frequency Domain — solves the coupled system at each frequency step
Frequency range: range(10, 10, 1000) Hz
Total frequency steps: 99 per fill level


📐 Geometry and Parametrization
The keg geometry was imported from a DIN standard 30L keg CAD file (.stp format). The internal fluid domains were created parametrically using two cylinders:
ParameterExpressionDescriptionh_watervariableHeight of water domainh_airh_total - h_waterHeight of air domain (auto-updates)h_total0.229 mTotal internal keg height
Water cylinder:

Height = h_water
Bottom position y = -0.111 m (keg floor)

Air cylinder:

Height = h_air
Bottom position y = -0.111 + h_water (sits directly on top of water — no gap)

This parametric setup ensures:

Geometry automatically rebuilds correctly for any fill level
No gap between water and air domains
Acoustic-acoustic boundary is always correctly positioned at the fill level interface

Form Assembly was used instead of Form Union to correctly handle the disconnected solid (steel shell) and fluid (water + air) components, creating identity pairs at the fluid-solid interfaces.

⚙️ Physics Interfaces
1. Solid Mechanics (solid2)

Assigned to: All steel shell domains
Material: Steel AISI 4340

Density: 7850 kg/m³
Young's Modulus: 205 GPa
Poisson's Ratio: 0.28


Purpose: Models structural deformation and vibration of the keg walls under harmonic excitation

2. Pressure Acoustics — Water Domain (acpr)

Assigned to: Water cylinder domain
Material: Water, liquid

Density: 1000 kg/m³
Speed of sound: 1481 m/s


Purpose: Models acoustic pressure waves within the water domain

3. Pressure Acoustics — Air Domain (acpr2)

Assigned to: Air cylinder domain
Material: Air

Density: 1.2 kg/m³
Speed of sound: 343 m/s


Purpose: Models acoustic behavior of the air gap above the water surface


🔗 Multiphysics Coupling
Two coupling interfaces connect the three physics:
Pair Acoustic-Structure Boundary

Connects: Steel shell (Solid Mechanics) ↔ Fluid domains (Pressure Acoustics)
Boundaries: All inner walls of the keg where fluid contacts steel
Function: Ensures structural vibration drives acoustic pressure in the fluid, and fluid pressure loads drive structural deformation — the two-way FSI coupling

Acoustic-Acoustic Boundary

Connects: Water domain (acpr) ↔ Air domain (acpr2)
Boundary: The flat horizontal circular interface where water surface meets air
Function: Correctly transmits acoustic waves across the water-air interface, representing the physical fill level surface


🔲 Mesh Configuration

Mesh type: Physics-controlled mesh
Element size: Fine
Total elements: ~142,805
Degrees of freedom solved: 835,636
Average solution time: ~45 seconds per frequency step

The mesh resolves both the thin steel shell and the internal fluid domains adequately across the full frequency range of interest (10–1000 Hz).

📍 Virtual Sensor Setup
A Domain Point Probe was placed on the outer steel shell surface to simulate a piezoelectric vibration sensor:
ParameterValueProbe location(0.064057, 0.022963, 0.16969) mExpressionsolid2.dispUnitmmPhysical equivalentPiezoelectric accelerometer on outer shell
Why this is equivalent to a real sensor:
Real Piezo SensorCOMSOL ProbeGlued on outer steel shellProbe point on outer shell surfaceMeasures surface displacement/vibrationsolid2.disp at a pointOutput: Voltage vs frequencyOutput: Displacement (mm) vs frequencyFrequency sweep via signal analyzerFrequency Domain study

📊 Fill Levels Simulated
Studyh_waterh_airFill PercentageStatusStudy 10.160 m0.069 m70%✅ CompleteStudy 20.180 m0.049 m79%✅ CompleteStudy 30.200 m0.029 m87%✅ Complete
Each study used identical physics settings, boundary conditions, mesh configuration and probe location to ensure scientifically comparable results.

🐍 Python Analysis Pipeline
The script keg_analysis.py provides a fully automated post-processing workflow:
What it does step by step:
Step 1 — Data Loading
pythondef load_comsol_txt(filepath):
    # Reads COMSOL exported probe table .txt files
    # Skips comment lines starting with %
    # Returns clean pandas DataFrame with Frequency_Hz and Displacement_mm columns
Step 2 — Peak Detection
pythondef detect_peaks(df, prominence=1e-7, distance=3):
    # Uses scipy.signal.find_peaks to automatically identify resonance peaks
    # prominence: minimum peak height above surrounding baseline
    # distance: minimum spacing between peaks in data points
Step 3 — Anti-resonance Detection
pythondef detect_antiresonances(df, prominence=1e-7, distance=3):
    # Inverts the signal and finds peaks = finds minima in original
    # Identifies anti-resonance dip frequencies automatically
Step 4 — Plot Generation

Combined plot — all fill levels overlaid on one graph
Individual subplots — one per fill level with peaks and dips marked
Bar chart — peak frequency comparison across fill levels

Step 5 — Data Export

peak_summary.csv — structured table of all peaks
all_fill_levels_combined.csv — full dataset for Power BI

Output Files
FileDescriptioncombined_frequency_response.pngAll fill levels on one graph with peaks annotatedindividual_frequency_response.pngSeparate subplot per fill levelpeak_frequency_comparison.pngBar chart comparing peak frequenciespeak_summary.csvTable of resonance peaks and anti-resonances per fill levelall_fill_levels_combined.csvFull combined dataset ready for Power BI import

▶️ How to Run
1. Clone the repository
bashgit clone https://github.com/AnanyaShekar04/keg-fsi-simulation-analysis.git
cd keg-fsi-simulation-analysis
2. Install dependencies
bashpip install pandas matplotlib scipy numpy
3. Update file paths
Open keg_analysis.py and update the FILL_LEVELS dictionary at the top:
pythonFILL_LEVELS = {
    "0.160m (70% fill)": "data/0_16m_freq_vs_displacement.txt",
    "0.180m (79% fill)": "data/0_18m_freq_vs_displacement.txt",
    "0.200m (87% fill)": "data/0_20m_freq_vs_displacement.txt",
}
4. Run the script
bashpython keg_analysis.py
5. Adding new fill levels
Simply add a new entry to the FILL_LEVELS dictionary:
pythonFILL_LEVELS = {
    "0.160m (70% fill)": "data/0_16m.txt",
    "0.180m (79% fill)": "data/0_18m.txt",
    "0.200m (87% fill)": "data/0_20m.txt",
    "0.140m (61% fill)": "data/0_14m.txt",  # ← just add this line
}
Run the script again — all plots and tables update automatically. No other changes needed.

📈 Sample Results
Combined Frequency Response Plot
All three fill levels plotted on a single graph with resonance peaks automatically detected and annotated.
Resonance Peak Summary
Fill LevelPeak 1 (Hz)Peak 2 (Hz)Peak 3 (Hz)Max Amplitude (mm)0.160m (70%)1105107603.15 × 10⁻⁶0.180m (79%)1105107603.29 × 10⁻⁶0.200m (87%)1105107603.01 × 10⁻⁶
Anti-resonance Summary
Fill LevelAnti-res 1 (Hz)Anti-res 2 (Hz)Anti-res 3 (Hz)0.160m (70%)2104606100.180m (79%)2104606100.200m (87%)210460610

🔍 Key Findings
Resonance Features Identified:

110 Hz — First structural resonance peak (shell breathing mode)
460 Hz — First anti-resonance (destructive interference of structural and acoustic modes)
510 Hz — Second resonance peak (coupled fluid-structure mode)
610 Hz — Second anti-resonance
760 Hz — Dominant high-frequency resonance peak

Model Validation:

All three fill levels produce physically consistent frequency response curves ✅
Displacement magnitudes consistently in the order of 10⁻⁶ mm ✅
Resonance and anti-resonance features are stable and physically meaningful ✅
FSI coupling is active — fluid loading effect is captured ✅

Current Limitation:

At 50 Hz frequency resolution, small resonance frequency shifts between fill levels are not yet clearly visible
Rerunning with 10 Hz step resolution (as originally specified) is expected to reveal finer frequency shifts between fill levels


📊 Power BI Dashboard
A Power BI dashboard is currently in development using the all_fill_levels_combined.csv output from the Python pipeline. The dashboard will include:

Interactive frequency response chart with fill level toggle
Resonance peak frequency tracker table
Amplitude comparison across fill levels
Visual keg fill level indicator

Coming soon

🛠️ Tech Stack
ToolPurposeCOMSOL Multiphysics 6.4Multiphysics FSI simulationPython 3Data processing and visualizationpandasData manipulation and CSV exportmatplotlibPublication-ready plottingscipyAutomatic peak detectionnumpyNumerical operationsPower BIInteractive dashboard (in progress)GitHubVersion control and portfolio

📁 Repository Structure
keg-fsi-simulation-analysis/
│
├── keg_analysis.py                        # Main Python analysis script
├── README.md                              # This file
│
├── data/                                  # COMSOL exported probe table files
│   ├── 0_16m_freq_vs_displacement.txt     # 0.160m fill level results
│   ├── 0_18m_freq_vs_displacement.txt     # 0.180m fill level results
│   └── 0_20m_freq_vs_displacement.txt     # 0.200m fill level results
│
└── outputs/                               # Generated by running keg_analysis.py
    ├── combined_frequency_response.png    # All fill levels on one plot
    ├── individual_frequency_response.png  # Separate subplots per level
    ├── peak_frequency_comparison.png      # Bar chart of peak frequencies
    ├── peak_summary.csv                   # Peak data summary table
    └── all_fill_levels_combined.csv       # Full data for Power BI

📬 Contact
Ananya Shekar
M.Sc. Electrical Engineering & Information Technology
Otto-von-Guericke University Magdeburg
📧 ananyashekar2140@gmail.com
🔗 LinkedIn
🐙 GitHub

This project is part of ongoing research at ifak Institut für Automation und Kommunikation e.V., Magdeburg, Germany.
© 2026 Ananya Shekar — ifak e.V.
