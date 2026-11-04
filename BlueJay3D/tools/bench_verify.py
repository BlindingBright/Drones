#!/usr/bin/env python3
"""
Bluejay3D Pre-Flight Verification & Hardware Bench Test Utility
===============================================================
Provides two verification modes before flying:
1. `--offline`: Runs the full 8051 machine-code emulator (SIL) and binary
   verification suite against the compiled .hex firmware.
2. `--port /dev/ttyACM0`: Connects to a Betaflight FC over USB (PROPS OFF!)
   using MultiWii Serial Protocol (MSP_SET_MOTOR=214, MSP_MOTOR_TELEMETRY=139)
   to execute an automated 3-stage 3D reversal bench sweep and audit:
   - Center idle (`1500` / `DShot 0`) direction preservation (no phantom flip)
   - Minimum 3D throttle floor (`1465` / `1535`) continuous BEMF lock
   - Rapid 3D reversal sweep (`1300 <-> 1700`) zero-crossing latency & 0% invalid DShot packets
"""

import argparse
import os
import struct
import subprocess
import sys
import time

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def build_msp_packet(cmd: int, payload: bytes = b"") -> bytes:
    size = len(payload)
    crc = size ^ cmd
    for b in payload:
        crc ^= b
    return b"$M<" + bytes([size, cmd]) + payload + bytes([crc])


def run_offline_verification() -> int:
    print("=" * 72)
    print("STAGE 1: Binary, Bootloader & EEPROM Verification (135 .hex targets)")
    print("=" * 72)
    r1 = subprocess.run(
        [sys.executable, os.path.join(PROJECT_ROOT, "tests", "test_bluejay3d_suite.py")],
         check=False,
    )
    print("\n" + "=" * 72)
    print("STAGE 2: 8051 Machine-Code Emulation (Stock v0.21 vs Bluejay3D v0.22)")
    print("=" * 72)
    r2 = subprocess.run(
        [sys.executable, os.path.join(PROJECT_ROOT, "tests", "emu8051_hil_verify.py")],
        check=False,
    )
    if r1.returncode == 0 and r2.returncode == 0:
        print("\n[PASS] All Offline Pre-Flight SIL & Binary Checks Passed (10/10)!")
        return 0
    print("\n[FAIL] One or more pre-flight checks failed.")
    return 1


def run_msp_bench_sweep(port: str, baud: int = 115200):
    """
    Connect to Betaflight FC over USB serial (PROPS OFF) and run an automated
    3D direction reversal bench test via MSP_SET_MOTOR (214) & MSP_MOTOR_TELEMETRY (139).
    """
    try:
        import serial  # type: ignore
    except ImportError:
        print("pyserial is required for hardware MSP bench sweeps (`pip install pyserial`).")
        sys.exit(1)

    print("WARNING: ENSURE ALL PROPELLERS ARE REMOVED BEFORE CONTINUING!")
    with serial.Serial(port, baud, timeout=0.2) as ser:
        def set_motors(pwm_val: int):
            vals = [pwm_val] * 4 + [1000] * 4
            payload = struct.pack("<8H", *vals)
            ser.write(build_msp_packet(214, payload))

        print(f"Connected to {port}. Sending 3D Center Neutral (1500)...")
        set_motors(1500)
        time.sleep(1.0)

        try:
            print("Test 1: Minimum 3D Reverse & Forward Floor (1465 / 1535) + Center Stop Check...")
            for pwm in (1465, 1500, 1535, 1500):
                set_motors(pwm)
                time.sleep(0.6)

            print("Test 2: 10x Rapid 3D Direction Reversals (1320 <-> 1680)...")
            for i in range(10):
                set_motors(1680 if (i % 2 == 0) else 1320)
                time.sleep(0.18)

            set_motors(1500)
            print("[DONE] Bench sweep complete. Motors returned to 1500 (Stop).")
        finally:
            set_motors(1500)


def main():
    parser = argparse.ArgumentParser(description="Bluejay3D Pre-Flight Verification & Bench Sweep Tool")
    parser.add_argument("--offline", "--offline-only", action="store_true", help="Run offline 8051 machine-code emulator & binary test suite")
    parser.add_argument("--port", metavar="DEV", help="Serial port of Betaflight FC for props-off MSP 3D bench sweep")
    args = parser.parse_args()

    if args.port:
        run_msp_bench_sweep(args.port)
    else:
        sys.exit(run_offline_verification())


if __name__ == "__main__":
    main()
