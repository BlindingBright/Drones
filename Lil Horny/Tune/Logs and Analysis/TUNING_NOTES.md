# 3D Whoop Tuning Notes

**Craft:** 31mm props · 0802 16000kv · TBS Lucid AIO (AM32 ESC) · DJI O4 Lite · 2S 300mAh · ~30 g
**Firmware:** Betaflight 4.5.1 (AT32F435), 8k gyro / 8k PID, DShot600 bidirectional, 3D feature ON

## Pass 1 baseline: what the log showed (86 s, 24 reversals)

| Finding | Evidence | Fix in Pass 2 |
|---|---|---|
| **Wrong motor pole count** | Gyro noise line matches 12 poles (164× floor) vs 14 (1.8×) | `motor_poles = 12` |
| Reversals are slow and uneven | ~111 ms to get back to 60% rpm; motors differ by ~50 ms | idle 4%, thrust_linear, AM32 settings |
| Front motors (m1/m3) slowest | Slowest motor in 19 of 24 reversals; they run higher rpm (O4 Lite weight up front) | AM32 braking/startup, idle |
| PID fights the reversal | Motors pinned 2047 vs idle for 150 ms, then overshoot (peak error 48°/s median, 106 p90) | thrust_linear, idle |
| I-term zeroed 250 ms after every reversal | Hard-coded in Betaflight's 3D mixer, so it can't be changed in CLI | Stronger I/yaw so it recovers faster |
| Pitch overshoot | Step peak 1.34 with ~14 Hz ringing | f_pitch 105, d_min_pitch 38 |
| Roll FF overshoot then sag | Peak 1.14 → settles 0.88 | f_roll 110, i_roll 88 |
| Yaw under-holds | Settles at 0.82 of setpoint | p_yaw 50, i_yaw 95 |
| Big voltage sag | 7.86 V → 6.26 V | None. Pilot wants to feel the pack fade as the land cue, so vbat_sag_compensation stays 0 |
| Reverse thrust weaker at low end | At 20% command: 148k fwd vs 121k rev eRPM | (prop physics, so this is for awareness) |

Filters were left unchanged in Pass 2 so the pole fix can be measured on its own. Once the RPM filter is
tracking correctly, Pass 3 can probably open up the gyro/D-term lowpass for less delay.

## Pass 2 results (5 logs: 1 = prop-loss crash, 2/3 = arm blips, 4 = stall crash, 5 = good flight, truncated by full flash)

| Metric (log 5 vs Pass 1) | Pass 1 | Pass 2 |
|---|---|---|
| Steady tracking error roll / pitch / yaw (°/s RMS) | 14.9 / 13.9 / 9.2 | **9.0 / 6.3 / 2.9** |
| Filtered gyro 400–1000 Hz | -26 dB | **-31 dB** (RPM filter now on target) |
| D-term 400–1000 Hz | -21 dB | **-32 dB** |
| Reversal spin-up to 60% rpm (median) | 111 ms | 114 ms (logs 1/4: 122–150 ms) |
| Motor spread at reversal | 51 ms | **77 ms (worse)** |
| Reversal peak error median / p90 | 48 / 106 | **72 / 291 (worse)** |

- **Log 1 crash = prop loss on motor 2 (rear-left):** commanded full, rpm shot to 700k (normal max ~450k), so it was spinning with no load.
- **Log 4 crash = motor 0 (rear-right) failed to restart after a reversal:** 0 rpm while commanded full for 750 ms.
  Motor 0 is also the slowest reverser in log 5. Check that motor (hair/grit, bent shaft, crash damage).
- Reversals got worse while AM32 firmware + ESC settings changed in the same pass as the CLI. Cause found:
  the AM32 2.21 update reset **timing from 15° to 22.5°**. Pass 3 flies with it set back to 15°.
  (Sine startup was already OFF; AM32 settings as of Pass 3: timing 15, comp PWM, variable PWM,
  bidirectional, stuck rotor ON, startup power 100, poles 12, running brake 10.)
