"""Tic-tock / hard-3D maneuver wobble analysis.

Auto-finds 'hard 3D' seconds: throttle swings through most of both directions (min<1150 and max>1850)
or 2+ reversals, with big pitch commands. Inside those it reports:
  - 8-60 Hz wobble per axis and its dominant frequency
  - wobble split by phase: upright / inverted, low/high motor output, motor saturation
  - D/P share of PID output, motor saturation %
usage: python tools/ticktock.py "a.BBL" "b.BBL#n@x-y" ...   or  "file.BBL@54-70" to force a window
"""
import sys

import numpy as np
from scipy import signal

from bbl_load import load

for path in sys.argv[1:]:
    d, h = load(path)
    t = (d["time"] - d["time"][0]) / 1e6
    fs = len(t) / t[-1]
    Mall = np.stack([d[f"motor[{m}]"] for m in range(4)])
    M = Mall.mean(axis=0)
    fw = M >= 1048
    pct = np.where(fw, (M - 1048) / 999, (M - 48) / 999) * 100
    thr = d["rcCommand[3]"]
    sw_t = t[np.flatnonzero(np.diff(fw.astype(int))) + 1]
    sel = np.zeros(len(t), bool)
    for s in np.arange(0, t[-1] - 1, 0.5):
        m = (t >= s) & (t < s + 1)
        big_thr = thr[m].min() < 1150 and thr[m].max() > 1850
        nrev = ((sw_t >= s) & (sw_t < s + 1)).sum()
        pitchy = np.abs(d["setpoint[1]"][m]).max() > 120
        if (big_thr or nrev >= 2) and pitchy:
            sel |= m
    sel[-int(1.0 * fs):] = False
    if sel.sum() < fs:
        print(f"\n{path}: no tic-tock style maneuvers found"); continue
    b, a = signal.butter(2, [8, 60], "bandpass", fs=fs)
    wob = [signal.filtfilt(b, a, d[f"setpoint[{x}]"] - d[f"gyroADC[{x}]"]) for x in range(3)]
    calm = ~sel & (np.abs(thr - 1500) > 100)
    sat = ((Mall >= 2040) | ((Mall >= 1040) & (Mall <= 1047))).any(axis=0)
    print(f"\n{path}: hard-3D time {sel.sum()/fs:.1f}s (reversals inside: {int(np.sum(np.isin(np.round(sw_t*fs), np.flatnonzero(sel))))})")
    for x, nm in enumerate(("roll", "pitch", "yaw")):
        f, p = signal.welch(wob[x][sel], fs, nperseg=512)
        s_ = (f >= 8) & (f <= 60)
        print(f"  {nm:5s} wobble RMS {np.sqrt(np.mean(wob[x][sel]**2)):5.1f}  (calm flight {np.sqrt(np.mean(wob[x][calm]**2)):4.1f})"
              f"  peak {f[s_][np.argmax(p[s_])]:4.0f} Hz")
    print("  roll/pitch wobble by phase:")
    for nm, m in (("upright  <30%", sel & fw & (pct < 30)), ("upright  >=30%", sel & fw & (pct >= 30)),
                  ("inverted <30%", sel & ~fw & (pct < 30)), ("inverted >=30%", sel & ~fw & (pct >= 30)),
                  ("any motor saturated", sel & sat)):
        if m.sum() > 50:
            print(f"    {nm:20s} {m.sum()/fs:4.1f}s   {np.sqrt(np.mean(wob[0][m]**2)):5.1f} / {np.sqrt(np.mean(wob[1][m]**2)):5.1f}")
    print(f"  motor saturation in maneuver: {sat[sel].mean()*100:.1f}%  (calm {sat[calm].mean()*100:.1f}%)")
    for x, nm in ((0, "roll"), (1, "pitch")):
        P, D, I = (np.sqrt(np.mean(d[f"axis{k}[{x}]"][sel] ** 2)) for k in "PDI")
        print(f"  {nm:5s} RMS  P {P:5.1f}  D {D:5.1f}  I {I:5.1f}")
