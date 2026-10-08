"""Where does the 9-18 Hz roll/pitch flutter live? Median band amplitude by motor output % and direction.

Mechanical looseness tends to grow with throttle; a gain problem from thrust_linear grows at LOW output.
usage: python tools/flutter_vs_throttle.py "a.BBL#n" ...
"""
import sys

import numpy as np
from scipy import signal

from bbl_load import load

BANDS = ((0, 20), (20, 35), (35, 50), (50, 70), (70, 101))
for path in sys.argv[1:]:
    d, h = load(path)
    t = (d["time"] - d["time"][0]) / 1e6
    fs = len(t) / t[-1]
    M = np.mean([d[f"motor[{m}]"] for m in range(4)], axis=0)
    fw = M >= 1048
    pct = np.where(fw, (M - 1048) / 999, (M - 48) / 999) * 100
    b, a = signal.butter(2, [9, 18], "bandpass", fs=fs)
    lb, la = signal.butter(2, 2, fs=fs)
    print(path)
    print("        " + " ".join(f"{d_}{lo:>3}-{hi:<3}%" for lo, hi in BANDS for d_ in "FR"))
    for ax, nm in ((0, "roll "), (1, "pitch")):
        e = signal.filtfilt(b, a, d[f"setpoint[{ax}]"] - d[f"gyroADC[{ax}]"])
        env = np.sqrt(np.clip(signal.filtfilt(lb, la, e ** 2), 0, None))
        cells = []
        for lo, hi in BANDS:
            for dirn in (True, False):
                s = (pct >= lo) & (pct < hi) & (fw == dirn)
                s[-int(2 * fs):] = False
                cells.append(f"{np.median(env[s]):9.1f}" if s.sum() > 500 else f"{'-':>9}")
        print(f"  {nm} " + " ".join(cells))
