"""
Synthetic test data for the noise-test analysis, in the project layout:
    <root>/data/2099-01-01 .. 2099-01-03/   ENLIGHTEN-format CSV files
    <root>/log_export/<same dates>/        Noise Test Log export (frames/, events/)

Known values the scripts should recover:
    offset 800 counts, dark rate 2.0 counts/s, read noise 8 counts, gain 1 count/e-,
    DSNU 3 counts; N2 peak 0.6 counts/(mW s) in air; A_N2/A_O2 = 3.43 (k_O2 = 1.087);
    background 0.05 counts/(mW s) with 0.5 % fixed pattern (PRNU);
    warm-up: Ophir within 1 % after about 11.5 min, background/mW within 2 % after about 7.3 min;
    linear response to 55,000 counts, compressing above (t_f,max for N2 at 160 mW about 300 s); k_CO2 = 1.30.

Usage:
    python make_synth.py <template ENLIGHTEN csv> <root>
"""

import json
import sys
from pathlib import Path

import numpy as np

rng = np.random.default_rng(7)
tpl, root = Path(sys.argv[1]), Path(sys.argv[2])
lines = tpl.read_text().splitlines()
h = next(i for i, l in enumerate(lines) if l.startswith("Wavenumber,Processed"))
wn = np.array([float(l.split(",")[0]) for l in lines[h + 1:] if l.strip()])
n = len(wn)
valid = np.zeros(n, bool); valid[20:747] = True
dsnu = rng.normal(0, 3, n)
prnu = 1 + rng.normal(0, 0.005, n)
g = lambda c, a, s=7.1: a * np.exp(-0.5 * ((wn - c) / s) ** 2)
A_N2 = 0.6                                   # counts/(mW s), air, peak
SHAPE = {"air": g(2331, A_N2) + g(1556, A_N2 / 3.43),
         "n2": g(2331, A_N2 / 0.7808), "ar": 0 * wn,
         "co2": (g(1285, 0.6) + g(1388, 1.0)) * (1.30 / 0.979) * (A_N2 / 0.7808) / 1.6}
BG = 0.05


def spectrum(gas, P, t, extra_bg=1.0):
    sig = (SHAPE[gas] + BG * extra_bg) * P * t * prnu
    e = rng.poisson(np.clip(sig + 2.0 * t, 0, None)).astype(float)
    y = 800 + dsnu + e + rng.normal(0, 8, n)
    y = np.where(y > 55000, 55000 + (y - 55000) * 0.5, y)
    return np.minimum(y, 65535)


def write(day, name, y, t, ts, temp=-13.0):
    d = root / "data" / day; d.mkdir(parents=True, exist_ok=True)
    meta = {"ENLIGHTEN Version": "4.0.14", "Scan Averaging": "1", "Boxcar": "1", "Baseline Correction Algo": "None",
            "Raman Intensity Corrected": "False", "Deconvolved": "False", "Integration Time": str(int(t * 1000)),
            "Timestamp": ts.strftime("%Y-%m-%d %H:%M:%S.%f"), "Temperature": f"{temp + rng.normal(0, 0.1):.3f}"}
    with open(d / name, "w") as f:
        for k, v in meta.items():
            f.write(f"{k},{v}\n")
        f.write("\nWavenumber,Processed,Dark\n")
        for w, v, ok in zip(wn, y, valid):
            f.write(f"{w:.2f},{f'{v:.2f}' if ok else 'NA'},\n")


def log(day, kind, doc_id, data):
    d = root / "log_export" / day / kind; d.mkdir(parents=True, exist_ok=True)
    (d / f"{doc_id}.json").write_text(json.dumps({"id": doc_id, "data": data}))


from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
LA = ZoneInfo("America/Los_Angeles")
k = 0


