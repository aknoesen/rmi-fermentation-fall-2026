"""
Shared tools for the 2026 pre-campaign noise-floor analysis (M0 to M6).

Reads ENLIGHTEN CSV files (single-spectrum and batch), checks acquisition
settings against the plan, loads the Noise Test Log export, and provides the
baseline and peak-fitting routines used by the measurement scripts.

Plan:   Box ... 2026 Measurements/Communications and docs/INTEGRATION_TIME_PLAN.md
Primer: NOISE_PRIMER.md (definitions of every noise term used here)
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
from scipy import sparse
from scipy.optimize import curve_fit
from scipy.sparse.linalg import spsolve

LOCAL_TZ = ZoneInfo("America/Los_Angeles")   # instrument computer clock

# Windows, cm-1. QUIET is the published TIM noise window; CH is the volatiles window.
QUIET = (3718.0, 3918.0)
CH = (2800.0, 3000.0)
N2_WIN = (2290.0, 2375.0)
O2_WIN = (1520.0, 1595.0)

ALS_LAM, ALS_P, ALS_NITER = 1e9, 0.001, 10     # as in the TIM analysis
FULL_SCALE = 65535.0
WARN_FRACTION = 0.75


# --------------------------------------------------------------------------
# ENLIGHTEN files
# --------------------------------------------------------------------------

@dataclass
class Spectrum:
    path: Path
    index: int                     # position within a batch file (0 for single)
    meta: dict
    wn: np.ndarray                 # wavenumber, cm-1
    y: np.ndarray                  # "Processed" column (raw counts when processing is off)
    dark: np.ndarray | None        # "Dark" column, None when empty
    issues: list = field(default_factory=list)

    @property
    def name(self) -> str:
        return self.path.name if self.index == 0 and self.meta.get("_n", 1) == 1 \
            else f"{self.path.name}#{self.index + 1}"

    @property
    def t_s(self) -> float:
        return float(self.meta.get("Integration Time", "nan")) / 1000.0

    @property
    def temp_c(self) -> float:
        try:
            return float(self.meta.get("Temperature", "nan"))
        except ValueError:
            return float("nan")

    @property
    def timestamp(self) -> datetime | None:
        ts = self.meta.get("Timestamp", "")
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
            try:
                return datetime.strptime(ts, fmt).replace(tzinfo=LOCAL_TZ)
            except ValueError:
                pass
        return None

    def valid(self) -> np.ndarray:
        return np.isfinite(self.y)


def _num(s: str) -> float:
    try:
        return float(s)
    except (TypeError, ValueError):
        return float("nan")


def read_enlighten(path: str | Path) -> list[Spectrum]:
    """Read a single or batch ENLIGHTEN CSV. Returns one Spectrum per scan."""
    path = Path(path)
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
        rows = list(csv.reader(fh))
    hdr_i = next(i for i, r in enumerate(rows) if r and r[0] in ("Wavenumber", "Pixel"))
    cols = rows[hdr_i]
    proc_idx = [j for j, c in enumerate(cols) if c == "Processed"]
    dark_idx = [j for j, c in enumerate(cols) if c == "Dark"]
    wn_col = cols.index("Wavenumber") if "Wavenumber" in cols else 0
    n = len(proc_idx)
    cps = (len(cols) - 1) // n if n else 1          # columns per spectrum
    data = [r for r in rows[hdr_i + 1:] if r and r[0].strip()]
    wn = np.array([_num(r[wn_col]) for r in data])
    metas = [dict(_n=n) for _ in range(n)]
    for r in rows[:hdr_i]:
        if not r or not r[0]:
            continue
        for k in range(n):
            j = 1 + k * cps
            metas[k][r[0]] = r[j] if j < len(r) else ""
    out = []
    for k in range(n):
        y = np.array([_num(r[proc_idx[k]]) if proc_idx[k] < len(r) else np.nan for r in data])
        d = None
        if k < len(dark_idx):
            dv = np.array([_num(r[dark_idx[k]]) if dark_idx[k] < len(r) else np.nan for r in data])
            if np.isfinite(dv).any():
                d = dv
        s = Spectrum(path, k, metas[k], wn, y, d)
        s.issues = check_settings(s)
        out.append(s)
    return out


def check_settings(s: Spectrum) -> list[str]:
    """Settings the plan requires (README_START_HERE, 'Settings to change in ENLIGHTEN first')."""
    m, bad = s.meta, []
    if m.get("Baseline Correction Algo", "None") not in ("None", ""):
        bad.append(f"baseline correction {m['Baseline Correction Algo']} (must be None)")
    if m.get("Scan Averaging", "1") != "1":
        bad.append(f"scan averaging {m['Scan Averaging']} (must be 1)")
    if m.get("Boxcar", "1") != "1":
        bad.append(f"boxcar {m['Boxcar']} (must be 1)")
    if m.get("Raman Intensity Corrected", "False") != "False":
        bad.append("Raman intensity correction on")
    if m.get("Deconvolved", "False") != "False":
        bad.append("deconvolution on")
    if s.dark is not None:
        bad.append("dark subtraction on (Dark column filled)")
    return bad


def read_dir(folder: str | Path) -> list[Spectrum]:
    """Every spectrum in every ENLIGHTEN CSV in a folder (not recursive)."""
    out = []
    for p in sorted(Path(folder).glob("*.csv")):
        try:
            out.extend(read_enlighten(p))
        except (StopIteration, ValueError, IndexError):
            continue        # not an ENLIGHTEN spectrum file (e.g. a run_log export)
    return out


# --------------------------------------------------------------------------
# Noise Test Log export
# --------------------------------------------------------------------------

def load_log(folder: str | Path | None) -> tuple[list[dict], list[dict]]:
    """Frames and events exported from the Noise Test Log (one JSON per document)."""
    if not folder:
        return [], []
    folder = Path(folder)

    def _load(sub):
        rows = []
        for p in sorted((folder / sub).glob("*.json")):
            d = json.loads(p.read_text())
            body = d.get("data", d)
            body = dict(body)
            body.setdefault("id", d.get("id", p.stem))
            rows.append(body)
        return rows
    return _load("frames"), _load("events")


def _log_time(entry: dict) -> datetime | None:
    try:
        return datetime.fromisoformat(str(entry.get("ts", "")).replace("Z", "+00:00"))
    except ValueError:
        return None


def match_log(spectra: list[Spectrum], frames: list[dict], max_minutes: float = 20.0) -> dict:
    """Map spectrum file -> log entry: by file name first, then by nearest time stamp."""
    by_name = {}
    for f in frames:
        nm = str(f.get("file", "")).strip()
        if nm:
            by_name[nm.lower()] = f
            by_name[Path(nm).stem.lower()] = f
    result = {}
    for s in spectra:
        key = s.path.name.lower()
        hit = by_name.get(key) or by_name.get(s.path.stem.lower())
        how = "name"
        if hit is None and s.timestamp is not None:
            best, dt_best = None, None
            for f in frames:
                t = _log_time(f)
                if t is None:
                    continue
                dt = abs((t - s.timestamp).total_seconds()) / 60.0
                if dt <= max_minutes and (dt_best is None or dt < dt_best):
                    best, dt_best = f, dt
            hit, how = best, (f"time ({dt_best:.1f} min)" if best else "none")
        result[s.path.name] = (hit, how if hit else "none")
    return result


def ophir_mean(entry: dict | None) -> float:
    if not entry:
        return float("nan")
    a, b = _num(entry.get("ophir_start_mW")), _num(entry.get("ophir_end_mW"))
    vals = [v for v in (a, b) if math.isfinite(v)]
    return float(np.mean(vals)) if vals else float("nan")


# --------------------------------------------------------------------------
# Baseline, windows, peaks
# --------------------------------------------------------------------------

def als(y: np.ndarray, lam: float = ALS_LAM, p: float = ALS_P, niter: int = ALS_NITER) -> np.ndarray:
    """Asymmetric least squares baseline (Eilers and Boelens), as in the TIM analysis."""
    n = len(y)
    D = sparse.diags([1.0, -2.0, 1.0], [0, -1, -2], shape=(n, n - 2))
    DD = lam * D.dot(D.transpose())
    w = np.ones(n)
    z = y
    for _ in range(niter):
        W = sparse.spdiags(w, 0, n, n)
        z = spsolve((W + DD).tocsc(), w * y)
        w = p * (y > z) + (1 - p) * (y < z)
    return z


def residual(s: Spectrum) -> tuple[np.ndarray, np.ndarray]:
    """ALS-corrected residual over the valid pixels: (wn, y - baseline)."""
    v = s.valid()
    wn, y = s.wn[v], s.y[v]
    return wn, y - als(y)


def window(wn: np.ndarray, y: np.ndarray, win: tuple[float, float]) -> np.ndarray:
    m = (wn >= win[0]) & (wn <= win[1])
    return y[m]


def window_sigma(s: Spectrum, win: tuple[float, float]) -> float:
    """Published TIM definition: SD of ALS-corrected residuals across one window, one spectrum."""
    wn, r = residual(s)
    w = window(wn, r, win)
    return float(np.std(w, ddof=1)) if len(w) > 2 else float("nan")


def window_level(s: Spectrum, win: tuple[float, float]) -> float:
    """Mean raw level (counts) in a window: background + dark + offset."""
    v = s.valid()
    w = window(s.wn[v], s.y[v], win)
    return float(np.mean(w)) if len(w) else float("nan")


def _gauss_lin(x, a, x0, sig, c0, c1):
    return a * np.exp(-0.5 * ((x - x0) / sig) ** 2) + c0 + c1 * (x - x0)


def fit_band(s: Spectrum, win: tuple[float, float]) -> dict:
    """One Gaussian on a linear local baseline. Returns amplitude, centre, FWHM, area, peak counts."""
    v = s.valid()
    m = v & (s.wn >= win[0]) & (s.wn <= win[1])
    x, y = s.wn[m], s.y[m]
    out = dict(amp=np.nan, center=np.nan, fwhm=np.nan, area=np.nan, peak=np.nan, ok=False)
    if len(x) < 6:
        return out
    out["peak"] = float(np.max(y))
    base0 = float(np.median(np.r_[y[:3], y[-3:]]))
    p0 = [max(y.max() - base0, 1.0), x[np.argmax(y)], 7.0, base0, 0.0]
    try:
        p, _ = curve_fit(_gauss_lin, x, y, p0=p0, maxfev=20000,
                         bounds=([0, win[0], 2.0, -np.inf, -np.inf], [np.inf, win[1], 40.0, np.inf, np.inf]))
        a, x0, sig = p[0], p[1], abs(p[2])
        out.update(amp=float(a), center=float(x0), fwhm=float(2.3548 * sig),
                   area=float(a * sig * math.sqrt(2 * math.pi)), ok=True)
    except (RuntimeError, ValueError):
        pass
    return out


def saturation_flag(peak: float) -> str:
    if not math.isfinite(peak):
        return ""
    if peak >= 65000:
        return "SATURATED"
    if peak > WARN_FRACTION * FULL_SCALE:
        return "above 75% of full scale"
    return ""


def write_md_table(rows: list[dict], cols: list[str], fmt: dict | None = None) -> str:
    fmt = fmt or {}
    head = "| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n"
    body = ""
    for r in rows:
        cells = []
        for c in cols:
            v = r.get(c, "")
            if isinstance(v, float):
                v = format(v, fmt.get(c, ".3g")) if math.isfinite(v) else ""
            cells.append(str(v))
        body += "| " + " | ".join(cells) + " |\n"
    return head + body
