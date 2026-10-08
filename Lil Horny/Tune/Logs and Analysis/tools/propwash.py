"""Propwash & low-throttle analysis.

Propwash windows: motor output fell >=20 points in the previous 300 ms and is now below 35%
(throttle chops / dives into own wash), excluding 400 ms after 3D reversals.
Reports 15-100 Hz tracking-error RMS per axis (the wobble band), its dominant frequency,
and tracking error by motor-output band (low throttle authority).
usage: python tools/propwash.py "a.BBL" "b.BBL#5" ...
"""
import sys

import numpy as np
from scipy import signal

from bbl_load import load

for path in sys.argv[1:]:
    d, h = load(path)
    t = (d["time"] - d["time"][0]) / 1e6
    fs = len(t) / t[-1]
    M = np.mean([d[f"motor[{m}]"] for m in range(4)], axis=0)
    fw = M >= 1048
    pct = np.where(fw, (M - 1048) / 999, (M - 48) / 999) * 100
    pct_s = signal.filtfilt(*signal.butter(2, 10, fs=fs), pct)
    ok = np.ones(len(t), bool)
    for i in np.flatnonzero(np.diff(fw.astype(int))) + 1:
        ok[max(i - int(0.05 * fs), 0):i + int(0.4 * fs)] = False
    ok[-int(2 * fs):] = False
    lag = int(0.3 * fs)
    drop = np.zeros(len(t))
    drop[lag:] = np.maximum.accumulate(np.lib.stride_tricks.sliding_window_view(pct_s, lag + 1).max(axis=1)[:, None], axis=1)[:, 0] - pct_s[lag:]
    pw = ok & (drop >= 20) & (pct_s < 35)
    b, a = signal.butter(2, [15, 100], "bandpass", fs=fs)
    print(f"\n{path}: propwash windows {pw.sum()/fs:.1f}s of {t[-1]:.0f}s")
    for ax, nm in enumerate(("roll", "pitch", "yaw")):
        e = d[f"setpoint[{ax}]"] - d[f"gyroADC[{ax}]"]
        eb = signal.filtfilt(b, a, e)
        f, p = signal.welch(np.where(pw, eb, 0)[pw] if pw.sum() > 256 else eb[:256], fs, nperseg=256)
        s = (f >= 15) & (f <= 100)
        steady = ok & ~pw & (pct_s > 35)
        print(f"  {nm:5s} wash 15-100Hz err RMS {np.sqrt(np.mean(eb[pw]**2)):5.1f}  (steady {np.sqrt(np.mean(eb[steady]**2)):4.1f})"
              f"  peak freq {f[s][np.argmax(p[s])]:.0f}Hz   wash D RMS "
              + (f"{np.sqrt(np.mean(d[f'axisD[{ax}]'][pw]**2)):5.1f}" if ax < 2 else "  -"))
    print("  error RMS by motor output & direction: full-band r/p/y | 8-60Hz wobble r/p | wobble peak Hz")
    bw, aw = signal.butter(2, [8, 60], "bandpass", fs=fs)
    wob = [signal.filtfilt(bw, aw, d[f"setpoint[{a}]"] - d[f"gyroADC[{a}]"]) for a in range(2)]
    for dirn, dn in ((True, "FWD"), (False, "REV")):
        for lo, hi in ((0, 10), (10, 20), (20, 35), (35, 60), (60, 101)):
            s = ok & (pct_s >= lo) & (pct_s < hi) & (fw == dirn)
            if s.sum() < 500:
                continue
            r = [np.sqrt(np.mean((d[f"setpoint[{a}]"] - d[f"gyroADC[{a}]"])[s] ** 2)) for a in range(3)]
            w = [np.sqrt(np.mean(x[s] ** 2)) for x in wob]
            f, p = signal.welch(wob[0][s] + wob[1][s], fs, nperseg=512)
            sel = (f >= 8) & (f <= 60)
            print(f"    {dn} {lo:3d}-{hi:<3d}% {s.sum()/fs:5.1f}s   {r[0]:5.1f} {r[1]:5.1f} {r[2]:5.1f} | {w[0]:4.1f} {w[1]:4.1f} | {f[sel][np.argmax(p[sel])]:3.0f}")
