"""Print every header (config) of each log in a .BBL file plus field names.

usage: python tools/bbl_headers.py "file.BBL"      (all logs)
       python tools/bbl_headers.py "file.BBL#3"    (just log 3)
"""
import sys

from orangebox import Parser

path = sys.argv[1]
only = None
if "#" in path:
    path, only = path.rsplit("#", 1)
    only = int(only)
p = Parser.load(path)
print("log count:", p.reader.log_count)
for i in range(1, p.reader.log_count + 1):
    if only and i != only:
        continue
    p.set_log_index(i)
    print(f"\n===== LOG {i} =====")
    for k, v in p.headers.items():
        print(f"{k}: {v}")
    print("FIELDS:", p.field_names)