- **Roll flutter 10–16 Hz** is new in Pass 2. It grows with throttle and is stronger inverted, and the frequency
  shifts between packs. That fits a loose battery, not a PID gain problem. Fix the mount before touching PIDs.

## Pass 3 results (94 s, one clean flight, battery mount fixed, AM32 timing back to 15°)

| Metric | Pass 1 | Pass 2 (log 5) | Pass 3 |
|---|---|---|---|
| Steady tracking error roll / pitch / yaw (°/s RMS) | 14.9 / 13.9 / 9.2 | 9.0 / 6.3 / 2.9 | **7.7** / 6.6 / 3.0 |
| Motor spread at reversal | 51 ms | 77 ms | **52 ms** |
| Reversal peak error median / p90 | 48 / 106 | 72 / 291 | **54 / 135** |
| Reversal spin-up to 60% rpm | 111 ms | 114 ms | 115 ms (ESC-limited) |
| Step peak roll / pitch | 1.14 / 1.34 | 1.13 / 1.38 | **1.08 / 1.22** |

- Timing 15° fixed the Pass 2 reversal regression; no stalls.
- Remaining "propwash" = **12–15 Hz roll/pitch wobble that grows with throttle** (also present in Pass 1).
  TPA (D cut 65% at full throttle) is the prime suspect. Pass 4: tpa_rate 45 at 1450, d_min_roll 34.
- Low reverse throttle (inverted near center): pitch error ~13 °/s, mostly slow drift not wobble, so it's
  authority / I-term after the hard-coded 250 ms reset. Possible next levers: thrust_linear, anti_gravity.
- Next ESC-only experiment once Pass 4 is settled: AM32 startup power 100 → 120 for faster reversal spin-up.

## Pass 4 results (49 s; crash at 47.8 s was an impact, 9.4 g, motors healthy, trimmed off)

| Wobble 8–60 Hz, roll (upright) | 10–20% | 35–60% | 60–100% |
|---|---|---|---|
| Pass 3 | 7.2 | 5.0 | 8.4 |
| **Pass 4** | **2.3** | **3.5** | **5.8** |

- TPA 45 @ 1450 + d_min_roll 34 cut upright wobble 30–70%. Steady pitch error best yet (5.5).
- Roll step response clean: 1.12 peak, settles at 1.0.
- Cost: D-term noise +50% (80–500 Hz), motor-command jitter 10 → 14 upright, **17 inverted**.
  Inverted is the noisiest state (reverse flow through the ducts is turbulent). Watch motor temps.
- Inverted wobble did not improve (35–60%: 4.5 → 5.7, short sample of 9 s).
- Pitch still overshoots (1.55, only 20 windows). Pass 5: p_pitch 44, f_pitch 95.
- ESC test in Pass 5: AM32 startup power 100 → 120 (reversal spin-up stuck at ~112 ms).
- Pilot report after Pass 4: motor temps fine, so there's still room for D despite the extra noise.

## Pass 5 results (66 s; tree hit at 55.8 s, 7.1 g, recovered, motors fine; analyzed 0–55.5 s)

| Metric | Pass 3 | Pass 4 | Pass 5 |
|---|---|---|---|
| Steady error roll / pitch / yaw | 7.7 / 6.6 / 3.0 | 7.7 / 5.5 / 2.8 | **6.3** / 6.5 / **2.6** |
| Step peak roll / pitch / yaw | 1.08 / 1.22 / 0.86 | 1.12 / 1.55 / 0.85 | **1.03 / 1.35 / 0.92** |
| Pitch t50 (speed) | 11 ms | 11 ms | 17 ms (slower) |
| Reversal spin-up / motor spread | 115 / 52 ms | 112 / 47 ms | 122 / 70 ms (worse) |
| Motor jitter upright / inverted | 10 / 10 | 14 / 17 | 16 / 24 |

- AM32 startup power 120 didn't help reversals, so revert to 100.
- Worst reversal (43.2 s) = 800°/s roll with throttle lingering at center: direction flipped twice in
  140 ms and props were near 0 rpm for ~300 ms. That's physics/technique, not tune.
