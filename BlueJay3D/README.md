# BlueJay3D

**Bluejay 8-bit ESC firmware with AM32 & ESCape32 improvements for 3D (reversible-motor) flight.**
Tic-tocks, punch-outs from reversals, and flips through center stick reverse cleanly without the desyncs, 100 ms motor drop-outs, or center-stick stutters of stock 8-bit firmware.

> **Status: `v0.22.0-3D` (test firmware).** Built on Bluejay `v0.21.0` with **9 compounding 3D commutation, active braking, DShot, and telemetry fixes** backported from 32-bit **AM32** and **ESCape32**, plus **7 tunable 3D EEPROM settings**.
> Firmware is ready to flash for **[63 ESC target layouts / 135 files](TARGETS.md)** (`EFM8BB1`, `EFM8BB2`, and `EFM8BB51` across 24, 48, and 96 kHz).
> Verified via 8051 machine-code Hardware-in-the-Loop (HIL) emulation and binary test suites. We need flight logs from more 3D pilots and quads — pair it with **[BetaFlight 3D Edition](../BetaFlight%203D%20Edition/)** or stock Betaflight!

> **New in `v0.22.0-3D`:** the recommended 3D settings are baked in as factory defaults, plus the standalone **[Bluejay3D Configurator](configurator/)** (works online via WebSerial 4-way passthrough or offline with `.hex` / `.bin` files) and the **[Pre-Flight Bench Verification Suite](tools/bench_verify.py)**.

## Start here

