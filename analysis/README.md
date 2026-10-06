# Analysis scripts

Analysis for the pre-campaign measurements in `docs/INTEGRATION_TIME_PLAN.md`. Written by Claude in consultation with André Knoesen, 6 October 2026.

| Script | Measurement | Does |
|---|---|---|
| `process_day.py` | all | Runs every analysis that applies to one day's data and writes `DAY_REPORT.md` |
| `check_files.py` | intake | ENLIGHTEN settings, saturation, detector temperature, Noise Test Log match, for every file |
| `m1_dark.py` | M1 | Offset, read noise, dark rate, fixed pattern (DSNU), hot pixels, gain from darks; writes the dark model |
| `m1b_warmup.py` | M1b | Warm-up time: Ophir within 1 % and background per mW within 2 % of final |
| `m2_ramp.py` | M2 | The five pass criteria for each power step and the hold |
| `m3_saturation.py` | M3 | Linear range and t_f,max for house N₂ and pure CO₂ |
| `m45_noise_time.py` | M4, M5 | σ of the mean of m frames vs total time in both windows, slope and its reading; temporal vs spatial noise; cosmic rays; photon-transfer gain (M4); k_O₂ from ambient air (M5) |
| `m6_rehearsal.py` | M6 | Per acquisition: timing, frames, pressure drift; N₂/O₂ repeatability; argon change over the day |
| `co2_factor.py` | optional | k_CO₂ from equal-pressure CO₂ and N₂ fills, with the non-ideality correction |
| `nf_common.py` | | Shared: ENLIGHTEN reader (single and batch files), settings check, log matching, ALS baseline, band fits |
| `tests/make_synth.py` | | Synthetic data with known values in the project layout |

## Daily workflow

1. Diego uploads to Box (`2026 Measurements\YYYY-MM-DD\`) and signals André.
2. Claude copies the day's files from Box to `data\YYYY-MM-DD\` and exports the Noise Test Log to `log_export\YYYY-MM-DD\`.
3. `python process_day.py YYYY-MM-DD --setpoint -13`
4. `data\YYYY-MM-DD\analysis\` (DAY_REPORT.md, summaries, plots) is copied to the Box day folder's `analysis\` subfolder for Diego. The latest dark model is kept in `results\dark_model.json`.

Requires Python 3.9+ with numpy, scipy and matplotlib. These are not installed on this computer; the scripts currently run in Claude's workspace.

## Validation on synthetic data, 6 October 2026

`python tests/make_synth.py <any ENLIGHTEN csv> <root>`, then `process_day.py` for each of the three synthetic days.

| Quantity | True | Recovered |
|---|---|---|
| Offset | 800 counts | 799.5 |
| Dark rate | 2.0 counts/s | 2.001 |
| Read noise | 8 counts | 7.64 |
| Gain, from darks / from photon transfer | 1.0 count/e⁻ | 0.96 / 1.09 |
| Warm-up, Ophir within 1 % | 11.5 min | 12 min |
| Warm-up, background within 2 % | 7.3 min | 5 to 7 min |
| M2 linearity, 70 to 240 mW | constant | within 0.6 % |
| M3 t_f,max, N₂ at 160 mW | 304 s | 300 s |
| M4 slope, argon (random-limited) | −0.5 | −0.49 quiet, −0.55 C–H |
| k_O₂ from air | 1.087 | 1.098 ± 0.016 |
| k_CO₂ | 1.30 | 1.31 |

On the real 4 October N₂ batch file the settings check flags dark subtraction, ALS baseline and scan averaging 3, and the N₂ fit gives FWHM 16.7 cm⁻¹, matching the 2024 resolution.
