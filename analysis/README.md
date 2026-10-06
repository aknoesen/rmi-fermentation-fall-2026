# Noise-test analysis scripts, Fall 2026

Analysis for the pre-campaign measurements in `INTEGRATION_TIME_PLAN.md` (Box: `2026 Measurements\Communications and docs`). Written by Claude in consultation with André Knoesen, 6 October 2026.

| Script | Does |
|---|---|
| `nf_common.py` | Reads ENLIGHTEN CSV files (single and batch), checks the acquisition settings, matches files to Noise Test Log entries, ALS baseline, window σ, Gaussian band fits |
| `check_files.py` | Intake check for a day folder: settings, saturation, detector temperature, log match. Run first on every new batch |
| `m1_dark.py` | M1: offset, read noise, dark rate, dark non-uniformity, hot pixels, conversion gain from darks; writes `M1_dark_model.json` |
| `m2_ramp.py` | M2: the five pass criteria for each power step and the hold; uses the M1 dark model |
| `tests/make_synth.py` | Synthetic spectra with known values, to test the scripts |

## Workflow for each batch

1. Diego uploads to Box (`2026 Measurements\YYYY-MM-DD\`) and signals André.
2. Claude copies the day's files from Box to `data\YYYY-MM-DD\` and exports the Noise Test Log to `log_export\YYYY-MM-DD\`.
3. `python check_files.py data\YYYY-MM-DD --log log_export\YYYY-MM-DD`
4. The measurement scripts, e.g. `python m1_dark.py data\2026-10-07 --log log_export\2026-10-07 --setpoint -13`
5. Results (`*_summary.md` and plots) go to `data\YYYY-MM-DD\analysis\` and are copied to the Box day folder's `analysis\` subfolder for Diego.

Requires Python with numpy, scipy and matplotlib. These are not installed on this computer; the scripts currently run in Claude's workspace.

## Validation, 6 October 2026

On synthetic data with known values:

| Quantity | True | Recovered |
|---|---|---|
| Offset | 800 counts | 799.8 |
| Dark rate | 2.0 counts/s | 1.999 |
| Read noise | 8 counts | 8.04 |
| Conversion gain | 1.0 count/e⁻ | 0.93 |
| N₂ area per mW·s across 70 to 240 mW | constant | within 0.5 % |
| Hold drift | −1.2 %/h | −1.43 %/h |

On the real 4 October N₂ batch file: settings check flags dark subtraction, ALS baseline and scan averaging 3, as expected; N₂ fit gives FWHM 16.7 cm⁻¹, matching the 2024 instrument resolution.
