# Building BlueJay3D from Source

The complete source code for **BlueJay3D (`v0.22.0-3D`)** is located right here in **[`firmware/`](firmware/)**, based on **[Bluejay `v0.21.0`](https://github.com/mathiasvr/bluejay)** with 9 backported AM32/ESCape32 3D commutation, active braking, DShot, and telemetry improvements.

## Download the code

```bash
git clone -b bluejay3d https://github.com/BlindingBright/Drones.git
cd "Drones/BlueJay3D/firmware"
```

## Build (Linux, macOS, or WSL)

BlueJay3D uses the Keil `AX51.exe` macro assembler (run via `wine`) paired with our standalone, dependency-free Python OMF-251 absolute linker and Intel HEX generator (**[`tools/omf2hex.py`](tools/omf2hex.py)**), which avoids Keil `LX51` evaluation size limits on 8-bit targets.

### 1. Build a single ESC target

Specify `LAYOUT` (`A`–`Z`), `MCU` (`H` for `EFM8BB21`, `X` for `EFM8BB51`), `DEADTIME` (`0`–`120`), and `PWM` (`24`, `48`, or `96`):

```bash
cd "BlueJay3D/firmware"
make LAYOUT=O MCU=H DEADTIME=5 PWM=48 single_target
```

The compiled firmware is written to `build/hex/O_H_5_48_v0.22.0-3D.hex`.

### 2. Build the popular 3D target suite

```bash
make popular_3d
```

### 3. Build all 800+ combinations

```bash
make all
```

## Run the Pre-Flight Verification & Emulation Suites

Before flashing or releasing any build, run the automated test suites from the `BlueJay3D/` directory:

```bash
cd "BlueJay3D"

# 1. Static Binary & EEPROM Integrity Suite (6/6 checks)
python3 tests/test_bluejay3d_suite.py

# 2. Cycle-Accurate 8051 Machine-Code Emulation Suite (4/4 HIL tests)
python3 tests/emu8051_hil_verify.py

# 3. Combined Offline + Optional Live MSP Props-Off Bench Verifier
python3 tools/bench_verify.py --offline-only
```

## Key Source Files Modified in `v0.22.0-3D`

| File | Summary of `v0.22.0-3D` Changes |
|---|---|
| [`firmware/src/Settings/BluejaySettings.asm`](firmware/src/Settings/BluejaySettings.asm) | Bumps `EEPROM_LAYOUT_REVISION` to `208` (`v0.22.0-3D`), sets `DEFAULT_PGM_DIRECTION = 3` (Bidirectional 3D), and defines defaults for all 7 new 3D parameters (`0x1A1B–0x1A21`). |
| [`firmware/src/Modules/Common.asm`](firmware/src/Modules/Common.asm) | Allocates bit-addressable 3D control flags (`Flags3`, `Flags_3D`) and direct RAM variables (`Pwm_3D_Brake_Limit`, `Pwm_3D_Brake_Floor`, `Pwm_3D_Min_Duty`, `Brake_Speed_Threshold`, `Rcp_Dir_Change_Filter_Cnt`). |
| [`firmware/src/Modules/Settings.asm`](firmware/src/Modules/Settings.asm) | Decodes EEPROM parameters `Pgm_3D_Brake_Strength` .. `Pgm_3D_Glitch_Filter` at boot into fast register/RAM lookup values. |
| [`firmware/src/Bluejay.asm`](firmware/src/Bluejay.asm) | Implements AM32/ESCape32 proportional reversal braking, 0-step low-RPM changeover, mid-brake reversal cancellation, `Flag_Motor_Started` reversal boost reset, `Demag_Detected_Metric` reset, 1:1 `initial_run_phase` routing, and 1 ms (`wait1ms`) fast desync recovery. |
| [`firmware/src/Modules/Power.asm`](firmware/src/Modules/Power.asm) | Suppresses post-reversal demag FET cutoffs (`All_Pwm_Fets_Off`), removes the 50% (`#127`) initial-phase torque choke in 3D mode, locks braking duty across all 6 commutation steps, and enforces `Pwm_3D_Min_Duty` near center stick. |
| [`firmware/src/Modules/Isrs.asm`](firmware/src/Modules/Isrs.asm) | Fixes Timer 1 ISR DShot `0` direction corruption, fixes DShot `48` & `1048` (`tlm=0`) deadband stop traps, and adds multi-frame direction glitch filtering. |
| [`firmware/src/Modules/DShot.asm`](firmware/src/Modules/DShot.asm) | Fixes the 8-bit overflow (+254 µs jump) in `dshot_tlm_create_packet` using a 10-bit circular rotate (`rl A / rl A`) and reports `0x0FFF` (`0 eRPM`) during startup and direction-change braking. |

## Sharing a build or requesting a target

If you build and fly another target, please upload your logs through the **[log upload form](https://docs.google.com/forms/d/e/1FAIpQLSfmN5fuS82CXPKGCXlqQAUPCoa6tT8LgZesW7zxZt6WFHSnpw/viewform)** *(or [GitHub Log Upload Form](https://github.com/BlindingBright/Drones/issues/new?template=bluejay3d_log_upload.yml))*.
Need a target built for you? **[Request a build here](https://docs.google.com/forms/d/e/1FAIpQLSegPRjFi6s6WUmWW0QfRsDMLYOeNchlNj9iVQxU-3Z2g0Upxw/viewform)** *(or via [GitHub Target Request](https://github.com/BlindingBright/Drones/issues/new?template=bluejay3d_target_request.yml))*.
