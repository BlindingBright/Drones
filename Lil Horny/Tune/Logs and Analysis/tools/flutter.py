"""Low-frequency flutter check (2-60 Hz): gyro error and accel spectra in steady flight.

A loose battery/mount shows as a narrow low-frequency peak that is strong in accel and in the
gyro tracking error, often rising with throttle (more vibration energy to excite it).
usage: python tools/flutter.py "a.BBL#n" "b.BBL#n" ...  (labels = file names)
"""
import sys

import numpy as np
from scipy import signal

from bbl_load import load

for path in sys.argv[1:]:
    d, h = load(path)
    t = (d["time"] - d["time"][0]) / 1e6
    fs = len(t) / t[-1]
    thr = d["rcCommand[3]"]
    M = np.mean([d[f"motor[{m}]"] for m in range(4)], axis=0)
    fly = np.abs(thr - 1500) > 60
    fwd = (M >= 1048).astype(int)
    for i in np.flatnonzero(np.diff(fwd)) + 1:
        fly[max(i - int(0.05 * fs), 0):i + int(0.4 * fs)] = False
    fly[-int(2 * fs):] = False  # drop crash tail
    print(f"\n{path}  ({fly.sum()/fs:.0f}s steady)")
    for nm, x in (("roll err", d["setpoint[0]"] - d["gyroADC[0]"]), ("pitch err", d["setpoint[1]"] - d["gyroADC[1]"]),
                  ("accY", d["accSmooth[1]"]), ("accX", d["accSmooth[0]"])):
        f, p = signal.welch(x[fly], fs, nperseg=4096)
        s = (f >= 4) & (f <= 60)
        pk = np.argsort(p[s])[::-1][:3]
        floor = np.median(p[s])
        print(f"  {nm:9s} 4-60Hz RMS={np.sqrt(np.trapezoid(p[s], f[s])):7.1f}  top peaks: " +
              ", ".join(f"{f[s][k]:.1f}Hz ({p[s][k]/floor:.0f}x)" for k in pk))
