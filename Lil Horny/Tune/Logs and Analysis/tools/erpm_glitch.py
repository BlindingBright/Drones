"""Count physically impossible eRPM jumps (telemetry errors or desync-like events), and where they happen.

A 0802 can't change by >120k eRPM in one 0.5 ms log frame. Each glitch is reported with time since the
last direction switch, so reversal-related events (ESC restart trouble) stand out.
usage: python tools/erpm_glitch.py "a.BBL" ...
"""
import sys

import numpy as np

from bbl_load import load

JUMP = 120_000
for path in sys.argv[1:]:
    d, h = load(path)
    t = (d["time"] - d["time"][0]) / 1e6
    E = np.stack([d[f"eRPM[{m}]"] for m in range(4)]) * 100
    M = np.mean([d[f"motor[{m}]"] for m in range(4)], axis=0)
    sw_t = t[np.flatnonzero(np.diff((M >= 1048).astype(int))) + 1]
    ev = []
    for m in range(4):
        idx = np.flatnonzero(np.abs(np.diff(E[m])) > JUMP) + 1
        # merge samples within 50 ms into one event
        last = -1
        for i in idx:
            if last < 0 or t[i] - t[last] > 0.05:
                prev = sw_t[sw_t <= t[i]]
                ev.append((t[i], m, (t[i] - prev[-1]) * 1000 if len(prev) else np.nan))
            last = i
    near = [e for e in ev if e[2] < 300]
    name = path.split("\\")[-1][:40]
    print(f"{name:40s} {t[-1]:5.0f}s  glitch events {len(ev):3d} ({len(ev)/t[-1]*60:4.1f}/min)  "
          f"within 300 ms of a switch: {len(near):3d}  per motor {np.bincount([e[1] for e in ev], minlength=4)}")
    for e in near[:6]:
        print(f"      t={e[0]:7.2f}s motor {e[1]}  {e[2]:4.0f} ms after switch")
