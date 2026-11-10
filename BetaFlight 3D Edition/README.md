# BetaFlight 3D Edition

**Betaflight with improvements for 3D (reversible-motor) flight.** Tic-tocks, punch-outs from reversals and flips through
center hold their attitude better instead of drifting after every motor reversal, and the 2D shortcuts that send a 3D quad into
reverse (failsafe, low-voltage cutoff, throttle curve) are fixed.

> **Status: v0.3.3-test (test firmware, Betaflight 2026.6.2 base, [90 boards](BOARDS.md)).** Developed and flight-tested by
> ZoeFPV on a 31 mm whoop and a 6S 5-inch. v0.3.3 has flown on the **5-inch** (several packs with blackbox logs); the whoop tune
> was flown on the earlier Betaflight 4.5 version (v0.3.1) and has since flown on 2026.6 (v0.3.3): the pilot says it felt good, logs to follow. We need logs from more pilots and more
> quads before proposing it to the main Betaflight project. Use it for testing; for everyday flying official Betaflight is the safe choice.

## ⭐ Presets: ready-to-paste tunes

Flash the firmware for your board, paste the preset for your quad into the Betaflight CLI, check the motors, fly. A preset changes the
tune only: **it never touches your board, ports, switches, motor order or rates**, and it saves nothing if any line is rejected.

