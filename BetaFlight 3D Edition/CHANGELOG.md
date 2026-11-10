# BetaFlight 3D Edition: version history

Every version is a test release. Each adds to the one before, and saved settings survive an upgrade (the 3D settings are appended to
the existing settings structure, never reordered). What each change does is explained in [HOW_IT_WORKS.md](HOW_IT_WORKS.md).

| Version | Date | Base | What changed | Boards |
|---|---|---|---|---|
| **[v0.3.3-test](https://github.com/BlindingBright/betaflight/releases/tag/v0.3.3-3d-test)** (current) | 2026-11-10 | Betaflight 2026.6.2 | **Frozen I-term is no longer rotated** (`iterm_rotation` leaked the loaded trim between axes during the hold). **Reverse airmode / throttle limits use the right bounds** (stock applied the upright bounds to reverse motors). No new settings. Flown on a 6S 5-inch. 5-inch and 31 mm whoop **[presets](PRESETS.md)** | 90 |
| [v0.3.2-test](https://github.com/BlindingBright/betaflight/releases/tag/v0.3.2-3d-test) | 2026-11-05 | Betaflight 2026.6.2 | The v0.3.1 3D changes ported to 2026.6.2. New fix: altitude hold (also failsafe landing) and GPS rescue run the motors upright | 90 |
| [v0.3.1-test](https://github.com/BlindingBright/betaflight/releases/tag/v0.3.1-3d-test) | 2026-11-03 | Betaflight 4.5.1 | Best flying settings are now the **defaults**. Fixes where stock sends reverse thrust: low-voltage cutoff, failsafe stage 2, `thr_mid`. `vbat_sag_compensation` works in 3D. RPM release falls back to the timer without RPM telemetry. (A v0.3.1-experimental build existed for a few days: superseded.) The last flown 4.5 version | 89 |
| [v0.3.0-test](https://github.com/BlindingBright/betaflight/releases/tag/v0.3.0-3d-test) | 2026-10-31 | Betaflight 4.5.1 | **`3d_anti_gravity = GATED`** and `3d_ag_approach_pct`; **`3d_dyn_idle`**. "Restart sync" and "reverse gain" were tried and removed. Public best-settings file | 44 |
| [v0.2.2-test](https://github.com/BlindingBright/betaflight/releases/tag/v0.2.2-3d-test) | 2026-10-30 | Betaflight 4.5.1 | **`3d_iterm_release = RPM`** works (release when all motors have restarted); **`3d_iterm_load`** `FLIP`/`RELEASE`; cap `3d_iterm_max_ms` | 44 |
| v0.2.0 | 2026-10-30 | Betaflight 4.5.1 | RPM release (first version), `3d_iterm_axes`, learning settings; the learned memory persists across disarms | Lucid |
| [v0.1.0-test](https://github.com/BlindingBright/betaflight/releases/tag/v0.1.0-3d-test) | 2026-10-29 | Betaflight 4.5.1 | First release: **`3d_iterm_mode`** `RESET`/`HOLD`/`PER_DIRECTION`, `3d_iterm_reset_ms`, debug mode `3D_ITERM`, blackbox header | 41 |

## Upgrading

- **From v0.3.2:** flash v0.3.3 over it. Settings are kept. With `iterm_rotation = ON` the held I-term now stays put.
- **From v0.3.1 / Betaflight 4.5:** 2026.6 renamed D-max (`d_*` is the base D, `d_max_*` the maximum; 4.5 had `d_min_*` / `d_*`) and
  `dshot_idle_value` (now `motor_idle`), so a 4.5 `diff all` does not paste as-is. Back up first, flash, then use a [preset](PRESETS.md)
  or the [testing guide](TESTING_GUIDE.md).
- **From stock Betaflight 2026.6:** your `diff all` pastes straight in.
- New *defaults* only arrive with a full chip erase, `defaults`, or by pasting a preset.

## Branches in the source repository

| Branch | What it is |
|---|---|
| **`3d-v0.3.3`** (default) | Current: v0.3.3-test on Betaflight 2026.6.2 |
| `3d-v0.3.2` | v0.3.2-test (2026.6.2) |
| `3d-iterm-memory` | v0.3.1-test, the flown Betaflight 4.5.1 version |
| `3d-v0.3`, `3d-iterm-v0.2`, `3d-iterm-memory-2026.6` | Older and intermediate versions |
