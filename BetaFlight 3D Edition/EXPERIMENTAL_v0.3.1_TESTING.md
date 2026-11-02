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

## Before tests 1–3: switch position and logs

- [ ] **3D must be ON (3D mode switch off).** Fixes 1–3 only act in normal 3D; with the 3D mode switch (`3D DISABLE / SWITCH`)
      active, Betaflight flies forward-only and keeps its stock behaviour. Use the switch position you fly 3D in: if you can't
      reverse the motors, you're in the wrong position. (Example: with `aux 1 29 1 900 1700`, 3D is on only with AUX2 above 1700.)
- [ ] **Leave blackbox on.** The bench tests are armed, so they log. Props-off motor sound can fool you (angle mode and PID twitch
      the motors, and direction at idle is hard to see), so judge each test from the log values given below, too.
- [ ] Keep the quad **flat and still** on the bench.

## Test 1: low-voltage cutoff (bench, props off, ~5 min)

**What it does.** When the battery goes critical, the low-voltage cutoff scales the throttle down to `vbat_cutoff_percent` over
10 seconds. Stock Betaflight scales toward the bottom of the stick. In 3D the bottom is full reverse, so at 50% a centered stick
became about half reverse throttle: the quad would drive itself into the ground (or the sky, inverted) the moment the cutoff
kicked in. v0.3.1 scales toward stick center instead.

**How to test.** Note your values first: `get vbat_cutoff_percent`, `get vbat_min_cell_voltage`, `get vbat_warning_cell_voltage`.
Betaflight only reaches *critical* by passing through *warning*, so both thresholds go above a charged pack:
```
set vbat_cutoff_percent = 50
set vbat_warning_cell_voltage = 450
set vbat_min_cell_voltage = 440
save
```
- [ ] Props off, plug in a charged pack (not above 4.40 V/cell), arm with the stick centered. The cutoff triggers right away and
      ramps down to 50% over about 10 seconds. **Confirm it engaged** (critical-battery warning on the OSD/goggles) before judging.
      Wait those 10 s before the checks below.
- [ ] **Stick centered: motors stay at idle** (stock: they spin up in reverse). Log: `rcCommand[3]` ≈ 1500.
- [ ] Full forward stick: forward thrust, reduced. Full reverse stick: reverse thrust, reduced. With `thr_expo = 25` the log shows
      `rcCommand[3]` ≈ 1705 / ≈ 1295 (about 40% each way; without throttle expo it's 50%).
- [ ] Disarm, **unplug** (the cutoff stays latched until power-off), **put all three values back** (Betaflight defaults:
      `vbat_cutoff_percent = 100`, `vbat_min_cell_voltage = 330`, `vbat_warning_cell_voltage = 350`), then `save`.
      The warning voltage matters: sag compensation (test 4) uses it and switches itself off if it's left above the full voltage.

## Test 2: failsafe stage 2 throttle (bench, props off, ~5 min)

**What it does.** When the radio link is lost for longer than `failsafe_delay`, Betaflight enters failsafe stage 2 and puts
`failsafe_throttle` on the throttle channel (default 1000). In 3D, 1000 is **full reverse**. With `failsafe_procedure = DROP`
(default) the quad disarms right away, so it's a blip; with `AUTO-LAND` it's held for `failsafe_off_delay` (about a second by
default), and even a "gentle landing" value like 1300 is 40% reverse. v0.3.1: values at or below 1500 give zero thrust; values
above 1500 are upright thrust, as before. Failsafe switches to angle mode (if your board has an accelerometer), which levels the
quad upright, so upright thrust is the right direction to land with. Without an accelerometer the quad isn't levelled, and
AUTO-LAND isn't a good idea in 3D anyway.

**Important:** in 3D a centered stick counts as *throttle low*. If the throttle has been low for longer than
`failsafe_throttle_low_delay` (10 s) when the link drops, Betaflight treats the quad as landed and disarms immediately: stage 2
never runs and the test proves nothing. So the throttle must be **off center at the moment you switch the transmitter off**.

**How to test.** Note your values first: `get failsafe_procedure`, `get failsafe_throttle`.
```
set failsafe_procedure = AUTO-LAND
set failsafe_throttle = 1000
save
```
- [ ] Props off, battery in, arm. Give a **little forward throttle** (motors clearly above idle) and, **while holding it**, switch
      the transmitter off.
- [ ] About 1.5 s at idle (stage 1), then stage 2 for about 1 s: **motors stay at idle**, then they disarm
      (stock: full reverse for that second).
- [ ] Log check: the failsafe phase goes to **2 (LANDING)** before 3 (LANDED), and `rcCommand[3]` ≈ 1500 during it. If the phase
      jumps straight to 3, stage 2 didn't run: repeat with the throttle held further off center.
- [ ] Optional, above-center value: `set failsafe_throttle = 1600`, save, repeat. In stage 2 the motors run ~15% **forward**
      (`rcCommand[3]` ≈ 1576), also if you were holding reverse throttle before the loss. They never run in reverse.
      (On the bench the quad can't level, so it simply shows forward thrust.)
- [ ] Disarm, unplug, **put your values back** (Betaflight defaults: `failsafe_procedure = DROP`, `failsafe_throttle = 1000`),
      then `save`.

## Test 3: `thr_mid` (bench, props off, ~3 min)

**What it does.** The throttle curve (`thr_mid`, `thr_expo`) is laid over the whole stick. With throttle expo, `thr_mid` moves the
curve's flat spot, and in 3D that moved zero thrust away from stick center: with `thr_expo = 25` and `thr_mid = 25`, center stick
gave 1442, about 11% reverse. (Without throttle expo `thr_mid` changes nothing, in stock or here.) v0.3.1 keeps the curve centered
in normal 3D (`thr_expo` still works); with the 3D mode switch active, `thr_mid` works as in 2D.

**How to test.** This needs throttle expo (`get thr_expo`; if it's 0, `set thr_expo = 25` for the test). Note your values first:
`get thr_mid`, `get thr_expo`.
```
set thr_mid = 25
save
```
- [ ] Props off, battery in, arm with the stick centered. **Motors stay at idle** (stock: ~11% reverse). Log: `rcCommand[3]` ≈ 1500.
- [ ] Throttle feels the same both ways from center.
- [ ] Disarm, unplug, put your values back (default `thr_mid = 50`), `save`.

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
- [ ] Packs 3–4, battery unplugged, first check `get vbat_warning_cell_voltage` shows your normal value (default 350), then add:
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
