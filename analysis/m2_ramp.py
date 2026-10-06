"""
M2: power ramp in ambient air at 60 psi.

Applies the five pass criteria from INTEGRATION_TIME_PLAN.md, M2:
  1. N2 band area per mW.s within 2 % of the lowest-power (about 70 mW) value
  2. Quiet-window background per mW.s within 5 % of the lowest-power value
  3. Reference-state Ophir reading within 2 % of its pre-ramp value
  4. Hold: no trend above 2 %/h in background or N2 area
  5. Hold: Ophir drift under 2 % (enclosure temperature is checked by hand)

Power is the Ophir reading at the fiber output (mean of start and end) from
the Noise Test Log. Background per mW.s uses the quiet-window level minus the
dark model from M1 (offset + rate * t); without it, offset and dark are
included and criterion 2 is reported as indicative only.

Usage:
    python m2_ramp.py <folder> --log <log export> [--dark <M1_dark_model.json>] [--out <folder>]
"""

import argparse
import csv
import json
import math
from datetime import datetime
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import nf_common as nf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--log", required=True)
    ap.add_argument("--dark", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()

    spectra = nf.read_dir(a.folder)
    frames, events = nf.load_log(a.log)
    matches = nf.match_log(spectra, frames)
    dark = json.loads(Path(a.dark).read_text()) if a.dark else None
    out = Path(a.out or Path(a.folder) / "analysis"); out.mkdir(parents=True, exist_ok=True)

    rows, issues = [], set()
    for s in spectra:
        entry, how = matches[s.path.name]
        if not entry or entry.get("mid") != "M2":
            continue
        issues.update(s.issues)
        P = nf.ophir_mean(entry); t = s.t_s
        n2 = nf.fit_band(s, nf.N2_WIN); o2 = nf.fit_band(s, nf.O2_WIN)
        bg = nf.window_level(s, nf.QUIET)
        if dark:
            bg -= dark["offset_counts"] + dark["dark_rate_counts_per_s"] * t
        rows.append(dict(file=s.name, plan=entry.get("plan", ""), hwp=entry.get("waveplate_angle_deg", ""),
                         P_mW=P, t_s=t, n2_area=n2["area"], o2_area=o2["area"], n2_peak=n2["peak"],
                         n2_per_mWs=n2["area"] / (P * t) if P and t else float("nan"),
                         bg_per_mWs=bg / (P * t) if P and t else float("nan"),
                         ophir_drift_pct=_drift(entry), sat=nf.saturation_flag(n2["peak"]),
                         time=s.timestamp.isoformat() if s.timestamp else "", matched_by=how))
    if not rows:
        raise SystemExit("No M2 spectra matched to the log.")
    rows.sort(key=lambda r: r["time"])

    # Steps: group ramp frames by half-wave plate angle (else by power within 3 %)
    steps = {}
    for r in rows:
        if r["plan"] != "step":
            continue
        k = str(r["hwp"]) or f"{r['P_mW']:.0f}"
        steps.setdefault(k, []).append(r)
    step_rows = []
    for k, g in steps.items():
        step_rows.append(dict(hwp=k, frames=len(g), P_mW=float(np.nanmean([r["P_mW"] for r in g])),
                              n2_per_mWs=float(np.nanmean([r["n2_per_mWs"] for r in g])),
                              bg_per_mWs=float(np.nanmean([r["bg_per_mWs"] for r in g])),
                              max_peak=float(np.nanmax([r["n2_peak"] for r in g]))))
    step_rows.sort(key=lambda r: r["P_mW"])
    ref = step_rows[0] if step_rows else None
    for r in step_rows:
        r["n2_dev_pct"] = 100 * (r["n2_per_mWs"] / ref["n2_per_mWs"] - 1)
        r["bg_dev_pct"] = 100 * (r["bg_per_mWs"] / ref["bg_per_mWs"] - 1)
        r["c1_n2"] = "pass" if abs(r["n2_dev_pct"]) <= 2 else "FAIL"
        r["c2_bg"] = "pass" if abs(r["bg_dev_pct"]) <= 5 else "FAIL"
        r["saturation"] = nf.saturation_flag(r["max_peak"])

    # Criterion 3: reference-state Ophir readings from the quick log
    oph = [(e.get("ts", ""), nf._num(e.get("value"))) for e in events if e.get("type") == "ophir"]
    oph = [(t, v) for t, v in sorted(oph) if math.isfinite(v)]
    c3 = ""
    if len(oph) >= 2:
        dev = 100 * (oph[-1][1] / oph[0][1] - 1)
        c3 = f"first {oph[0][1]:g} mW, last {oph[-1][1]:g} mW, change {dev:+.2f} % ({'pass' if abs(dev) <= 2 else 'FAIL'})"

    # Criteria 4 and 5: the hold
    hold = [r for r in rows if r["plan"] == "hold"]
    c4 = c5 = ""
    if len(hold) >= 3:
        t0 = datetime.fromisoformat(hold[0]["time"])
        h = np.array([(datetime.fromisoformat(r["time"]) - t0).total_seconds() / 3600 for r in hold])
        for key, label in (("n2_area", "N2 area"), ("bg_per_mWs", "background")):
            y = np.array([r[key] for r in hold])
            slope = np.polyfit(h, y, 1)[0] / np.nanmean(y) * 100
            c4 += f"{label} trend {slope:+.2f} %/h ({'pass' if abs(slope) <= 2 else 'FAIL'}); "
        Ps = np.array([r["P_mW"] for r in hold])
        d = 100 * (np.nanmax(Ps) - np.nanmin(Ps)) / np.nanmean(Ps)
        c5 = f"Ophir range over the hold {d:.2f} % ({'pass' if d <= 2 else 'FAIL'}); enclosure temperature: check by hand"

    with open(out / "M2_frames.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    if step_rows:
        plt.figure(figsize=(5.4, 3.6))
        P = [r["P_mW"] for r in step_rows]
        plt.plot(P, [r["n2_per_mWs"] / ref["n2_per_mWs"] for r in step_rows], "o-", label="N₂ area per mW·s")
        plt.plot(P, [r["bg_per_mWs"] / ref["bg_per_mWs"] for r in step_rows], "s-", label="background per mW·s")
        for y0, dy in ((1, 0.02), (1, 0.05)):
            plt.axhspan(y0 - dy, y0 + dy, alpha=0.08)
        plt.xlabel("Ophir at fiber output (mW)"); plt.ylabel("relative to lowest step"); plt.legend(fontsize=8)
        plt.title("M2: linearity with power"); plt.tight_layout(); plt.savefig(out / "M2_linearity.png", dpi=150); plt.close()

    md = ["# M2 power ramp: results\n",
          ("All frames have the required ENLIGHTEN settings.\n" if not issues else
           "**Settings not as required:** " + "; ".join(sorted(issues)) + "\n"),
          "" if dark else "\n*No M1 dark model supplied: background includes offset and dark, so criterion 2 is indicative only.*\n",
          "\n## Steps (criteria 1 and 2)\n",
          nf.write_md_table(step_rows, ["hwp", "frames", "P_mW", "n2_dev_pct", "c1_n2", "bg_dev_pct", "c2_bg", "max_peak", "saturation"],
                            {"P_mW": ".1f", "n2_dev_pct": "+.2f", "bg_dev_pct": "+.2f", "max_peak": ".0f"}) if step_rows else "No ramp frames.\n",
          f"\n## Reference-state Ophir (criterion 3)\n\n{c3 or 'Fewer than two Ophir readings in the log.'}\n",
          f"\n## Hold (criteria 4 and 5)\n\n{(c4 + chr(10) + chr(10) + c5) if hold else 'No hold frames.'}\n",
          "\nP_op is one step below the highest step passing all five criteria (plan, M2).\n"]
    (out / "M2_summary.md").write_text("\n".join(md))
    print("\n".join(md))


def _drift(entry):
    a, b = nf._num(entry.get("ophir_start_mW")), nf._num(entry.get("ophir_end_mW"))
    return 100 * (b - a) / a if a and math.isfinite(a) and math.isfinite(b) else float("nan")


if __name__ == "__main__":
    main()
