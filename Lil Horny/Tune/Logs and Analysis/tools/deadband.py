"""Infer the 3D throttle deadband from where motor direction actually switches, and count
'chatter' (direction flipping back within 250 ms while the stick lingers near center).

usage: python tools/deadband.py "file.BBL" ...
"""
import sys

import numpy as np

from bbl_load import load

for path in sys.argv[1:]:
    d, h = load(path)
    t = (d["time"] - d["time"][0]) / 1e6
    fs = len(t) / t[-1]
    thr = d["rcCommand[3]"]
    M = np.mean([d[f"motor[{m}]"] for m in range(4)], axis=0)
    fw = (M >= 1048).astype(int)
    sw = np.flatnonzero(np.diff(fw)) + 1
    to_f = [thr[i] for i in sw if fw[i] == 1]
    to_r = [thr[i] for i in sw if fw[i] == 0]
    chatter = int(np.sum(np.diff(sw) < 0.25 * fs))
    print(f"{path}: {len(sw)} switches, chatter (flip back <250 ms) = {chatter}")
    if to_f:
        print(f"  -> FWD when throttle >= {min(to_f):.0f}  (values {sorted(int(x) for x in to_f)[:6]}...)")
    if to_r:
        print(f"  -> REV when throttle <= {max(to_r):.0f}  (values {sorted((int(x) for x in to_r), reverse=True)[:6]}...)")
    near = np.abs(thr - 1500) < 25
    print(f"  time with stick within +/-25 of center: {near.sum()/fs:.1f}s")
