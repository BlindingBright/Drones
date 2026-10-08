"""Noise spectra (unfiltered gyro / filtered gyro / D-term), filter delay and step response.

Step response uses the PID-Toolbox style Wiener deconvolution of gyro vs setpoint in sliding windows.
usage: python tools/noise_step.py "log.BBL" out_prefix
"""
import sys

import numpy as np
from scipy import signal

from bbl_load import load

path, out = sys.argv[1], sys.argv[2]
d, h = load(path)
t = (d["time"] - d["time"][0]) / 1e6
fs = len(t) / t[-1]
thr = d["rcCommand[3]"]
fly = np.abs(thr - 1500) > 60  # off the 3D centre (motors loaded)
# also drop 400 ms after every direction switch (BF zeroes I-term for 250 ms there)
_fwd = (np.mean([d[f"motor[{i}]"] for i in range(4)], axis=0) >= 1048).astype(int)
for _i in np.flatnonzero(np.diff(_fwd)) + 1:
    fly[max(_i - int(0.05 * fs), 0):_i + int(0.4 * fs)] = False

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def psd(x):
    f, p = signal.welch(x[fly], fs, nperseg=1024)
    return f, 10 * np.log10(p + 1e-12)

fig, axs = plt.subplots(3, 3, figsize=(16, 11))
names = ["roll", "pitch", "yaw"]
for a in range(3):
    f, pu = psd(d[f"gyroUnfilt[{a}]"])
    f, pf = psd(d[f"gyroADC[{a}]"])
    axs[0, a].plot(f, pu, label="gyro unfiltered")
    axs[0, a].plot(f, pf, label="gyro filtered")
    axs[0, a].set_title(f"{names[a]} gyro PSD (dB)")
    if a < 2:
        f, pd = psd(d[f"axisD[{a}]"])
        axs[1, a].plot(f, pd, color="C3")
        axs[1, a].set_title(f"{names[a]} D-term PSD (dB)")
    # bands
    for lo, hi in ((20, 80), (80, 200), (200, 400), (400, 1000)):
        sel = (f >= lo) & (f < hi)
        print(f"{names[a]:5s} {lo:4d}-{hi:4d}Hz  unfilt {pu[sel].mean():6.1f} dB  filt {pf[sel].mean():6.1f} dB  "
              f"atten {pu[sel].mean()-pf[sel].mean():5.1f} dB" + (f"  Dterm {pd[sel].mean():6.1f} dB" if a < 2 else ""))
    # filter delay via cross-correlation unfilt -> filt
    x = d[f"gyroUnfilt[{a}]"][fly]; y = d[f"gyroADC[{a}]"][fly]
    n = 20000
    c = signal.correlate(y[:n] - y[:n].mean(), x[:n] - x[:n].mean(), mode="full")
    lag = (np.argmax(c) - (n - 1)) / fs * 1000
    print(f"{names[a]:5s} gyro filter delay ~{lag:.2f} ms")
    if a < 2:
        print(f"{names[a]:5s} D-term RMS {np.sqrt(np.mean(d[f'axisD[{a}]'][fly]**2)):.1f}  P RMS {np.sqrt(np.mean(d[f'axisP[{a}]'][fly]**2)):.1f}")
for ax in axs[0]:
    ax.legend(); ax.grid(alpha=.3); ax.set_xlabel("Hz")
for ax in axs[1, :2]:
    ax.grid(alpha=.3); ax.set_xlabel("Hz")

# step response (Wiener deconvolution, 1 s windows, setpoint must move)
def step_resp(sp, gy, fs, wlen=1.0, rlen=0.5):
    N = int(wlen * fs); R = int(rlen * fs)
    win = np.hanning(N)
    out = []
    for s in range(0, len(sp) - N, N // 4):
        a = sp[s:s + N]; b = gy[s:s + N]
        if np.abs(a).max() < 40 or not fly[s:s + N].all():
            continue
        A = np.fft.fft(a * win); B = np.fft.fft(b * win)
        H = (B * np.conj(A)) / (np.abs(A) ** 2 + 0.0001 * np.abs(A).max() ** 2 * 0 + 1e-3 * np.mean(np.abs(A) ** 2))
        imp = np.real(np.fft.ifft(H))[:R]
        out.append(np.cumsum(imp))
    return np.array(out)

tt = np.arange(int(0.5 * fs)) / fs * 1000
for a in range(3):
    S = step_resp(d[f"setpoint[{a}]"], d[f"gyroADC[{a}]"], fs)
    if len(S) == 0:
        continue
    S = S[(S[:, -200:].mean(axis=1) > 0.5) & (S[:, -200:].mean(axis=1) < 1.5)]
    m = S.mean(axis=0)
    t50 = tt[np.argmax(m >= 0.5)]
    peak = m[: int(0.2 * fs)].max()
    print(f"{names[a]:5s} step: windows={len(S)} t50={t50:.1f}ms peak={peak:.2f} settle(200-500ms)={m[int(0.2*fs):].mean():.2f}")
    axs[2, a].plot(tt, m, "k", lw=2)
    axs[2, a].set_xlim(0, 300); axs[2, a].set_ylim(0, 1.6); axs[2, a].axhline(1, color="gray", lw=.5)
    axs[2, a].set_title(f"{names[a]} step response (peak {peak:.2f}, t50 {t50:.0f}ms)"); axs[2, a].grid(alpha=.3)

# throttle -> rpm linearity per direction
ax = axs[1, 2]
M = np.mean([d[f"motor[{i}]"] for i in range(4)], axis=0)
E = np.mean([d[f"eRPM[{i}]"] for i in range(4)], axis=0) * 100
fw = M >= 1048
ax.plot((M[fw] - 1048) / 999 * 100, E[fw] / 1000, ",", alpha=.3, label="forward")
ax.plot((M[~fw] - 48) / 999 * 100, E[~fw] / 1000, ",", alpha=.3, label="reverse")
ax.set_xlabel("motor command % of half-range"); ax.set_ylabel("mean eRPM (k)"); ax.legend(); ax.grid(alpha=.3)
ax.set_title("command vs RPM by direction")
for lo in (3, 5, 10, 20, 40, 60, 80):
    sf = fw & (np.abs((M - 1048) / 999 * 100 - lo) < 1.5)
    sr = (~fw) & (np.abs((M - 48) / 999 * 100 - lo) < 1.5)
    print(f"cmd {lo:2d}%  fwd eRPM {np.median(E[sf]) if sf.any() else np.nan:8.0f}  rev eRPM {np.median(E[sr]) if sr.any() else np.nan:8.0f}")
fig.tight_layout(); fig.savefig(out + "_noise_step.png", dpi=80)
print("plot ->", out + "_noise_step.png")
sat = np.mean([(d[f"motor[{i}]"] >= 2040) | ((d[f"motor[{i}]"] >= 1040) & (d[f"motor[{i}]"] <= 1047)) for i in range(4)], axis=1)
print("motor time at full output (fwd or rev):", (sat * 100).round(2), "%")
idle = np.mean([(d[f"motor[{i}]"] <= 78) | ((d[f"motor[{i}]"] >= 1076) & (d[f"motor[{i}]"] <= 1078)) for i in range(4)], axis=1)
print("motor time at idle clamp:", (idle * 100).round(2), "%")
