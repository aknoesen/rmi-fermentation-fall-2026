"""
M6: dress rehearsal of one campaign day, ambient air standing in for headspace.

Reports, per acquisition (argon start, air runs, argon end):
  - start and end time, number of frames, total integration time
  - fill pressure drift over the acquisition from the log (plan: under 1 %)
  - for air: N2/O2 area ratio from the mean of the acquisition's frames
Then the repeatability of N2/O2 across the air runs (relative SD, against
the 10.3 % repeat-to-repeat scatter of Day 1 in 2024), the gaps between run
starts, and the change in the argon background between start and end of day.

Usage:
    python m6_rehearsal.py <folder> --log <log export> [--dark <M1_dark_model.json>] [--out <folder>]
"""

import argparse
import copy
from pathlib import Path

import numpy as np

import nf_common as nf

ORDER = ["ar_am", "air1", "air2", "air3", "ar_pm"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("--log", required=True)
    ap.add_argument("--dark", default=None); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    spectra = nf.read_dir(a.folder)
    frames, _ = nf.load_log(a.log)
    dark = nf.load_dark(a.dark)
    out = Path(a.out or Path(a.folder) / "analysis"); out.mkdir(parents=True, exist_ok=True)
    pairs = nf.by_entry(spectra, frames, "M6")
    if not pairs:
        raise SystemExit("No M6 spectra matched to the log.")

    rows, ratios, starts, ar_bg = [], [], [], {}
    for plan in ORDER:
        g = [(s, e) for s, e in pairs if e.get("plan") == plan]
        if not g:
            continue
        ss = [s for s, _ in g]
        wn, Y = nf.stack(ss)
        mean = copy.copy(ss[0]); mean.wn, mean.y = wn, Y.mean(axis=0); mean.dark = None
        p1 = [nf._num(e.get("pressure_start_psig")) for _, e in g]
        p2 = [nf._num(e.get("pressure_end_psig")) for _, e in g]
        p1 = [x for x in p1 if np.isfinite(x)]; p2 = [x for x in p2 if np.isfinite(x)]
        drift = 100 * (p2[-1] - p1[0]) / p1[0] if p1 and p2 else float("nan")
        row = dict(acq=plan, start=ss[0].timestamp.strftime("%H:%M") if ss[0].timestamp else "",
                   end=ss[-1].timestamp.strftime("%H:%M") if ss[-1].timestamp else "",
                   frames=len(ss), T_min=sum(s.t_s for s in ss) / 60, p_drift_pct=drift,
                   p_check="" if not np.isfinite(drift) else ("pass" if abs(drift) <= 1 else "FAIL"))
        if plan.startswith("air"):
            n2, o2 = nf.fit_band(mean, nf.N2_WIN), nf.fit_band(mean, nf.O2_WIN)
            row["n2_o2"] = n2["area"] / o2["area"] if o2["area"] else float("nan")
            ratios.append(row["n2_o2"])
            if ss[0].timestamp:
                starts.append(ss[0].timestamp)
        else:
            P = np.nanmean([nf.ophir_mean(e) for _, e in g])
            ar_bg[plan] = (nf.window_level(mean, nf.QUIET) - nf.dark_level(dark, ss[0].t_s)) / (P * ss[0].t_s)
        rows.append(row)

    md = ["# M6 rehearsal: results", "",
          nf.write_md_table(rows, ["acq", "start", "end", "frames", "T_min", "p_drift_pct", "p_check", "n2_o2"],
                            {"T_min": ".1f", "p_drift_pct": "+.2f", "n2_o2": ".3f"}), ""]
    if len(ratios) >= 2:
        r = np.array(ratios); rsd = 100 * r.std(ddof=1) / r.mean()
        md.append(f"- N2/O2 repeatability across {len(r)} air runs: **{rsd:.2f} % RSD** (2024 Day 1 scatter: 10.3 %)")
    if len(starts) >= 2:
        gaps = [(b - a_).total_seconds() / 60 for a_, b in zip(starts, starts[1:])]
        md.append(f"- Gaps between air-run starts: {', '.join(f'{g:.0f}' for g in gaps)} min (planned 120)")
    if len(ar_bg) == 2:
        ch = 100 * (ar_bg["ar_pm"] / ar_bg["ar_am"] - 1)
        md.append(f"- Argon background per mW·s, end of day vs start: **{ch:+.2f} %**")
    md.append("\nThe 30-minute window holds only if each acquisition's end time leaves room for the purge before the next run.")
    print(nf.save_md(out / "M6_summary.md", md))


if __name__ == "__main__":
    main()
