"""Per-second timeline: reversals, throttle range, stick activity and 8-60 Hz wobble per axis.
Use it to find maneuvers (tic-tocks = many reversals + big alternating pitch) and where wobble lives.

usage: python tools/timeline.py "file.BBL" [start end]
"""
import sys

import numpy as np
from scipy import signal

from bbl_load import load

d, h = load(sys.argv[1])
t = (d["time"] - d["time"][0]) / 1e6
fs = len(t) / t[-1]
t0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0
t1 = float(sys.argv[3]) if len(sys.argv) > 3 else t[-1]
M = np.mean([d[f"motor[{m}]"] for m in range(4)], axis=0)
fw = (M >= 1048).astype(int)
sw_t = t[np.flatnonzero(np.diff(fw)) + 1]
b, a = signal.butter(2, [8, 60], "bandpass", fs=fs)
wob = [signal.filtfilt(b, a, d[f"setpoint[{x}]"] - d[f"gyroADC[{x}]"]) for x in range(3)]
print(" sec  rev  thr min-max  |sp| r/p/y max     wobble r/p/y RMS   motor max  sat%")
for s in np.arange(np.floor(t0), t1, 1.0):
    m = (t >= s) & (t < s + 1)
    if m.sum() < 10:
        continue
    nrev = int(((sw_t >= s) & (sw_t < s + 1)).sum())
    sp = [np.abs(d[f"setpoint[{x}]"][m]).max() for x in range(3)]
    w = [np.sqrt(np.mean(x[m] ** 2)) for x in wob]
    mot = np.stack([d[f"motor[{k}]"][m] for k in range(4)])
    sat = np.mean((mot >= 2040) | ((mot >= 1040) & (mot <= 1047))) * 100
    flag = " <<" if max(w[:2]) > 15 else ""
    print(f"{s:4.0f}  {nrev:3d}  {d['rcCommand[3]'][m].min():5.0f}-{d['rcCommand[3]'][m].max():<5.0f} "
          f"{sp[0]:5.0f}/{sp[1]:5.0f}/{sp[2]:4.0f}   {w[0]:5.1f}/{w[1]:5.1f}/{w[2]:5.1f}   {mot.max():6.0f}  {sat:4.1f}{flag}")
