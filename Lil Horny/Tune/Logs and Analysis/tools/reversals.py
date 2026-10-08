"""Analyze 3D direction reversals (motor output crossing the DShot 3D split at 1048).

For each reversal: per-motor time to reach eRPM minimum (prop stop) and time to spin back up,
spread between motors, attitude tracking error around the event, and I-term reset.
usage: python tools/reversals.py "log.BBL" [--plot out.png]
"""
import sys

import numpy as np

from bbl_load import load

path = sys.argv[1]
d, h = load(path)
t = (d["time"] - d["time"][0]) / 1e6
fs = len(t) / t[-1]
ms = lambda n: n / fs * 1000
M = np.stack([d[f"motor[{i}]"] for i in range(4)])
E = np.stack([d[f"eRPM[{i}]"] for i in range(4)]) * 100  # true eRPM
thr = d["rcCommand[3]"]
SP = np.stack([d[f"setpoint[{a}]"] for a in range(3)])
G = np.stack([d[f"gyroADC[{a}]"] for a in range(3)])
I = np.stack([d[f"axisI[{a}]"] for a in range(3)])
err = SP - G

fwd = (M.mean(axis=0) >= 1048).astype(int)
sw = np.flatnonzero(np.diff(fwd)) + 1
armed_ok = d["motor[0]"] > 0
print(f"log {path}: {t[-1]:.1f}s, {len(sw)} direction switches ({len(sw)/t[-1]*60:.0f}/min)")

base_err = np.sqrt(np.mean(err ** 2, axis=1))
print("whole-flight RMS tracking error deg/s  roll %.1f pitch %.1f yaw %.1f" % tuple(base_err))

W = int(0.4 * fs)
rows = []
for i0 in sw:
    if i0 < int(0.1 * fs) or i0 + W >= len(t):
        continue
    # skip switches that bounce back within 60 ms (stick dither on center)
    nxt = sw[sw > i0]
    if len(nxt) and nxt[0] - i0 < int(0.06 * fs):
        continue
    to_fwd = fwd[i0] == 1
    seg = E[:, i0:i0 + W]
    pre = E[:, i0 - int(0.03 * fs):i0].mean(axis=1)
    kmin = seg.argmin(axis=1)
    emin = seg.min(axis=1)
    # spin-up: first sample after minimum where eRPM back above 60% of pre-event (or 15k eRPM floor)
    tgt = np.maximum(0.6 * pre, 15000)
    kup = []
    for m in range(4):
        after = np.flatnonzero(seg[m, kmin[m]:] >= tgt[m])
        kup.append(kmin[m] + after[0] if len(after) else W)
    kup = np.array(kup)
    e = err[:, i0:i0 + int(0.3 * fs)]
    stalled = (seg < 500).sum(axis=1)  # samples near zero rpm
    # throttle stick speed through center (us per ms)
    j = slice(max(i0 - int(0.05 * fs), 0), i0 + int(0.05 * fs))
    stick_rate = abs(thr[j][-1] - thr[j][0]) / 100.0
    rows.append(dict(t=t[i0], to_fwd=to_fwd, tmin=ms(kmin), tup=ms(kup), spread_min=ms(kmin.max() - kmin.min()),
                     spread_up=ms(kup.max() - kup.min()), pre=pre, emin=emin,
                     rms=np.sqrt(np.mean(e ** 2, axis=1)), peak=np.abs(e).max(axis=1),
                     stall_ms=ms(stalled.max()), stick=stick_rate,
                     iterm_zero=ms((np.abs(I[:2, i0:i0 + W]).max(axis=0) < 0.5).sum())))

print(f"analyzed {len(rows)} clean reversals")
for name, sel in (("REV->FWD", True), ("FWD->REV", False)):
    rr = [r for r in rows if r["to_fwd"] == sel]
    if not rr:
        continue
    A = lambda k: np.array([r[k] for r in rr])
    print(f"\n== {name}: n={len(rr)}")
    print("  time to prop stop (ms, per motor median):", np.median(A("tmin"), axis=0).round(1))
    print("  time back to 60%% rpm (ms, per motor median):", np.median(A("tup"), axis=0).round(1))
    print("  time back to 60%% rpm p90 (ms):", np.percentile(A("tup"), 90, axis=0).round(1))
    print("  motor spread at stop  median %.1f ms  p90 %.1f ms" % (np.median(A("spread_min")), np.percentile(A("spread_min"), 90)))
    print("  motor spread spin-up  median %.1f ms  p90 %.1f ms" % (np.median(A("spread_up")), np.percentile(A("spread_up"), 90)))
    print("  pre-event eRPM median:", np.median(A("pre"), axis=0).round(0))
    print("  time near 0 rpm (ms) median %.1f p90 %.1f max %.1f" % (np.median(A("stall_ms")), np.percentile(A("stall_ms"), 90), A("stall_ms").max()))
    print("  err RMS 0-300ms (r,p,y) median:", np.median(A("rms"), axis=0).round(1), " ratio vs flight:", (np.median(A("rms"), axis=0) / base_err).round(2))
    print("  err PEAK 0-300ms (r,p,y) median:", np.median(A("peak"), axis=0).round(0), " p90:", np.percentile(A("peak"), 90, axis=0).round(0))
    print("  I-term ~0 after reversal (ms) median %.0f" % np.median(A("iterm_zero")))

# which motor is slowest to come back?
allup = np.array([r["tup"] for r in rows])
print("\nper-motor mean spin-up ms (all reversals):", allup.mean(axis=0).round(1))
slow = np.argmax(allup, axis=1)
print("slowest-motor counts m0..m3:", np.bincount(slow, minlength=4))
worst = sorted(rows, key=lambda r: -r["peak"][:2].max())[:8]
print("\nworst reversals by roll/pitch peak error:")
for r in worst:
    print(f"  t={r['t']:6.2f}s {'R->F' if r['to_fwd'] else 'F->R'} peak={r['peak'].round(0)} spinup={r['tup'].round(0)} stall={r['stall_ms']:.0f}ms")

if "--plot" in sys.argv:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out = sys.argv[sys.argv.index("--plot") + 1]
    picks = worst[:4]
    fig, axs = plt.subplots(3, len(picks), figsize=(5 * len(picks), 9), sharex=True)
    for c, r in enumerate(picks):
        i0 = np.searchsorted(t, r["t"])
        sl = slice(i0 - int(0.15 * fs), i0 + int(0.45 * fs))
        tt = (t[sl] - r["t"]) * 1000
        for m in range(4):
            axs[0, c].plot(tt, E[m, sl] / 1000, label=f"m{m}")
        axs[0, c].set_title(f"t={r['t']:.2f}s {'R->F' if r['to_fwd'] else 'F->R'}")
        axs[0, c].set_ylabel("eRPM (k)")
        for a, nm in enumerate("rpy"):
            axs[1, c].plot(tt, G[a, sl], label=f"gyro {nm}")
            axs[1, c].plot(tt, SP[a, sl], "--", lw=0.8)
        axs[1, c].set_ylabel("deg/s")
        axs[2, c].plot(tt, thr[sl], "k", label="throttle")
        axs[2, c].plot(tt, M[:, sl].T, lw=0.7)
        axs[2, c].set_xlabel("ms from switch")
        for ax in axs[:, c]:
            ax.axvline(0, color="gray", lw=0.5)
            ax.grid(alpha=0.3)
    axs[0, 0].legend()
    axs[1, 0].legend()
    fig.tight_layout()
    fig.savefig(out, dpi=90)
    print("plot ->", out)
