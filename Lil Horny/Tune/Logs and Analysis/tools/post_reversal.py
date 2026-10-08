"""Wobble (8-60 Hz tracking error, roll & pitch) vs time since a 3D direction switch.

Bins after each switch: 0-130 ms (props crossing zero / spinning up), 130-250 ms (spin-up done,
Betaflight I-term still held at zero), 250-500 ms (I-term back, quad in its own wash), 500-1000 ms.
Also shows average throttle depth in each bin (TPA cuts D above tpa_breakpoint).
usage: python tools/post_reversal.py "a.BBL" "b.BBL#n@x-y" ...
"""
import sys

import numpy as np
from scipy import signal

from bbl_load import load

BINS = ((0, 130), (130, 250), (250, 500), (500, 1000))
print(f"{'log':34s} {'n':>3}  " + "  ".join(f"{lo:>4}-{hi:<4}ms r/p (thr%)" for lo, hi in BINS) + "   calm r/p")
for path in sys.argv[1:]:
    d, h = load(path)
    t = (d["time"] - d["time"][0]) / 1e6
    fs = len(t) / t[-1]
    M = np.mean([d[f"motor[{m}]"] for m in range(4)], axis=0)
    fw = M >= 1048
    thr = np.abs(d["rcCommand[3]"] - 1500) / 500 * 100
    b, a = signal.butter(2, [8, 60], "bandpass", fs=fs)
    w = [signal.filtfilt(b, a, d[f"setpoint[{x}]"] - d[f"gyroADC[{x}]"]) ** 2 for x in range(2)]
    sw = np.flatnonzero(np.diff(fw.astype(int))) + 1
    sw = sw[(sw > fs) & (sw < len(t) - 2 * fs)]
    acc = {bn: ([], [], []) for bn in BINS}
    near = np.zeros(len(t), bool)
    for i0 in sw:
        near[i0:i0 + int(1.0 * fs)] = True
        for lo, hi in BINS:
            s = slice(i0 + int(lo / 1000 * fs), i0 + int(hi / 1000 * fs))
            acc[(lo, hi)][0].extend(w[0][s]); acc[(lo, hi)][1].extend(w[1][s]); acc[(lo, hi)][2].extend(thr[s])
    calm = ~near & (thr > 15)
    cells = []
    for bn in BINS:
        r, p, th = acc[bn]
        cells.append(f"{np.sqrt(np.mean(r)):5.1f}/{np.sqrt(np.mean(p)):5.1f} ({np.mean(th):3.0f}%)    ")
    name = path.split("\\")[-1][:34]
    print(f"{name:34s} {len(sw):3d}  " + "  ".join(cells) + f" {np.sqrt(np.mean(w[0][calm])):4.1f}/{np.sqrt(np.mean(w[1][calm])):4.1f}")
