# BetaFlight 3D Edition: pilot testing guide (v0.2.2-test)

Thanks for helping test! About 20 minutes on the bench, then **4 packs of flying with one settings change in the middle.**

## The short version

| | What you do |
|---|---|
| 1 | Back up your settings (`diff all`) |
| 2 | Flash the 3D Edition file for **your** board ([BOARDS.md](BOARDS.md)) |
| 3 | Paste **Block A** (stock behaviour), bench-check with props off |
| 4 | Fly **pack 1 and pack 2** |
| 5 | Paste **Block B** (the new I-term handling) |
| 6 | Fly **pack 3 and pack 4** |
| 7 | [Upload the 4 logs](https://forms.gle/Vfq3c2W7Lp5FE36t5) and say how it felt |

Everything else below is the detail for each step. Every step has a checkbox so you can keep your place.

**What you're testing:** after every motor reversal, stock Betaflight throws away the I-term (the trim the quad has
learned) and keeps it at zero for a fixed 250 ms. But a 3D quad needs a *different* trim upright than inverted, so after
every flip it drifts until the trim rebuilds. The 3D Edition remembers both trims, loads the right one on each flip,
and (with RPM telemetry) lets the I-term go as soon as all motors have actually restarted (~150 ms on a whoop) instead
of waiting 250 ms. On ZoeFPV's whoop this cut the trim error in the first 250 ms after a flip by about 65%, and the
pitch drift after flips by about 20%. Now we need other quads.

---

## 0. What you need

