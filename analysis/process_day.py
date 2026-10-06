"""
Run every analysis that applies to one day's data and collect a day report.

Expects the project layout:
    data/YYYY-MM-DD/            ENLIGHTEN files copied from Box
    log_export/YYYY-MM-DD/      Noise Test Log export (frames/, events/)
    results/dark_model.json     latest M1 dark model (written here after M1)

Usage:
    python process_day.py YYYY-MM-DD [--root <project folder>] [--setpoint -13]

Writes data/YYYY-MM-DD/analysis/ (per-measurement summaries and plots) and
DAY_REPORT.md there; copy that analysis folder to the Box day folder for Diego.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import nf_common as nf

HERE = Path(__file__).resolve().parent
STEPS = [("M1", "m1_dark.py", []), ("M1b", "m1b_warmup.py", ["dark"]), ("M2", "m2_ramp.py", ["dark"]),
         ("M3", "m3_saturation.py", ["dark"]), ("M4", "m45_noise_time.py", ["dark", "mid"]),
         ("M5", "m45_noise_time.py", ["dark", "mid"]), ("M6", "m6_rehearsal.py", ["dark"]), ("CO2", "co2_factor.py", [])]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("date"); ap.add_argument("--root", default=str(HERE.parent)); ap.add_argument("--setpoint", type=float, default=None)
    a = ap.parse_args()
    root = Path(a.root)
    data, log = root / "data" / a.date, root / "log_export" / a.date
    out = data / "analysis"; out.mkdir(parents=True, exist_ok=True)
    (root / "results").mkdir(exist_ok=True)
    dark_path = root / "results" / "dark_model.json"

    spectra = nf.read_dir(data)
    frames, _ = nf.load_log(log)
    present = {(m[0] or {}).get("mid") for m in nf.match_log(spectra, frames).values()}
    report = [f"# Day report, {a.date}", ""]
    chk = subprocess.run([sys.executable, str(HERE / "check_files.py"), str(data), "--log", str(log)], capture_output=True, text=True)
    report += ["## Intake check", "", chk.stdout.strip() or chk.stderr.strip(), ""]

    for mid, script, opts in STEPS:
        if mid not in present:
            continue
        cmd = [sys.executable, str(HERE / script), str(data), "--log", str(log), "--out", str(out)]
        if mid == "M1" and a.setpoint is not None:
            cmd += ["--setpoint", str(a.setpoint)]
        if "dark" in opts and dark_path.exists():
            cmd += ["--dark", str(dark_path)]
        if "mid" in opts:
            cmd += ["--mid", mid]
        r = subprocess.run(cmd, capture_output=True, text=True)
        report += [r.stdout.strip() if r.returncode == 0 else f"## {mid}\n\nFailed:\n\n```\n{r.stderr.strip()[-1500:]}\n```", ""]
        if mid == "M1" and (out / "M1_dark_model.json").exists():
            shutil.copy(out / "M1_dark_model.json", dark_path)
    if not present - {None}:
        report.append("No spectra matched to Noise Test Log entries.")
    (out / "DAY_REPORT.md").write_text("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