def frame(day, mid, plan, gas, P, t, ts, **extra):
    global k
    k += 1
    name = f"{mid}_{plan}_{k:04d}.csv"
    if gas == "dark":
        y = 800 + dsnu + rng.poisson(2.0 * t, n) + rng.normal(0, 8, n)
    else:
        y = spectrum(gas, P, t, extra.pop("extra_bg", 1.0))
    write(day, name, y, t, ts)
    log(day, "frames", f"f{k}", dict(mid=mid, plan=plan, file=name, ophir_start_mW=str(P), ophir_end_mW=str(P),
                                     ts=ts.astimezone(timezone.utc).isoformat(), **{a: str(b) for a, b in extra.items()}))


# Day 1: M1 darks
d1, t0 = "2099-01-01", datetime(2099, 1, 1, 21, 0, tzinfo=LA)
for t, c in [(0.01, 2), (10, 2), (30, 2), (100, 2), (300, 2), (1000, 2), (3000, 1)]:
    for _ in range(c):
        frame(d1, "M1", "d", "dark", 0, t, t0); t0 += timedelta(seconds=t + 5)

# Day 2: M1b, M2, M3, M4
d2 = "2099-01-02"
for plan, start in (("am", datetime(2099, 1, 2, 7, 0, tzinfo=LA)), ("mid", datetime(2099, 1, 2, 12, 0, tzinfo=LA))):
    log(d2, "events", f"on_{plan}", dict(type="laser_on", value="", ts=start.astimezone(timezone.utc).isoformat()))
    for i in range(45):
        m = i + 1
        P = 70 * (1 - 0.1 * np.exp(-m / 5)); xb = 1 + 0.05 * np.exp(-m / 8)
        frame(d2, "M1b", plan, "air", P, 60, start + timedelta(minutes=m), extra_bg=xb)
ts = datetime(2099, 1, 2, 9, 0, tzinfo=LA)
for P, hwp in ((70, 0), (105, 10), (160, 20), (240, 30)):
    t = 30000 / (A_N2 * P)
    for _ in range(3):
        frame(d2, "M2", "step", "air", P, t, ts, waveplate_angle_deg=hwp); ts += timedelta(minutes=3)
for i in range(12):
    frame(d2, "M2", "hold", "air", 240, 30000 / (A_N2 * 240), ts, waveplate_angle_deg=30); ts += timedelta(minutes=5)
log(d2, "events", "o1", dict(type="ophir", value="70.0", ts="2099-01-02T15:59:00+00:00"))
log(d2, "events", "o2", dict(type="ophir", value="69.9", ts="2099-01-02T18:00:00+00:00"))
for plan, gas in (("n2", "n2"), ("co2", "co2")):
    for t in (40, 80, 160, 240, 320, 400, 480):
        frame(d2, "M3", plan, gas, 160, t, ts); ts += timedelta(minutes=4)
for plan, t, c in (("p10", 12, 2), ("p3", 40, 2), ("p1", 120, 2), ("seq", 120, 12)):
    for _ in range(c):
        frame(d2, "M4", plan, "ar", 160, t, ts); ts += timedelta(minutes=3)

# Day 3: M5, M6, CO2
d3, ts = "2099-01-03", datetime(2099, 1, 3, 8, 0, tzinfo=LA)
for _ in range(12):
    frame(d3, "M5", "seq", "air", 160, 120, ts); ts += timedelta(minutes=2.5)
for plan, gas, c in (("ar_am", "ar", 10), ("air1", "air", 5), ("air2", "air", 5), ("air3", "air", 5), ("ar_pm", "ar", 10)):
    ts = ts + timedelta(minutes=95 if plan.startswith("air") and plan != "air1" else 10)
    for _ in range(c):
        frame(d3, "M6", plan, gas, 160, 120, ts, pressure_start_psig=60.0, pressure_end_psig=59.8); ts += timedelta(minutes=2.1)
for plan, gas in (("co2", "co2"), ("n2a", "n2"), ("n2b", "n2")):
    for _ in range(3):
        frame(d3, "CO2", plan, gas, 160, 60, ts); ts += timedelta(minutes=2)
print("synthetic data written to", root)
