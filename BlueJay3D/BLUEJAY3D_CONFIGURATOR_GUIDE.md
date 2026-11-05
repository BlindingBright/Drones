# Bluejay3D Configurator Local Launcher & Guide

A standalone local WebSerial 4-way configurator, patcher, and flashing tool for **Bluejay3D v0.22.0-3D** (EFM8BB1, BB21, and BB51 ESCs).

---

## 🚀 Quick Launch (One-Click)

### Linux / macOS
```bash
# In the terminal (or double-click run_bluejay3d_configurator.sh):
./run_bluejay3d_configurator.sh
```
*(On Linux desktops, you can also use `Bluejay3D_Configurator.desktop` to launch from your application menu).*

### Windows
```cmd
# Double-click or run:
run_bluejay3d_configurator.bat
```

The launcher will:
1. Scan for connected flight controllers (`/dev/ttyACM*`, `/dev/ttyUSB*`, or Windows `COM*`).
2. Warn if another process has the serial port locked.
3. Automatically find an available local port (default `8088`).
4. Start the local backend server.
5. Automatically open Chrome, Brave, Edge, or Chromium to `http://127.0.0.1:8088/`.

---

## 🔌 Connecting & Disconnecting

### 1. Connecting
1. **Remove all propellers from the drone** (bench safety).
2. Connect your drone via USB, and plug in a LiPo battery (ESCs need battery power to respond over 4-way passthrough).
3. In the top right corner of the Configurator, click **`🔌 Connect ESC (WebSerial 4-Way)`**.
4. In the browser dialog, pick your flight controller USB CDC port (e.g., `Betaflight FC` / `/dev/ttyACM1`).
5. Click **Read ESCs** to read back all 4 ESCs' layouts, firmware revisions, and 3D parameters.

### 2. Disconnecting (Port Release)
When you are done flashing or editing ESC settings:
* Click the red **`🚫 Disconnect`** button in the top navigation bar (or inside the ESC status panel).
* **What this does:**
  - Sends the clean 4-Way Interface Exit command (`0x34`) to the flight controller so Betaflight returns to normal MSP mode.
  - Closes the WebSerial port in the browser and releases the OS device lock.
  - Prevents "Device or resource busy" errors when switching over to Betaflight Configurator or running the automated motor test harness.

*(If you physically unplug the USB cable while connected, the configurator detects it and automatically resets to the disconnected state).*

---

## 🛠️ Key Capabilities

- **3D Backported Parameters (AM32 / ESCape32 parity)**:
  - 3D Braking Strength (`0x11`)
  - 3D Braking Speed / Decel Ramp (`0x12`)
  - 3D Minimum Duty Cycle floor (`0x13`)
  - 3D Reversal Boost kick (`0x14`)
  - Fast Restart Commutation Lock (`0x16`)
  - Fast Angle Tracking (`0x17`)
  - Zero-Cross Glitch Filter (`0x18`)
- **Built-in Target Library**: Access all pre-compiled Bluejay3D v0.22.0-3D hex files (`A_H_0` through `Z_H_30`, 24k, 48k, and 96k PWM).
- **Offline / Simulation Mode**: Load existing `.hex` or `.bin` dumps, simulate 3D reversals, and export patched hex files without needing a drone plugged in.
