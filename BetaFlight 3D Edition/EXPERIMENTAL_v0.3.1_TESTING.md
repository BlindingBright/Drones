# BetaFlight 3D Edition v0.3.1-experimental: testing guide

> **⚠ EXPERIMENTAL AND UNTESTED.** This is the active working branch that ZoeFPV is testing internally. It has passed the unit
> tests and a build for every board, but **it has not flown yet**, and bench tests 1–3 below are the first check of fixes 1–3 on
> real hardware (the unit tests cover the 3D math, not the wiring into Betaflight's throttle and failsafe code). For normal testing use the stable
> **[v0.3.0-test](README.md)**. Fly this only if you're comfortable bench-testing first and sending logs.

| | |
|---|---|
| Firmware | [v0.3.1-experimental release](https://github.com/BlindingBright/betaflight/releases/tag/v0.3.1-experimental) (44 boards, same names as [BOARDS.md](BOARDS.md)) |
| Version check | CLI `version` shows `4.5.1 ... (d9ea2fd30)` |
| Source | branch [`3d-v0.3.1-experimental`](https://github.com/BlindingBright/betaflight/tree/3d-v0.3.1-experimental) |
| Stable version | v0.3.0-test, branch `3d-iterm-memory` / `3d-v0.3` |
| Logs | [log form](https://forms.gle/Vfq3c2W7Lp5FE36t5): say "v0.3.1-experimental" in the report |

## What's in it

v0.3.1 = v0.3.0 + four **fixes** to how Betaflight behaves in 3D:

| # | Fix | Active when | What it does |
|---|---|---|---|
| 1 | Low-voltage cutoff | `vbat_cutoff_percent` < 100 | Throttle is cut back toward stick center (zero thrust), not toward full reverse |
| 2 | Failsafe stage 2 throttle | failsafe stage 2 (signal lost) | Never reverse thrust: `failsafe_throttle` at or below 1500 gives zero thrust, above 1500 upright thrust as before |
| 3 | `thr_mid` | `thr_mid` ≠ 50 | Stick center stays zero thrust whatever `thr_mid` is |
| 4 | Sag compensation | `vbat_sag_compensation` > 0 | Works in 3D (stock silently skips it) |

Fixes 1–3 are on by themselves in normal 3D mode (center stick = stopped). They only change anything if you use those
settings, and then only to remove reverse thrust that stock Betaflight would command. 3D switched mode and the 3D mode switch
keep stock behaviour. Fix 4 is off until you set `vbat_sag_compensation`.

## Before you start

- [ ] Back up `diff all` (Configurator → CLI → `diff all` → Save to File).
- [ ] Flash the v0.3.1-experimental `.hex` for **your** board; `version` shows `(d9ea2fd30)`.
- [ ] Battery **unplugged** for every paste / save / disconnect (3D: saving with a battery in can spin the motors up).
- [ ] **Props off** for every bench test below.
- [ ] Before each bench test, type `get <setting>` for each setting it changes and **note your values**, so you can put them back.

### Base settings (the v0.3.0 best settings)
Paste on top of your own tune (needs RPM telemetry, `dshot_bidir = ON`). Without RPM telemetry, leave out the two RPM-based lines
and the dynamic idle lines (see the main [testing guide](TESTING_GUIDE.md), Block B).
```
set 3d_iterm_mode = PER_DIRECTION
set 3d_iterm_release = RPM
set 3d_iterm_load = FLIP
set 3d_anti_gravity = GATED
set 3d_ag_approach_pct = 15
set 3d_dyn_idle = ON
set debug_mode = 3D_ITERM
profile 0
set dyn_idle_min_rpm = 50
set dyn_idle_max_increase = 100
save
```
`dyn_idle_min_rpm`: 50 for 1S/2S whoops (flown); 30 for 5-inch (log replay only, not flown).

- [ ] Bench check (props off): arm with the stick centered, ~10 reversals through center. All four motors restart cleanly,
      center stick settles back to idle. Disarm.

### What the base settings already do (from v0.3.0)
| Setting | What it does | How it was tested |
|---|---|---|
| `3d_iterm_mode = PER_DIRECTION`, `3d_iterm_release = RPM`, `3d_iterm_load = FLIP` | Remembers the I-term trim for upright and inverted, loads the right one at each flip, releases the hold as soon as all motors have restarted (~150 ms instead of a fixed 250 ms) | Lil Horny, 2 days: trim error after a flip ~65% smaller, drift ~20% lower |
| `3d_anti_gravity = GATED`, `3d_ag_approach_pct = 15` | Anti-gravity stops treating every flip as a throttle chop | Lil Horny, 1 day A/B (with dyn idle): less shake in the first 60 ms after a flip |
| `3d_dyn_idle = ON` + `dyn_idle_*` | Dynamic idle works in 3D; gives the restarting motors more command after a flip | Same A/B; restart command ~10% instead of ~3%, no stalls |

## Test 1: low-voltage cutoff (bench, props off, ~5 min)

**What it does.** When the battery hits `vbat_min_cell_voltage`, the low-voltage cutoff scales the throttle down to
`vbat_cutoff_percent`. Stock Betaflight scales toward the bottom of the stick. In 3D the bottom is full reverse, so at 50% a
centered stick became about half reverse throttle: the quad would drive itself into the ground (or the sky, inverted) the moment
the cutoff kicked in. v0.3.1 scales toward stick center instead.

**How to test.** Note your values first: `get vbat_cutoff_percent`, `get vbat_min_cell_voltage`. This forces the cutoff on
with a charged battery:
```
set vbat_cutoff_percent = 50
set vbat_min_cell_voltage = 420
save
```
- [ ] Props off, battery in, arm with the stick centered. The cutoff triggers right away and ramps down to 50% over about
      10 seconds. **Confirm it engaged** (critical-battery warning on the OSD or beeper) before judging; a LiHV pack or one resting
      above 4.20 V/cell won't go critical. Wait those 10 s before the checks below.
- [ ] **Stick centered: motors stay at idle** (stock: they spin up in reverse).
- [ ] Full forward stick: forward thrust, roughly half of normal. Full reverse stick: reverse thrust, roughly half.
- [ ] Disarm, unplug, **put your values back** (Betaflight defaults: `vbat_cutoff_percent = 100`, `vbat_min_cell_voltage = 330`),
      then `save`.

## Test 2: failsafe stage 2 throttle (bench, props off, ~5 min)

**What it does.** When the radio link is lost for longer than `failsafe_delay`, Betaflight enters failsafe stage 2 and puts
`failsafe_throttle` on the throttle channel (default 1000). In 3D, 1000 is **full reverse**. With `failsafe_procedure = DROP`
(default) the quad disarms right away, so it's a blip; with `AUTO-LAND` it's held for `failsafe_off_delay` (about a second by
default), and even a "gentle landing" value like 1300 is 40% reverse. v0.3.1: values at or below 1500 give zero thrust; values
above 1500 are upright thrust, as before. Failsafe switches to angle mode (if your board has an accelerometer), which levels the
quad upright, so upright thrust is the right direction to land with. Without an accelerometer the quad isn't levelled, and
AUTO-LAND isn't a good idea in 3D anyway.

**How to test.** Note your values first: `get failsafe_procedure`, `get failsafe_throttle`.
```
set failsafe_procedure = AUTO-LAND
set failsafe_throttle = 1000
save
```
- [ ] Props off, battery in, arm with the stick centered (motors idle).
- [ ] Switch the transmitter off. After about 1.5 s (stage 1), stage 2 starts: **motors stay at idle until they disarm**
      (stock: they spin up in full reverse for about a second).
- [ ] Optional, above-center value: `set failsafe_throttle = 1600`, save. Arm, switch the transmitter off: in stage 2 the motors
      run ~20% **forward** (upright), also if you were holding reverse throttle before the loss. They never run in reverse.
      (On the bench the quad can't level, so it simply shows forward thrust.)
- [ ] Disarm, unplug, **put your values back** (Betaflight defaults: `failsafe_procedure = DROP`, `failsafe_throttle = 1000`),
      then `save`.

## Test 3: `thr_mid` (bench, props off, ~3 min)

**What it does.** The throttle curve (`thr_mid`, `thr_expo`) is laid over the whole stick. In 3D, `thr_mid` sits at stick center,
so anything other than 50 moved zero thrust away from center: with `thr_mid = 45`, center stick gave 1450, which with a small
3D deadband is already reverse. v0.3.1 keeps the curve centered in normal 3D (`thr_expo` still works); with the 3D mode switch active, `thr_mid`
works as in 2D.

**How to test.** Note your value first: `get thr_mid`.
```
set thr_mid = 45
save
```
- [ ] Props off, battery in, arm with the stick centered. **Motors stay at idle** (stock: center stick is in reverse).
- [ ] Throttle feels the same both ways from center.
- [ ] Disarm, unplug, put your value back (default 50), `save`.

## Test 4: sag compensation (flight, 2 + 2 packs)

**What it does.** `vbat_sag_compensation` holds back the top of the motor range when the battery is full and gives it back as
the voltage drops, so the quad feels the same at the start and end of a pack. Stock Betaflight only does this in 2D. v0.3.1
takes the same fraction off the top of the direction the motors are running; idle and dynamic idle are untouched.

The amount follows Betaflight's stock math: most at 4.20 V/cell, nothing at `vbat_warning_cell_voltage` (3.50 V by default).
**Expect a small effect on whoops:** Lil Horny's packs sit at ~3.85 → 3.4 V/cell under load, so the replay says it would hold
back ~6% at the start of a pack and almost nothing after. Packs that stay higher under load (bigger quads) should see more.

**How to test.** Same props, same spot, battery in the marked position, fly all 4 packs the same way (20+ flips, hold the new
direction 1–2 s after most).
- [ ] Packs 1–2: base settings as above.
- [ ] Packs 3–4, battery unplugged, add:
```
profile 0
set vbat_sag_compensation = 100
save
```
- [ ] Bench check props off, then fly.
- [ ] Notice: do the first and last minutes of a pack feel more alike? Any loss of punch at the start of a pack?

## What to send

Upload through the [log form](https://forms.gle/Vfq3c2W7Lp5FE36t5) (say "v0.3.1-experimental"), or ZoeFPV's testers drop logs
in the shared Drive folder. Per test:
1. Tests 1–3: did the motors do what the checkbox says? Anything unexpected (stutter, wrong direction, no disarm)?
2. Test 4: which pack had which settings; first vs last minute of the pack; anything odd (stalls, desyncs, hot motors).
3. Board, ESC firmware, motors/props/cells.
4. Optional, for slower boards (F411): CLI `tasks` output with the base settings, so we can confirm the PID loop time.

## Safety

- Battery unplugged for every paste, save and disconnect.
- Props off for tests 1–3. Put every setting back after each bench test.
- If anything behaves unexpectedly: disarm, unplug, flash v0.3.0-test or official Betaflight, paste your `diff all` backup.