1. **[Find your ESC's firmware (`TARGETS.md`)](TARGETS.md)** (63 ESC layouts / 135 `.hex` builds across 24, 48, and 96 kHz)
2. **[Follow the pilot testing guide (`TESTING_GUIDE.md`)](TESTING_GUIDE.md)**: 2-minute props-off bench check, then 4 packs with one settings change in the middle (Block A vs Block B)
3. **[Upload your logs (Google Form)](https://forms.gle/Vfq3c2W7Lp5FE36t5)** *(or attach to a [GitHub Log Issue](https://github.com/BlindingBright/Drones/issues/new?template=bluejay3d_log_upload.yml))*

## Downloads

| | File | |
|---|---|---|
| **Firmware: `O_H_5` (48 kHz)** *(BetaFPV, CrazyBee F4, Mobula6/7, Meteor65/75)* | `O_H_5_48_v0.22.0-3D.hex` | **[⬇ 48 kHz](firmware/hex/O_H_5_48_v0.22.0-3D.hex)** · [⬇ 24 kHz](firmware/hex/O_H_5_24_v0.22.0-3D.hex) · [⬇ 96 kHz](firmware/hex/O_H_5_96_v0.22.0-3D.hex) |
| **Firmware: `Z_H_30` (48 kHz)** *(HGLRC Zeus, Flywoo Goku, GEPRC Taker 8-bit)* | `Z_H_30_48_v0.22.0-3D.hex` | **[⬇ 48 kHz](firmware/hex/Z_H_30_48_v0.22.0-3D.hex)** · [⬇ 24 kHz](firmware/hex/Z_H_30_24_v0.22.0-3D.hex) · [⬇ 96 kHz](firmware/hex/Z_H_30_96_v0.22.0-3D.hex) |
| **Firmware: `A_H_5` (48 kHz)** *(EMAX Tinyhawk, Racerstar, Cicada)* | `A_H_5_48_v0.22.0-3D.hex` | **[⬇ 48 kHz](firmware/hex/A_H_5_48_v0.22.0-3D.hex)** · [⬇ 24 kHz](firmware/hex/A_H_5_24_v0.22.0-3D.hex) · [⬇ 96 kHz](firmware/hex/A_H_5_96_v0.22.0-3D.hex) |
| **Firmware: `S_H_50` (48 kHz)** *(Happymodel CrazyBee V2/V3, Crux3, Bassline)* | `S_H_50_48_v0.22.0-3D.hex` | **[⬇ 48 kHz](firmware/hex/S_H_50_48_v0.22.0-3D.hex)** · [⬇ 24 kHz](firmware/hex/S_H_50_24_v0.22.0-3D.hex) · [⬇ 96 kHz](firmware/hex/S_H_50_96_v0.22.0-3D.hex) |
| **Firmware: `G_H_30` (24 kHz)** *(SpeedyBee BLS 50A/55A, Diatone Mamba BLS)* | `G_H_30_24_v0.22.0-3D.hex` | **[⬇ 24 kHz](firmware/hex/G_H_30_24_v0.22.0-3D.hex)** · [⬇ 48 kHz](firmware/hex/G_H_30_48_v0.22.0-3D.hex) · [⬇ 96 kHz](firmware/hex/G_H_30_96_v0.22.0-3D.hex) |
| **Firmware: `A_X_5` & `B_X_30`** *(EFM8BB51 newer 2024+ AIOs & 4-in-1s)* | `A_X_5_48_v0.22.0-3D.hex` | **[⬇ A_X_5 48k](firmware/hex/A_X_5_48_v0.22.0-3D.hex)** · [⬇ B_X_30 48k](firmware/hex/B_X_30_48_v0.22.0-3D.hex) · [all BB51](TARGETS.md#efm8bb51-targets-_x_) |
| **All ESC targets (63 layouts / 135 files)** | [TARGETS.md](TARGETS.md) | Board-to-target lookup table + direct `.hex` links & [SHA-256 hashes](firmware/SHA256SUMS.txt) |
| **Pilot testing guide** | [TESTING_GUIDE.md](TESTING_GUIDE.md) | **Start here** — 2-min bench check + 4-pack Block A / Block B flight test |
| **Bluejay3D Configurator** | [configurator/](configurator/) | WebSerial 4-way passthrough + offline `.hex` / `.bin` editor + 3D reversal simulator |
| **3D EEPROM Presets** | [presets/](presets/) | [`BlockA_Stock_v021_Baseline.bin`](presets/BlockA_Stock_v021_Baseline.bin) · [`BlockB_1S_2S_Whoop.bin`](presets/BlockB_1S_2S_Whoop.bin) · [`BlockB_3_4_Toothpick.bin`](presets/BlockB_3_4_Toothpick.bin) · [`BlockB_5inch_Acro.bin`](presets/BlockB_5inch_Acro.bin) |
| **Log & feedback upload** | [Google Form](https://forms.gle/Vfq3c2W7Lp5FE36t5) · [GitHub Form](https://github.com/BlindingBright/Drones/issues/new?template=bluejay3d_log_upload.yml) | Upload up to 10 `.BBL` logs at once |
| **Pre-flight bench verifier** | [`tools/bench_verify.py`](tools/bench_verify.py) | 8051 machine-code SIL emulator + automated props-off MSP motor reversal sweep |
| **Technical breakdown** | [ARCHITECTURE_AND_FIXES.md](ARCHITECTURE_AND_FIXES.md) | Deep dive into all 9 stock Bluejay 3D bugs and the AM32/ESCape32 assembly backports |
| **Source code & build guide** | [firmware/src/](firmware/src/) · [BUILD_FROM_SOURCE.md](BUILD_FROM_SOURCE.md) | Full EFM8 8051 assembly source + Python OMF-251 linker (`tools/omf2hex.py`) |

**ESC layout or board not in [the list](TARGETS.md)?** **[Request a build for your ESC / board](https://forms.gle/1p93ZjiqDp1PLWA96)** (Google Form, no sign-in needed) or **[open a Target Request issue](https://github.com/BlindingBright/Drones/issues/new?template=bluejay3d_target_request.yml)**, or contact ZoeFPV (Discord link at [zoefpv.com](https://zoefpv.com)).

*(Maintainer note: to spin up dedicated standalone Google Forms for BlueJay3D in your own Google Drive, run `python3 tools/create_bluejay3d_forms.py` or paste [`tools/create_bluejay3d_forms.gs`](tools/create_bluejay3d_forms.gs) into [script.google.com](https://script.google.com).)*

## Send logs & feedback

### 👉 [Upload your blackbox logs and report (Google Form)](https://forms.gle/Vfq3c2W7Lp5FE36t5)

You can upload up to 10 `.BBL` blackbox logs at once, along with your ESC/drone details, a screenshot of your Bluejay3D Configurator settings, and a short flight report.
Uploading files in Google Forms requires a Google sign-in. Without a Google account, you can drag-and-drop a `.zip` of your logs directly into our **[GitHub Log Upload Form](https://github.com/BlindingBright/Drones/issues/new?template=bluejay3d_log_upload.yml)**.

---

## Why stock Bluejay desyncs in 3D (and what `v0.22.0-3D` fixes)

Stock Bluejay (`v0.21.0`) was designed around unidirectional flight. When flown in 3D (`Bidirectional 3D`), **9 separate bugs compound during every direction reversal**:

| # | Stock Bluejay `v0.21.0` Bug in 3D | `BlueJay3D v0.22.0-3D` Fix (AM32 / ESCape32 Backport) |
|---|---|---|
| **1** | **Missing startup boost on 3D reversals:** `Flag_Motor_Started` is only cleared at initial power-on. Mid-air direction flips skip `Startup_Pwr` boost (`Power.asm`), starving the motor of re-acceleration torque. | Clears `Flag_Motor_Started` at zero-crossing (`Bluejay.asm` `run6_bidir`) when `3D Reversal Boost` is enabled, restoring full `Startup_Pwr` punch on every flip. |
| **2** | **Demag carryover cuts FETs after flip:** Back-EMF spikes during braking inflate `Demag_Detected_Metric`. Right after reversing, `Demag_Comp = High` triggers `All_Pwm_Fets_Off` (`Power.asm`), killing the motor mid-flip. | Resets `Demag_Detected_Metric = 0` on reversal and suppresses power-cut during `Flag_Dir_Change_Brake` and `Flag_Initial_Run_Phase`. |
| **3** | **50% low-RPM torque choke:** `set_pwm_limit_low_rpm` caps `Pwm_Limit_By_Rpm` at `#127` (`50%`) during `Flag_Initial_Run_Phase` and slews it by only `+1` per commutation. | Unlocks 100% (`#255`) initial-phase torque ceiling and 1:1 fast throttle tracking (`Pwm_Limit = Pwm_Limit_By_Rpm`) in 3D mode. |
| **4** | **Weak (~2%) & overwritten direction-change braking:** `Pwm_Limit` is set to `Pgm_Startup_Pwr` (~2%) during braking, immediately overwritten by `set_pwm_limit_low_rpm`, and locked into 6 forced braking steps even at low RPM. | Programmable **AM32-style proportional reversal braking** (`Pwm_3D_Brake_Limit` up to `47%` + `9.4%` active floor), locked across all 6 commutation steps, with **0-step instant flip** below the handover eRPM and **mid-brake reversal cancellation**. |
| **5** | **DShot `0` (center stick) corrupts direction:** DShot `0` falls through `t1_int_normal_range` (`Isrs.asm`), wrapping `A - 48` and overwriting `Flag_Rcp_Dir_Rev` at stick center. | Explicit `jz t1_int_dshot_zero` branch in Timer 1 ISR: sets `Rcp_Stop` cleanly and preserves `Flag_Rcp_Dir_Rev` (stick hysteresis). |
| **6** | **DShot `48` & `1048` deadband traps:** Exact boundary frames (`48` with `tlm=0` and `1048` with `tlm=0`) evaluate `Rcp_Timeout_Cntd` to `0`, triggering `Flag_Rcp_Stop = 1` at the edge of the 3D deadband. | Forces `Rcp_Timeout_Cntd >= 1` for all non-zero DShot frames (`48..2047`) and enforces a **programmable 3D Minimum Duty Floor** (`Pwm_3D_Min_Duty`, default `2.4%–3.1%`) so the BEMF comparator never loses lock near center stick. |
| **7** | **12–18 commutation blind-spot after flip:** `initial_run_phase` jumps to `run_to_wait_for_comm` instead of `run6_check_timeout`, making the ESC **deaf to rapid tic-tock counter-reversals** for 12–18 steps after every flip. | Routes 3D mode (`Flag_Pgm_Bidir`) through `run6_check_timeout` -> `run6_bidir` on every single commutation step. |
| **8** | **100 ms total motor shutdown on desync:** Any comparator timeout in `run6_timeout_check` turns off all FETs and calls `wait100ms` (a full tenth of a second of dead air) before retrying. | Backports **ESCape32's 1 ms fast desync recovery** (`wait1ms` + 6 fast re-sync attempts + `Demag_Detected_Metric = 0`), recovering mid-air desyncs **100× faster** before the quad can drop an arm. |
| **9** | **eRPM telemetry 8-bit overflow (+254 µs spike):** `dshot_tlm_create_packet` (`DShot.asm`) shifts `Comm_Period4x_H` left twice in an 8-bit register (`rlc A`), silently dropping bits 7 & 6 when period >= 128 µs (< 6,500 eRPM) and feeding false high-RPM spikes to Betaflight's RPM filter and `3d_iterm_release = RPM`. | Replaces lossy 8-bit shifts with a lossless **10-bit circular rotate** (`rl A / rl A` + mask) and reports clean `0x0FFF` (`0 eRPM`) during startup and direction-change braking. |

---

## New 3D EEPROM Settings (`0x1A1B–0x1A21`)

All 7 settings default to the recommended 3D values when you flash `v0.22.0-3D`. You can tune them via the **[Bluejay3D Configurator](configurator/)** or load our one-click [`.bin` presets](presets/).

| EEPROM Address | Setting | Default (Range) | What it does |
|---|---|---|---|
| `0x1A1B` | `Pgm_3D_Brake_Strength` | `8` (`1–10`, `0=Legacy`) | Maximum PWM duty applied during active direction-change braking (`12 × N` out of 255; `8 = 96/255 = 37.6%`), plus a `9.4%` active braking floor. |
| `0x1A1C` | `Pgm_3D_Brake_Speed` | `5` (`1–10`) | Zero-cross eRPM handover threshold (`Comm_Period4x_H >= N + 3`). Higher values flip direction earlier while the prop still has momentum (`7 ≈ 6.7k eRPM` for whoops; `5 ≈ 5.0k eRPM` for toothpicks; `4 ≈ 4.0k eRPM` for 5"). |
| `0x1A1D` | `Pgm_3D_Min_Duty` | `3` (`0–15`) | Minimum active PWM duty floor in 3D mode (`2 × N` out of 255; `3 = 2.35%`, `4 = 3.14%`). Prevents BEMF zero-cross dropout at the edge of the 3D deadband. |
| `0x1A1E` | `Pgm_3D_Rev_Boost` | `1` (`0=OFF, 1=ON`) | Clears `Flag_Motor_Started` on every 3D direction reversal so `Startup_Pwr` boost engages on mid-air flips. |
| `0x1A1F` | `Pgm_3D_Fast_Restart` | `1` (`0=100ms, 1=1ms`) | Replaces the stock `100 ms` desync shutdown with `1 ms` fast recovery and 6 rapid re-sync attempts. |
| `0x1A20` | `Pgm_3D_Fast_Track` | `1` (`0=OFF, 1=ON`) | Unlocks 100% (`#255`) initial-phase torque ceiling and 1:1 `Pwm_Limit` tracking after a reversal. |
| `0x1A21` | `Pgm_3D_Glitch_Filter` | `1` (`0=1, 1=2, 2=3 frames`) | Consecutive opposite-direction DShot frames required before triggering a reversal during active running. |

---

## Best settings (`v0.22.0-3D`)

### 1. ESC Settings (Bluejay3D Configurator)

| Parameter | 🐝 1S/2S 3D Whoop (`0702–1002`) | ⚡ 3"–4" Toothpick (`1204–1404`) | 🚁 5-inch 3D Acro (`2207–2306`) |
|---|---|---|---|
| **Preset file** | [`BlockB_1S_2S_Whoop.bin`](presets/BlockB_1S_2S_Whoop.bin) | [`BlockB_3_4_Toothpick.bin`](presets/BlockB_3_4_Toothpick.bin) | [`BlockB_5inch_Acro.bin`](presets/BlockB_5inch_Acro.bin) |
| **PWM Frequency** | **48 kHz** (or 96 kHz on 1S) | **48 kHz** | **24 kHz** |
| **Motor Direction** | `Bidirectional 3D` (`3`) | `Bidirectional 3D` (`3`) | `Bidirectional 3D` (`3`) |
| **Commutation Timing** | `Medium (15°)` | `Medium (15°)` | `Medium (15°)` |
| **Demag Compensation** | `High` *(safe in v0.22.0-3D!)* | `High` | `High` |
| **Startup Power (Min / Max)** | `1.25x` (`33` / `29`) | `1.125x` (`29` / `25`) | `1.00x` (`25` / `21`) |
| **3D Brake Strength** | `8` (`37.6%` cap) | `8` (`37.6%` cap) | `6` (`28.2%` cap — protects FETs) |
| **3D Brake Speed (Handover)** | `7` (`~6.7k eRPM`) | `5` (`~5.0k eRPM`) | `4` (`~4.0k eRPM`) |
| **3D Min Duty Floor** | `4` (`3.14%`) | `3` (`2.35%`) | `3` (`2.35%`) |
| **3D Rev Boost / Fast Restart / Fast Track** | `ON` / `ON (1ms)` / `ON` | `ON` / `ON (1ms)` / `ON` | `ON` / `ON (1ms)` / `ON` |
| **3D Glitch Filter** | `1` (`2 frames`) | `1` (`2 frames`) | `2` (`3 frames`) |

### 2. Flight Controller Settings (BetaFlight 3D Edition `v0.3.1` recommended)

Because BlueJay3D fixes the 8-bit eRPM telemetry overflow at low RPM and reports clean `0 eRPM` (`0x0FFF`) during reversal braking, it pairs directly with **[BetaFlight 3D Edition](../BetaFlight%203D%20Edition/)**:

```
feature 3D
set dshot_bidir = ON
set motor_poles = 12          # 12 for 0802/1103 whoops; 14 for 2207/2306 5-inch
set 3d_deadband_low = 1496
set 3d_deadband_high = 1504
set 3d_neutral = 1500
set 3d_iterm_mode = PER_DIRECTION
set 3d_iterm_release = RPM
set 3d_anti_gravity = GATED
set 3d_ag_approach_pct = 15
set 3d_dyn_idle = ON
profile 0
set dyn_idle_min_rpm = 50     # 50 on 1S/2S whoops; 30 on 5-inch
set dyn_idle_max_increase = 100
save
```

---

## Pre-flight verification (test before putting props on)

Every `.hex` binary in this repository has passed:
1. **Static Binary & EEPROM Verification (`tests/test_bluejay3d_suite.py`)**: 6/6 checks confirming bootloader preservation (`0x1C00`), code ceiling safety (`< 0x19FE`), and EEPROM layout (`0x1A00–0x1A21`).
2. **Cycle-Accurate 8051 Machine-Code Emulation (`tests/emu8051_hil_verify.py`)**: Executes the actual compiled `.hex` machine code on a virtual Silicon Labs EFM8 8051 CPU, verifying Timer 1 ISR DShot `0`/`48`/`1048` decoding, `compute_rcp_pwm_limit` 3D min-duty floor & 1:1 tracking, and lossless 10-bit eRPM GCR telemetry encoding.
3. **Props-Off MSP Bench Sweep (`tools/bench_verify.py`)**: Run `python3 tools/bench_verify.py --port /dev/ttyACM0` with props off to execute 20 automated forward↔reverse motor flips over Betaflight USB MSP and verify `< 120 ms` reversal time and `0` desyncs before flying.

---

## Credits and license

BlueJay3D is a 3D-focused fork of **[Bluejay](https://github.com/mathiasvr/bluejay)** by Mathias Rasmussen (`mathiasvr`) and **BLHeli_S** by Steffen Skaug (`4712`), with 3D commutation, proportional braking, and fast recovery techniques backported from **[AM32](https://github.com/AlkaMotors/AM32)** by AlkaMotors and **[ESCape32](https://github.com/neoxic/ESCape32)** by Arseniy (`neoxic`).
Like Bluejay, the firmware and its source code are licensed under **GPL-3.0** ([`firmware/COPYING`](firmware/COPYING)).
Developed for **ZoeFPV**'s "[Lil Horny](../Lil%20Horny/)" and "[BetaFlight 3D Edition](../BetaFlight%203D%20Edition/)".
