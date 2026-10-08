"""Compare ESC settings across logs, focused on 3D direction switching (AM32 min duty / KV tests).

Per reversal, per motor (all times from the moment BF switches direction):
  t_zero    : ms until the motor reaches its rpm minimum (prop stopped, about to reverse)
  t_restart : ms from that minimum until eRPM >= 100k in the new direction (absolute, so it
              doesn't depend on how fast the motor was spinning before)
  t_total   : t_zero + t_restart
Plus: motor spread (slowest - fastest t_total), attitude error peak 0-300 ms, slow restarts
(>200 ms), low-rpm roughness (eRPM ripple below 150k), and wobble at 0-20 % motor output.

usage: python tools/esc_compare.py out.png "label=file.BBL#n@a-b" "label2=file2.BBL" ...
"""
import sys

import numpy as np
from scipy import signal

from bbl_load import load

out = sys.argv[1]
runs = [a.split("=", 1) if "=" in a else (a, a) for a in sys.argv[2:]]
RESTART = 100_000
PRE, POST = 0.1, 0.45

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axs = plt.subplots(1, 2, figsize=(15, 5.5), sharey=True)
rows = []
for li, (label, paths) in enumerate(runs):
  # "a.BBL#1@0-69+a.BBL#2" pools several logs/segments into one run
  tz, tr, tt, spread, peak, curves = [], [], [], [], [], {1: [], 0: []}
  rough_s, wob_s, idle_s = [[] for _ in range(4)], [[], []], []
  for path in paths.split("+"):
    d, h = load(path)
    t = (d["time"] - d["time"][0]) / 1e6
    fs = len(t) / t[-1]
    M = np.stack([d[f"motor[{m}]"] for m in range(4)])
    E = np.stack([d[f"eRPM[{m}]"] for m in range(4)]) * 100
    SP = np.stack([d[f"setpoint[{a}]"] for a in range(2)])
    G = np.stack([d[f"gyroADC[{a}]"] for a in range(2)])
    fw = (M.mean(axis=0) >= 1048).astype(int)
    sw = np.flatnonzero(np.diff(fw)) + 1
    W, P0 = int(POST * fs), int(PRE * fs)
    for k, i0 in enumerate(sw):
        if i0 < P0 or i0 + W >= len(t):
            continue
        if k + 1 < len(sw) and sw[k + 1] - i0 < W:
            continue  # another switch inside the window: not a clean reversal
        seg = E[:, i0:i0 + W]
        kmin = seg.argmin(axis=1)
        kre = np.array([kmin[m] + (np.flatnonzero(seg[m, kmin[m]:] >= RESTART)[:1].tolist() or [W - kmin[m]])[0]
                        for m in range(4)])
        tz.append(kmin / fs * 1000)
        tr.append((kre - kmin) / fs * 1000)
        tt.append(kre / fs * 1000)
        spread.append((kre.max() - kre.min()) / fs * 1000)
        peak.append(np.abs(SP[:, i0:i0 + int(0.3 * fs)] - G[:, i0:i0 + int(0.3 * fs)]).max())
        curves[fw[i0]].append(E[:, i0 - P0:i0 + W].mean(axis=0))

    # low-rpm roughness: eRPM ripple (20-200 Hz) while 5k < eRPM < 150k, away from reversals
    ok = np.ones(len(t), bool)
    for i in sw:
        ok[max(i - int(0.05 * fs), 0):i + int(0.4 * fs)] = False
    b, a = signal.butter(2, [20, 200], "bandpass", fs=fs)
    for m in range(4):
        rip = signal.filtfilt(b, a, E[m])
        s = ok & (E[m] > 5000) & (E[m] < 150_000)
        rough_s[m].extend(rip[s] ** 2)
    Mm = M.mean(axis=0)
    pct = np.where(Mm >= 1048, (Mm - 1048) / 999, (Mm - 48) / 999) * 100
    bw, aw = signal.butter(2, [8, 60], "bandpass", fs=fs)
    low = ok & (pct < 20)
    for a_ in range(2):
        wob_s[a_].extend(signal.filtfilt(bw, aw, SP[a_] - G[a_])[low] ** 2)
    idle_s.extend(E[:, ok & (pct < 6)].ravel())

  tz, tr, tt = np.array(tz), np.array(tr), np.array(tt)
  rough = [np.sqrt(np.mean(r)) for r in rough_s if len(r) > 200]
  wob = [np.sqrt(np.mean(w)) for w in wob_s] if len(wob_s[0]) > 500 else [np.nan] * 2
  idle_rpm = np.median(idle_s) if len(idle_s) > 400 else np.nan
  if True:
    n = len(tt)
    row = dict(label=label, n=n,
               t_zero=np.median(tz) if n else np.nan, t_restart=np.median(tr) if n else np.nan,
               t_total=np.median(tt) if n else np.nan, t_total_p90=np.percentile(tt, 90) if n else np.nan,
               spread=np.median(spread) if n else np.nan, peak=np.median(peak) if n else np.nan,
               peak_p90=np.percentile(peak, 90) if n else np.nan,
               slow=int((tt > 200).sum()) if n else 0,
               rough=np.mean(rough) / 1000 if rough else np.nan, wob=np.mean(wob), idle=idle_rpm / 1000,
               per_motor=np.median(tt, axis=0) if n else np.full(4, np.nan))
    rows.append(row)
    xs = (np.arange(-P0, W) / fs) * 1000
    for c, (dirn, ttl) in enumerate(((1, "REV -> FWD"), (0, "FWD -> REV"))):
        if curves[dirn]:
            axs[c].plot(xs, np.median(curves[dirn], axis=0) / 1000, color=f"C{li}", lw=2,
                        label=f"{label} (n={len(curves[dirn])})")
        axs[c].set_title(f"{ttl}: median of mean-motor eRPM")
for ax in axs:
    ax.axvline(0, color="k", lw=.6)
    ax.axhline(RESTART / 1000, color="gray", lw=.6, ls="--")
    ax.set_xlabel("ms from direction switch")
    ax.grid(alpha=.3)
    ax.legend()
axs[0].set_ylabel("eRPM (k)")
fig.tight_layout()
fig.savefig(out, dpi=85)

hdr = (f"{'run':28s} {'n':>3} {'stop':>6} {'restart':>8} {'total':>6} {'tot p90':>8} {'spread':>7} "
       f"{'slow>200':>8} {'err pk':>7} {'pk p90':>7} {'lowRPM rough':>12} {'low-thr wob r/p':>16} {'idle eRPM':>9}")
print(hdr)
print("-" * len(hdr))
for r in rows:
    print(f"{r['label'][:28]:28s} {r['n']:3d} {r['t_zero']:6.0f} {r['t_restart']:8.0f} {r['t_total']:6.0f} "
          f"{r['t_total_p90']:8.0f} {r['spread']:7.0f} {r['slow']:8d} {r['peak']:7.0f} {r['peak_p90']:7.0f} "
          f"{r['rough']:11.1f}k {r['wob']:16.1f} " + ("        -" if np.isnan(r['idle']) else f"{r['idle']:8.0f}k"))
print("\nper-motor median total switch time (ms) m0..m3:")
for r in rows:
    print(f"  {r['label'][:28]:28s} {np.round(r['per_motor']).astype(int) if r['n'] else '-'}")
print("\n(stop/restart/total = ms, median over clean reversals; lower = faster switching)")
print("plot ->", out)
