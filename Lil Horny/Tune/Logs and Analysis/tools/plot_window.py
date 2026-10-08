"""Scope-style plot of a time window: throttle & direction, motors, eRPM, roll/pitch gyro vs setpoint,
P/D terms and TPA-relevant throttle. usage: python tools/plot_window.py "file.BBL" start end out.png"""
import sys

import numpy as np

from bbl_load import load

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

d, h = load(sys.argv[1])
t0, t1, out = float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
t = (d["time"] - d["time"][0]) / 1e6
s = (t >= t0) & (t <= t1)
tt = t[s]
fig, axs = plt.subplots(6, 1, figsize=(15, 15), sharex=True)
M = np.stack([d[f"motor[{m}]"] for m in range(4)])
axs[0].plot(tt, d["rcCommand[3]"][s], "k", label="throttle")
axs[0].axhline(1500, color="gray", lw=.5)
axs[0].plot(tt, np.where(M.mean(axis=0)[s] >= 1048, 1950, 1050), color="C3", lw=.8, label="direction (hi=upright)")
for m in range(4):
    axs[1].plot(tt, M[m, s], lw=.7, label=f"m{m}")
    axs[2].plot(tt, d[f"eRPM[{m}]"][s] / 10, lw=.7, label=f"m{m}")
axs[1].axhline(1048, color="k", lw=.5)
for x, nm, ax in ((0, "roll", axs[3]), (1, "pitch", axs[4])):
    ax.plot(tt, d[f"gyroADC[{x}]"][s], label=f"gyro {nm}")
    ax.plot(tt, d[f"setpoint[{x}]"][s], "--", label=f"setpoint {nm}")
    ax.set_ylabel("deg/s")
for x, nm in ((0, "roll"), (1, "pitch")):
    axs[5].plot(tt, d[f"axisD[{x}]"][s], lw=.8, label=f"D {nm}")
    axs[5].plot(tt, d[f"axisP[{x}]"][s], lw=.8, alpha=.6, label=f"P {nm}")
axs[2].set_ylabel("eRPM (k)")
for ax in axs:
    ax.grid(alpha=.3)
    ax.legend(loc="upper left", fontsize=8, ncol=4)
axs[-1].set_xlabel("s")
fig.tight_layout()
fig.savefig(out, dpi=75)
print("plot ->", out)