| | 🛸 **31 mm 3D whoop** | 🚁 **6S 5-inch 3D** |
|---|---|---|
| **Preset** | **[⬇ LilHorny_31mm_whoop_tune_preset_BF3D_v0.3.3.txt](tunes/LilHorny_31mm_whoop_tune_preset_BF3D_v0.3.3.txt)** | **[⬇ Unicorn_5inch_MAIN_tune_preset_BF3D_v0.3.3.txt](tunes/Unicorn_5inch_MAIN_tune_preset_BF3D_v0.3.3.txt)** |
| Made on | "Lil Horny": TBS Lucid AIO 1-2S, 31 mm props, AM32 | "Unicorn": Hobbywing XRotor F7 (flown) and a T-Motor F7 twin (hover-tested), 6S 2010 motors, APC 5x4 3D props, AM32 |
| Firmware | [Lucid AIO](https://github.com/BlindingBright/betaflight/releases/download/v0.3.3-3d-test/BetaFlight3DEdition_v0.3.3-test_TBS_LUCID_AIO.hex) · [all boards](BOARDS.md) | [XRotor F7](https://github.com/BlindingBright/betaflight/releases/download/v0.3.3-3d-test/BetaFlight3DEdition_v0.3.3-test_HOBBYWING_XROTORF7CONV.hex) · [T-Motor F7](https://github.com/BlindingBright/betaflight/releases/download/v0.3.3-3d-test/BetaFlight3DEdition_v0.3.3-test_TMOTORF7.hex) · [all boards](BOARDS.md) |
| Status | Tune flown on v0.3.1, then on v0.3.3 (2026.6): felt good, logs to follow | **Flown on v0.3.3**; feels close to perfect |

**Read [PRESETS.md](PRESETS.md) first**: requirements (3D set up, bidirectional DShot, your motor pole count), the exact steps, how to go back,
and how to adapt the tune to your quad.

## Start here

1. **[Find your board's firmware (BOARDS.md)](BOARDS.md)** and flash it.
2. **Paste a [preset](PRESETS.md)** for your quad (or follow the [testing guide](TESTING_GUIDE.md): 4 packs with one settings change in the middle).
3. Props off: check the motors, then fly.
4. **[Upload your logs](https://forms.gle/Vfq3c2W7Lp5FE36t5)** and say how it felt.

## What's different from stock Betaflight

| Change | Stock Betaflight in 3D | BetaFlight 3D Edition |
|---|---|---|
| **I-term at a motor reversal** | Zeroes it for a fixed 250 ms, so the quad loses its trim and drifts after every flip | Remembers one trim per direction, loads the right one at each flip, holds it frozen and releases it as soon as every motor has restarted (about 120-150 ms) |
| **Anti-gravity** | Treats the pass through center at every reversal as a throttle chop | Ignores the reversal and the approach to it |
| **Dynamic idle** | Not run in 3D at all | Runs in 3D: gives the restarting motors more command after a flip |
| **Failsafe, low-voltage cutoff, `thr_mid`, sag compensation, autopilot** | Treat the bottom of the stick as "off" (= full reverse), or do nothing in 3D | Fixed: never reverse, work in 3D |
| **Reverse mixer limits** (v0.3.3) | Use the upright bounds for reverse motors, so a motor can clip | Use the right bounds |
| **Held I-term with `iterm_rotation`** (v0.3.3) | Keeps rotating while "frozen", leaking trim between axes | Stays put until released |

**[Full breakdown: every change, how it works and why, with the settings reference → HOW_IT_WORKS.md](HOW_IT_WORKS.md)**

## Downloads

| | |
|---|---|
| **Firmware, 90 boards** | **[BOARDS.md](BOARDS.md)** · [v0.3.3-test release page](https://github.com/BlindingBright/betaflight/releases/tag/v0.3.3-3d-test) |
| **TBS Lucid AIO 1-2S** | **[⬇ BetaFlight3DEdition_v0.3.3-test_TBS_LUCID_AIO.hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.3-3d-test/BetaFlight3DEdition_v0.3.3-test_TBS_LUCID_AIO.hex)** · [copy in this folder](firmware/TBS_LUCID_AIO/BetaFlight3DEdition_v0.3.3-test_TBS_LUCID_AIO.hex) |
| **CrazyBee F4 SX1280** | **[⬇ BetaFlight3DEdition_v0.3.3-test_CRAZYBEEF4SX1280.hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.3-3d-test/BetaFlight3DEdition_v0.3.3-test_CRAZYBEEF4SX1280.hex)** · [copy in this folder](firmware/CRAZYBEEF4SX1280/BetaFlight3DEdition_v0.3.3-test_CRAZYBEEF4SX1280.hex) · [settings](tunes/3D_Edition_settings_CRAZYBEEF4SX1280.txt) |
| **Presets** | [31 mm whoop](tunes/LilHorny_31mm_whoop_tune_preset_BF3D_v0.3.3.txt) · [6S 5-inch](tunes/Unicorn_5inch_MAIN_tune_preset_BF3D_v0.3.3.txt) |
| **Source** | [zip](https://github.com/BlindingBright/betaflight/archive/refs/tags/v0.3.3-3d-test.zip) · [tar.gz](https://github.com/BlindingBright/betaflight/archive/refs/tags/v0.3.3-3d-test.tar.gz) · [browse](https://github.com/BlindingBright/betaflight/tree/3d-v0.3.3) · [build it yourself](BUILD_FROM_SOURCE.md) |

SHA-256: Lucid `f195b817d765873f931389979db72ff38e418500b9a702c985cb9b28dc84d7e4`,
CrazyBee `b670ed1eff615b650ab34b8852067746a23dc10d410871ee9b13facb8ff4b031`.
All boards are built from the same commit; after flashing, the CLI `version` command shows `2026.6.2 ... (fb947bea1)`.

**Board not in [the list](BOARDS.md)?** **[Request a build for your board](https://forms.gle/1p93ZjiqDp1PLWA96)** (Google Form, no sign-in
needed), or contact ZoeFPV (Discord link at [zoefpv.com](https://zoefpv.com)), or [build it yourself](BUILD_FROM_SOURCE.md). Requested boards get built and added to the list.

## Send logs & feedback

### 👉 [Upload your blackbox logs and report (Google Form)](https://forms.gle/Vfq3c2W7Lp5FE36t5)

You can upload several `.BBL` logs at once, along with your drone details, an AM32 settings screenshot and a short report. Every log
helps: results from different motors, props and frames are what tell us whether a change really works. Keep `debug_mode = 3D_ITERM`
on (the presets do). Uploading files needs a Google sign-in (that's how Google Forms handles files); without a Google account, attach
your logs to a [GitHub issue](https://github.com/BlindingBright/Drones/issues/new). Bugs and ideas are welcome as issues too.

## Results so far

Details and numbers in [HOW_IT_WORKS.md](HOW_IT_WORKS.md#evidence-and-limits).

- **Whoop (Lil Horny, 2 test days, 15 flights):** the I-term is released ~150 ms after a flip (vs 250 ms), learned trims fill to ~100 %,
  trim error in the 130-250 ms after a flip is about 65 % smaller, pitch drift after flips about 20 % lower. A same-day A/B of `GATED`
  anti-gravity + 3D dynamic idle (143 flips): not worse than stock in any window, about 19 % less shake in the first 60 ms after a flip, no stalls, pilot preferred it.
- **6S 5-inch (v0.3.3):** the held I-term did not change at all through 36 of 36 reversal holds (v0.3.2: up to 41 / 32 / 150 units in one
  hold); reverse motor outputs follow the corrected bounds; dynamic idle held the slowest motor at ~3000 rpm with no stalls in a hover test.
- Tried and dropped: "restart sync" made the shake after flips about 25 % worse.

One quad isn't proof: that's why we need your logs.

## Known issues

- On the 5-inch a small roll twitch (about 25 °/s at ~11 Hz) follows throttle changes; the cause is not found yet.
- The per-direction memory is often no better than zero on roll and yaw on the 5-inch (pitch trim is where it helps).
- The throttle safety fixes (failsafe, low-voltage cutoff, `thr_mid`, sag compensation) have unit tests but are not bench-tested on hardware: [FEATURE_TESTING.md](FEATURE_TESTING.md).
- Most of the 90 boards are built from the official Betaflight targets and have not been flown with the 3D Edition.

## Roadmap

- Whoop logs on v0.3.3, and a full 5-inch pack with dynamic idle.
- A better estimate of the per-direction trim (it stores a noisy average today).
- Prepare upstream pull requests (Betaflight `master`, one fix per PR, stock defaults). The reverse airmode bounds fix applies to stock Betaflight as is.
- Per-direction thrust / TPA.

## All the documents

| | |
|---|---|
| **[PRESETS.md](PRESETS.md)** | The two presets: requirements, steps, what they set and leave alone |
| **[HOW_IT_WORKS.md](HOW_IT_WORKS.md)** | Every change from stock Betaflight: how it works and why, settings reference, evidence |
| [BOARDS.md](BOARDS.md) | Firmware for all 90 boards |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | Pilot testing guide: 4 packs, stock vs 3D Edition |
| [FEATURE_TESTING.md](FEATURE_TESTING.md) | Bench and flight tests for the safety fixes |
| [CHANGELOG.md](CHANGELOG.md) | Version history and upgrade notes |
| [BUILD_FROM_SOURCE.md](BUILD_FROM_SOURCE.md) | Build the firmware yourself |
| More tune files | [best 3D settings](tunes/3D_Edition_best_settings_v0.3.1.txt) (just the 3D settings, any board with RPM telemetry; its dynamic idle value 50 is for whoops, use 30 on a 5-inch) · [Lucid testing-guide Block A](tunes/3D_Edition_starter_tune_TBS_LUCID_AIO.txt) (**stock** 3D behaviour for A/B testing, not for normal flying) · [ZoeFPV's full Lil Horny CLI](tunes/ZoeFPV_LilHorny_v0.3.3_full_CLI.txt) (reference; don't paste it whole) |

## Credits and license

Betaflight 3D Edition is a fork of [Betaflight](https://github.com/betaflight/betaflight) by the Betaflight team. Like Betaflight,
the firmware and its source are licensed under **GPL-3.0**. The guide and tune files in this folder follow
the [Drones repo license](../README.md#license).
Developed and flight-tested by **ZoeFPV** on "[Lil Horny](../Lil%20Horny/)" and the Unicorn 5-inch, with logs from fellow 3D pilots.
