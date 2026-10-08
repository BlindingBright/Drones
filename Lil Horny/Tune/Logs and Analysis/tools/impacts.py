"""List impacts (accel spikes) and tumbles (gyro > 1500 deg/s) so they can be trimmed out.

usage: python tools/impacts.py "file.BBL#n" [g_threshold=6]
"""
import sys

import numpy as np

from bbl_load import load

d, h = load(sys.argv[1])
thr_g = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
t = (d["time"] - d["time"][0]) / 1e6
acc = np.linalg.norm(np.stack([d[f"accSmooth[{i}]"] for i in range(3)]), axis=0) / float(h.get("acc_1G", 2048))
gy = np.abs(np.stack([d[f"gyroADC[{i}]"] for i in range(3)])).max(axis=0)
ev = np.flatnonzero((acc > thr_g) | (gy > 1500))
if not len(ev):
    print(f"{sys.argv[1]}: no impacts (> {thr_g} g) or tumbles (>1500 deg/s) in {t[-1]:.1f}s")
groups = np.split(ev, np.flatnonzero(np.diff(ev) > int(0.5 * len(t) / t[-1])) + 1) if len(ev) else []
for g in groups:
    print(f"  event {t[g[0]]:.2f}-{t[g[-1]]:.2f}s  peak {acc[g].max():.1f} g, gyro {gy[g].max():.0f} deg/s")
