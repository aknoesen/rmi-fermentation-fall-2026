"""
M1: bias and dark frames, laser off.

Gives the electronic offset, read noise, dark rate at the operating
temperature, dark non-uniformity, hot pixels, and (from the dark frames
themselves) an estimate of the conversion gain G in counts per electron.

Usage:
    python m1_dark.py <folder with M1 spectra> [--log <log export>] [--setpoint -13] [--out <folder>]

Writes to --out (default: <folder>/analysis):
    M1_summary.md, M1_by_time.csv, M1_dark_model.json, M1_level_vs_time.png, M1_variance_vs_level.png

Definitions follow NOISE_PRIMER.md. Temporal noise = SD over pixels of
(frame A - frame B)/sqrt(2) for a pair at one integration time: fixed
pattern cancels in the difference. Spatial scatter = SD over pixels of one
frame, which also contains the fixed pattern (DSNU).
"""

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import nf_common as nf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--log", default=None, help="Noise Test Log export folder (frames/, events/)")
    ap.add_argument("--setpoint", type=float, default=None, help="TEC setpoint, deg C")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    spectra = nf.read_dir(a.folder)
    frames, _ = nf.load_log(a.log)
    matches = nf.match_log(spectra, frames)
    # M1 frames: log entries with mid == M1, or every spectrum if there is no log
    if frames:
        spectra = [s for s in spectra if (matches[s.path.name][0] or {}).get("mid") == "M1"]
    if not spectra:
        raise SystemExit("No M1 spectra found.")
    out = Path(a.out or Path(a.folder) / "analysis")
    out.mkdir(parents=True, exist_ok=True)

    groups = defaultdict(list)
    for s in spectra:
        groups[round(s.t_s, 3)].append(s)
    ts = sorted(groups)

    rows, temps, issues = [], [], set()
    longest = None
    for t in ts:
        g = groups[t]
        Y = [s.y[s.valid()] for s in g]
        n = min(len(y) for y in Y)
        Y = np.array([y[:n] for y in Y])
        level = float(np.mean(Y))
        spatial = float(np.mean([np.std(y, ddof=1) for y in Y]))
        temporal = float(np.std(Y[0] - Y[1], ddof=1) / math.sqrt(2)) if len(Y) >= 2 else float("nan")
        temps += [s.temp_c for s in g]
        for s in g:
            issues.update(s.issues)
        rows.append(dict(t_s=t, frames=len(g), level=level, temporal_sd=temporal,
                         spatial_sd=spatial, dsnu=math.sqrt(max(spatial**2 - temporal**2, 0)) if math.isfinite(temporal) else float("nan")))
        longest = (t, Y[0])

    T = np.array([r["t_s"] for r in rows]); L = np.array([r["level"] for r in rows])
    if len(T) >= 2:
        rate, offset = np.polyfit(T, L, 1)
    else:
        rate, offset = float("nan"), float(L[0])
    bias = rows[0]
    read_noise = bias["temporal_sd"]

    # Conversion gain from darks: var = G * (level - offset) + read^2, in counts
    ok = [r for r in rows if math.isfinite(r["temporal_sd"]) and r["level"] - offset > 0]
    G = float("nan")
    if len(ok) >= 3:
        x = np.array([r["level"] - offset for r in ok]); v = np.array([r["temporal_sd"] ** 2 for r in ok])
        G, _ = np.polyfit(x, v, 1)

    # Hot pixels in the longest dark frame
    t_long, y_long = longest
    med = np.median(y_long); mad = np.median(np.abs(y_long - med)) * 1.4826
    hot = int(np.sum(y_long > med + 10 * mad)) if mad > 0 else 0

    temps = np.array([t for t in temps if math.isfinite(t)])
    temp_flag = ""
    if a.setpoint is not None and len(temps):
        dev = float(np.max(np.abs(temps - a.setpoint)))
        temp_flag = f"max deviation from setpoint {dev:.2f} deg C " + ("(PASS, within 0.5)" if dev <= 0.5 else "(FAIL, over 0.5)")

    # Outputs
    with open(out / "M1_by_time.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    model = dict(offset_counts=float(offset), dark_rate_counts_per_s=float(rate), read_noise_counts=float(read_noise),
                 gain_counts_per_e_from_darks=float(G), temp_mean_c=float(np.mean(temps)) if len(temps) else None,
                 note="Dark level per channel = offset + rate * t. Used by m2_ramp.py to remove dark and offset.")
    (out / "M1_dark_model.json").write_text(json.dumps(model, indent=2))

    plt.figure(figsize=(5, 3.4)); plt.plot(T, L, "o"); tt = np.linspace(0, T.max(), 50)
    if math.isfinite(rate): plt.plot(tt, offset + rate * tt, "-", lw=1)
    plt.xlabel("integration time (s)"); plt.ylabel("mean dark level (counts)"); plt.title("M1: dark level vs time")
    plt.tight_layout(); plt.savefig(out / "M1_level_vs_time.png", dpi=150); plt.close()
    if ok:
        plt.figure(figsize=(5, 3.4))
        plt.plot([r["level"] - offset for r in ok], [r["temporal_sd"] ** 2 for r in ok], "o")
        plt.xlabel("dark signal above offset (counts)"); plt.ylabel("temporal variance (counts²)")
        plt.title("M1: variance vs dark signal"); plt.tight_layout(); plt.savefig(out / "M1_variance_vs_level.png", dpi=150); plt.close()

    md = ["# M1 bias and dark frames: results\n",
          f"Spectra analysed: {len(spectra)} from `{Path(a.folder).name}`\n",
          "## Settings check\n",
          ("All frames have the required ENLIGHTEN settings.\n" if not issues else
           "**Settings not as required:** " + "; ".join(sorted(issues)) + "\n"),
          "## Per integration time\n",
          nf.write_md_table(rows, ["t_s", "frames", "level", "temporal_sd", "spatial_sd", "dsnu"],
                            {"t_s": "g", "level": ".1f", "temporal_sd": ".2f", "spatial_sd": ".2f", "dsnu": ".2f"}),
          "\nlevel = mean counts; temporal_sd = pixel noise from a frame pair; spatial_sd = scatter across pixels in one frame; dsnu = fixed pattern, sqrt(spatial² − temporal²).\n",
          "## Derived\n",
          f"- Electronic offset: **{offset:.1f} counts**\n",
          f"- Dark rate: **{rate:.4f} counts/s** per channel ({rate*1000:.1f} counts in 1000 s)\n",
          f"- Read noise (bias pair): **{read_noise:.2f} counts**\n",
          f"- Conversion gain from darks: **{G:.3f} counts per electron**" + (" (needs at least 3 pairs)" if not math.isfinite(G) else "") + "\n",
          f"- Hot pixels in the {t_long:g} s frame (above median + 10 MAD): **{hot}**\n",
          f"- Detector temperature: {temp_flag or 'setpoint not given'}\n"]
    (out / "M1_summary.md").write_text("\n".join(md))
    print("\n".join(md))


if __name__ == "__main__":
    main()
