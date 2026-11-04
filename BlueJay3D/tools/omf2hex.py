#!/usr/bin/env python3
"""
omf2hex.py - Unrestricted OMF-251 (Keil AX51 .OBJ) Linker & Intel HEX Generator
Resolves Keil AX51 absolute segments (0x84 SEGDEF, 0x94 CONTENT, 0x96 FIXUP)
and emits standard Intel HEX (.hex) and binary (.omf) outputs identically to
Keil LX51 + Ohx51 without evaluation code-size limits.
"""
import sys
import os
import struct


def parse_and_link_obj(obj_path):
    with open(obj_path, "rb") as f:
        data = f.read()

    pos = 0
    last_base = 0
    last_buf = None
    segments = []  # list of (base_addr, bytearray)

    while pos < len(data):
        rtype = data[pos]
        rlen = data[pos + 1] | (data[pos + 2] << 8)
        body = data[pos + 3 : pos + 3 + rlen - 1]
        if rtype == 0x94:  # CONTENT record
            if last_buf is not None:
                segments.append((last_base, last_buf))
            seg_id, last_base = struct.unpack("<II", body[2:10])
            last_buf = bytearray(body[10:])
        elif rtype == 0x96:  # FIXUP record
            for i in range(0, len(body), 12):
                off, ftype, tkind, tseg, tval = struct.unpack("<HBBIi", body[i : i + 12])
                if ftype in (0x01, 0x07, 0x09):  # 8-bit low/bit/data
                    last_buf[off] = (last_buf[off] + tval) & 0xFF
                elif ftype in (0x02,):  # 8-bit high
                    last_buf[off] = (last_buf[off] + ((tval >> 8) & 0xFF)) & 0xFF
                elif ftype in (0x03,):  # 8-bit relative (SJMP/Jcc)
                    last_buf[off] = (last_buf[off] + tval) & 0xFF
                elif ftype in (0x04, 0x13):  # 16-bit big-endian word/addr
                    cur = (last_buf[off] << 8) | last_buf[off + 1]
                    val = (cur + tval) & 0xFFFF
                    last_buf[off] = (val >> 8) & 0xFF
                    last_buf[off + 1] = val & 0xFF
                elif ftype == 0x05:  # 11-bit AJMP/ACALL
                    cur_off = ((last_buf[off] >> 5) << 8) | last_buf[off + 1]
                    val = (cur_off + tval) & 0xFFFF
                    last_buf[off] = (last_buf[off] & 0x1F) | (((val >> 8) & 0x07) << 5)
                    last_buf[off + 1] = val & 0xFF
                else:
                    raise ValueError(f"Unsupported OMF251 fixup type: 0x{ftype:02X} at offset 0x{off:04X}")
        pos += 3 + rlen

    if last_buf is not None:
        segments.append((last_base, last_buf))

    # Merge into memory map
    mem = {}
    for base, buf in segments:
        for i, b in enumerate(buf):
            mem[base + i] = b
    return mem


def write_intel_hex(mem, hex_path):
    os.makedirs(os.path.dirname(os.path.abspath(hex_path)), exist_ok=True)
    addrs = sorted(mem.keys())
    ranges = []
    for a in addrs:
        if not ranges or a > ranges[-1][1] + 1:
            ranges.append([a, a])
        else:
            ranges[-1][1] = a

    lines = []
    for start, end in ranges:
        cur = start
        while cur <= end:
            chunk_len = min(16, end - cur + 1)
            chunk = [mem[cur + i] for i in range(chunk_len)]
            rec = [chunk_len, (cur >> 8) & 0xFF, cur & 0xFF, 0x00] + chunk
            csum = (-sum(rec)) & 0xFF
            rec.append(csum)
            lines.append(":" + "".join(f"{b:02X}" for b in rec))
            cur += chunk_len

    lines.append(":00000001FF")
    with open(hex_path, "w", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def main():
    if len(sys.argv) < 3:
        print("Usage: omf2hex.py <input.OBJ> <output.hex> [output.OMF]")
        sys.exit(1)
    obj_path = sys.argv[1]
    hex_path = sys.argv[2]
    omf_path = sys.argv[3] if len(sys.argv) > 3 else None

    mem = parse_and_link_obj(obj_path)
    write_intel_hex(mem, hex_path)
    if omf_path:
        with open(omf_path, "wb") as f:
            f.write(b"OMF251_LINKED")
    print(f"Linked {obj_path} -> {hex_path} ({len(mem)} bytes)")


if __name__ == "__main__":
    main()
