"""List every log in a .BBL with duration, throttle use, reversals and how it ended.

usage: python tools/list_logs.py "file.BBL"
"""
import sys

import numpy as np
from orangebox import Parser

from bbl_load import load

path = sys.argv[1]
n = Parser.load(path).reader.log_count
for i in range(1, n + 1):
    d, h = load(f"{path}#{i}")
    t = (d["time"] - d["time"][0]) / 1e6
    M = np.stack([d[f"motor[{m}]"] for m in range(4)])
    E = np.stack([d[f"eRPM[{m}]"] for m in range(4)]) * 100
    fwd = (M.mean(axis=0) >= 1048).astype(int)
    rev = int(np.count_nonzero(np.diff(fwd)))
    tail = slice(max(len(t) - int(0.5 * len(t) / t[-1]), 0), None)  # last 0.5 s
    print(f"log {i}: {t[-1]:6.1f}s  reversals={rev:3d}  vbat {d['vbatLatest'].max()/100:.2f}->{d['vbatLatest'][-200:].mean()/100:.2f}V  "
          f"last0.5s eRPM per motor={np.round(E[:, tail].mean(axis=1)/1000).astype(int)}k  "
          f"last0.5s motor cmd={np.round(M[:, tail].mean(axis=1)).astype(int)}")
