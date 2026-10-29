# BetaFlight 3D Edition: pilot testing guide (TBS Lucid AIO, CrazyBee F4 SX1280)

Thanks for helping test! This guide takes about 20 minutes on the bench plus 4 packs of flying.
Follow it in order. Every step has a checkbox so you can keep your place.

> **Supported boards: TBS Lucid AIO 1-2S, and Happymodel CrazyBee F4 SX1280 (`CRAZYBEEF4SX1280`).**
> The steps are written for the Lucid. **CrazyBee pilots: read [the CrazyBee section](#crazybee-f4-sx1280-crazybeef4sx1280) first**:
> the ESC, firmware file and settings are different.
> Using a different flight controller? Don't flash either file. **[Request a build for your board](https://forms.gle/1p93ZjiqDp1PLWA96)**
> or contact ZoeFPV (Discord link at [zoefpv.com](https://zoefpv.com)).

**What you're testing:** stock Betaflight throws away the I-term (the "trim" the quad has learned) for 250 ms after every
motor reversal. A 3D quad needs a different trim upright than inverted, so after every flip it drifts until the trim
rebuilds. The new setting `3d_iterm_mode = PER_DIRECTION` remembers both trims and restores the right one on each flip.
You'll fly 2 packs with stock behaviour and 2 packs with the new mode, then send the logs.

---

## 0. What you need

- [ ] A 3D-capable quad on a **TBS Lucid AIO 1-2S** (built-in AM32 ESCs)
- [ ] **3D props** (symmetric/reversible) and charged packs. Use fresh, tight props: worn props wreck the logs
- [ ] [Betaflight Configurator](https://github.com/betaflight/betaflight-configurator/releases) and a USB data cable
- [ ] [esc-configurator.com](https://esc-configurator.com) (open in Chrome or Edge) to read your AM32 settings
- [ ] The files (all on the [project page](README.md#downloads)):
  - Firmware: [`BetaFlight3DEdition_v0.1.0-test_TBS_LUCID_AIO.hex`](https://github.com/BlindingBright/betaflight/releases/download/v0.1.0-3d-test/BetaFlight3DEdition_v0.1.0-test_TBS_LUCID_AIO.hex)
  - Starter tune: [`3D_Edition_starter_tune_TBS_LUCID_AIO.txt`](tunes/3D_Edition_starter_tune_TBS_LUCID_AIO.txt)

## 1. Safety first (read this)

- **Unplug the battery before you click Save or Disconnect in Betaflight Configurator.** With 3D + AM32, saving or
  disconnecting with a battery plugged in can spin the motors up to full throttle. Every "save" in this guide assumes
  the battery is unplugged.
- **Props off** for everything on the bench.
- In 3D, **throttle center = motors stopped**, and below center the motors spin backwards. Arm with the stick at center.
- If a motor stops or stutters in the air (an ESC desync), **disarm right away**. A stuck motor that keeps getting
  full command can cook the motor or ESC.
- This is test firmware. Fly somewhere you're happy to crash.

## 2. Back up your current setup

- [ ] Connect the quad by USB (no battery), open the **CLI** tab, type `diff all` and press Enter.
- [ ] Click **Save to File** and keep it somewhere safe. This is your way back.

## 3. Check your ESCs (AM32)

- [ ] Open [esc-configurator.com](https://esc-configurator.com), **Connect**, then **Read Setup**. Read only; don't write anything yet.
- [ ] Make sure **Bi-directional** (3D) is **on for all four ESCs**.
- [ ] **Take a screenshot** of the settings. The log form asks for it, because ESC settings change results a lot.

For reference, these are ZoeFPV's ESC settings. Use them as a starting point, not as rules:

| AM32 setting | ZoeFPV | Notes |
|---|---|---|
| Timing advance | 15° | an AM32 update once reset this to 22.5°, which caused stalls |
| Startup power | 125% | |
| Min duty cycle | 3% | |
| PWM frequency | **by rpm** | fixed 24 kHz / variable 24–48 caused restart desyncs on these motors |
| Complementary PWM | on | |
| Motor KV | default | |
| Stuck rotor protection | off | ZoeFPV's choice. Off means no jam protection after a crash, so disarm fast |

ZoeFPV runs an unreleased AM32 test build from the AM32 developer, which isn't distributed here. On standard AM32 (2.21), the
**PWM "by rpm"** setting matters most for clean 3D reversals.

## 4. Flash the firmware

- [ ] Battery **unplugged**. In Configurator go to **Firmware Flasher**.
- [ ] Click **Load Firmware [Local]** and pick `BetaFlight3DEdition_v0.1.0-test_TBS_LUCID_AIO.hex`.
- [ ] Click **Flash Firmware** and wait for "Programming: SUCCESSFUL".
- [ ] Connect, open the **CLI** and type `version`. You should see **`4.5.1`** and **`(481694999)`**.
- [ ] If your settings were wiped (the quad looks unconfigured), paste your `diff all` backup from step 2 into the CLI
  and press Enter.

## 5. Load the settings

Pick **one** of these:

- **A. Built like Lil Horny** (2S, 0802 motors, 31 mm 3D props): paste the whole
  [starter tune](tunes/3D_Edition_starter_tune_TBS_LUCID_AIO.txt) into the CLI and press Enter. It only changes 3D,
  motor, filter and PID settings. Your receiver, modes, OSD and board alignment stay as they are.
- **B. Different build, keep your own tune:** paste just these lines:
  ```
  set 3d_iterm_mode = RESET
  set 3d_iterm_reset_ms = 250
  set debug_mode = 3D_ITERM
  save
  ```

Then check it took. Reconnect, and in the CLI:
```
get 3d_iterm
get debug_mode
```
- [ ] You should see `3d_iterm_mode = RESET`, `3d_iterm_reset_ms = 250`, `debug_mode = 3D_ITERM`.

> `debug_mode = 3D_ITERM` doesn't show in Configurator's debug dropdown; it is set from the CLI only. It doesn't change how
> the quad flies; it records the new feature in the blackbox log.

## 6. Bench check (props OFF, 2 minutes)

- [ ] Props off, battery in, quad on the bench. Arm with throttle centered.
- [ ] Nudge the throttle up a little: motors spin one way. Nudge it below center: they stop and spin the other way.
  All four should change direction cleanly, every time.
- [ ] Do it about 10 times. If any motor stutters, doesn't restart, or squeals, **stop**. That's an ESC setting or hardware
  issue (see step 3), not the firmware.
- [ ] Disarm, then unplug the battery.

## 7. Fly the test (4 packs)

Fly **2 packs of each mode**. One pack can only show big differences, so two packs per mode are what make the result trustworthy.

| Packs | Set in CLI (battery unplugged, then `save`) |
|---|---|
| **Pack 1 and 2** (stock behaviour) | `set 3d_iterm_mode = RESET` |
| **Pack 3 and 4** (new mode) | `set 3d_iterm_mode = PER_DIRECTION` |

**Before every pack:**
- [ ] Blackbox tab: **Erase flash**. A full flash silently stops recording.
- [ ] Battery unplugged, set the mode, `save`, reconnect, and check with `get 3d_iterm_mode`.
- [ ] Same props, same spot, fully charged pack.

**Each pack (about 90 seconds):** fly this in order, and fly naturally in between if you like:
1. **10 s calm cruise**, upright, mid throttle.
2. **10 tic-tocks**: full stick through center both ways, at a steady rhythm.
3. **5 punch-outs** from inverted (flip, then punch hard), then **5** the other way.
4. **10 s steady inverted hover.**
5. **5 slow** throttle crossings through center.
6. Optional: **3 reversals mid-flip** (the hardest case).

**After every pack:**
- [ ] Battery unplugged. Blackbox tab: **Save flash to file** (or Activate Mass Storage and copy the `.BBL`).
- [ ] Name the file so it's clear, e.g. `YourCallsign_pack3_PER_DIRECTION.BBL`.
- [ ] Jot down how it felt: drift after flips, wobble, stalls, anything odd.

## 8. Send your logs

**[Upload your logs and report here](https://forms.gle/Vfq3c2W7Lp5FE36t5)** (Google Form).

- [ ] Add all your `.BBL` files in one go (up to 10 files, 100 MB each), plus your AM32 screenshot if you have one.
- [ ] Say which `3d_iterm_mode` each log was flown with, and write a few lines about how it felt.

Uploading needs a Google sign-in (that's how Google Forms handles files). No Google account? Zip the logs and attach them to a
[GitHub issue](https://github.com/BlindingBright/Drones/issues/new) instead.

## 9. Troubleshooting

| Problem | What to do |
|---|---|
| `version` doesn't show `(481694999)` | The flash didn't take. Flash again (step 4). |
| `get 3d_iterm_mode` says the setting doesn't exist | You're on stock firmware. Flash again (step 4). |
| A motor stalls, stutters or stops after a reversal | Disarm. Check AM32 settings (PWM **by rpm**, timing 15°), motor solder joints and props. Note it in the [form](https://forms.gle/Vfq3c2W7Lp5FE36t5). |
| The quad drifts or wobbles after flips | That's exactly what we're measuring. Keep flying the protocol and describe it in the [form](https://forms.gle/Vfq3c2W7Lp5FE36t5). |
| Motors spin up when you save or disconnect | The battery is still plugged in. Unplug it first, every time. |
| Want to go back to normal Betaflight | Flash official Betaflight 4.5.1 for TBS_LUCID_AIO, then paste your step 2 backup. |

## CrazyBee F4 SX1280 (`CRAZYBEEF4SX1280`)

Happymodel's F411 AIO with a built-in ExpressLRS receiver and a BLHeli_S 4-in-1 ESC. Follow the guide above, with
these changes:

| Step | On the CrazyBee |
|---|---|
| 0. Files | Firmware: [`BetaFlight3DEdition_v0.1.0-test_CRAZYBEEF4SX1280.hex`](https://github.com/BlindingBright/betaflight/releases/download/v0.1.0-3d-test/BetaFlight3DEdition_v0.1.0-test_CRAZYBEEF4SX1280.hex). Settings: [`3D_Edition_settings_CRAZYBEEF4SX1280.txt`](tunes/3D_Edition_settings_CRAZYBEEF4SX1280.txt). **Don't use the Lucid starter tune** (different motors and ESC). |
| 1. Safety | Same rules. The battery-unplugged rule matters for any 3D quad. |
| 3. ESCs | The ESC runs **BLHeli_S or Bluejay**, not AM32. In [esc-configurator.com](https://esc-configurator.com), set **Motor direction = Bidirectional** on all four ESCs. **Bluejay is recommended**: stock BLHeli_S has no RPM telemetry (no RPM filter, no eRPM in logs). Screenshot the settings for the form. |
| 4. Flash | Pick the CrazyBee `.hex`. The built-in ExpressLRS receiver keeps working; re-check your binding phrase / bind after flashing if it was wiped. |
| 5. Settings | Paste the [CrazyBee settings file](tunes/3D_Edition_settings_CRAZYBEEF4SX1280.txt) on top of your own tune. If you run **Bluejay**, uncomment `dshot_bidir = ON` and `motor_poles`. With stock BLHeli_S, leave `dshot_bidir` off or the quad won't arm. |
| 6–8 | Same bench check, the same 4-pack test and the same [log form](https://forms.gle/Vfq3c2W7Lp5FE36t5). Choose "Other (custom build from ZoeFPV)" as the flight controller and write **CrazyBee F4 SX1280** in the drone details. |

## Other boards

Only the TBS Lucid AIO and the CrazyBee F4 SX1280 are built so far. **[Request a build for your board](https://forms.gle/1p93ZjiqDp1PLWA96)**
(Google Form), contact ZoeFPV (Discord link at [zoefpv.com](https://zoefpv.com)), or compile it yourself, see
[BUILD_FROM_SOURCE.md](BUILD_FROM_SOURCE.md).
