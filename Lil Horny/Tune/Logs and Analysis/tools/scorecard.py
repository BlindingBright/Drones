"""One-shot scorecard for a 3D whoop log; appends to reports/scorecard.csv so passes can be compared.

usage: python tools/scorecard.py "Pass 2.BBL" "Pass 2 label"
"""
import csv
import os
import subprocess
import sys

import numpy as np
from scipy import signal

from bbl_load import load

path = sys.argv[1]
label = sys.argv[2] if len(sys.argv) > 2 else os.path.splitext(os.path.basename(path))[0]
d, h = load(path)
t = (d["time"] - d["time"][0]) / 1e6
fs = len(t) / t[-1]
M = np.stack([d[f"motor[{i}]"] for i in range(4)])
E = np.stack([d[f"eRPM[{i}]"] for i in range(4)]) * 100
SP = np.stack([d[f"setpoint[{a}]"] for a in range(3)])
G = np.stack([d[f"gyroADC[{a}]"] for a in range(3)])
thr = d["rcCommand[3]"]
fwd = (M.mean(axis=0) >= 1048).astype(int)
sw = np.flatnonzero(np.diff(fwd)) + 1

# --- reversal metrics
W = int(0.4 * fs)
spin, spread, peak = [], [], []
for i0 in sw:
    if i0 < int(0.1 * fs) or i0 + W >= len(t):
        continue
    seg = E[:, i0:i0 + W]
    pre = E[:, i0 - int(0.03 * fs):i0].mean(axis=1)
    kmin = seg.argmin(axis=1)
    tgt = np.maximum(0.6 * pre, 15000)
    kup = np.array([kmin[m] + (np.flatnonzero(seg[m, kmin[m]:] >= tgt[m])[:1].tolist() or [W - kmin[m]])[0] for m in range(4)])
    spin.append(kup.mean() / fs * 1000)
    spread.append((kup.max() - kup.min()) / fs * 1000)
    peak.append(np.abs(SP[:2, i0:i0 + int(0.3 * fs)] - G[:2, i0:i0 + int(0.3 * fs)]).max())

# --- steady-flight mask
fly = np.abs(thr - 1500) > 60
for i in sw:
    fly[max(i - int(0.05 * fs), 0):i + int(0.4 * fs)] = False

def band_db(x, lo, hi):
    f, p = signal.welch(x[fly], fs, nperseg=1024)
    s = (f >= lo) & (f < hi)
    return 10 * np.log10(p[s].mean())

def step_peak(a):
    N = int(fs); R = int(0.5 * fs); win = np.hanning(N); out = []
    sp, gy = SP[a], G[a]
    for s in range(0, len(sp) - N, N // 4):
        if np.abs(sp[s:s + N]).max() < 40 or not fly[s:s + N].all():
            continue
        A = np.fft.fft(sp[s:s + N] * win); B = np.fft.fft(gy[s:s + N] * win)
        imp = np.real(np.fft.ifft(B * np.conj(A) / (np.abs(A) ** 2 + 1e-3 * np.mean(np.abs(A) ** 2))))[:R]
        out.append(np.cumsum(imp))
    S = np.array(out)
    S = S[(S[:, -200:].mean(axis=1) > 0.5) & (S[:, -200:].mean(axis=1) < 1.5)]
    m = S.mean(axis=0)
    return m[: int(0.2 * fs)].max(), m[int(0.2 * fs):].mean()

err = SP - G
row = {
    "label": label,
    "duration_s": round(t[-1], 1),
    "motor_poles": h.get("motor_poles"),
    "reversals": len(sw),
    "rev_spinup_ms_med": round(float(np.median(spin)), 1) if spin else "",
    "rev_motor_spread_ms_med": round(float(np.median(spread)), 1) if spread else "",
    "rev_peak_err_med": round(float(np.median(peak)), 0) if peak else "",
    "rev_peak_err_p90": round(float(np.percentile(peak, 90)), 0) if peak else "",
    "steady_err_rms_roll": round(float(np.sqrt(np.mean(err[0][fly] ** 2))), 1),
    "steady_err_rms_pitch": round(float(np.sqrt(np.mean(err[1][fly] ** 2))), 1),
    "steady_err_rms_yaw": round(float(np.sqrt(np.mean(err[2][fly] ** 2))), 1),
    "gyro_unfilt_400_1000_db_roll": round(band_db(d["gyroUnfilt[0]"], 400, 1000), 1),
    "gyro_filt_80_400_db_roll": round(band_db(d["gyroADC[0]"], 80, 400), 1),
    "dterm_rms_roll": round(float(np.sqrt(np.mean(d["axisD[0]"][fly] ** 2))), 1),
    "dterm_rms_pitch": round(float(np.sqrt(np.mean(d["axisD[1]"][fly] ** 2))), 1),
}
for a, nm in enumerate(("roll", "pitch", "yaw")):
    pk, st = step_peak(a)
    row[f"step_peak_{nm}"] = round(float(pk), 2)
    row[f"step_settle_{nm}"] = round(float(st), 2)

for k, v in row.items():
    print(f"{k:32s} {v}")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports", "scorecard.csv")
new = not os.path.exists(out)
with open(out, "a", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(row))
    if new:
        w.writeheader()
    w.writerow(row)
print("appended ->", os.path.normpath(out))
