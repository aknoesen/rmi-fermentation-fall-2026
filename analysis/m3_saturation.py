"""
M3: saturation ceiling at P_op, house N2 (and pure CO2 if available) at 60 psi.

For each gas, the brightest band's peak counts are fitted as
    peak(t) = dark_level(t) + k * t
on the frames below 40,000 counts. The linear limit is the highest measured
peak whose fitted value is within 2 % of that line (conservative: linearity is
not claimed beyond what was measured). t_f,max keeps the brightest band at or below 75 %
of the linear limit:
    dark_level(t) + k * t <= 0.75 * limit
The plan's t_f,max is the smaller of the two gases.

Usage:
    python m3_saturation.py <folder> --log <log export> [--dark <M1_dark_model.json>] [--out <folder>]
"""

import argparse
import csv
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import nf_common as nf

BANDS = {"n2": ("House N2", nf.N2_WIN), "co2": ("Pure CO2", (1350.0, 1425.0))}   # CO2: upper dyad component


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("--log", required=True)
    ap.add_argument("--dark", default=None); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    spectra = nf.read_dir(a.folder)
    frames, _ = nf.load_log(a.log)
    dark = nf.load_dark(a.dark)
    out = Path(a.out or Path(a.folder) / "analysis"); out.mkdir(parents=True, exist_ok=True)
    pairs = nf.by_entry(spectra, frames, "M3")
    if not pairs:
        raise SystemExit("No M3 spectra matched to the log.")

    md = ["# M3 saturation ceiling: results", ""]
    rows, results = [], {}
    plt.figure(figsize=(5.6, 3.8))
    for plan, (label, win) in BANDS.items():
        g = [(s, e) for s, e in pairs if e.get("plan") == plan]
        if len(g) < 3:
            md.append(f"## {label}\n\n{'Not measured.' if not g else f'Too few frames ({len(g)}).'}\n")
            continue
        t = np.array([s.t_s for s, _ in g])
        # fitted peak height (Gaussian top on its local baseline): less noisy than the raw maximum
        pk = np.array([nf.fit_band(s, win)["top"] for s, _ in g])
        P = np.array([nf.ophir_mean(e) for _, e in g])
        above = pk - np.array([nf.dark_level(dark, x) for x in t])
        low = pk < 40000
        if low.sum() < 2:
            md.append(f"## {label}\n\nFewer than two frames below 40,000 counts; take shorter frames.\n")
            continue
        k = float(np.sum(above[low] * t[low]) / np.sum(t[low] ** 2))        # line through origin
        pred = np.array([nf.dark_level(dark, x) for x in t]) + k * t
        within = np.abs(pk / pred - 1) <= 0.02
        departs = (~within) & (pk > 40000)
        # Conservative: the highest peak still on the line. Linearity is not
        # claimed beyond what was measured.
        limit = float(np.max(pk[within]))
        off = nf.dark_level(dark, 0); rate = (dark or {}).get("dark_rate_counts_per_s", 0.0)
        tfmax = (0.75 * limit - off) / (k + rate)
        results[plan] = tfmax
        for x, y, p in zip(t, pk, P):
            rows.append(dict(gas=label, t_s=x, peak=y, ophir_mW=p, flag=nf.saturation_flag(y)))
        md += [f"## {label}", "",
               f"- Signal rate at the band peak: **{k:.1f} counts/s** (at {np.nanmean(P):.0f} mW on the Ophir)",
               f"- Linear up to at least **{limit:.0f} counts** (highest peak within 2 % of the line)" + ("" if departs.any() else "; no departure seen, so take longer frames if the limit should be pushed higher"),
               f"- t_f,max for this gas: **{tfmax:.0f} s**", ""]
        tt = np.linspace(0, t.max() * 1.1, 50)
        plt.plot(t, pk, "o", label=label); plt.plot(tt, np.array([nf.dark_level(dark, x) for x in tt]) + k * tt, "-", lw=1)
    plt.axhline(0.75 * 65535, ls=":", lw=1); plt.axhline(65535, ls="--", lw=1)
    plt.xlabel("frame time (s)"); plt.ylabel("brightest peak (counts)"); plt.legend(fontsize=8)
    plt.title("M3: peak counts vs frame time"); plt.tight_layout(); plt.savefig(out / "M3_saturation.png", dpi=150); plt.close()
    if rows:
        with open(out / "M3_frames.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    if results:
        md.append(f"**t_f,max = {min(results.values()):.0f} s** (smaller of the gases measured). Enter it in the M3 tab.")
    if not dark:
        md.append("\n*No M1 dark model supplied: the fit assumes zero offset, which shortens t_f,max slightly (conservative).*")
    print(nf.save_md(out / "M3_summary.md", md))


if __name__ == "__main__":
    main()
