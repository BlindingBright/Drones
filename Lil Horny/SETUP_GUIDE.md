# Lil Horny — Setup Guide

A step-by-step guide to building and setting up the Lil Horny 3D whoop. Follow it in order and tick
things off as you go.

> **What's a 3D whoop?** The motors can spin both ways, so the quad flies upright *and* upside down,
> flipping direction in mid-air. Because of that, a few settings are different from a normal whoop.
> Don't skip steps 4 and 5.

See it fly: <https://www.youtube.com/watch?v=3YmYATX25bI>

---

## 1. What you need

**Parts**

- [ ] Frame: Fractal 65/75 or Pavo Pico, cut down
- [ ] TBS Lucid AIO 1-2S (flight controller + AM32 ESC)
- [ ] DJI O4 Lite
- [ ] 4× 0802 16000kv motors
- [ ] Gemfan 123D props (31 mm)
- [ ] 2S 200–300 mAh batteries (Tattu recommended): [one](https://www.amazon.com/dp/B097BVFYLX/),
      [two](https://www.amazon.com/dp/B0D3F5YF9L), [three](https://www.amazon.com/dp/B0GXZCW923)
- [ ] M2 screws for the stack, and the small screws that came with your motors

**Software (all free)**

- [Betaflight Configurator](https://github.com/betaflight/betaflight-configurator/releases) (firmware 4.5.1)
- [am32.ca/configurator](https://am32.ca/configurator) (opens in Chrome or Edge)

**Files from this folder**

| File | What it's for |
|---|---|
| `Frame Files/stl/` and `Frame Files/*.obj` | Things to 3D print |
| `Tune/esc1_config.bin` … `esc4_config.bin` | ESC settings |
| `Tune/Lil Horny 3D Master Tune.txt` | Betaflight settings |

---

## 2. Print the parts

Print these from `Frame Files/`:

- [ ] **Camera Mount** (holds the O4 Lite camera)
- [ ] **Battery Mount** (shaped to fit around the Lucid's plugs; fits 200–300 mAh packs)
- [ ] **Antenna Mount**
- [ ] **Standoffs, in TPU**:
  - `Standoffs BOTTOM plate-O4 1.5mm x4` — goes between the frame and the O4 Lite
  - `Standoffs TOP O4-Lucid 4.7mm x4` — goes between the O4 Lite and the Lucid

`.obj` files open in most slicers (Bambu Studio, PrusaSlicer, Cura). The `stl/` folder has the same
standoffs as `.stl`, plus a few other heights if you need more or less room.

---

## 3. Build the stack

From the bottom up:

1. **Frame plate**
2. **1.5 mm TPU standoffs** (×4)
3. **DJI O4 Lite**
4. **4.7 mm TPU standoffs** (×4)
5. **TBS Lucid AIO**, with the USB port and motor plugs facing **up**

The boards sit turned 45° so their holes line up with the frame's diamond-shaped hole pattern.
Run M2 screws through the whole stack. Snug them up, but don't crush the TPU.

Then:

- [ ] Mount the motors and plug them into the Lucid
- [ ] Fit the camera mount, the antenna mount and the battery mount
- [ ] **Leave the props off** until step 6

---

## 4. Set up the ESCs (AM32)

> Props off for this whole step.

1. Plug in a battery, then connect USB.
2. Open [am32.ca/configurator](https://am32.ca/configurator) in Chrome and click **Connect**, then **Read Setup**.
3. **Update AM32 to 2.21** if it isn't on it already. Pick the release for the *same target your ESC
   shows now* (the Lucid is **AT32F421**).
4. Load the matching `Tune/escN_config.bin` onto each ESC, or just type in the values from the table
   below by hand. Then click **Write Setup**.
5. Click **Read Setup** again and check that all four ESCs show:

| Setting | Value |
|---|---|
| Bidirectional / 3D | **ON** |
| Motor poles | **12** |
| Timing advance | **15°** |
| Startup power | **100** |
| Minimum duty cycle | **3** |
| Complementary PWM | **ON** |
| Running brake level | **10** |
| Sinusoidal startup | **OFF** |
| Stall protection | **OFF** |
| Motor KV | **2100–2200** (the files use 2100; stock 2200 is also fine) |

> ⚠️ **Updating AM32 can reset these settings.** On mine, it quietly changed timing to 22.5°, and
> the quad flew noticeably worse. Always check after flashing.

---

## 5. Set up Betaflight

1. Make sure the Lucid is running **Betaflight 4.5.1**.
2. Open the **CLI** tab.
3. Open `Tune/Lil Horny 3D Master Tune.txt`, copy **everything**, paste it into the CLI and press Enter.
   It saves and reboots on its own.
4. Set up your receiver and modes like you would on any quad.

What the tune sets up for you:

- 3D mode on: **1496** low / **1500** neutral / **1504** high, with a deadband of **3**
- `motor_poles = 12`, bidirectional DShot on
- Filters, PIDs and four rate profiles

### Check the motors (props off!)

In the **Motors** tab, check that all four motors spin, and spin the right way, in **both** directions.

> ⚠️ **Don't use Betaflight's built-in "Motor direction" button.** It's currently bugged with this
> setup and can send the motors to **full throttle on the bench**. If a motor spins the wrong way,
> change its direction from the CLI instead.

---

## 6. First flight

- [ ] Props on, and check they're on the right motors for their spin direction
- [ ] Fly over something soft the first time
- [ ] Try gentle flips through center before doing anything aggressive
- [ ] Land when you feel the pack fade. Voltage sag compensation is left off on purpose so you can
      feel the battery getting low

---

## Troubleshooting

| Problem | Try this |
|---|---|
| A motor stops and won't restart after flipping direction | Check that motor for hair, grit or a bent shaft. Check AM32 timing is **15°**, not 22.5° |
| Wobble that gets worse with throttle | Check the battery is held tight in its mount. A loose pack causes a 10–16 Hz roll wobble |
| Reversals feel slow or uneven | Re-check every row in the ESC table in step 4. All four ESCs must match |
| A motor shoots to full speed in the Motors tab | Unplug the battery. Don't use the Motor direction button (see step 5) |

Want the full story of how this tune was made? Read
[`Tune/Logs and Analysis/TUNING_NOTES.md`](Tune/Logs%20and%20Analysis/TUNING_NOTES.md).

---

Lil Horny is released under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.en).
The frame is based on the Fractal 65 by Fractal Engineering.
