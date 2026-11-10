# Presets: ready-to-paste tunes for BetaFlight 3D Edition

Two complete 3D tunes, flown by ZoeFPV, ready to paste into the Betaflight CLI. Flash the firmware for your board, paste the
preset for your quad, check the motors, fly.

| | **31 mm 3D whoop** | **6S 5-inch 3D** |
|---|---|---|
| Preset file | **[LilHorny_31mm_whoop_tune_preset_BF3D_v0.3.3.txt](tunes/LilHorny_31mm_whoop_tune_preset_BF3D_v0.3.3.txt)** | **[Unicorn_5inch_MAIN_tune_preset_BF3D_v0.3.3.txt](tunes/Unicorn_5inch_MAIN_tune_preset_BF3D_v0.3.3.txt)** |
| Flown on | "Lil Horny": TBS Lucid AIO 1-2S, 31 mm props, AM32, 12-pole motors | "Unicorn": Hobbywing XRotor F7 (also a T-Motor F7 twin), 6S, 2010 ~1950 kv, APC 5x4 3D props, AM32, ~700 g with GoPro |
| Firmware | [Lucid AIO hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.3-3d-test/BetaFlight3DEdition_v0.3.3-test_TBS_LUCID_AIO.hex) · [other boards](BOARDS.md) | [XRotor F7 hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.3-3d-test/BetaFlight3DEdition_v0.3.3-test_HOBBYWING_XROTORF7CONV.hex) · [T-Motor F7 hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.3-3d-test/BetaFlight3DEdition_v0.3.3-test_TMOTORF7.hex) · [other boards](BOARDS.md) |
| Dynamic idle | 5000 rpm (flown) | 3000 rpm (hover-tested) |
| PIDs P-I-D (roll / pitch / yaw) | 54-88-46 / 53-95-50 / 50-95 | 35-85-20 / 37-92-21 / 32-85 |
| Flight status | Tune flown on BF3D v0.3.1 (Betaflight 4.5.1), translated to 2026.6. **Not flown on the 2026.6 base yet**: do a hover test first | **Flown** on v0.3.3 over several packs with blackbox logs; the pilot reports it feels close to perfect |

## What a preset is, and why it is not a plain `diff all`

A real `diff all` starts with `defaults` and your board name, and carries your ports, switches, motor order and sensor calibration.
Pasted onto someone else's quad it would wipe their setup or fail on a different board. A preset instead changes **the tune only**:

- **Sets:** the 3D settings, the PIDs and feedforward, the D-term and gyro filters, TPA, anti-gravity, thrust linearisation, dynamic
  idle, stick deadbands, and the 2026.6 defaults the tune depends on, *written out* so an old setup can't leak through.
- **Never touches:** `board_name`, serial ports, `aux` switches, `feature` lines (including `feature 3D`), motor order,
  `yaw_motors_reversed`, accelerometer calibration, `motor_poles`, the PID loop divider (`pid_process_denom`), and your rates.
- **Overwrites** PID profile 0 and names it (`Unicorn` / `LilHorny`). Other profiles are left alone.
- **Rates** are an optional block at the bottom of each file, commented out. Remove the `#` to use ZoeFPV's "Z' Magic" rates.
- **Safe on the wrong firmware:** the file is a command batch. If any line is rejected (for example the `3d_*` settings on stock Betaflight),
  `save` is blocked and **nothing is changed**.

## Before you paste (checklist)

- [ ] BetaFlight 3D Edition **v0.3.3** firmware on your board. `version` in the CLI shows `2026.6.2 ... (fb947bea1)`.
- [ ] 3D already set up and flying: `feature 3D` on, ESCs in bidirectional (3D) mode (AM32 or Bluejay), motor directions right.
- [ ] `dshot_bidir = ON` with `motor_pwm_protocol = DSHOT600` and RPM telemetry working (the RPM filter, 3D RPM release and dynamic idle need it).
- [ ] **Your motor pole count is set** (`motor_poles`: 12 for the usual whoop motors, 14 for 12N14P 2010 motors). Dynamic idle and the RPM
  filter compute rpm from it; a wrong count means wrong rpm.
