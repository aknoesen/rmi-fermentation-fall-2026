"""
Pre-launch and daily intake check: for every ENLIGHTEN file in a folder,
report the acquisition settings, saturation, detector temperature, and the
matching Noise Test Log entry.

Usage:
    python check_files.py <folder> [--log <log export>]
"""

import argparse
import nf_common as nf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder")
    ap.add_argument("--log", default=None)
    a = ap.parse_args()
    spectra = nf.read_dir(a.folder)
    frames, _ = nf.load_log(a.log)
    matches = nf.match_log(spectra, frames) if frames else {}
    rows = []
    for s in spectra:
        entry, how = matches.get(s.path.name, (None, "no log"))
        pk = float(max(s.y[s.valid()])) if s.valid().any() else float("nan")
        rows.append(dict(file=s.name, t_s=s.t_s, temp_c=s.temp_c, peak=pk, saturation=nf.saturation_flag(pk),
                         settings="ok" if not s.issues else "; ".join(s.issues),
                         log=(f"{entry.get('mid')} / {entry.get('plan')} by {how}" if entry else how)))
    print(nf.write_md_table(rows, list(rows[0].keys()), {"t_s": "g", "temp_c": ".2f", "peak": ".0f"}) if rows else "No ENLIGHTEN files.")


if __name__ == "__main__":
    main()
