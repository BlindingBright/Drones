"""Quick statistical overview of a 3D log: throttle/motor/eRPM distributions and reversal events."""
import sys

import numpy as np

from bbl_load import load

d, h = load(sys.argv[1])
t = (d["time"] - d["time"][0]) / 1e6
thr = d["rcCommand[3]"]
M = np.stack([d[f"motor[{i}]"] for i in range(4)])
E = np.stack([d[f"eRPM[{i}]"] for i in range(4)])

print("rcCommand[3] (throttle) pct:", np.percentile(thr, [0, 1, 5, 25, 50, 75, 95, 99, 100]).round(0))
print("setpoint[3] pct:", np.percentile(d["setpoint[3]"], [0, 1, 25, 50, 75, 99, 100]).round(0))
for i in range(4):
    print(f"motor[{i}] pct:", np.percentile(M[i], [0, 1, 5, 25, 50, 75, 95, 99, 100]).round(0))
for i in range(4):
    print(f"eRPM[{i}] pct:", np.percentile(E[i], [0, 1, 5, 25, 50, 75, 95, 99, 100]).round(0))
print("vbat pct:", np.percentile(d["vbatLatest"], [0, 5, 50, 95, 100]))
print("amp pct:", np.percentile(d["amperageLatest"], [0, 5, 50, 95, 100]))
print("flightModeFlags uniq:", np.unique(d["flightModeFlags"]))
print("stateFlags uniq:", np.unique(d["stateFlags"]))

# value histogram of motor output around mid to see 3D split
mm = M[0]
hist, edges = np.histogram(mm, bins=np.arange(0, 2100, 50))
for c, e in zip(hist, edges):
    if c:
        print(f"  motor0 {int(e):5d}-{int(e)+50:5d}: {c}")
hist, edges = np.histogram(thr, bins=np.arange(1000, 2050, 50))
for c, e in zip(hist, edges):
    if c:
        print(f"  thr {int(e):5d}-{int(e)+50:5d}: {c}")