- [ ] Your PID loop: the 5-inch preset was flown at 4 kHz (8 kHz gyro, `pid_process_denom = 2`). On a 3.2 kHz gyro (BMI270) keep denom 1. Presets leave it alone.
- [ ] Props off for the first check, and a **backup** of your settings.

## How to apply

1. In Betaflight Configurator open the **CLI** tab and type `diff all`. Copy the output somewhere safe: that is your way back.
2. Open the preset file and paste **the whole file** into the CLI box (or use "Load from file"), then Enter.
3. If any `###ERROR###` shows, **nothing was saved**: type `exit` and tell us the line. Otherwise it saves and the board reboots.
4. **Props off**, battery in: arm, and check all four motors spin the right way in both directions and idle smoothly. Disarm.
5. Hover test, then fly. Send your logs if you can: [README](README.md#send-logs--feedback).

To go back: paste your backup `diff all` (it begins with `defaults`, so it restores everything).

## What is in each preset

Both presets set the same 3D behaviour (the v0.3.3 defaults, written out; see [HOW_IT_WORKS.md](HOW_IT_WORKS.md)):
`PER_DIRECTION` I-term memory on all axes, `RPM` release, `FLIP` load, `GATED` anti-gravity with approach 15, 3D dynamic idle on,
`iterm_rotation` OFF, `debug_mode = 3D_ITERM`. Stick settings: `3d_deadband_low 1496`, `3d_deadband_high 1504`, `3d_neutral 1500`,
`3d_deadband_throttle 3`.

| | 31 mm whoop | 5-inch |
|---|---|---|
| Stick deadband (roll/pitch, yaw) | 3 / 3 | 2 / 2 |
| D-term filter | low-pass 1 (PT1) dynamic 90-180 Hz, low-pass 2 180 Hz | low-pass 1 (biquad) dynamic 70-140 Hz, low-pass 2 135 Hz |
| D / D max | 46 / 53 roll, 50 / 55 pitch | 20 / 25 roll, 21 / 27 pitch |
| Feedforward | smoothing 25, averaging off, boost 15 (the 4.5 defaults it was flown with) | 2026.6 defaults (smoothing 65, 2-point averaging), boost 5 |
| TPA | mode D, rate 35, breakpoint 1550 | mode D, rate 60, breakpoint 1350 |
| Thrust linearisation | 10 | 10 |
| Dynamic idle | `dyn_idle_min_rpm 50`, max increase 100 | `dyn_idle_min_rpm 30`, max increase 150 |
| Gyro filters | whoop values (dynamic low-pass 300-600 Hz, one dynamic notch) | 2026.6 simplified filter defaults |

## Adapting a preset to your quad

They are starting points, not magic. Different motors, props, weight or ESC firmware want different PIDs.

- **Soft or loose?** Raise P and feedforward a few percent at a time. **Warm motors or a high-pitched buzz?** Lower D or D max.
- **A touch at centre reverses the motors?** Raise `3d_deadband_throttle` (3 µs either side is tight).
- **Dynamic idle** (`dyn_idle_min_rpm`) must be *below* the rpm your slowest motor idles at with the stick centred (Motors tab or a
  log). Set it to 0 to turn it off.
- **A 6S 5-inch on different motors?** Check motor temperature after the first pack, and keep the loop-rate difference in mind.

## How the presets were made and checked

- The 5-inch preset is the XRotor's saved configuration after the final flight, with only hardware lines removed. Tested by loading it
  from `defaults` onto the XRotor (without saving): 95 lines, no errors, and the result matched the flown configuration with zero differences.
- The whoop preset is generated from the running configuration of Lil Horny after v0.3.3 was loaded; every line was checked against it,
  and nothing the whoop sets differently from default was missed. It has not yet been loaded onto the quad from a preset file.
- Every line was accepted by v0.3.3: the 5-inch file by loading it live (above), the whoop file because its values come from the quad's own
  running configuration.

ZoeFPV's full Lil Horny CLI, with its hardware lines, is here as a reference: [ZoeFPV_LilHorny_v0.3.3_full_CLI.txt](tunes/ZoeFPV_LilHorny_v0.3.3_full_CLI.txt).
Don't paste a full CLI like that on a different board.
