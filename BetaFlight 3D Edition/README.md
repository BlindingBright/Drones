# BetaFlight 3D Edition

**Betaflight with improvements for 3D (reversible-motor) flight.** Tic-tocks, punch-outs from reversals, and flips
through center should hold their attitude better instead of drifting after every motor reversal.

> **Status: v0.3.0-test (experimental).** Developed and flight-tested on the **TBS Lucid AIO 1-2S** (ZoeFPV's "Lil Horny",
> test passes 34–53). Firmware is built for **[44 boards](BOARDS.md)** (Betaflight 4.5.1 base).
> We need logs from more pilots and more quads before proposing it to the main Betaflight project.
> Use it for testing. For everyday flying, official Betaflight is the safe choice.

> **Experimental branch:** [v0.3.1-experimental](EXPERIMENTAL_v0.3.1_TESTING.md) adds 3D fixes for the low-voltage cutoff,
> failsafe throttle, `thr_mid` and sag compensation. **Untested**: it's the branch ZoeFPV is testing internally. Use v0.3.0 below
> unless you want to help bench-test it.

## Start here

1. **[Find your board's firmware (BOARDS.md)](BOARDS.md)**
2. **[Follow the testing guide](TESTING_GUIDE.md)**: 4 packs, one settings change in the middle
3. **[Upload your logs](https://forms.gle/Vfq3c2W7Lp5FE36t5)**

## Downloads

| | File | |
|---|---|---|
| **Firmware: TBS Lucid AIO 1-2S** | `BetaFlight3DEdition_v0.3.0-test_TBS_LUCID_AIO.hex` | **[⬇ Download](https://github.com/BlindingBright/betaflight/releases/download/v0.3.0-3d-test/BetaFlight3DEdition_v0.3.0-test_TBS_LUCID_AIO.hex)** · [copy in this folder](firmware/TBS_LUCID_AIO/BetaFlight3DEdition_v0.3.0-test_TBS_LUCID_AIO.hex) · [release page](https://github.com/BlindingBright/betaflight/releases/tag/v0.3.0-3d-test) |
| **Firmware: CrazyBee F4 SX1280** (`CRAZYBEEF4SX1280`) | `BetaFlight3DEdition_v0.3.0-test_CRAZYBEEF4SX1280.hex` | **[⬇ Download](https://github.com/BlindingBright/betaflight/releases/download/v0.3.0-3d-test/BetaFlight3DEdition_v0.3.0-test_CRAZYBEEF4SX1280.hex)** · [copy in this folder](firmware/CRAZYBEEF4SX1280/BetaFlight3DEdition_v0.3.0-test_CRAZYBEEF4SX1280.hex) · settings: [3D_Edition_settings_CRAZYBEEF4SX1280.txt](tunes/3D_Edition_settings_CRAZYBEEF4SX1280.txt) |
| **All boards (44)** | [BOARDS.md](BOARDS.md) | Whoop/AIO and 5-inch boards: SpeedyBee, Matek, Kakute, Mamba, Foxeer, iFlight, JHE, GEPRC, BetaFPV, Flywoo, DarwinFPV, Sequre… |
| **Pilot testing guide** | [TESTING_GUIDE.md](TESTING_GUIDE.md) | **Start here** |
| **Log & feedback upload** | [Google Form](https://forms.gle/Vfq3c2W7Lp5FE36t5) | Up to 10 logs at once |
| **Starter tune** (paste in CLI) | [3D_Edition_starter_tune_TBS_LUCID_AIO.txt](tunes/3D_Edition_starter_tune_TBS_LUCID_AIO.txt) | Lucid only: 3D, motor, filter, PID and Block A settings |
| **Best settings** (paste in CLI) | [3D_Edition_best_settings_v0.3.0.txt](tunes/3D_Edition_best_settings_v0.3.0.txt) | The recommended 3D settings (= Block B), any board with RPM telemetry |
| ZoeFPV's full `diff all` (reference) | [ZoeFPV_LilHorny_diff_all.txt](tunes/ZoeFPV_LilHorny_diff_all.txt) | Contains build-specific settings; don't paste it whole |
| **Source code** | [zip](https://github.com/BlindingBright/betaflight/archive/refs/tags/v0.3.0-3d-test.zip) · [tar.gz](https://github.com/BlindingBright/betaflight/archive/refs/tags/v0.3.0-3d-test.tar.gz) · [browse](https://github.com/BlindingBright/betaflight/tree/3d-iterm-memory) | How to build: [BUILD_FROM_SOURCE.md](BUILD_FROM_SOURCE.md) |

SHA-256: Lucid `0a614e286c6a5bf7a2000314e4af9cc27adbb445eebbd1547dae01676ee53250`,
CrazyBee `164c5c0bff1bee1b65159d196e856db2383666d7863ed4ef48076a81c1ef6ce4`.
All boards are built from the same commit; after flashing, the CLI `version` command shows `4.5.1 ... (9421121f7)`.
Older versions: [v0.2.2-test](https://github.com/BlindingBright/betaflight/releases/tag/v0.2.2-3d-test), [v0.1.0-test](https://github.com/BlindingBright/betaflight/releases/tag/v0.1.0-3d-test).

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
| `3d_anti_gravity` | `STOCK` / `GATED` | `GATED`: anti-gravity ignores the pass through center at a reversal (stock treats every flip as a throttle chop and boosts P while the motors restart). Chops and punches within one direction work as before. |
| `3d_ag_approach_pct` | 0–50 (0 = off) | With `GATED`, also ignore the throttle falling below this % on the way into a flip (most of a flip's anti-gravity boost happens there). Recommended 15. |
| `3d_dyn_idle` | `OFF` / `ON` | Dynamic idle in 3D (stock Betaflight skips it in 3D). Raises the idle of the current motor direction when the slowest motor drops below `dyn_idle_min_rpm`; in practice it gives the motors more command while they restart after a flip. Needs RPM telemetry. Recommended `dyn_idle_min_rpm` 50 on whoops (flown), 30 on 5-inch (log replay only, not flown), `dyn_idle_max_increase` 100. |
| `debug_mode = 3D_ITERM` | | Logs motor direction [0], ms since the reversal while holding (0 once released) [1], upright trims ×10 [2–4], inverted trims ×10 [5–7]. |
| Blackbox header | | Records `3d_deadband_throttle` and all `3d_*` settings. |

The learned trims are kept across disarms (not across a power cycle).

**Why:** stock Betaflight zeroes the I-term for 250 ms after every 3D reversal. A 3D quad needs a different trim upright
than inverted: logs from three 3D quads and two pilots (two whoops and a 5") show the trims differ by 20–60 units and often
flip sign. So after every flip the quad drifts until the I-term rebuilds.

**Results so far (Lil Horny):**
- I-term handling (`PER_DIRECTION` + `RPM` + `FLIP`, 2 test days, 15 flights): the I-term is released ~150 ms after the flip
  (right after the motors restart, vs 250 ms), the learned trims fill to ~100%, the trim error in the 130–250 ms after a flip is
  about 65% smaller, and pitch drift after flips about 20% lower.
- v0.3.0 (one same-day A/B, 2 + 2 packs, 143 flips: stock vs `GATED` + approach 15 + 3D dynamic idle): **not worse than stock
  in any window measured**, less shake in the first 60 ms after a flip (about −19%; later windows within noise), the restarting
  motors get ~10% command instead of ~3%, no stalls or desyncs, and the pilot preferred it. One day, one quad: indicative only.
- Tried and dropped: "restart sync" (all four motors forced to the same command while they restart) made the shake after flips
  ~25% worse.

One quad isn't proof: that's why we need your logs.

## Best settings (v0.3.0)
Paste on top of your own tune (battery unplugged), or use [the file](tunes/3D_Edition_best_settings_v0.3.0.txt). Needs RPM
telemetry (`dshot_bidir = ON`); without it, see the testing guide's Block B for the no-telemetry version.
```
set 3d_iterm_mode = PER_DIRECTION
set 3d_iterm_release = RPM
set 3d_iterm_load = FLIP
set 3d_anti_gravity = GATED
set 3d_ag_approach_pct = 15
set 3d_dyn_idle = ON
profile 0
set dyn_idle_min_rpm = 50
set dyn_idle_max_increase = 100
save
```
`dyn_idle_min_rpm`: 50 for 1S/2S whoops (flown); 30 for 5-inch is from log replay only, not flown yet (keep it below the rpm of
your slowest motor at center stick). 3D dynamic idle and the approach gate have only flown on one whoop so far: bench-check
props off first, and please send logs.

## Roadmap (ideas found in the logs and the code, not built yet)

- **Motor restart watchdog**: warn and log when a motor fails to restart after a reversal.
- **Betaflight 2026.6 port** of v0.3.0.
- Per-direction thrust / TPA 
- Fixes for 3D bugs in stock Betaflight: the low-voltage cutoff shifts the 3D center into reverse; a failsafe *landing*
  sends full reverse throttle; `vbat_sag_compensation` silently does nothing in 3D (dynamic idle is fixed in v0.3.0 with
  `3d_dyn_idle`); and `thr_mid` other
  than 50 shifts the 3D center.

## Credits and license

Betaflight 3D Edition is a fork of [Betaflight](https://github.com/betaflight/betaflight) by the Betaflight team. Like Betaflight,
the firmware and its source are licensed under **GPL-3.0**. The guide and tune files in this folder follow
the [Drones repo license](../README.md#license).
Developed and flight-tested by **ZoeFPV** on "[Lil Horny](../Lil%20Horny/)", with logs from fellow 3D pilots.
