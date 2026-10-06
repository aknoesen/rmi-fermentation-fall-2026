"""
Optional: CO2 response factor relative to N2 from equal-pressure fills.

Pure CO2 then pure N2 (then N2 again) at the same 60 psi and laser power.
At equal pressure and temperature the number densities differ only through
non-ideality: n = p / (Z R T). At 515 kPa and 40 deg C, Z(CO2) = 0.979 from
the second virial coefficient (B = -105 cm3/mol at 313 K); Z(N2) = 1.000. So
    k_CO2 = [A_CO2 / (P t)] / [A_N2 / (P t)] * Z_CO2 / Z_N2
with A from direct integration over 1240-1440 cm-1 (dyad plus hot bands, as
in the TIM composition) and 2290-2375 cm-1, and P the Ophir reading.

Usage:
    python co2_factor.py <folder> --log <log export> [--out <folder>]
"""

import argparse
from pathlib import Path

import numpy as np

import nf_common as nf

Z_CO2, Z_N2 = 0.979, 1.000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("--log", required=True); ap.add_argument("--out", default=None)
    a = ap.parse_args()
    spectra = nf.read_dir(a.folder)
    frames, _ = nf.load_log(a.log)
    out = Path(a.out or Path(a.folder) / "analysis"); out.mkdir(parents=True, exist_ok=True)
    pairs = nf.by_entry(spectra, frames, "CO2")
    if not pairs:
        raise SystemExit("No CO2-factor spectra matched to the log.")
    res = {}
    for plan, win in (("co2", nf.CO2_WIN), ("n2a", nf.N2_WIN), ("n2b", nf.N2_WIN)):
        g = [(s, e) for s, e in pairs if e.get("plan") == plan]
        if g:
            res[plan] = float(np.mean([nf.integrate_band(s, win) / (nf.ophir_mean(e) * s.t_s) for s, e in g]))
    md = ["# CO2 response factor: results", ""]
    if "co2" in res and "n2a" in res:
        n2 = np.mean([res[k] for k in ("n2a", "n2b") if k in res])
        k = res["co2"] / n2 * Z_CO2 / Z_N2
        md += [f"- CO2 manifold per mW·s: {res['co2']:.4g}", f"- N2 per mW·s: {res['n2a']:.4g}" + (f", repeat {res['n2b']:.4g}" if "n2b" in res else "")]
        if "n2b" in res:
            md.append(f"- N2 repeat vs first fill: **{100 * (res['n2b'] / res['n2a'] - 1):+.2f} %** (coupling stability between fills)")
        md += [f"- **k_CO2 = {k:.3f}** relative to N2 (tabulated 1.45; 2024 estimate of the effective value about 1.27)", "",
               "Areas by direct integration; the effective factor includes the detection-chain response, as k_O2 does."]
    else:
        md.append("Need at least one CO2 fill and one N2 fill.")
    print(nf.save_md(out / "CO2_summary.md", md))


if __name__ == "__main__":
    main()
