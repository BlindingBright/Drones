# BetaFlight 3D Edition

**Betaflight with improvements for 3D (reversible-motor) flight.** Tic-tocks, punch-outs from reversals, and flips
through center should hold their attitude better instead of drifting after every motor reversal.

> **Status: v0.3.3-test (test firmware, Betaflight 2026.6.2 base).** The 3D changes were developed and flight-tested on the
> **TBS Lucid AIO 1-2S** (ZoeFPV's "Lil Horny", test passes 34–56) on the Betaflight 4.5.1 base (v0.3.1). On the 2026.6.2 base,
> v0.3.3 has **flown on a 6S 5-inch** (Hobbywing XRotor F7, AM32; five packs, about 250 motor reversals). The whoop has not flown on
> 2026.6 yet. Firmware is built for **[90 boards](BOARDS.md)**.
> We need logs from more pilots and more quads before proposing it to the main Betaflight project.
> Use it for testing. For everyday flying, official Betaflight is the safe choice.

> **New in v0.3.3:** two more 3D fixes, both confirmed in blackbox logs on the 5-inch; no new settings, saved settings are kept.
> (1) With `iterm_rotation = ON`, the I-term held after a motor reversal is no longer rotated between axes while it is held.
> (2) In reverse, airmode and the throttle limits now use the bounds of the mix the motors actually get (stock used the upright
> bounds, so a motor could clip or full reverse throttle was pulled down too far). Upright and non-3D flight are unchanged.
>
> **v0.3.2:** BetaFlight 3D Edition moved to **Betaflight 2026.6.2** (was 4.5.1), the first step toward proposing it
> upstream. Same 3D features and defaults as v0.3.1, plus one 3D fix: altitude hold (which 2026.6 also uses for failsafe
> landing) and GPS rescue now run the motors upright. **Upgrading from v0.3.1 / Betaflight 4.5:** 2026.6 renamed D-max
> (`d_*` = base, `d_max_*` = max) and `dshot_idle_value` (now `motor_idle`), so a 4.5 `diff all` doesn't paste as-is.
> v0.3.1 stays available as the flown 4.5 fallback. **[New-feature testing notes](V0.3.1_FEATURE_TESTING.md)**.

## Start here

1. **[Find your board's firmware (BOARDS.md)](BOARDS.md)**
2. **[Follow the testing guide](TESTING_GUIDE.md)**: 4 packs, one settings change in the middle
   (and, if you can, the [new-feature tests](V0.3.1_FEATURE_TESTING.md))
3. **[Upload your logs](https://forms.gle/Vfq3c2W7Lp5FE36t5)**

## Downloads

| | File | |
|---|---|---|
| **Firmware: TBS Lucid AIO 1-2S** | `BetaFlight3DEdition_v0.3.3-test_TBS_LUCID_AIO.hex` | **[⬇ Download](https://github.com/BlindingBright/betaflight/releases/download/v0.3.3-3d-test/BetaFlight3DEdition_v0.3.3-test_TBS_LUCID_AIO.hex)** · [copy in this folder](firmware/TBS_LUCID_AIO/BetaFlight3DEdition_v0.3.3-test_TBS_LUCID_AIO.hex) · [release page](https://github.com/BlindingBright/betaflight/releases/tag/v0.3.3-3d-test) |
| **Firmware: CrazyBee F4 SX1280** (`CRAZYBEEF4SX1280`) | `BetaFlight3DEdition_v0.3.3-test_CRAZYBEEF4SX1280.hex` | **[⬇ Download](https://github.com/BlindingBright/betaflight/releases/download/v0.3.3-3d-test/BetaFlight3DEdition_v0.3.3-test_CRAZYBEEF4SX1280.hex)** · [copy in this folder](firmware/CRAZYBEEF4SX1280/BetaFlight3DEdition_v0.3.3-test_CRAZYBEEF4SX1280.hex) · settings: [3D_Edition_settings_CRAZYBEEF4SX1280.txt](tunes/3D_Edition_settings_CRAZYBEEF4SX1280.txt) |
| **All boards (90)** | [BOARDS.md](BOARDS.md) | Whoop/AIO and 5-inch boards: Fractal SP8, BetaFPV, GEPRC, HGLRC, NewBeeDrone, Holybro, SpeedyBee, Matek, Kakute, Mamba, Foxeer, iFlight, JHE, GEPRC, BetaFPV, Flywoo, DarwinFPV, Sequre… |
| **Pilot testing guide** | [TESTING_GUIDE.md](TESTING_GUIDE.md) | **Start here** |
| **Log & feedback upload** | [Google Form](https://forms.gle/Vfq3c2W7Lp5FE36t5) | Up to 10 logs at once |
| **Starter tune** (paste in CLI) | [3D_Edition_starter_tune_TBS_LUCID_AIO.txt](tunes/3D_Edition_starter_tune_TBS_LUCID_AIO.txt) | Lucid only, v0.3.2 / 2026.6 names: 3D, motor, filter, PID and Block A settings ([4.5 / v0.3.1 version](tunes/3D_Edition_starter_tune_TBS_LUCID_AIO_v0.3.1_BF4.5.txt)) |
| **Best settings** (paste in CLI) | [3D_Edition_best_settings_v0.3.1.txt](tunes/3D_Edition_best_settings_v0.3.1.txt) | The recommended 3D settings (= v0.3.1 defaults + dynamic idle), any board with RPM telemetry |
| **5-inch 3D tune** (paste in CLI) | [Unicorn_5inch_MAIN_tune_preset_BF3D_v0.3.3.txt](tunes/Unicorn_5inch_MAIN_tune_preset_BF3D_v0.3.3.txt) | ZoeFPV's 6S 5-inch 3D tune (2010-size ~1950 kv, 5x4 3D props, AM32), flown on v0.3.3. Tune only: never touches your board, ports, switches, motor order or rates (rates are an optional block). Needs v0.3.3 firmware and 3D already set up; any error = nothing saved. Read the header first |
| ZoeFPV's full CLI (reference) | [ZoeFPV_LilHorny_v0.3.3_full_CLI.txt](tunes/ZoeFPV_LilHorny_v0.3.3_full_CLI.txt) (2026.6) · [old 4.5 diff](tunes/ZoeFPV_LilHorny_diff_all.txt) | Contains build-specific settings; don't paste it whole |
| **Source code** | [zip](https://github.com/BlindingBright/betaflight/archive/refs/tags/v0.3.3-3d-test.zip) · [tar.gz](https://github.com/BlindingBright/betaflight/archive/refs/tags/v0.3.3-3d-test.tar.gz) · [browse](https://github.com/BlindingBright/betaflight/tree/3d-v0.3.3) | How to build: [BUILD_FROM_SOURCE.md](BUILD_FROM_SOURCE.md) |

SHA-256: Lucid `ae46eced191b3740b6b31a505b1924af0012286effee05e2f872fea08c0963ad`,
CrazyBee `72ee667984f30bf42824d999f110595920d2b734cc7df3224a11fae79e55955a`.
All boards are built from the same commit; after flashing, the CLI `version` command shows `2026.6.2 ... (fb947bea1)`.
Older versions: [v0.3.2-test](https://github.com/BlindingBright/betaflight/releases/tag/v0.3.2-3d-test) (first 2026.6.2 build), [v0.3.1-test](https://github.com/BlindingBright/betaflight/releases/tag/v0.3.1-3d-test) (Betaflight 4.5.1, the flown version), [v0.3.0-test](https://github.com/BlindingBright/betaflight/releases/tag/v0.3.0-3d-test), [v0.2.2-test](https://github.com/BlindingBright/betaflight/releases/tag/v0.2.2-3d-test), [v0.1.0-test](https://github.com/BlindingBright/betaflight/releases/tag/v0.1.0-3d-test).

**Board not in [the list](BOARDS.md)?** **[Request a build for your board](https://forms.gle/1p93ZjiqDp1PLWA96)** (Google Form, no sign-in needed),
or contact ZoeFPV (Discord link at [zoefpv.com](https://zoefpv.com)), or [build it yourself](BUILD_FROM_SOURCE.md).
Requested boards get built and added to the list.

## Send logs & feedback

### 👉 [Upload your blackbox logs and report (Google Form)](https://forms.gle/Vfq3c2W7Lp5FE36t5)

You can upload several `.BBL` logs at once, along with your drone details, an AM32 settings screenshot and a short report. Every
log helps. Results from different motors, props and frames are what tell us whether a change really works.
Uploading files needs a Google sign-in (that's how Google Forms handles files). Without a Google account, attach your logs to a
[GitHub issue](https://github.com/BlindingBright/Drones/issues/new) instead. Bugs and ideas are also welcome as issues.

## What's different from stock Betaflight

The 3D settings **default to the best settings found so far** (v0.3.1; earlier versions defaulted to stock). The
[testing guide](TESTING_GUIDE.md)'s Block A sets stock behaviour for comparison; this table is the reference.

| Setting | Default (stock) | What it does |
|---|---|---|
| `3d_iterm_mode` | `PER_DIRECTION` (`RESET`); also `HOLD` | What happens to the I-term when the motors reverse. `PER_DIRECTION` keeps a separate learned trim for upright and inverted and loads the right one on each flip. During the hold after a reversal the I-term is frozen, so it can't wind up while the props pass through zero rpm. |
| `3d_iterm_release` | `RPM` (`TIME`) | When the hold ends. `TIME`: after `3d_iterm_reset_ms`. `RPM`: as soon as **all motors have restarted** (eRPM from bidirectional DShot), within `3d_iterm_min_ms`…`3d_iterm_max_ms`. Without RPM telemetry, `RPM` uses the `TIME` hold. |
| `3d_iterm_reset_ms` | 0–500 (250) | Hold length for `TIME`. Stock Betaflight hard-codes 250 ms. |
| `3d_iterm_min_ms` / `3d_iterm_max_ms` | 50 / 400 | Shortest and longest hold with `RPM`. |
| `3d_iterm_rpm_pct` | 10–90 (40) | A motor counts as restarted when its eRPM falls below and comes back above this % of the in-flight average. |
| `3d_iterm_load` | `FLIP`; also `RELEASE` | When `PER_DIRECTION` loads the learned trim: at the reversal, or when the hold ends. |
| `3d_iterm_learn_thr` | 0–150 (50) | The trims learn only above this % of the quad's own average throttle (works for any size of quad). |
| `3d_iterm_learn_hz_x10` | 1–50 (5 = 0.5 Hz) | How fast the learned trims follow the I-term in steady flight. |
| `3d_iterm_axes` | `ALL`; also `PITCH` / `ROLL_PITCH` | Which axes use the learned trims (the others reset like stock). |
| `3d_anti_gravity` | `GATED` (`STOCK`) | `GATED`: anti-gravity ignores the pass through center at a reversal (stock treats every flip as a throttle chop and boosts P while the motors restart). Chops and punches within one direction work as before. |
| `3d_ag_approach_pct` | 15 (0 = off), 0–50 | With `GATED`, also ignore the throttle falling below this % on the way into a flip (most of a flip's anti-gravity boost happens there). |
| `3d_dyn_idle` | `ON` (`OFF`) | Dynamic idle in 3D (stock Betaflight skips it in 3D). Raises the idle of the current motor direction when the slowest motor drops below `dyn_idle_min_rpm`; in practice it gives the motors more command while they restart after a flip. **Does nothing until you set `dyn_idle_min_rpm`** (stock default 0) and have RPM telemetry: 50 on whoops (flown), 30 on 5-inch (log replay only, not flown), `dyn_idle_max_increase` 100. |
| `debug_mode = 3D_ITERM` | | Logs motor direction [0], ms since the reversal while holding (0 once released) [1], upright trims ×10 [2–4], inverted trims ×10 [5–7]. |
| Blackbox header | | Records `3d_deadband_throttle` and all `3d_*` settings. |

The learned trims are kept across disarms (not across a power cycle).

**Upgrading without a full chip erase keeps your saved 3D settings**, so the new defaults only arrive with a full chip erase,
`defaults`, or by pasting the [best settings](tunes/3D_Edition_best_settings_v0.3.1.txt). Check with `get 3d_`.

**3D fixes (v0.3.1+, no settings):** stock Betaflight treats the bottom of the throttle stick as "off". In 3D that's full reverse,
and a few features send you there:

| Stock behaviour in 3D | BetaFlight 3D Edition |
|---|---|
| Low-voltage cutoff (`vbat_cutoff_percent` < 100) scales the throttle toward the bottom: center stick becomes reverse thrust | Scales toward stick center (zero thrust) |
| Failsafe stage 2 sends `failsafe_throttle` (default 1000 = full reverse); with `AUTO-LAND` for about a second | ≤ 1500 gives zero thrust; above 1500 upright thrust as before (failsafe levels the quad upright) |
| `thr_mid` ≠ 50 with `thr_expo` (2026.6: also `thr_hover` ≠ 50) moves zero thrust off stick center | Stick center stays zero thrust |
| `vbat_sag_compensation` silently does nothing in 3D | Works in 3D, on the active direction's band |
| (2026.6) Altitude hold, also engaged by failsafe landing, and GPS rescue set the throttle but keep the last motor direction: after a link loss in reverse they drive the motors in reverse | Motors run upright while the autopilot sets the throttle (v0.3.2) |

They act only in normal 3D (not with the 3D mode switch or `3d_switched_mode`) and only if you use those settings, so with the
defaults normal flying is unchanged. None of the four has been tested on real hardware yet: see the
[new-feature testing notes](V0.3.1_FEATURE_TESTING.md) for status and bench tests.

**Why:** stock Betaflight zeroes the I-term for 250 ms after every 3D reversal. A 3D quad needs a different trim upright
than inverted: logs from three 3D quads and two pilots (two whoops and a 5") show the trims differ by 20–60 units and often
flip sign. So after every flip the quad drifts until the I-term rebuilds.

**Results so far (Lil Horny):**
- I-term handling (`PER_DIRECTION` + `RPM` + `FLIP`, 2 test days, 15 flights): the I-term is released ~150 ms after the flip
  (right after the motors restart, vs 250 ms), the learned trims fill to ~100%, the trim error in the 130–250 ms after a flip is
  about 65% smaller, and pitch drift after flips about 20% lower.
- v0.3.1 (Pass 56): flies like the Pass 53 best settings, no loop overruns or stalls.
- v0.3.2 (Betaflight 2026.6.2 base): flown on the 6S 5-inch before v0.3.3; its logs are what exposed the two v0.3.3 bugs.
- v0.3.3 (6S 5-inch, Hobbywing XRotor F7, AM32; whoop not flown on 2026.6 yet): in the pack flown with `iterm_rotation = ON`
  the held I-term did not change at all through its 36 reversal holds (v0.3.2: up to 41 / 32 / 150 units on roll / pitch / yaw in
  one hold), and in every pack the reverse motor outputs follow the corrected bounds. On v0.3.2 the old bounds cut 2–3 % (at most 13 %) of the motor band more than
  needed on about 4 % of inverted time. Unit tests: mixer 33, PID 18, rc 4.
- v0.3.0 (one same-day A/B, 2 + 2 packs, 143 flips: stock vs `GATED` + approach 15 + 3D dynamic idle): **not worse than stock
  in any window measured**, less shake in the first 60 ms after a flip (about −19%; later windows within noise), the restarting
  motors get ~10% command instead of ~3%, no stalls or desyncs, and the pilot preferred it. One day, one quad: indicative only.
- Tried and dropped: "restart sync" (all four motors forced to the same command while they restart) made the shake after flips
  ~25% worse.

One quad isn't proof: that's why we need your logs.

## Best settings (v0.3.1 – v0.3.3)
The 3D values are the defaults. Dynamic idle also needs these two stock settings (battery unplugged; skip them without RPM
telemetry):
```
profile 0
set dyn_idle_min_rpm = 50
set dyn_idle_max_increase = 100
save
```
`dyn_idle_min_rpm`: 50 for 1S/2S whoops (flown); 30 for 5-inch has only been hover-tested so far (keep it below the rpm of
your slowest motor at center stick). Upgraded without a full chip erase, or coming back from an A/B test? Paste the full
[best settings file](tunes/3D_Edition_best_settings_v0.3.1.txt). 3D dynamic idle and the approach gate have only flown on one
whoop so far: bench-check props off first, and please send logs.

## Roadmap (ideas found in the logs and the code, not built yet)

- Fly the whoop on v0.3.3 (Betaflight 2026.6.2) and a full 5-inch pack with dynamic idle, then prepare upstream pull requests
  (Betaflight `master`, one fix per PR, stock defaults). The reverse airmode bounds fix applies to stock Betaflight as-is.
- Per-direction I-term memory: a better estimate of the trim it stores (today it is often no better than zero on roll and yaw).
- Per-direction thrust / TPA.
- Propose the 3D fixes to the main Betaflight project once they're confirmed on hardware.

## Credits and license

Betaflight 3D Edition is a fork of [Betaflight](https://github.com/betaflight/betaflight) by the Betaflight team. Like Betaflight,
the firmware and its source are licensed under **GPL-3.0**. The guide and tune files in this folder follow
the [Drones repo license](../README.md#license).
Developed and flight-tested by **ZoeFPV** on "[Lil Horny](../Lil%20Horny/)", with logs from fellow 3D pilots.
