"""Crash forensics: plot the last N seconds of a log and flag per-motor anomalies.

Prop loss  -> one motor's eRPM jumps well above what its command normally gives (unloaded).
Stall/desync -> motor commanded high but eRPM collapses toward 0.
usage: python tools/crash.py "file.BBL#4" out.png [seconds=4]
"""
import sys

import numpy as np

from bbl_load import load

path, out = sys.argv[1], sys.argv[2]
secs = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0
d, h = load(path)
t = (d["time"] - d["time"][0]) / 1e6
fs = len(t) / t[-1]
M = np.stack([d[f"motor[{m}]"] for m in range(4)])
E = np.stack([d[f"eRPM[{m}]"] for m in range(4)]) * 100
G = np.stack([d[f"gyroADC[{a}]"] for a in range(3)])
SP = np.stack([d[f"setpoint[{a}]"] for a in range(3)])
acc = np.stack([d[f"accSmooth[{a}]"] for a in range(3)]) / float(h.get("acc_1G", 2048))

# command -> eRPM model from the whole log, per direction (median per 2% bin)
pct = np.where(M >= 1048, (M - 1048) / 999, (M - 48) / 999) * 100
fw = M >= 1048
def model(p, f):
    bins = np.arange(0, 102, 2)
    tab = {}
    for dirn in (True, False):
        sel = fw == dirn
        idx = np.digitize(pct[sel], bins)
        vals = E[sel]
        tab[dirn] = np.array([np.median(vals[idx == k]) if (idx == k).sum() > 50 else np.nan for k in range(len(bins) + 1)])
    k = np.digitize(p, bins)
    return np.where(f, tab[True][k], tab[False][k])
expected = model(pct, fw)
ratio = E / np.maximum(expected, 1)

s0 = max(len(t) - int(secs * fs), 0)
sl = slice(s0, None)
# smooth ratio over 20 ms
k = max(int(0.02 * fs), 1)
rs = np.array([np.convolve(r, np.ones(k) / k, mode="same") for r in ratio])
print(f"{path}: {t[-1]:.2f}s, showing last {secs}s")
for m in range(4):
    over = np.flatnonzero((rs[m, sl] > 1.6) & (M[m, sl] % 1000 > 100))
    stall = np.flatnonzero((E[m, sl] < 5000) & (pct[m, sl] > 40))
    msg = []
    if len(over):
        msg.append(f"RPM >1.6x expected (unloaded?) from t={t[s0 + over[0]]:.2f}s for {len(over)/fs*1000:.0f}ms")
    if len(stall):
        msg.append(f"commanded >40% but ~0 rpm from t={t[s0 + stall[0]]:.2f}s for {len(stall)/fs*1000:.0f}ms")
    print(f"  motor {m}: " + ("; ".join(msg) if msg else "normal"))
gmag = np.abs(G[:, sl]).max(axis=1)
amag = np.linalg.norm(acc[:, sl], axis=0)
print(f"  peak gyro r/p/y {gmag.round(0)} deg/s, peak accel {amag.max():.1f} g at t={t[s0 + amag.argmax()]:.2f}s")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig, axs = plt.subplots(5, 1, figsize=(14, 13), sharex=True)
tt = t[sl]
for m in range(4):
    axs[0].plot(tt, E[m, sl] / 1000, label=f"m{m}")
    axs[1].plot(tt, M[m, sl], label=f"m{m}")
    axs[2].plot(tt, rs[m, sl], label=f"m{m}")
axs[0].set_ylabel("eRPM (k)"); axs[1].set_ylabel("motor cmd\n(<1048 = reverse)"); axs[1].axhline(1048, color="k", lw=.5)
axs[2].set_ylabel("rpm / expected"); axs[2].axhline(1, color="k", lw=.5); axs[2].set_ylim(0, 3)
for a, nm in enumerate("rpy"):
    axs[3].plot(tt, G[a, sl], label=f"gyro {nm}")
    axs[3].plot(tt, SP[a, sl], "--", lw=.7)
axs[3].set_ylabel("deg/s")
axs[4].plot(tt, amag, "k", label="|accel| g"); axs[4].plot(tt, d["rcCommand[3]"][sl] / 1000, label="throttle/1000")
axs[4].set_xlabel("s")
for ax in axs:
    ax.legend(loc="upper left", fontsize=8); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(out, dpi=80)
print("plot ->", out)
