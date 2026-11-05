# Building BetaFlight 3D Edition from source

The code lives in the Betaflight fork **[BlindingBright/betaflight](https://github.com/BlindingBright/betaflight)**:

| Version | Branch | Base | Release commit |
|---|---|---|---|
| **v0.3.2-test** (current) | **`3d-v0.3.2`** | Betaflight **2026.6.2** (`e0b7bb01b`) | `ea347bdd5` (tag `v0.3.2-3d-test`) |
| v0.3.1-test (flown, 4.5 fallback) | `3d-iterm-memory` | Betaflight 4.5.1 (`77d01ba3b`) | `161e867a9` (tag `v0.3.1-3d-test`) |

## Download the code

| What | Link |
|---|---|
| Exact source of the v0.3.2-test release (zip) | <https://github.com/BlindingBright/betaflight/archive/refs/tags/v0.3.2-3d-test.zip> |
| Same, tar.gz | <https://github.com/BlindingBright/betaflight/archive/refs/tags/v0.3.2-3d-test.tar.gz> |
| v0.3.1-test source (4.5.1) | <https://github.com/BlindingBright/betaflight/archive/refs/tags/v0.3.1-3d-test.zip> |
| Browse the code | <https://github.com/BlindingBright/betaflight/tree/3d-v0.3.2> |
| Just the changes vs Betaflight 2026.6.2 | <https://github.com/BlindingBright/betaflight/compare/2026.6.2...3d-v0.3.2> |

Or with git:
```bash
git clone -b 3d-v0.3.2 https://github.com/BlindingBright/betaflight.git
cd betaflight
```

## Build v0.3.2 (Linux, macOS, or Windows with WSL)

Board configs are the **config** submodule (`src/config`), pinned at `3a406c5`, the revision Betaflight 2026.6.2 uses:

```bash
git submodule update --init src/config   # or: make configs
make arm_sdk_install                     # downloads the pinned compiler into ./tools
make CONFIG=TBS_LUCID_AIO                # or CONFIG=<your board>
```

The firmware lands in `obj/betaflight_2026.6.2_<MCU>_<BOARD>.hex`. Flash it with Betaflight Configurator →
Firmware Flasher → **Load Firmware [Local]**.

Notes from building it:
- Board configs are grouped by manufacturer: `ls src/config/configs/*/` (e.g. `configs/TEBS/TBS_LUCID_AIO`).
- Commit your changes before building a test binary and run `touch src/main/build/version.c` afterwards. Otherwise the
  firmware reports `norevision` instead of the commit hash, and logs can't be traced to a build.

## Run the unit tests

```bash
make CC=gcc CXX=g++ test_mixer_3d_unittest test_rc_3d_unittest test_pid_unittest
```
v0.3.2: mixer 30, rc_3d 4, PID 17 tests pass; the full suite (`make CC=gcc CXX=g++ test`) runs 62 binaries / 510 tests. Seven
flight-plan tests (`flight_plan_*`, `flight_failsafe*`, `osd_nav_map`, `telemetry_mavlink_mission`) don't compile with gcc's C++
front end on stock 2026.6.2 either (`_Static_assert` in `pg/flight_plan.h`).

## Build v0.3.1 (Betaflight 4.5.1)

```bash
git clone -b 3d-iterm-memory https://github.com/BlindingBright/betaflight.git && cd betaflight
git clone -b 4.5-config https://github.com/betaflight/config.git src/config
git -C src/config checkout 283a21f
make arm_sdk_install && make CONFIG=TBS_LUCID_AIO        # obj/betaflight_4.5.1_<MCU>_<BOARD>.hex
```
4.5's test harness only accepts clang 7–16; with a newer clang, build the tests with gcc (`make CC=gcc CXX=g++ ...`).

## Sharing a build

If you build for another board and fly it, please send the logs through the
[log form](README.md#send-logs--feedback) and say which board and commit you built. Builds for other boards can also be
[requested with the build request form](https://forms.gle/1p93ZjiqDp1PLWA96) or from ZoeFPV (Discord link at [zoefpv.com](https://zoefpv.com)).

## Targets not in the official config repo

- **`FRACSP8AIO`** (Fractal Engineering SP8), from Fractal's target definition (FractalEngineer/config, branch `SP8-AIO`):
  - v0.3.2 / 2026.6: copy [targets/FRACSP8AIO/2026.6/config.h](targets/FRACSP8AIO/2026.6/config.h) (unchanged) to
    `src/config/configs/FRAC/FRACSP8AIO/config.h`, then `make CONFIG=FRACSP8AIO`.
  - v0.3.1 / 4.5: [targets/FRACSP8AIO/4.5/config.h](targets/FRACSP8AIO/4.5/config.h) to `src/config/configs/FRACSP8AIO/`
    (one change for 4.5: `SERIAL_PORT_UART1` → `SERIAL_PORT_USART1`).
