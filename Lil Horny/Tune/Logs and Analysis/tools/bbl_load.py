"""Decode a Betaflight .BBL into numpy arrays (cached as .npz next to the log).

usage (module):  from bbl_load import load; d, headers = load("file.BBL", log_index=1)
usage (cli):     python tools/bbl_load.py "file.BBL"   -> builds cache, prints summary
Any tool accepts "file.BBL#N" to pick log N of a multi-log file, and "@start-end" (seconds)
to trim, e.g. "file.BBL#1@0-46" to drop a crash at the end, and "+" to join segments,
e.g. "file.BBL@0-40+file.BBL@42-64" to skip a hit in the middle.
"""
import json
import os
import sys

import numpy as np
from orangebox import Parser


def load(path, log_index=1):
    # "a.BBL@0-40+a.BBL@42-64" joins segments end to end (time made continuous) to skip a hit mid-flight
    if "+" in path:
        parts = [load(p, log_index) for p in path.split("+")]
        h = parts[0][1]
        out, offset = {}, 0.0
        for d, _ in parts:
            dt = np.median(np.diff(d["time"]))
            tt = d["time"] - d["time"][0] + offset
            offset = tt[-1] + dt
            for k, v in d.items():
                out.setdefault(k, []).append(tt if k == "time" else v)
        return {k: np.concatenate(v) for k, v in out.items()}, h
    # "file.BBL@0-46" keeps only 0-46 s (e.g. cut off a crash); combine as "file.BBL#2@5-40"
    if "@" in path:
        path, span = path.rsplit("@", 1)
        t0, t1 = (float(x) for x in span.split("-"))
        d, h = load(path, log_index)
        t = (d["time"] - d["time"][0]) / 1e6
        keep = (t >= t0) & (t <= t1)
        return {k: v[keep] for k, v in d.items()}, h
    # "file.BBL#3" selects log 3 inside a multi-log file
    if "#" in path:
        path, idx = path.rsplit("#", 1)
        log_index = int(idx)
    cache = f"{os.path.splitext(path)[0]}.log{log_index}.npz"
    hcache = cache + ".headers.json"
    if os.path.exists(cache) and os.path.getmtime(cache) > os.path.getmtime(path):
        z = np.load(cache)
        with open(hcache) as f:
            headers = json.load(f)
        return {k: z[k] for k in z.files}, headers

    p = Parser.load(path)
    p.set_log_index(log_index)
    names = p.field_names
    rows = []
    try:
        for fr in p.frames():
            rows.append(fr.data)
    except Exception as e:  # truncated log (flash full / power cut): keep what parsed
        print(f"warning: log {log_index} truncated after {len(rows)} frames ({type(e).__name__})", file=sys.stderr)
    n = len(names)
    rows = [r for r in rows if len(r) >= n]
    def num(v):
        try:
            return float(v)
        except (TypeError, ValueError):
            return np.nan

    arr = np.array([[num(v) for v in r[:n]] for r in rows], dtype=np.float64)
    d = {name: arr[:, i] for i, name in enumerate(names)}
    headers = {k: v for k, v in p.headers.items()}
    np.savez_compressed(cache, **d)
    with open(hcache, "w") as f:
        json.dump(headers, f, default=str, indent=1)
    return d, headers


if __name__ == "__main__":
    d, h = load(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 1)
    t = (d["time"] - d["time"][0]) / 1e6
    print(f"frames={len(t)} duration={t[-1]:.1f}s rate={len(t)/t[-1]:.0f}Hz")
