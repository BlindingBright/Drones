"""Verify motor_poles by matching gyroUnfilt spectral peaks to eRPM-predicted motor frequency.

The log is decimated (not anti-alias filtered) so predicted frequencies are folded around Nyquist.
For each candidate pole count we sum the spectral energy at the predicted (aliased) fundamental;
the right pole count lines up with the real noise line.
"""
import sys

import numpy as np

from bbl_load import load

d, h = load(sys.argv[1])
t = (d["time"] - d["time"][0]) / 1e6
fs = len(t) / t[-1]
nyq = fs / 2
g = d["gyroUnfilt[0]"] + d["gyroUnfilt[1]"]
erpm = np.mean([d[f"eRPM[{i}]"] for i in range(4)], axis=0) * 100

N = 512
win = np.hanning(N)
freqs = np.fft.rfftfreq(N, 1 / fs)
scores = {p: [] for p in (8, 10, 12, 14, 16)}
for s in range(0, len(g) - N, N // 2):
    e = erpm[s:s + N]
    if e.mean() < 150000 or e.std() > 0.08 * e.mean():
        continue  # want steady, reasonably high rpm windows
    spec = np.abs(np.fft.rfft((g[s:s + N] - g[s:s + N].mean()) * win)) ** 2
    spec /= np.median(spec) + 1e-9
    for p in scores:
        f = e.mean() / 60 / (p / 2)
        fa = abs(((f + nyq) % fs) - nyq)  # alias fold
        k = int(round(fa / (fs / N)))
        if 2 < k < len(spec) - 3:
            scores[p].append(spec[k - 1:k + 2].max())
for p, v in scores.items():
    print(f"poles={p:2d}: windows={len(v)} median peak/median-floor={np.median(v):.1f}")
