"""
M1b: laser warm-up from a cold start, ambient air at 60 psi.

Warm-up time is the time after switch-on after which BOTH hold for every
later frame (plan, M1b):
  - the Ophir reading is within 1 % of its final value
  - the quiet-window background per mW is within 2 % of its final value
"Final" is the mean of the last five frames of that start; the test uses a
five-frame running mean so that frame-to-frame noise does not mask the trend. Switch-on is the
"Laser on" event in the Noise Test Log; without one, the first frame.

Usage:
    python m1b_warmup.py <folder> --log <log export> [--dark <M1_dark_model.json>] [--out <folder>]
"""

import argparse
import csv
from datetime import datetime
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import nf_common as nf


def settle_time(t_min, y, tol_pct, smooth=5):
    """First time after which the running mean (over `smooth` frames, which
    keeps frame-to-frame noise from masking the trend) stays within tol_pct
    of the final value."""
    y = np.asarray(y, float)
    k = np.ones(smooth) / smooth
    ys = np.convolve(y, k, mode="same")
    ys[:smooth // 2] = y[:smooth // 2]; ys[-(smooth // 2):] = np.mean(y[-smooth:])
    final = np.nanmean(y[-5:])
    dev = np.abs(ys / final - 1) * 100
    for i in range(len(y)):
        if np.all(dev[i:] <= tol_pct):
            return float(t_min[i]), float(final)
    return float("nan"), float(final)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("--log", required=True)
    ap.add_argument("--dark", default=None); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    spectra = nf.read_dir(a.folder)
    frames, events = nf.load_log(a.log)
    dark = nf.load_dark(a.dark)
    out = Path(a.out or Path(a.folder) / "analysis"); out.mkdir(parents=True, exist_ok=True)
    pairs = nf.by_entry(spectra, frames, "M1b")
    if not pairs:
        raise SystemExit("No M1b spectra matched to the log.")
    on_times = sorted(nf._log_time(e) for e in events if e.get("type") == "laser_on" and nf._log_time(e))

    md = ["# M1b laser warm-up: results", ""]
    rows_all = []
    plt.figure(figsize=(6, 3.8))
    for plan, label in (("am", "Cold start, morning"), ("mid", "Restart after 2 h off")):
        g = [(s, e) for s, e in pairs if e.get("plan") == plan]
        if len(g) < 6:
            md.append(f"## {label}\n\nToo few frames ({len(g)}).\n")
            continue
        t_first = g[0][0].timestamp
        on = max([t for t in on_times if t <= t_first], default=t_first)
        rows = []
        for s, e in g:
            P = nf.ophir_mean(e)
            bg = nf.window_level(s, nf.QUIET) - nf.dark_level(dark, s.t_s)
            rows.append(dict(start=plan, file=s.name, minutes=(s.timestamp - on).total_seconds() / 60,
                             ophir_mW=P, bg_per_mW=bg / P if P else np.nan,
                             n2_area_per_mW=nf.fit_band(s, nf.N2_WIN)["area"] / P if P else np.nan))
        t = np.array([r["minutes"] for r in rows])
        tp, pf = settle_time(t, np.array([r["ophir_mW"] for r in rows]), 1.0)
        tb, bf = settle_time(t, np.array([r["bg_per_mW"] for r in rows]), 2.0)
        warm = np.nanmax([tp, tb]) if np.isfinite(tp) and np.isfinite(tb) else np.nan
        md += [f"## {label}", "",
               f"- Ophir settles to within 1 % of {pf:.1f} mW after **{tp:.1f} min**",
               f"- Background per mW settles to within 2 % after **{tb:.1f} min**",
               f"- **Warm-up time: {warm:.1f} min**" if np.isfinite(warm) else "- Did not settle within the record",
               f"- Frame-to-frame scatter of background per mW: {np.nanstd(np.diff([r['bg_per_mW'] for r in rows])) / np.sqrt(2) / bf * 100:.2f} % (if near 2 %, use longer frames)", ""]
        rows_all += rows
        plt.plot(t, [r["bg_per_mW"] / bf for r in rows], "o-", ms=3, label=f"{label}: background/mW")
        plt.plot(t, [r["ophir_mW"] / pf for r in rows], "s--", ms=3, label=f"{label}: Ophir")
    plt.axhspan(0.98, 1.02, alpha=0.08); plt.xlabel("minutes after switch-on"); plt.ylabel("relative to final")
    plt.legend(fontsize=7); plt.title("M1b: warm-up"); plt.tight_layout(); plt.savefig(out / "M1b_warmup.png", dpi=150); plt.close()
    if rows_all:
        with open(out / "M1b_frames.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows_all[0])); w.writeheader(); w.writerows(rows_all)
    if not dark:
        md.append("*No M1 dark model supplied: background includes offset and dark.*")
    md.append("Enter the warm-up times in the M1b tab of the Noise Test Log.")
    print(nf.save_md(out / "M1b_summary.md", md))


if __name__ == "__main__":
    main()
