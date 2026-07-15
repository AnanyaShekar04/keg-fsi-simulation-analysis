# Data source

- **`fill_level_0.14m.csv`, `0.16m.csv`, `0.18m.csv`, `0.20m.csv`:** 100% raw
  COMSOL Probe Table exports (Boundary Probe 1, average displacement, sensor
  at top), model `50l_30l_keg_simulation_FORMUNION_test.mph`, COMSOL
  6.4.0.378, May 2026. Full 10-1000 Hz sweep at 1 Hz resolution (991 points
  each). No modeled or interpolated values anywhere in these files.
- **`empty_keg_baseline.csv`:** raw COMSOL export, 10 Hz resolution,
  10-180 Hz, as originally exported for this baseline run.
- **`quarter_half_600_1000hz.csv`:** raw COMSOL export for quarter fill
  (0.066 m) and half fill (0.133 m), but only covering 600-1000 Hz at
  10 Hz resolution -- this run targeted the high-frequency shell modes
  specifically, since the primary resonance behavior (10-60 Hz) was
  already characterized in the four fill levels above. Units are
  **micrometers (um)**, not meters -- different from the other CSVs in
  this folder. No low-frequency data exists for these two fill levels.

All `data_source` columns read `comsol_raw` -- there is no modeled or
synthetic data in this repository.