- **Effective 3D deadband is ±3 µs** (switches at 1497 / 1503 every pass). Almost no dead zone, which is crisp,
  but the slightest dither at center flips direction. Only 1 chatter event in 4 flights, so left as is.
  Raising `3d_deadband_throttle` to ~10–15 would stop it at the cost of a small dead spot.
- Raw gyro noise inverted rising each pass, so likely worn/damaged props. Fresh props for Pass 6.
- Pass 6: d_min_pitch 42, f_pitch 100.

## Pass 6 results: MASTER TUNE (106 s clean flight, fresh props, startup power back to 100)

| Metric | Pass 1 | Pass 6 | Change |
|---|---|---|---|
| Steady error roll / pitch / yaw (°/s) | 14.9 / 13.9 / 9.2 | 7.5 / 6.1 / 2.9 | −50% / −56% / −68% |
| Step peak roll / pitch | 1.14 / 1.34 | **1.00 / 1.13** | overshoot gone / mostly gone |
| Reversal peak error median / p90 | 48 / 106 | **37 / 84** | best of all passes |
| Inverted motor jitter | (Pass 5: 24) | 16 | fresh props fixed it |
| Reversal spin-up | 111 ms | 127 ms | ESC/motor limit, ~110–127 every pass |

Full config: `whoop3d_master.txt`. Remaining ideas, only if something bugs you in flight:
- Yaw tracks at ~0.8 of setpoint in every pass regardless of P/I. Steady yaw error is tiny, so only chase it if yaw feels loose.
- `3d_deadband_throttle` (currently ±3 µs) if center-stick direction flips ever annoy you.
- Fresh props after crashes. Pass 5→6 showed worn props alone raised inverted noise 50%.

## Pass 11 tic-tock wobble → Pass 12 (2026-10-08)

