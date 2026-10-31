# Building BetaFlight 3D Edition from source

The code lives in the Betaflight fork **[BlindingBright/betaflight](https://github.com/BlindingBright/betaflight)**,
branch **`3d-iterm-memory`**, based on Betaflight **4.5.1** (`77d01ba3b`). The v0.2.2-test release is commit `b5fa258ef`
(tag `v0.2.2-3d-test`).

## Download the code

| What | Link |
|---|---|
| Exact source of the v0.2.2-test release (zip) | <https://github.com/BlindingBright/betaflight/archive/refs/tags/v0.2.2-3d-test.zip> |
| Same, tar.gz | <https://github.com/BlindingBright/betaflight/archive/refs/tags/v0.2.2-3d-test.tar.gz> |
| Older v0.1.0-test source | <https://github.com/BlindingBright/betaflight/archive/refs/tags/v0.1.0-3d-test.zip> |
| Latest development branch (zip) | <https://github.com/BlindingBright/betaflight/archive/refs/heads/3d-iterm-memory.zip> |
| Browse the code | <https://github.com/BlindingBright/betaflight/tree/3d-iterm-memory> |
| Just the changes vs Betaflight 4.5.1 | <https://github.com/BlindingBright/betaflight/compare/77d01ba3b...3d-iterm-memory> |

Or with git:
```bash
git clone -b 3d-iterm-memory https://github.com/BlindingBright/betaflight.git
cd betaflight
```

## Build (Linux, macOS, or Windows with WSL)

Betaflight 4.5 boards come from the separate **config** repo. Use its `4.5-config` branch:

```bash
git clone -b 4.5-config https://github.com/betaflight/config.git src/config
git -C src/config checkout 283a21f      # the board-config revision the release was built with (optional)
make arm_sdk_install                     # downloads the pinned GCC 10.3.1 into ./tools
make CONFIG=TBS_LUCID_AIO                # or CONFIG=<your board>
```

The firmware lands in `obj/betaflight_4.5.1_<MCU>_<BOARD>.hex`. Flash it with Betaflight Configurator →
Firmware Flasher → **Load Firmware [Local]**.

Notes from building it:
- If `make arm_sdk_install` downloads but `make` still says the compiler is missing, extract it by hand:
  `tar -C tools -xjf downloads/gcc-arm-none-eabi-10.3-2021.10-*-linux.tar.bz2`, then
  `touch tools/gcc-arm-none-eabi-10.3-2021.10/bin/arm-none-eabi-gcc-10.3.1`.
- Commit (or stash) your changes before building a test binary, and run `touch src/main/build/version.c` after
  committing. Otherwise the firmware reports `norevision` instead of the commit hash, and logs can't be traced to a build.
- Board names: `ls src/config/configs`. Not every board fits every feature; the 3D Edition changes add a few KB (the F411 builds are at 51–65% of flash).

## Run the unit tests

```bash
cd src/test
make CC=gcc CXX=g++ test_pid_unittest test_cli_unittest test_rc_controls_unittest test_blackbox_unittest
```
(Betaflight 4.5's test harness only accepts clang 7–16; with a newer clang, build the tests with gcc as above.)

## Sharing a build

If you build for another board and fly it, please send the logs through the
[log form](README.md#send-logs--feedback) and say which board and commit you built. Builds for other boards can also be
[requested with the build request form](https://forms.gle/1p93ZjiqDp1PLWA96) or from ZoeFPV (Discord link at [zoefpv.com](https://zoefpv.com)).
