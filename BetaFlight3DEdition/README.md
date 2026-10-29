# BetaFlight 3D Edition

**Betaflight with improvements for 3D (reversible-motor) flight.** Tic-tocks, punch-outs from reversals, and flips
through center should hold their attitude better instead of drifting after every motor reversal.

> **Status: v0.1.0-test (experimental).** Built on Betaflight 4.5.1 for the **TBS Lucid AIO 1-2S**.
> We need logs from more pilots to prove it before proposing it to the main Betaflight project.
> Use it for testing. For everyday flying, official Betaflight is the safe choice.

## Downloads

| | File | |
|---|---|---|
| **Firmware: TBS Lucid AIO 1-2S** | `BetaFlight3DEdition_v0.1.0-test_TBS_LUCID_AIO.hex` | **[⬇ Download](https://github.com/BlindingBright/betaflight/releases/download/v0.1.0-3d-test/BetaFlight3DEdition_v0.1.0-test_TBS_LUCID_AIO.hex)** · [copy in this folder](firmware/TBS_LUCID_AIO/BetaFlight3DEdition_v0.1.0-test_TBS_LUCID_AIO.hex) · [release page](https://github.com/BlindingBright/betaflight/releases/tag/v0.1.0-3d-test) |
| **Pilot testing guide** | [TESTING_GUIDE.md](TESTING_GUIDE.md) | **Start here** |
| **Starter tune** (paste in CLI) | [3D_Edition_starter_tune_TBS_LUCID_AIO.txt](tunes/3D_Edition_starter_tune_TBS_LUCID_AIO.txt) | 3D, motor, filter and PID settings only |
| ZoeFPV's full `diff all` (reference) | [ZoeFPV_LilHorny_diff_all.txt](tunes/ZoeFPV_LilHorny_diff_all.txt) | Contains build-specific settings; don't paste it whole |
| **Source code** | [zip](https://github.com/BlindingBright/betaflight/archive/refs/tags/v0.1.0-3d-test.zip) · [tar.gz](https://github.com/BlindingBright/betaflight/archive/refs/tags/v0.1.0-3d-test.tar.gz) · [browse](https://github.com/BlindingBright/betaflight/tree/3d-iterm-memory) | How to build: [BUILD_FROM_SOURCE.md](BUILD_FROM_SOURCE.md) |

SHA-256 of the Lucid hex: `170a951bc9b7e4c9442fd3cb070f5328d8f59d3019741664842d41ddbe6fc237`.
After flashing, the CLI `version` command shows `4.5.1 ... (481694999)`.

**Other flight controllers:** not built yet. **Contact ZoeFPV for a custom build** (Discord link at
[zoefpv.com](https://zoefpv.com)), or [build it yourself](BUILD_FROM_SOURCE.md).

## Send logs & feedback

### 👉 Log upload form: coming soon. Until then, attach logs to a [GitHub issue](https://github.com/BlindingBright/Drones/issues/new)

You can upload several `.BBL` logs at once, along with your drone details, an AM32 settings screenshot and a short report. Every
log helps. Results from different motors, props and frames are what tell us whether a change really works.
Bugs and ideas are also welcome as [GitHub issues](https://github.com/BlindingBright/Drones/issues).

## What's different from Betaflight 4.5.1

Every new setting **defaults to stock behaviour**, so flashing this alone changes nothing until you turn a feature on.

| Setting | Values | What it does |
|---|---|---|
| `3d_iterm_mode` | `RESET` (stock) / `HOLD` / `PER_DIRECTION` | What happens to the I-term when the motors reverse. `PER_DIRECTION` keeps a separate learned trim for upright and for inverted, on all three axes, and loads the right one on each flip. It also stops the I-term changing while the props pass through zero rpm, so it can't wind up. |
| `3d_iterm_reset_ms` | 0–500 (default 250) | Length of that post-reversal window. Stock Betaflight hard-codes 250 ms. |
| `debug_mode = 3D_ITERM` | | Logs motor direction [0], window active [1], upright trim ×10 [2–4], inverted trim ×10 [5–7]. |
| Blackbox header | | Now records `3d_deadband_throttle`, `3d_iterm_mode` and `3d_iterm_reset_ms`. |

**Why:** stock Betaflight zeroes the I-term for 250 ms after every 3D reversal. A 3D quad needs a different trim upright
than inverted. Logs from three different 3D quads, from two pilots (two whoops and a 5"), show the trims differ by 20–60 units and often
flip sign. So after every flip, the quad drifts until the I-term rebuilds. `PER_DIRECTION` restores the right trim right away.

## Roadmap (ideas found in the logs and the code, not built yet)

- **Motor restart watchdog**: warn and log when a motor fails to restart after a reversal.
- **3D-aware anti-gravity**: anti-gravity treats every reversal as a throttle chop and raises P while the props
  are stopped (test first with `set anti_gravity_p_gain = 0`).
- Per-direction thrust / TPA (whoop props are weaker reversed).
- Fixes for 3D bugs in stock Betaflight: the low-voltage cutoff shifts the 3D center into reverse; a failsafe *landing*
  sends full reverse throttle; `vbat_sag_compensation` and dynamic idle silently do nothing in 3D; and `thr_mid` other
  than 50 shifts the 3D center.

## Credits and license

Betaflight 3D Edition is a fork of [Betaflight](https://github.com/betaflight/betaflight) by the Betaflight team. Like Betaflight,
the firmware and its source are licensed under **GPL-3.0**. The guide and tune files in this folder follow
the [Drones repo license](../README.md#license).
Developed and flight-tested by **ZoeFPV** on "[Lil Horny](../Lil%20Horny/)", with logs from fellow 3D pilots.
