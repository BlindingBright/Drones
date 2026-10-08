"""Median eRPM while Betaflight commands (near) idle in each direction: shows how ESC settings
like AM32 min duty / KV change the real idle speed at the same dshot_idle_value.

usage: python tools/idle_rpm.py "a.BBL#n@x-y" ...
"""
import sys

import numpy as np

from bbl_load import load

for path in sys.argv[1:]:
    d, h = load(path)
    M = np.stack([d[f"motor[{m}]"] for m in range(4)])
    E = np.stack([d[f"eRPM[{m}]"] for m in range(4)]) * 100
    lo = float(h.get("motorOutput", [48])[0]) if isinstance(h.get("motorOutput"), list) else 48
    out = []
    for name, base in (("fwd", 1048 + (lo - 48)), ("rev", lo)):
        s = (M >= base) & (M <= base + 15)  # within ~1.5% of idle command
        out.append(f"{name} idle eRPM {np.median(E[s]) / 1000:5.0f}k (n={s.sum()})" if s.sum() > 50 else f"{name} idle: n/a")
    print(f"{path}: " + " | ".join(out))
