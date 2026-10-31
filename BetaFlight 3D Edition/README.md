# BetaFlight 3D Edition

**Betaflight with improvements for 3D (reversible-motor) flight.** Tic-tocks, punch-outs from reversals, and flips
through center should hold their attitude better instead of drifting after every motor reversal.

> **Status: v0.2.2-test (experimental).** Developed and flight-tested on the **TBS Lucid AIO 1-2S** (ZoeFPV's "Lil Horny",
> test passes 34–50). Firmware is built for **[44 boards](BOARDS.md)** (Betaflight 4.5.1 base).
> We need logs from more pilots and more quads before proposing it to the main Betaflight project.
> Use it for testing. For everyday flying, official Betaflight is the safe choice.

## Start here

1. **[Find your board's firmware (BOARDS.md)](BOARDS.md)**
2. **[Follow the testing guide](TESTING_GUIDE.md)**: 4 packs, one settings change in the middle
3. **[Upload your logs](https://forms.gle/Vfq3c2W7Lp5FE36t5)**

## Downloads

| | File | |
|---|---|---|
| **Firmware: TBS Lucid AIO 1-2S** | `BetaFlight3DEdition_v0.2.2-test_TBS_LUCID_AIO.hex` | **[⬇ Download](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_TBS_LUCID_AIO.hex)** · [copy in this folder](firmware/TBS_LUCID_AIO/BetaFlight3DEdition_v0.2.2-test_TBS_LUCID_AIO.hex) · [release page](https://github.com/BlindingBright/betaflight/releases/tag/v0.2.2-3d-test) |
| **Firmware: CrazyBee F4 SX1280** (`CRAZYBEEF4SX1280`) | `BetaFlight3DEdition_v0.2.2-test_CRAZYBEEF4SX1280.hex` | **[⬇ Download](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_CRAZYBEEF4SX1280.hex)** · [copy in this folder](firmware/CRAZYBEEF4SX1280/BetaFlight3DEdition_v0.2.2-test_CRAZYBEEF4SX1280.hex) · settings: [3D_Edition_settings_CRAZYBEEF4SX1280.txt](tunes/3D_Edition_settings_CRAZYBEEF4SX1280.txt) |
| **All boards (44)** | [BOARDS.md](BOARDS.md) | Whoop/AIO and 5-inch boards: SpeedyBee, Matek, Kakute, Mamba, Foxeer, iFlight, JHE, GEPRC, BetaFPV, Flywoo, DarwinFPV, Sequre… |
| **Pilot testing guide** | [TESTING_GUIDE.md](TESTING_GUIDE.md) | **Start here** |
| **Log & feedback upload** | [Google Form](https://forms.gle/Vfq3c2W7Lp5FE36t5) | Up to 10 logs at once |
| **Starter tune** (paste in CLI) | [3D_Edition_starter_tune_TBS_LUCID_AIO.txt](tunes/3D_Edition_starter_tune_TBS_LUCID_AIO.txt) | Lucid only: 3D, motor, filter, PID and Block A settings |
| ZoeFPV's full `diff all` (reference) | [ZoeFPV_LilHorny_diff_all.txt](tunes/ZoeFPV_LilHorny_diff_all.txt) | Contains build-specific settings; don't paste it whole |
| **Source code** | [zip](https://github.com/BlindingBright/betaflight/archive/refs/tags/v0.2.2-3d-test.zip) · [tar.gz](https://github.com/BlindingBright/betaflight/archive/refs/tags/v0.2.2-3d-test.tar.gz) · [browse](https://github.com/BlindingBright/betaflight/tree/3d-iterm-memory) | How to build: [BUILD_FROM_SOURCE.md](BUILD_FROM_SOURCE.md) |

SHA-256: Lucid `a73e3ab1b083e2ceec6347ebaf312f9a3fbe6c8de6e868424a34c19c25091f8b`,
CrazyBee `80e41631b6082ced75328c2f63c5fade6fecca45dd8f724806b59ec0a5ce6d30`.
All boards are built from the same commit; after flashing, the CLI `version` command shows `4.5.1 ... (b5fa258ef)`.
Older v0.1.0-test files: [v0.1.0-test release](https://github.com/BlindingBright/betaflight/releases/tag/v0.1.0-3d-test).

**Board not in [the list](BOARDS.md)?** **[Request a build for your board](https://forms.gle/1p93ZjiqDp1PLWA96)** (Google Form, no sign-in needed),
or contact ZoeFPV (Discord link at [zoefpv.com](https://zoefpv.com)), or [build it yourself](BUILD_FROM_SOURCE.md).
Requested boards get built and added to the list.

## Send logs & feedback

### 👉 [Upload your blackbox logs and report (Google Form)](https://forms.gle/Vfq3c2W7Lp5FE36t5)

You can upload several `.BBL` logs at once, along with your drone details, an AM32 settings screenshot and a short report. Every
log helps. Results from different motors, props and frames are what tell us whether a change really works.
Uploading files needs a Google sign-in (that's how Google Forms handles files). Without a Google account, attach your logs to a
[GitHub issue](https://github.com/BlindingBright/Drones/issues/new) instead. Bugs and ideas are also welcome as issues.

## What's different from Betaflight 4.5.1

Every new setting **defaults to stock behaviour**, so flashing this alone changes nothing until you turn a feature on.
The [testing guide](TESTING_GUIDE.md) has copy-paste blocks; this table is the reference.

| Setting | Values (default first) | What it does |
|---|---|---|
| `3d_iterm_mode` | `RESET` (stock) / `HOLD` / `PER_DIRECTION` | What happens to the I-term when the motors reverse. `PER_DIRECTION` keeps a separate learned trim for upright and inverted and loads the right one on each flip. During the hold after a reversal the I-term is frozen, so it can't wind up while the props pass through zero rpm. |
| `3d_iterm_release` | `TIME` / `RPM` | When the hold ends. `TIME`: after `3d_iterm_reset_ms`. `RPM`: as soon as **all motors have restarted** (eRPM from bidirectional DShot), within `3d_iterm_min_ms`…`3d_iterm_max_ms`. Needs `dshot_bidir = ON`. |
| `3d_iterm_reset_ms` | 0–500 (250) | Hold length for `TIME`. Stock Betaflight hard-codes 250 ms. |
| `3d_iterm_min_ms` / `3d_iterm_max_ms` | 50 / 400 | Shortest and longest hold with `RPM`. |
| `3d_iterm_rpm_pct` | 10–90 (40) | A motor counts as restarted when its eRPM falls below and comes back above this % of the in-flight average. |
| `3d_iterm_load` | `FLIP` / `RELEASE` | When `PER_DIRECTION` loads the learned trim: at the reversal, or when the hold ends. `FLIP` is the recommended test setting. |
| `3d_iterm_learn_thr` | 0–150 (50) | The trims learn only above this % of the quad's own average throttle (works for any size of quad). |
| `3d_iterm_learn_hz_x10` | 1–50 (5 = 0.5 Hz) | How fast the learned trims follow the I-term in steady flight. |
| `3d_iterm_axes` | `ALL` / `PITCH` / `ROLL_PITCH` | Which axes use the learned trims (the others reset like stock). |
| `debug_mode = 3D_ITERM` | | Logs motor direction [0], ms since the reversal while holding (0 once released) [1], upright trims ×10 [2–4], inverted trims ×10 [5–7]. |
| Blackbox header | | Records `3d_deadband_throttle` and all `3d_iterm_*` settings. |

The learned trims are kept across disarms (not across a power cycle).

**Why:** stock Betaflight zeroes the I-term for 250 ms after every 3D reversal. A 3D quad needs a different trim upright
than inverted: logs from three 3D quads and two pilots (two whoops and a 5") show the trims differ by 20–60 units and often
flip sign. So after every flip the quad drifts until the I-term rebuilds.

**Results so far (Lil Horny, 2 test days, 15 flights):** with `PER_DIRECTION` + `RPM` + `FLIP`, the I-term is released ~150 ms after
the flip (right after the motors restart, vs 250 ms), the learned trims fill to ~100%, the trim error in the 130–250 ms after a
flip is about 65% smaller, and pitch drift after flips about 20% lower. Wobble right after the flip is unchanged. One quad isn't
proof: that's why we need your logs.

## Roadmap (ideas found in the logs and the code, not built yet)

- **Motor restart watchdog**: warn and log when a motor fails to restart after a reversal.
- **3D-aware anti-gravity**: anti-gravity treats every reversal as a throttle chop and raises P and I while the props
  are stopped (next test on Lil Horny).
- **Betaflight 2026.6 port** of v0.2.2.
- Per-direction thrust / TPA 
- Fixes for 3D bugs in stock Betaflight: the low-voltage cutoff shifts the 3D center into reverse; a failsafe *landing*
  sends full reverse throttle; `vbat_sag_compensation` and dynamic idle silently do nothing in 3D; and `thr_mid` other
  than 50 shifts the 3D center.

## Credits and license

Betaflight 3D Edition is a fork of [Betaflight](https://github.com/betaflight/betaflight) by the Betaflight team. Like Betaflight,
the firmware and its source are licensed under **GPL-3.0**. The guide and tune files in this folder follow
the [Drones repo license](../README.md#license).
Developed and flight-tested by **ZoeFPV** on "[Lil Horny](../Lil%20Horny/)", with logs from fellow 3D pilots.
