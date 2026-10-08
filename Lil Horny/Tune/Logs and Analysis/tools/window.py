"""Print a coarse table of throttle, motors, accel and gyro over a time window.

usage: python tools/window.py "file.BBL" start end [step=0.05]
"""
import sys

import numpy as np

from bbl_load import load

d, h = load(sys.argv[1])
t0, t1 = float(sys.argv[2]), float(sys.argv[3])
step = float(sys.argv[4]) if len(sys.argv) > 4 else 0.05
t = (d["time"] - d["time"][0]) / 1e6
acc = np.linalg.norm(np.stack([d[f"accSmooth[{i}]"] for i in range(3)]), axis=0) / float(h.get("acc_1G", 2048))
print("   time   thr | motor0..3              | eRPM k 0..3       | acc g | gyro r/p/y | setpoint r/p/y")
for tt in np.arange(t0, t1, step):
    i = np.searchsorted(t, tt)
    mot = " ".join(f"{int(d[f'motor[{m}]'][i]):4d}" for m in range(4))
    erpm = " ".join(f"{d[f'eRPM[{m}]'][i] / 10:4.0f}" for m in range(4))
    gy = " ".join(f"{int(d[f'gyroADC[{a}]'][i]):5d}" for a in range(3))
    sp = " ".join(f"{int(d[f'setpoint[{a}]'][i]):5d}" for a in range(3))
    print(f"{tt:7.2f} {int(d['rcCommand[3]'][i]):5d} | {mot} | {erpm} | {acc[i]:4.1f} | {gy} | {sp}")
