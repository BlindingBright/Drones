"""Upright vs inverted (forward vs reverse motors) at matched motor output: gyro noise, D-term,
motor-command jitter. Reverse thrust through a duct is turbulent; this shows how much worse it is.
usage: python tools/direction_noise.py "a.BBL" [lo hi]   (motor-output % band, default 35 60)
"""
import sys

import numpy as np
from scipy import signal

from bbl_load import load

path = sys.argv[1]
lo, hi = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) > 3 else (35, 60)
d, h = load(path)
t = (d["time"] - d["time"][0]) / 1e6
fs = len(t) / t[-1]
Mall = np.stack([d[f"motor[{m}]"] for m in range(4)])
M = Mall.mean(axis=0)
fw = M >= 1048
pct = np.where(fw, (M - 1048) / 999, (M - 48) / 999) * 100
ok = np.ones(len(t), bool)
for i in np.flatnonzero(np.diff(fw.astype(int))) + 1:
    ok[max(i - int(0.05 * fs), 0):i + int(0.4 * fs)] = False
hp = signal.butter(2, 20, "highpass", fs=fs)
mj = np.mean([np.abs(signal.filtfilt(*hp, Mall[m])) for m in range(4)], axis=0)  # motor command jitter
print(f"{path}  motor output {lo:.0f}-{hi:.0f}%")
for dirn, dn in ((True, "UPRIGHT (fwd)"), (False, "INVERTED (rev)")):
    s = ok & (pct >= lo) & (pct < hi) & (fw == dirn)
    if s.sum() < 1000:
        print(f"  {dn}: not enough data"); continue
    out = [f"  {dn:15s} {s.sum()/fs:5.1f}s  motor jitter {np.mean(mj[s]):5.1f}"]
    for a, nm in ((0, "roll"), (1, "pitch")):
        for key, lab in ((f"gyroUnfilt[{a}]", "gyroRaw"), (f"axisD[{a}]", "D")):
            x = signal.filtfilt(*hp, d[key])
            bands = []
            for blo, bhi in ((20, 80), (80, 200), (200, 500)):
                b, a_ = signal.butter(2, [blo, bhi], "bandpass", fs=fs)
                bands.append(np.sqrt(np.mean(signal.filtfilt(b, a_, d[key])[s] ** 2)))
            out.append(f"{nm} {lab} 20-80/80-200/200-500Hz {bands[0]:5.1f}/{bands[1]:5.1f}/{bands[2]:5.1f}")
    print("\n    ".join(out))
