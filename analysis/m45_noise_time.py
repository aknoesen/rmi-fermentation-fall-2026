"""
M4 (argon) and M5 (ambient air): noise versus total integration time.

From the twelve consecutive frames at t_f,max ("seq"):
  - sigma of the mean of the first m frames, m = 1 .. 12, in the quiet window
    (3718-3918 cm-1) and the C-H window (2800-3000 cm-1), ALS-corrected as in TIM
  - the log-log slope of that curve and its reading (plan, Section 5)
  - temporal noise per pixel (scatter across the twelve) against spatial sigma
  - cosmic-ray hits per frame (pixels above the 12-frame median by > 8 robust SD)
From the frame pairs (M4 only, "p10", "p3", "p1"):
  - photon transfer: temporal variance against signal above dark gives the
    conversion gain G (counts per electron)
For M5, also the N2/O2 area ratio and the oxygen factor
    k_O2 = 3.7279 / (A_N2 / A_O2)      (dry air; deployed configuration)

Usage:
    python m45_noise_time.py <folder> --log <log export> --mid M4|M5 [--dark <M1_dark_model.json>] [--out <folder>]
"""

import argparse
import csv
import math
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import nf_common as nf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("--log", required=True)
    ap.add_argument("--mid", required=True, choices=["M4", "M5"])
    ap.add_argument("--dark", default=None); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    spectra = nf.read_dir(a.folder)
    frames, _ = nf.load_log(a.log)
    dark = nf.load_dark(a.dark)
    out = Path(a.out or Path(a.folder) / "analysis"); out.mkdir(parents=True, exist_ok=True)
    pairs = nf.by_entry(spectra, frames, a.mid)
    if not pairs:
        raise SystemExit(f"No {a.mid} spectra matched to the log.")
    gas = "argon" if a.mid == "M4" else "ambient air"
    md = [f"# {a.mid} noise versus time, {gas}: results", ""]
    issues = set().union(*[set(s.issues) for s, _ in pairs])
    md.append("All frames have the required ENLIGHTEN settings." if not issues else
              "**Settings not as required:** " + "; ".join(sorted(issues)))
    md.append("")

    seq = [s for s, e in pairs if e.get("plan") == "seq"]
    curve = []
    if len(seq) >= 3:
        wn, Y = nf.stack(seq)
        tf = seq[0].t_s
        for m in range(1, len(seq) + 1):
            r = nf.residual_of(wn, Y[:m].mean(axis=0))
            curve.append(dict(m=m, T_s=m * tf,
                              sigma_quiet=float(np.std(nf.window(wn, r, nf.QUIET), ddof=1)),
                              sigma_ch=float(np.std(nf.window(wn, r, nf.CH), ddof=1))))
        bq = nf.loglog_slope([c["T_s"] for c in curve], [c["sigma_quiet"] for c in curve])
        bc = nf.loglog_slope([c["T_s"] for c in curve], [c["sigma_ch"] for c in curve])
        # temporal vs spatial, single frame
        tq = float(np.median(np.std(Y[:, (wn >= nf.QUIET[0]) & (wn <= nf.QUIET[1])], axis=0, ddof=1)))
        tc = float(np.median(np.std(Y[:, (wn >= nf.CH[0]) & (wn <= nf.CH[1])], axis=0, ddof=1)))
        # cosmic rays
        med = np.median(Y, axis=0); dev = Y - med
        rsd = 1.4826 * np.median(np.abs(dev), axis=0) + 1e-9
        hits = [int(np.sum(d > 8 * rsd)) for d in dev]
        ch_mask = (wn >= nf.CH[0]) & (wn <= nf.CH[1])
        hits_ch = [int(np.sum((d > 8 * rsd) & ch_mask)) for d in dev]
        md += ["## Integration-time curve (twelve consecutive frames)", "",
               nf.write_md_table(curve, ["m", "T_s", "sigma_quiet", "sigma_ch"], {"T_s": ".0f", "sigma_quiet": ".2f", "sigma_ch": ".2f"}),
               f"- Quiet window: slope **{bq:+.2f}**, {nf.slope_reading(bq)}",
               f"- C–H window: slope **{bc:+.2f}**, {nf.slope_reading(bc)}",
               f"- Single frame, quiet window: temporal (pixel, frame to frame) **{tq:.2f}** vs spatial (across window) **{curve[0]['sigma_quiet']:.2f}** counts",
               f"- Single frame, C–H window: temporal **{tc:.2f}** vs spatial **{curve[0]['sigma_ch']:.2f}** counts",
               "  " + ("Spatial is well above temporal: fixed structure is a large part of the floor (NOISE_PRIMER Section 7)." if curve[0]['sigma_quiet'] > 1.3 * tq else "Spatial close to temporal: the single-frame floor is mostly random noise (NOISE_PRIMER Section 7)."),
               f"- Cosmic-ray candidates per frame: {hits} (in the C–H window: {sum(hits_ch)} in total)", ""]
        plt.figure(figsize=(5.4, 3.8))
        T = [c["T_s"] for c in curve]
        for key, lab in (("sigma_quiet", "quiet 3718–3918"), ("sigma_ch", "C–H 2800–3000")):
            y = [c[key] for c in curve]; plt.loglog(T, y, "o-", ms=3, label=lab)
            plt.loglog(T, y[0] * (np.array(T) / T[0]) ** -0.5, ":", lw=1)
        plt.xlabel("total integration time (s)"); plt.ylabel("σ of mean (counts)")
        plt.title(f"{a.mid}: σ vs total time (dotted: −0.5)"); plt.legend(fontsize=8); plt.tight_layout()
        plt.savefig(out / f"{a.mid}_sigma_vs_time.png", dpi=150); plt.close()
        with open(out / f"{a.mid}_curve.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(curve[0])); w.writeheader(); w.writerows(curve)
    else:
        md.append(f"Fewer than three 'seq' frames ({len(seq)}); no integration-time curve.\n")

    # Photon transfer (pairs, M4)
    pt = []
    for plan in ("p10", "p3", "p1"):
        g = [s for s, e in pairs if e.get("plan") == plan]
        if len(g) >= 2:
            wn, Y = nf.stack(g[:2])
            q = (wn >= nf.QUIET[0]) & (wn <= nf.QUIET[1])
            sig = float(np.mean(Y[:, q])) - nf.dark_level(dark, g[0].t_s)
            var = float(np.var((Y[0, q] - Y[1, q]), ddof=1) / 2)
            pt.append(dict(plan=plan, t_s=g[0].t_s, signal=sig, variance=var))
    if pt:
        md += ["## Photon transfer (frame pairs, quiet window)", "",
               nf.write_md_table(pt, ["plan", "t_s", "signal", "variance"], {"t_s": "g", "signal": ".1f", "variance": ".1f"})]
        if len(pt) >= 2 and dark:
            G, c0 = np.polyfit([p["signal"] for p in pt], [p["variance"] for p in pt], 1)
            md.append(f"Conversion gain from photon transfer: **{G:.3f} counts per electron** (intercept {c0:.1f} counts², read noise squared plus dark shot noise)")
        elif not dark:
            md.append("*No M1 dark model: signal includes offset, so the gain is not computed.*")
        md.append("")

    # Oxygen factor (M5)
    if a.mid == "M5" and seq:
        ratios = []
        for s in seq:
            n2, o2 = nf.fit_band(s, nf.N2_WIN), nf.fit_band(s, nf.O2_WIN)
            if n2["ok"] and o2["ok"] and o2["area"] > 0:
                ratios.append(n2["area"] / o2["area"])
        if ratios:
            r = np.array(ratios); mean, sd = r.mean(), r.std(ddof=1) if len(r) > 1 else float("nan")
            k = nf.DRY_AIR_N2_O2 / mean
            k_sd = k * sd / mean if math.isfinite(sd) else float("nan")
            md += ["## Oxygen response factor (ambient air, deployed configuration)", "",
                   f"- A_N2/A_O2 = **{mean:.3f} ± {sd:.3f}** over {len(r)} frames (2024: 3.433 ± 0.060)",
                   f"- k_O2 = 3.7279 / ratio = **{k:.3f} ± {k_sd:.3f}** (2024, transferred: 1.086 ± 0.019)",
                   "  Assumes dry ambient air; water vapour dilutes N2 and O2 equally and does not bias the ratio.", ""]
    if not dark:
        md.append("*No M1 dark model supplied.*")
    print(nf.save_md(out / f"{a.mid}_summary.md", md))


if __name__ == "__main__":
    main()