- [ ] A 3D-capable quad with ESCs that can run **bidirectional (3D)**: AM32, Bluejay, BLHeli_32, or BLHeli_S
- [ ] **3D props** and charged packs. Fresh, tight props; worn props wreck the logs.
- [ ] A flight controller **with blackbox** (onboard flash or SD card). No blackbox? You can still help, see [No blackbox](#no-blackbox-on-your-board).
- [ ] [Betaflight Configurator](https://github.com/betaflight/betaflight-configurator/releases) and a USB data cable
- [ ] [am32.ca/configurator](https://am32.ca/configurator) (Chrome or Edge) to check your ESC settings
- [ ] Your firmware file from **[BOARDS.md](BOARDS.md)** (44 boards). The name must match your board exactly.

## 1. Safety first (read this)

- **Unplug the battery before you click Save or Disconnect in Configurator, and before pasting CLI that ends in `save`.**
  With 3D, saving or disconnecting with a battery in can spin the motors up. Every "save" in this guide assumes no battery.
- **Props off** for everything on the bench.
- In 3D, **throttle center = motors stopped**; below center the motors spin backwards. Arm with the stick at center.
- If a motor stops or stutters in the air (desync), **disarm right away**.
- This is test firmware. Fly somewhere you're happy to crash.

## 2. Back up your current setup

- [ ] USB in (no battery) → **CLI** tab → type `diff all` → Enter.
- [ ] **Save to File**. This is your way back.

## 3. Check your ESCs

- [ ] [am32.ca/configurator](https://am32.ca/configurator) → **Connect** → **Read Setup**.
- [ ] **Bidirectional / 3D must be ON for all four motors.**
- [ ] Note one thing for step 8: **do you have RPM telemetry?** (`dshot_bidir = ON` in Betaflight works.)
  AM32, Bluejay and BLHeli_32 have it. Stock BLHeli_S does **not**.
- [ ] Screenshot the ESC settings; the log form asks for it.

For reference, ZoeFPV's AM32 settings on the Lucid whoop (a starting point, not rules):

| AM32 setting | ZoeFPV | Notes |
|---|---|---|
| Timing advance | 15° | an AM32 update once reset this to 22.5°, which caused stalls |
| Startup power | 125% | |
| Min duty cycle | 3% | |
| PWM frequency | **by rpm** | fixed 24 kHz / variable 24–48 caused restart desyncs on these motors |
| Complementary PWM | on | |
| Stuck rotor protection | off | ZoeFPV's choice; off means no jam protection after a crash, so disarm fast |

## 4. Flash the firmware

- [ ] Battery unplugged → **Firmware Flasher** → **Load Firmware [Local]** → pick your `BetaFlight3DEdition_v0.2.2-test_<BOARD>.hex`.
- [ ] **Flash Firmware** → wait for "Programming: SUCCESSFUL".
- [ ] Connect → **CLI** → `version`. You should see **`4.5.1`** and **`(b5fa258ef)`**, and your board name.
- [ ] If your settings were wiped, paste your `diff all` backup from step 2 and press Enter.
  (Coming from Betaflight 4.4 or 2026.x? A few lines may be rejected. Re-enter those by hand; check receiver and ports.)

## 5. Paste Block A (packs 1 and 2: stock behaviour)

Battery unplugged. Paste into the CLI and press Enter:

```
feature 3D
set 3d_iterm_mode = RESET
set 3d_iterm_release = TIME
set 3d_iterm_reset_ms = 250
set 3d_iterm_load = FLIP
set 3d_iterm_min_ms = 50
set 3d_iterm_max_ms = 400
set 3d_iterm_rpm_pct = 40
set 3d_iterm_learn_thr = 50
set 3d_iterm_learn_hz_x10 = 5
set 3d_iterm_axes = ALL
set debug_mode = 3D_ITERM
save
```

This is exactly stock Betaflight behaviour, plus logging. It also resets every 3D Edition setting to its default, so it's safe
if you flew v0.1 or v0.2.0 before. Your PIDs, rates, receiver, OSD and other 3D settings (deadband etc.) are not touched.

**TBS Lucid AIO built like Lil Horny** (2S, 0802, 31 mm 3D props)? Paste the [starter tune](tunes/3D_Edition_starter_tune_TBS_LUCID_AIO.txt)
instead; it already contains Block A. **CrazyBee F4 SX1280?** Use [its settings file](tunes/3D_Edition_settings_CRAZYBEEF4SX1280.txt) (also contains Block A).

- [ ] Reconnect, type `get 3d_iterm` and check: `3d_iterm_mode = RESET`, `3d_iterm_release = TIME`, `3d_iterm_reset_ms = 250`.
- [ ] `get debug_mode` shows `3D_ITERM` (it isn't in Configurator's dropdown; CLI only; it doesn't change how the quad flies).

## 6. Bench check (props OFF, 2 minutes)

- [ ] Props off, battery in. Arm with throttle centered.
- [ ] Nudge the throttle up: motors spin one way. Below center: they stop and spin the other way. All four, cleanly.
- [ ] Do it about 10 times. If a motor stutters, doesn't restart or squeals, **stop**: that's ESC settings or hardware, not the firmware.
- [ ] Disarm, unplug the battery.

## 7. Fly pack 1 and pack 2 (Block A)

**Before every pack:**
- [ ] Blackbox tab → **Erase flash**. A full flash silently stops recording.
- [ ] Same props, same spot, fully charged pack, **battery in the same position every time** (mark it on the frame).

**Each pack (fly the whole pack, the same way every time):**
- [ ] **Lots of flips through center, 20 or more, and after most flips hold the new direction for 1–2 seconds**
      (hover or cruise) before the next one. The analysis measures what happens in the second after a flip, so back-to-back
      flips with no pause can't be measured.
- [ ] Mix upright → inverted and inverted → upright, some gentle and some full-stick (punch-outs).
- [ ] Some calm cruising upright and some inverted.

**After every pack:**
- [ ] Battery unplugged → Blackbox tab → **Save flash to file**. Name it e.g. `YourCallsign_pack1_RESET.BBL`.
- [ ] Jot down how it felt: drift after flips, wobble, stalls, anything odd.

## 8. Paste Block B (packs 3 and 4: the new I-term handling)

Battery unplugged. Pick the one that matches step 3:

**With RPM telemetry** (`dshot_bidir = ON`: AM32, Bluejay, BLHeli_32):
```
set 3d_iterm_mode = PER_DIRECTION
set 3d_iterm_release = RPM
save
```

**Without RPM telemetry** (stock BLHeli_S):
```
set 3d_iterm_mode = PER_DIRECTION
save
```
(Without telemetry the firmware can't see the motors restart, so it keeps the 250 ms timer. Don't use `RPM` there: it would wait the 400 ms cap every time.)

- [ ] Reconnect, `get 3d_iterm` → `3d_iterm_mode = PER_DIRECTION` (and `3d_iterm_release = RPM` if you have telemetry).

## 9. Fly pack 3 and pack 4 (Block B)

Exactly like step 7: erase flash first, same routine, same battery position.

- [ ] Plug in, then **cruise ~5 seconds upright and ~5 seconds inverted before the first flip**. The learned trims start
      empty at power-up and fill in during steady flight.
- [ ] Name the logs e.g. `YourCallsign_pack3_PER_DIRECTION.BBL`.

## 10. Send your logs

**[Upload your logs and report here](https://forms.gle/Vfq3c2W7Lp5FE36t5)** (Google Form).

- [ ] All 4 `.BBL` files in one go (up to 10 files, 100 MB each), plus your ESC screenshot.
- [ ] Say which packs were Block A and Block B, and how it felt.

Uploading needs a Google sign-in. No Google account? Zip the logs and attach them to a
[GitHub issue](https://github.com/BlindingBright/Drones/issues/new).

Then you're done. If you want to go back to your own setup: **flash official Betaflight** and paste your step 2 backup.

---

## Troubleshooting

| Problem | What to do |
|---|---|
| `version` doesn't show `(b5fa258ef)` | The flash didn't take, or it's an older 3D Edition file. Flash again (step 4). |
| `get 3d_iterm` says a setting doesn't exist | You're on stock Betaflight or 3D Edition v0.1. Flash the v0.2.2 file. |
| Blackbox stops before the pack ends | Erase before every pack. Still full? `set blackbox_sample_rate = 1/8` (fits a full whoop pack on 8 MB flash; this is what Lil Horny uses). |
| A motor stalls, stutters or stops after a reversal | Disarm. Check ESC settings, solder joints, props. Mention it in the [form](https://forms.gle/Vfq3c2W7Lp5FE36t5). |
| The quad drifts or wobbles after flips | That's what we're measuring. Keep flying the routine and describe it. |
| Motors spin up when you save or disconnect | The battery is still plugged in. Unplug it first, every time. |
| Won't arm after flashing or Block A | Check `dshot_bidir`: if it's ON with stock BLHeli_S (no RPM telemetry), set it OFF. Check that your receiver still works (Receiver tab). |

## Board notes

### CrazyBee F4 SX1280 (`CRAZYBEEF4SX1280`)
BLHeli_S ESC. In [am32.ca/configurator](https://am32.ca/configurator) set **Motor direction = Bidirectional**. **Bluejay is recommended**: stock BLHeli_S has no RPM
telemetry. Use the [CrazyBee settings file](tunes/3D_Edition_settings_CRAZYBEEF4SX1280.txt) in step 5; with Bluejay, uncomment
`dshot_bidir` and `motor_poles`. Built-in ExpressLRS keeps working; re-check binding after flashing.

### No blackbox on your board
Some boards (e.g. DarwinFPV TinyApe `DARWINF4SX1280HD`) have no flash chip, so they can't record logs. You can still help:
fly the same 4 packs, record **DVR**, and describe in the [form](https://forms.gle/Vfq3c2W7Lp5FE36t5) how the flips felt
in packs 1–2 vs 3–4. Leave `debug_mode` as it is; it does nothing without a log.

### 5-inch and bigger props
Same blocks. Bigger props restart slower; with `RPM` release the firmware waits for the motors (up to the 400 ms cap), so nothing
to change. Not on Betaflight 4.5.1? See [BOARDS.md](BOARDS.md) for the 2026.6 note.

### Other boards
Full list and notes: **[BOARDS.md](BOARDS.md)**. Not there? **[Request a build](https://forms.gle/1p93ZjiqDp1PLWA96)**,
contact ZoeFPV (Discord link at [zoefpv.com](https://zoefpv.com)), or [build it yourself](BUILD_FROM_SOURCE.md).
