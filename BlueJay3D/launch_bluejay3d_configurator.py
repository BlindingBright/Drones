#!/usr/bin/env python3
"""Launch Wrapper for Bluejay3D Web Configurator.

Provides:
- Auto-detection of available HTTP port (default 8088).
- USB serial port scan (/dev/ttyACM*, /dev/ttyUSB*, COM ports) & lock checking.
- Auto-opening in a WebSerial-capable Chromium browser (Chrome, Brave, Edge, Chromium).
- Self-contained server management with graceful Ctrl+C shutdown.
"""

import glob
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import webbrowser
from urllib.request import urlopen

# Determine Configurator Directory dynamically
_cur = os.path.abspath(os.path.dirname(__file__))
if os.path.isdir(os.path.join(_cur, "configurator")):
    CONFIGURATOR_DIR = os.path.join(_cur, "configurator")
elif os.path.isdir(os.path.join(_cur, "Bluejay3D", "configurator")):
    CONFIGURATOR_DIR = os.path.join(_cur, "Bluejay3D", "configurator")
elif os.path.isdir(os.path.join(_cur, "BlueJay3D", "configurator")):
    CONFIGURATOR_DIR = os.path.join(_cur, "BlueJay3D", "configurator")
else:
    CONFIGURATOR_DIR = os.path.join(_cur, "Drones", "BlueJay3D", "configurator")


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) == 0


def find_available_port(start_port: int = 8088) -> int:
    for port in range(start_port, start_port + 20):
        if not is_port_in_use(port):
            return port
    return start_port


def is_bluejay3d_server(port: int) -> bool:
    try:
        url = f"http://127.0.0.1:{port}/api/targets"
        with urlopen(url, timeout=1.0) as resp:
            return resp.status == 200
    except Exception:
        return False


def get_connected_serial_devices():
    devices = []
    if sys.platform.startswith("linux") or sys.platform == "darwin":
        ports = sorted(glob.glob("/dev/ttyACM*") + glob.glob("/dev/ttyUSB*"))
        for p in ports:
            holder = None
            try:
                res = subprocess.run(["lsof", p], capture_output=True, text=True, check=False)
                if res.returncode == 0 and res.stdout.strip():
                    lines = res.stdout.strip().splitlines()
                    if len(lines) > 1:
                        holder = lines[1].split()[0]
            except Exception:
                pass
            devices.append({"port": p, "holder": holder})
    elif sys.platform == "win32":
        try:
            import serial.tools.list_ports
            for p in serial.tools.list_ports.comports():
                devices.append({"port": p.device, "holder": None})
        except ImportError:
            pass
    return devices


def open_browser(url: str):
    """Attempt to open in a WebSerial-compatible browser (Chrome, Brave, Edge, Chromium)."""
    # Priority list of Chromium executables
    candidates = [
        "google-chrome",
        "google-chrome-stable",
        "brave",
        "brave-browser",
        "/opt/brave-bin/brave",
        "microsoft-edge",
        "microsoft-edge-stable",
        "chromium",
        "chromium-browser"
    ]

    for cand in candidates:
        exe = shutil.which(cand) or (cand if os.path.isfile(cand) and os.access(cand, os.X_OK) else None)
        if exe:
            try:
                subprocess.Popen([exe, url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception:
                pass

    # Generic fallback
    try:
        webbrowser.open(url)
        return True
    except Exception:
        return False


def main():
    print("=" * 72)
    print("           BLUEJAY3D CONFIGURATOR LOCAL LAUNCHER")
    print("=" * 72)

    # Check for connected quad
    serial_devs = get_connected_serial_devices()
    if serial_devs:
        print("\n[USB SERIAL SCAN]")
        for dev in serial_devs:
            if dev["holder"]:
                print(f"  • {dev['port']} -> In use by process: {dev['holder']} (Click Disconnect in that app first)")
            else:
                print(f"  • {dev['port']} -> Ready to connect (Available)")
        print("  💡 Tip: Verify all propellers are REMOVED before flashing or spinning motors.")
    else:
        print("\n[USB SERIAL SCAN] No Flight Controller USB ports detected currently.")
        print("  Plug in your drone via USB anytime while the Configurator is open.")

    target_port = 8088
    if is_port_in_use(target_port):
        if is_bluejay3d_server(target_port):
            print(f"\n[INFO] Bluejay3D Configurator is already running at http://127.0.0.1:{target_port}/")
            open_browser(f"http://127.0.0.1:{target_port}/")
            print("Opened in browser. Exiting launcher.")
            return
        else:
            target_port = find_available_port(8089)

    url = f"http://127.0.0.1:{target_port}/"
    print(f"\n[SERVER START] Starting Bluejay3D Configurator on {url}...")

    # Start server in thread or subprocess
    server_script = os.path.join(CONFIGURATOR_DIR, "server.py")
    server_proc = subprocess.Popen(
        [sys.executable, server_script, "--serve", "--port", str(target_port)],
        cwd=CONFIGURATOR_DIR
    )

    # Wait for server to respond
    for _ in range(30):
        if is_port_in_use(target_port):
            break
        time.sleep(0.1)

    print(f"  ✓ Web Server active at: {url}")
    print("  ✓ Opening WebSerial-capable browser...")
    open_browser(url)

    print("\n" + "-" * 72)
    print("  HOW TO USE:")
    print("  1. In the browser, click '🔌 Connect ESC (WebSerial 4-Way)'.")
    print("  2. Select your drone's USB serial port (e.g. /dev/ttyACM1 or COMx).")
    print("  3. Read, tune 3D parameters, or flash Bluejay3D v0.22.0-3D hex files.")
    print("  4. When finished, CLICK THE NEW '🚫 Disconnect' BUTTON to cleanly")
    print("     release the serial port for Betaflight or other test harnesses!")
    print("-" * 72)
    print("\n[SERVER RUNNING] Press Ctrl+C in this terminal to shut down the server.\n")

    try:
        server_proc.wait()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Stopping Bluejay3D Configurator server...")
        server_proc.terminate()
        try:
            server_proc.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            server_proc.kill()
        print("Server stopped cleanly. Goodbye!")


if __name__ == "__main__":
    main()