Tic-tocks at 54–58 s and 62–69 s: wobble bursts sit in the ~0.5 s after **every** direction switch
(props spinning back up into the quad's own wash), calm during the steady full-throttle swings.
`tools/post_reversal.py`, wobble r/p (°/s) by time since switch:

| Log | 0–130 ms | 130–250 ms | 250–500 ms | calm |
|---|---|---|---|---|
| Pass 1 | 5.3 / 5.0 | 13.5 / 9.3 | 13.1 / 8.3 | 5.5 / 4.9 |
| Pass 6 | 3.4 / 3.3 | 9.9 / 5.9 | 11.2 / 8.9 | 4.0 / 2.8 |
| Pass 11 | 7.9 / 6.2 | 18.1 / 12.3 | 17.7 / 11.5 | 3.9 / 3.2 |

- Present in every pass (not caused by the AM32 change). ~12 Hz. Throttle there is 22–46%, below the TPA
  breakpoint, so TPA isn't cutting D. The 130–250 ms window is also when Betaflight holds I-term at zero (hard-coded).
- Roll is ~50% worse than pitch and has less D. Pass 13: d_min_roll 34→38, d_roll 40→44 (matching pitch).
- Pass 12 (flown first, pilot's choice): dshot_idle_value 400 → 200. AM32 min duty 3 adds on top of BF idle
  (effective ~7% now), so 2% puts it back near ~5%. Watch center float, center-crossing smoothness, and the 0–130 ms wobble.
- Expect a reduction, not elimination; some of this is the physics of flying through your own wash.

## Pass 12 results: idle 4% → 2% (67 s; branch hit at 40.9 s and odd last 2 s trimmed: `@0-39.5+@41.5-64.5`)

| | Pass 11 (idle 4%) | **Pass 12 (idle 2%)** |
|---|---|---|
| Idle eRPM upright / inverted | 82k / 108k | **79k / 79k** (back to pre-ESC-test level) |
| Switch time median / p90 | 126 / 148 ms | 126 / 160 ms |
| Stop / restart phase | 84 / 36 ms | 76 / 43 ms |
| Attitude kick during switch, median / p90 | 84 / 185 | **48 / 161** |
| Post-switch wobble 0–130 / 130–250 / 250–500 ms (roll) | 7.9 / 18.1 / 17.7 | 7.0 / **20.7** / 16.3 |
| Same, pitch | 6.2 / 12.3 / 11.5 | **4.8 / 11.0 / 8.0** |
| Steady error r / p / y | 9.3 / 8.2 / 3.8 | **7.9 / 7.1 / 3.6** |
| Step peak roll / pitch | 1.06 / 1.22 | 1.04 / 1.20 |

- Keep 2%: same switch speed, center crossings ~40% smoother, inverted idle no longer higher than upright.
- Remaining hot spot: roll 130–250 ms after a switch (20.7). That's the target of Pass 13 (roll D 38/44).

## Pass 13 results: roll D 38/44 (98 s; crash at 97.55 s = collision while inverted, tracking clean right before)

| Roll wobble after a switch (°/s) | 0–130 | 130–250 | 250–500 | 500–1000 ms |
|---|---|---|---|---|
| Pass 12 | 7.0 | 20.7 | 16.3 | 9.7 |
| **Pass 13** | **6.0** | 20.9 | **13.6** | **8.3** |

- Attitude kick during switches: median 43, p90 108, the best of any pass (Pass 12: 48 / 158).
- Pilot: "feels better". Kept, and the master is updated.
- The 130–250 ms roll peak did not move with more D. That window = Betaflight's hard-coded I-term hold +
  motors finishing their restart at different times (35–42 ms spread); roll has less inertia than pitch so it shows more.
  Likely the floor for this hardware/firmware combination.
- Cost: roll D-term 20–80 Hz +48% upright, motor jitter 15 → 18 upright, 20 → 24 inverted.
  Pilot report after Pass 13: motor temps fine.
- Pass 14 (optional): thrust_linear 20 → 10, since the ESC now provides the low-end boost.

## Pass 14 results: thrust_linear 10 (128 s, no impacts; flash filled up). KEPT, master updated

| Wobble after a switch, roll / pitch (°/s) | 0–130 | 130–250 | 250–500 | 500–1000 ms |
|---|---|---|---|---|
| Pass 13 (TL 20) | 6.0 / 4.6 | 20.9 / 11.1 | 13.6 / 10.1 | 8.3 / 6.3 |
| **Pass 14 (TL 10)** | 7.0 / 5.5 | **9.1 / 6.5** | **10.4 / 7.5** | 8.6 / 7.1 |

- The 130–250 ms peak D couldn't touch dropped 56%: the ESC and thrust_linear were both boosting the restart.
- Low-rpm eRPM ripple 2.1k → 1.2k (smoothest yet); inverted motor jitter 24 → 17; switch kick p90 108 → 82 (best).
- Switch time unchanged (125 ms).
- Cost: inverted near center (REV 10–35% output) pitch tracking a bit looser (full-band 9–13 → 12–17 °/s), over ~3 s of flight.
- Roll step peak 1.04 → 0.93 (slightly soft). Optional Pass 15: f_roll 110 → 120.
- Remaining reversal flutters: (1) reversing mid-flip, where the front motors pin at the new-direction idle and pitch
  overshoots (3D mixer limit); (2) impossible eRPM jumps 60–140 ms after switches (`tools/erpm_glitch.py`):
  present on AM32 2.21 at every setting (~0.1–0.8 per reversal), ~none on factory 2.03, mostly motor 0 (ESC M1, the
  motor that stalled in Pass 2). Either 2.21 restart telemetry or brief desyncs. Worth sending to Alka, and check motor 0.

## AM32 ESC settings (esc-configurator.com, Chrome, battery plugged in, props off)

Read the settings first and **screenshot them as a backup**. All 4 ESCs should match.

| Setting | Recommend | Why |
|---|---|---|
| Bidirectional / 3D | **ON** | Required for 3D (already on, since it flies) |
| Motor poles | **12** | Matches the motors |
| Complementary PWM | **ON** | Active braking lets the prop stop faster before it reverses |
| Sinusoidal startup | **OFF** (keep) | Sine range is 15% but idle is 4%, so with it ON every reversal would run in slow open-loop sine mode |
| Low RPM power protect | not shown in Multi ESC Config Tool 1.86 | |
| Stuck rotor protection | ON for now | Possible reason motor 0 never retried in the log 4 stall. Revisit only if stalls repeat at 15° timing |
| Stall protection | OFF | Meant for crawlers |
| Startup power | **100** | 120 tested in Pass 5: reversals got slower/less even. Keep 100 |
| Timing advance | **15°** | AM32 2.21 update silently reset it to 22.5°, and Pass 2 flew at 22.5°. Prime suspect for the slower reversals and the motor 0 restart failure |
| Motor KV | 10220 (field max) | Real motors are 16000kv but AM32 can't store more than 10220; leave it at max |
| Running brake level | 10 (max) | Good: strongest braking on decel = faster stop before reversal |
| PWM frequency | leave, or try 48 kHz | Smoother/quieter on tiny motors, small efficiency cost |

**Updating AM32:** in esc-configurator, flash the latest **stable** release for the *exact same target name*
the ESC reports now (Lucid AIO = AT32F421). Flashing can reset settings, so re-apply the table above.
Change ESC things in a **separate flight** from CLI changes so we can tell what helped.

## Test procedure per pass
1. Paste the CLI file, `save`, and check the motors tab (props off) that all 4 spin correctly both directions.
2. Fly a full pack with a mix of: slow center crossings, fast flips through center, inverted hover, punch-outs.
3. Drop the .BBL in this folder and run `.\analyze.ps1 "Pass 2 Full Flight.BBL" "Pass 2"`.
4. Compare rows in `reports/scorecard.csv`. Key numbers: `rev_spinup_ms_med`, `rev_motor_spread_ms_med`,
   `rev_peak_err_med/p90`, `step_peak_*`, `gyro_unfilt_400_1000_db_roll`.
5. Feel and motor temps matter as much as the numbers. Note both.

## Tools (`tools/`)
- `bbl_load.py`: decodes .BBL to numpy (cached .npz)
- `bbl_headers.py`: dumps every config value in the log
- `poles_check.py`: verifies motor_poles from gyro noise vs eRPM
- `reversals.py`: per-reversal motor stop/spin-up timing, motor spread, attitude error, plot of the worst events
- `noise_step.py`: gyro/D-term spectra, filter attenuation, step response, command→rpm by direction
- `scorecard.py`: one-row summary appended to `reports/scorecard.csv`
- `list_logs.py`: lists every log inside a multi-log .BBL (any tool accepts `"file.BBL#N"`)
- `crash.py`: last seconds before a crash, flags prop loss (rpm too high) vs stall (rpm 0 at high command)
- `flutter.py` / `flutter_vs_throttle.py`: 2–60 Hz flutter peaks, and where in the throttle range they live
- `propwash.py`: wobble after throttle chops, and tracking error by motor-output band split upright vs inverted
- `direction_noise.py`: upright vs inverted gyro/D-term noise and motor jitter at the same motor output
- `esc_compare.py`: ESC A/B comparison of switch time (stop / restart / total), motor spread, low-rpm roughness,
  with an overlay plot of median eRPM through reversals (see `ESC_TEST_PLAN.md`)
- `post_reversal.py`: wobble vs time since each direction switch (tic-tocks / post-reversal propwash)
- `ticktock.py`, `timeline.py`, `plot_window.py`: find hard 3D maneuvers, per-second overview, scope plot of a window
- `deadband.py`: actual 3D center deadband from where direction switches, plus chatter count
- `window.py`: quick table of throttle/motors/rpm/gyro over a time range (`window.py file 43.0 43.8`)
- Any tool accepts `"file.BBL@0-47.6"` to trim (e.g. cut a crash off the end)
