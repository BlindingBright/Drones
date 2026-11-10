# What BetaFlight 3D Edition changes from stock Betaflight, how it works, and why

BetaFlight 3D Edition (BF3D) is stock **Betaflight 2026.6.2** plus about 500 lines of changes, all in the 3D (reversible-motor)
code. Everything else is untouched. This page lists **every** change, what stock Betaflight does in that spot, what BF3D does
instead, and the evidence for it. Settings are collected in the [reference table](#settings-reference) at the end.

> **When none of this applies:** with `feature 3D` off, the firmware flies as stock Betaflight: 2D flight is bit-for-bit unchanged.
> With the 3D mode switch (`3D DISABLE / SWITCH`) active or `3d_switched_mode = ON`, the throttle safety fixes in
> [section 4](#4-throttle-safety-fixes-no-settings) are skipped and stock behaviour applies there.

**Contents**
[Background](#background-what-happens-when-a-3d-quad-reverses) ·
[1. I-term at a reversal](#1-the-i-term-at-a-motor-reversal) ·
[2. Anti-gravity](#2-anti-gravity-at-a-reversal) ·
[3. Dynamic idle in 3D](#3-dynamic-idle-in-3d) ·
[4. Throttle safety fixes](#4-throttle-safety-fixes-no-settings) ·
[5. Reverse mixer fix](#5-reverse-mixer-fix-v033-no-setting) ·
[6. Logging](#6-logging-and-diagnostics) ·
[7. Tried and dropped](#7-tried-and-dropped) ·
[Settings reference](#settings-reference) ·
[What did not change](#what-did-not-change) ·
[Evidence and limits](#evidence-and-limits)

---

## Background: what happens when a 3D quad reverses

In 3D mode the throttle stick centre is "zero thrust". Above centre the motors spin one way (the quad flies upright), below centre
they spin the other way (inverted, or braking). When the stick crosses the small dead zone around centre
(`3d_deadband_throttle`, default 3 µs either side), the flight controller **reverses the motors**:

1. Each motor has to slow to a stop and spin up the other way. For a few tens of milliseconds the props produce almost no thrust.
2. The mixer's sign flips: a roll correction that needed *motor 1 faster* now needs *motor 1 slower*.
3. The "trim" the quad needs flips too. With the centre of gravity not exactly at the thrust centre, an upright quad needs a
   little pitch correction held in its I-term, and an inverted one needs a *different* (often opposite) one.

Stock Betaflight handles (3) crudely, and ignores several other places where 2D logic misbehaves in 3D. That is what BF3D fixes.

---

## 1. The I-term at a motor reversal

### What stock does

Stock Betaflight **sets the I-term of every axis to zero, on every PID loop, for a fixed 250 ms** after any motor reversal.
That is sensible for the first moments (the props have no grip, so integrating would just wind up), but it has three costs:

- **The quad throws away its trim.** After every flip it starts from zero and the I-term has to rebuild from scratch, so the
  quad drifts in pitch until it has. Logs from three 3D quads and two pilots show the upright and inverted trims differ by
  20–60 PID units and often flip sign, so the loss is real, not small.
- **250 ms is too long** on a quad whose motors restart faster (about 120-150 ms measured on a whoop and a 5-inch), and
  too short on a bigger one with slower motors.
- It is a fixed timer, so it ignores what the motors are actually doing.

### What BF3D does

Four separate pieces, each with its own setting, so they can be switched back to stock one by one.

**A. Freeze instead of zero** (`3d_iterm_mode`). During the hold after a reversal the I-term is *frozen*: it neither grows
nor shrinks, so it cannot wind up while the props pass through zero rpm.

| Mode | Behaviour during the hold |
|---|---|
| `RESET` | Like stock: I-term forced to zero (but the *end* of the hold can still be made smarter, see C) |
| `HOLD` | I-term keeps its value and is frozen |
| `PER_DIRECTION` (default) | Load the remembered trim of the *new* direction, then freeze it |

**B. Per-direction memory** (`PER_DIRECTION`). The firmware keeps one remembered I-term per motor direction and per axis.
While the quad flies steadily in a direction, the memory follows the real I-term (a slow low-pass filter,
`3d_iterm_learn_hz_x10`, default 0.5 Hz). At a reversal it loads the memory of the direction you are entering.

It learns only when the numbers are trustworthy: armed and flying, not in a hold, the mixer **not saturated**, and throttle at
least `3d_iterm_learn_thr` (default 50 %) of *this quad's own* average throttle in that direction. That last rule is relative so
it works for any size of quad and keeps the approach to centre (where the I-term swings with deceleration) out of the memory.
`3d_iterm_axes` chooses which axes use the memory (the others restart from zero, like stock). The memory survives a disarm,
not a power cycle.

`3d_iterm_load` chooses *when* the memory is applied: `FLIP` (default) loads it at the reversal and holds it, `RELEASE` keeps the
I-term at zero like stock and loads the memory when the hold ends. `FLIP` was flown more and is the default.

**C. Release when the motors have actually restarted** (`3d_iterm_release = RPM`). Instead of a fixed 250 ms, the hold ends
when **every motor** has restarted, judged from bidirectional-DShot eRPM:

- eRPM is *unsigned* (it cannot tell the direction), so a motor counts as restarted only after its eRPM has dropped **below**
  `3d_iterm_rpm_pct` (default 40 %) of the quad's average in-flight eRPM (the props crossing zero) and then climbed back **above** it.
- The hold lasts at least `3d_iterm_min_ms` (50) and at most `3d_iterm_max_ms` (400), the fallback if a restart is never seen.
- Implausible eRPM jumps are ignored: an AM32 desync reports a fixed high value at once, which a real spool-up never does. A
  reading may rise only as fast as a motor can spin up.
- The in-flight average is taken from steady flight only, so a throttle punch does not inflate it.
- **Without RPM telemetry** (no bidirectional DShot), `RPM` falls back to the fixed time `3d_iterm_reset_ms` (250 by default).
  Never run it without telemetry and expect the 400 ms cap: it will simply use the timer.

Typical measured hold: about 150 ms on a 2S whoop, 120-140 ms on a 6S 5-inch.

**D. Frozen means frozen (v0.3.3).** Betaflight can *rotate* the I-term between axes as the quad rotates (`iterm_rotation`, default
OFF, but many 5-inch tunes turn it ON). Stock rotation kept running during the hold, so a trim loaded for the new direction moved
between axes while the quad finished rolling out of the flip (for example yaw I leaking into roll). v0.3.3 skips the rotation while the
I-term is frozen; stock rotation resumes at release. Found by replaying the rotation maths on logged gyro data: it reproduced the
I-term's change during 55 holds to within about 0.3 units, then vanished (36 of 36 holds with zero change) once fixed.
It has no effect when `iterm_rotation` is OFF.

### Why

A flip is the one moment a 3D quad is both least controllable (props with no grip) and most in need of the right trim.
Stock gives up the trim for a fixed time. BF3D keeps the trim of the direction you are entering and releases it the moment the
props can use it.

### Honest limits

- The memory is a *noisy estimate* of the trim. On Lil Horny pitch trim is large (about +20 to +27 upright, −37 to −57 inverted)
  and the memory beats starting from zero. On the 5-inch the real trim is small next to flip-to-flip variation and the memory is
  often **no better than zero on roll and yaw**; improving the estimate is on the [roadmap](README.md#roadmap).
- Per-pack variation on a single quad is ±20-40 %, so no single flight proves a benefit. That is why logs from other quads matter.

---

## 2. Anti-gravity at a reversal

### What stock does

Anti-gravity watches how fast the throttle moves. A fast change means the battery is sagging or the quad is accelerating, so it
**boosts the I-term gain and P** for a moment. In 3D the throttle *magnitude* passes through zero on every reversal, which looks
exactly like a full throttle chop. Anti-gravity fires on every flip, boosting P while the motors restart.
Measured on the whoop: P up 9-22 % on the approach, 12-14 % during the restart, and I-term gain ×3-4.

### What BF3D does (`3d_anti_gravity = GATED`)

- At the reversal the anti-gravity filter is reset.
- While the I-term is held, the throttle change is ignored.
- `3d_ag_approach_pct` (default 15): also ignore the throttle while it is **falling below this % on the way into a flip**, where
  most of the boost used to happen.

Chops and punches within one direction work exactly as before.

---

## 3. Dynamic idle in 3D

### What stock does

Dynamic idle raises the motor idle when the slowest motor drops below a target rpm, so the motors never get slow enough to stall
or desync. **Stock Betaflight does not run it in 3D at all**: the code lives only in the 2D branch.

### What BF3D does (`3d_dyn_idle = ON`, plus `dyn_idle_min_rpm`)

- Runs the stock dynamic-idle controller in 3D. It measures the slowest motor's rpm from bidirectional DShot, compares it with
  `dyn_idle_min_rpm` (in units of 100 rpm: 30 = 3000 rpm) and adds a P + I + D correction to the idle of the **current direction**.
  The correction is capped by `dyn_idle_max_increase`.
- Right after a flip the slowest motor is near zero rpm, so the controller gives the restarting motors extra command. In
  practice that shortens the restart.
- No 1 % zero-throttle offset when it is on. Stock adds one whenever dynamic idle is configured, even in 3D, where zero throttle is the
  stick centre and the offset adds thrust there.
- A 3D-only change: once every motor is clearly above target (25 % margin) the integral term falls as fast as it rose. Near the target
  it keeps the stock slow fall, so it does not hunt.
- DShot only. **It does nothing until you set `dyn_idle_min_rpm` above 0** (stock default 0) and have RPM telemetry. Set it below
  the rpm your slowest motor idles at with the stick centred.

| Quad | `dyn_idle_min_rpm` | `dyn_idle_max_increase` | Status |
|---|---|---|---|
| 1S/2S whoop (31 mm) | 50 | 100 | Flown on Lil Horny |
| 6S 5-inch | 30 | 150 (default) | Hover-tested; the log shows the slowest motor held at ~3000 rpm |

**5-inch hover log** (XRotor, dynamic idle at 3000 rpm): the slowest motor sat at about 3000-3100 rpm and was below 3000 rpm for
0.13 s and 0.21 s in two tests of about 30 s each, with no stalls, no zero-rpm readings and no desync-like jumps. After a flip all motors were back above
3000 rpm in a median 43-45 ms (73 ms without dynamic idle on an earlier flight), and the lowest rpm reached in the 450 ms after a flip
rose from about 510 to about 740-790. Small sample (31 flips), and the flying differed: the no-dynamic-idle number comes from a hard 102-flip pack, these two from gentle hover tests. The slower tail (p90) did not improve. A full-pack flight is still to come.

---

## 4. Throttle safety fixes (no settings)

Stock Betaflight treats the bottom of the throttle stick as "off". In 3D the bottom of the stick is **full reverse**, and several
2D code paths send you there. These apply in normal 3D (not with the 3D mode switch or `3d_switched_mode`):

| Stock behaviour in 3D | BF3D |
|---|---|
| **Low-voltage cutoff** (`vbat_cutoff_percent` < 100) scales the throttle toward the bottom of the stick, so centre stick turns into reverse thrust | Scales toward stick centre (zero thrust) |
| **Failsafe stage 2** sends `failsafe_throttle` (default 1000 = full reverse) | At or below 1500 gives zero thrust, above 1500 gives upright thrust as before. Failsafe forces angle mode, so the quad levels upright |
| **`thr_mid` / `thr_hover`** other than 50 move zero thrust off stick centre | Stick centre stays zero thrust, whatever those are set to (the expo curve still applies) |
| **`vbat_sag_compensation`** silently does nothing in 3D | Works in 3D, capping the top of the current direction's band by the same fraction as in 2D |
| **Altitude hold** (which 2026.6 also uses for failsafe landing) **and GPS rescue** keep the *last motor direction*: after a link loss in reverse they drive the motors in reverse | Motors run upright while the autopilot sets the throttle |

Defaults (`vbat_cutoff_percent = 100`, `vbat_sag_compensation = 0`, `failsafe_procedure = DROP`, `thr_mid = 50`) keep the first four
from acting, so normal flying never exercises them. They matter the day a battery sags or a link drops. They have unit tests but have **not
been bench-tested on hardware** yet: see [FEATURE_TESTING.md](FEATURE_TESTING.md).

---

## 5. Reverse mixer fix (v0.3.3, no setting)

### What stock does

When the motors run in reverse, the mixer applies the roll/pitch/yaw correction **negated**. But the airmode / throttle limiter
that keeps every motor inside its range computes its limits from the **un-negated** correction. When the corrections are
symmetric the two agree. With roll, pitch and yaw commanded together they are not, so a motor can clip at the end of its range, or
full reverse throttle can be pulled down further than needed. This is in every mixer type, and in stock Betaflight 4.5.1 and 2026.6.2 too.

### What BF3D does

Applies the direction sign when the correction is computed, so the limiter sees exactly what the motors will get. Upright and 2D
flight are bit-identical (the sign is +1). Verified two ways: a unit test that fails on the old code (reverse with PID sums S must equal
forward with −S, for all four mixer types), and a replay of the 5-inch logs, where the logged inverted motor outputs followed the *old* bounds
exactly. On about 4 % of inverted time the old bounds cut 2-3 % (at most 13 %) of the motor band more than needed.

---

## 6. Logging and diagnostics

- `debug_mode = 3D_ITERM` logs: motor direction [0], ms since the reversal while holding (0 once released) [1], upright memory
  ×10 for roll/pitch/yaw [2-4], inverted memory ×10 [5-7]. Please keep it on when you send logs.
- The blackbox header records `3d_deadband_throttle` and every `3d_*` setting, so a log says which behaviour it was flown with.

---

## 7. Tried and dropped

- **Restart sync** (force all four motors to the same command while they restart): the command spread went to zero but the restart
  spread did not change, and the shake after flips got about 25 % worse. Removed.
- **Raw I-term saved at the flip** and **HOLD of the pre-flip I-term**: 2-4 times worse than zero in a replay of logged flips, because
  they capture the throttle chop and deceleration on the approach. This is why the memory is a slow average of *steady* flight.
- **A shorter fixed hold (150 ms)** on the whoop: released before all motors had restarted and pitch wound the wrong way (74 % worse).
- **A new tuning knob per estimator detail**: deliberately not added; BF3D prefers fixed rules and few settings.

---

## Settings reference

All are CLI settings (`get 3d_` lists them). **Stock-equivalent values** (`RESET`, `TIME`, `STOCK`, `OFF`) give stock behaviour for that part.

| Setting | BF3D default | Values | Stock-equivalent | Section |
|---|---|---|---|---|
| `3d_iterm_mode` | `PER_DIRECTION` | `RESET`, `HOLD`, `PER_DIRECTION` | `RESET` | [1A](#1-the-i-term-at-a-motor-reversal) |
| `3d_iterm_release` | `RPM` | `TIME`, `RPM` | `TIME` | 1C |
| `3d_iterm_reset_ms` | 250 | 0-500 | 250 | 1C (the `TIME` hold and the `RPM` fallback) |
| `3d_iterm_min_ms` / `3d_iterm_max_ms` | 50 / 400 | 0-500 / 50-1000 | n/a | 1C |
| `3d_iterm_rpm_pct` | 40 | 10-90 | n/a | 1C |
| `3d_iterm_load` | `FLIP` | `FLIP`, `RELEASE` | n/a | 1B |
| `3d_iterm_learn_thr` | 50 | 0-150 | n/a | 1B |
| `3d_iterm_learn_hz_x10` | 5 (0.5 Hz) | 1-50 | n/a | 1B |
| `3d_iterm_axes` | `ALL` | `ALL`, `PITCH`, `ROLL_PITCH` | n/a | 1B |
| `3d_anti_gravity` | `GATED` | `STOCK`, `GATED` | `STOCK` | [2](#2-anti-gravity-at-a-reversal) |
| `3d_ag_approach_pct` | 15 | 0-50 (0 = off) | 0 | 2 |
| `3d_dyn_idle` | `ON` | `OFF`, `ON` | `OFF` | [3](#3-dynamic-idle-in-3d) |
| `debug_mode` | | `3D_ITERM` | n/a | [6](#6-logging-and-diagnostics) |

To get fully stock 3D behaviour for a comparison: `3d_iterm_mode = RESET`, `3d_iterm_release = TIME`, `3d_iterm_reset_ms = 250`,
`3d_anti_gravity = STOCK`, `3d_dyn_idle = OFF` (the [testing guide](TESTING_GUIDE.md)'s Block A does this). The always-on fixes
(sections 1D, 4 and 5) have no switch.

**Saved settings survive an upgrade on the same Betaflight base** (v0.3.2 to v0.3.3, or 4.5.1 to 4.5.1). New 3D fields are appended to the existing settings
structure with no version bump, so flashing a newer BF3D over an older one keeps your saved 3D deadbands and settings. Across Betaflight bases
(4.5 to 2026.6) paste a full CLI or a preset instead. The flip side: new *defaults* only arrive with a full chip erase,
`defaults`, or by pasting a [preset](PRESETS.md).

---

## What did not change

Everything not listed above is stock Betaflight 2026.6.2: PID controller and filters, rates, RPM filter, dynamic notch,
feedforward, TPA, anti-gravity outside 3D, OSD, receivers, every non-3D feature. 15 source files differ from stock, all in the
mixer, RC/3D handling, PID anti-gravity and iterm-freeze hooks, CLI settings, blackbox header and the debug mode.
Unit tests (real mixer, DShot and RC code, both motor directions): mixer 33, rc_3d 4, PID 18; the full suite runs 62 binaries / 518 tests.
Seven flight-plan tests don't compile with gcc's C++ front end on stock 2026.6.2 either.

---

## Evidence and limits

| What | Where | Result |
|---|---|---|
| Per-direction memory + RPM release + `FLIP` | Lil Horny (2S whoop), 2 test days, 15 flights | Hold ends ~150 ms after a flip (vs 250); learned trims fill to ~100 %; trim error in the 130-250 ms after a flip about 65 % smaller; pitch drift after flips about 20 % lower |
| `GATED` anti-gravity + approach 15 + 3D dynamic idle | Lil Horny, one same-day A/B, 2 + 2 packs, 143 flips | Not worse than stock in any window; about 19 % less shake in the first 60 ms after a flip; restarting motors get ~10 % command instead of ~3 %; no stalls; pilot preferred it. One day, one quad |
| Frozen I-term not rotated (v0.3.3) | 6S 5-inch (XRotor, AM32) | 36 of 36 reversal holds with zero I-term change; v0.3.2 changed up to 41 / 32 / 150 units on roll / pitch / yaw in one hold |
| Reverse mixer bounds (v0.3.3) | same 5-inch | Logged inverted motor outputs follow the corrected bounds in every pack |
| Dynamic idle 3000 rpm | same 5-inch, hover | Slowest motor held at ~3000 rpm, no stalls (see [section 3](#3-dynamic-idle-in-3d)) |
| Safety fixes (section 4) | unit tests only | Not yet bench-tested on hardware |
| Whoop on the 2026.6 base | not flown yet | Same 3D code; tune translated from the flown 4.5 one |

Known open issue: on the 5-inch a small roll twitch (about 25 °/s at ~11 Hz) follows throttle changes. It was already present on stock-like
tunes and is not caused by the 3D changes as far as the logs show; the cause is not found yet.

One quad is not proof. Please [send your logs](README.md#send-logs--feedback).
