# BlueJay3D: Pilot Testing Guide (`v0.22.0-3D`)

Thanks for helping test **BlueJay3D**! About 15 minutes on the bench, then **4 packs of flying with one ESC preset change in the middle.**

## The short version

| | What you do |
|---|---|
| 1 | Back up your current ESC settings (screenshot) and Betaflight `diff all` |
| 2 | Flash the `v0.22.0-3D` `.hex` file for **your** ESC layout ([`TARGETS.md`](TARGETS.md)) |
| 3 | Apply **Block A** (stock Bluejay v0.21 behaviour), bench-check with props off |
| 4 | Fly **pack 1 and pack 2** |
| 5 | Apply **Block B** (the new BlueJay3D 3D handling), bench-check with props off |
| 6 | Fly **pack 3 and pack 4** |
| 7 | [Upload the 4 logs](https://docs.google.com/forms/d/e/1FAIpQLSfmN5fuS82CXPKGCXlqQAUPCoa6tT8LgZesW7zxZt6WFHSnpw/viewform) *(or via [GitHub Issue](https://github.com/BlindingBright/Drones/issues/new?template=bluejay3d_log_upload.yml))* and say how it felt |

Everything else below is the detail for each step. Every step has a checkbox so you can keep your place.

**What you're testing:** stock Bluejay `v0.21.0` was designed around unidirectional flight. On a 3D quad, reversing motor direction mid-air hits 9 compounding bugs: `Startup_Pwr` boost never engages after initial arming, post-reversal demag spikes trigger FET power-cuts, `Initial_Run_Phase` chokes torque to 50% and blinds the ESC to counter-reversals for 12–18 commutation steps, direction-change braking is overwritten to ~2% duty, DShot `0`/`48`/`1048` have center-stick deadband traps, a single missed zero-cross shuts the motor off for a full `100 ms`, and low-RPM eRPM telemetry overflows 8 bits (+254 µs spike).
**BlueJay3D (`v0.22.0-3D`)** fixes all 9 issues and backports AM32/ESCape32's proportional active braking, 3D minimum duty floor, reversal startup boost, and 1 ms fast desync recovery.

---

## 0. What you need

- [ ] A 3D-capable quad with **8-bit EFM8 ESCs** (`EFM8BB1`, `EFM8BB2`, or `EFM8BB51`) that run Bluejay or BLHeli_S
- [ ] **3D props** and 4 charged packs. Fresh, tight props; loose or bent props cause false vibrations in the logs
- [ ] A flight controller **with blackbox** (onboard flash or SD card). No blackbox? You can still help — see [No blackbox](#no-blackbox-on-your-board)
- [ ] [Betaflight Configurator](https://github.com/betaflight/betaflight-configurator/releases) and a USB data cable
- [ ] Either the **[Bluejay3D Configurator](configurator/)** (open `configurator/index.html` in Chrome/Edge or run `python3 configurator/server.py`) or **[esc-configurator.com](https://esc-configurator.com)**
- [ ] Your ESC firmware file from **[`TARGETS.md`](TARGETS.md)** (63 layouts / 135 `.hex` files). **The 5-character layout code (`O_H_5`, `Z_H_30`, etc.) must match your ESCs exactly.**

## 1. Safety first (read this)

- **Props OFF for every step on the bench** (flashing, saving settings, and bench-checking reversals).
- **Unplug the battery before clicking Save or Disconnect in Betaflight Configurator.**
- In 3D mode, **throttle stick center (1500) = motors stopped**; below center = reverse thrust; above center = forward thrust. Always arm with the throttle stick centered.
- If a motor stops, stutters, or squeals in the air (desync), **disarm right away**.
- This is test firmware. Fly over grass or somewhere you're happy to crash.

## 2. Back up your current setup

- [ ] **Betaflight backup:** Plug in USB (no battery) → Betaflight Configurator → **CLI** tab → type `diff all` → **Save to File**.
- [ ] **ESC backup:** Take **props OFF**, plug in battery, open [esc-configurator.com](https://esc-configurator.com) (or the [Bluejay3D Configurator](configurator/)) → **Connect** → **Read Settings**.
- [ ] Write down or screenshot your exact **ESC Target code** (e.g. `O_H_5`, `Z_H_30`, `G_H_30`, `A_X_5`) and which ESCs have **Reversed** direction checked.

## 3. Flash `BlueJay3D v0.22.0-3D` to all 4 ESCs

You only flash the firmware **once** for the entire test (Block A and Block B use the same firmware binary with different settings, or you can pre-bake Block A / Block B directly into the `.hex` inside the Bluejay3D Configurator before flashing):

- [ ] Download the matching `.hex` for your ESC layout from **[`TARGETS.md`](TARGETS.md)** (48 kHz recommended for 1S/2S whoops & toothpicks; 24 kHz for 5-inch).
- [ ] With **props OFF** and **battery plugged in**, connect in **[esc-configurator.com](https://esc-configurator.com)** or the **[Bluejay3D Configurator](configurator/)** (`python3 configurator/server.py` → `http://localhost:8085`).
- [ ] Click **Flash All** → **Select Local Firmware (`.hex`)** → choose your `*_v0.22.0-3D.hex` file → flash all 4 ESCs.
- [ ] Verify that all 4 ESCs report **`Bluejay3D v0.22`** and that **Motor Direction** is set to **`Bidirectional 3D`** (or **`Bidirectional 3D Rev`** for any motor that needs to spin the opposite way).

## 4. Apply Block A (packs 1 and 2: stock Bluejay v0.21 behaviour)

To make Packs 1–2 a true A/B comparison on the same hardware and day, **Block A** configures `v0.22.0-3D` to use legacy `v0.21.0` commutation/braking parameters:

- [ ] Open the **[Bluejay3D Configurator](configurator/)** (`configurator/index.html` in Chrome/Edge).
- [ ] Click the **`⚠️ Block A: Stock Bluejay v0.21 Baseline`** preset button (or load [`presets/BlockA_Stock_v021_Baseline.bin`](presets/BlockA_Stock_v021_Baseline.bin)):
  - `Motor Direction` = `Bidirectional 3D`
  - `Commutation Timing` = `Medium (15°)`
  - `Demag Compensation` = `Low`
  - `Startup Power (Min / Max)` = `1.00x` (`21` / `5`)
  - `3D Brake Strength` = `1`
  - `3D Min Duty Floor` = `0 (0%)`
  - `3D Reversal Startup Boost` = `OFF`
  - `3D Fast Desync Restart` = `OFF (100 ms)`
  - `3D Fast 1:1 Throttle Track` = `OFF`
  - `3D Glitch Filter` = `0 (1 frame)`
- [ ] Click **Write Settings to ESC** (via WebSerial 4-way passthrough) — *or click **Download Customized `.HEX`** and flash that `.hex` in esc-configurator.com*.
- [ ] In Betaflight Configurator (battery unplugged), make sure bidirectional DShot and 3D mode are enabled (`feature 3D`, `set dshot_bidir = ON`, `set motor_poles = 12` for whoops or `14` for 5-inch).

## 5. Bench check (props OFF, 2 minutes)

- [ ] **Props OFF**, battery plugged in.
- [ ] **Manual check:** In Betaflight Configurator → **Motors** tab (or armed on the bench with your radio), move the throttle slightly above 1500 (forward) and slightly below 1500 (reverse) about 10 times.
  - Verify all 4 motors spin the right way in both directions, and `E: 0.00%` DShot telemetry error is shown.
- [ ] **Optional automated MSP bench sweep:** Close Betaflight Configurator and run:
  ```bash
  python3 tools/bench_verify.py --port /dev/ttyACM0
  ```
  It runs 20 automated forward↔reverse step transitions and prints your exact reversal latency (`ms`), minimum duty health, and desync count (`0`).
- [ ] Unplug the battery.

## 6. Fly pack 1 and pack 2 (Block A)

**Before every pack:**
- [ ] Betaflight Configurator → **Blackbox** tab → **Erase flash**.
- [ ] Same props, same flying spot, fully charged pack, **battery in the same position every time**.

**Each pack (fly the same routine on every pack):**
- [ ] **20 or more flips through center stick**, holding the new direction for **1–2 seconds** after most flips before the next one.
- [ ] Include a mix of:
  - Gentle upright ↔ inverted hover flips across stick center
  - Rapid **tic-tocks** (continuous upright ↔ inverted reversals)
  - High-RPM **punch-out reversals** (fast throttle chop across center stick)
- [ ] **After each pack:** Unplug battery → Blackbox tab → **Save flash to file**. Name them `YourCallsign_pack1_BlockA_Stock.BBL` and `YourCallsign_pack2_BlockA_Stock.BBL`.

## 7. Apply Block B (packs 3 and 4: the new BlueJay3D 3D handling)

Now enable the full **BlueJay3D (`v0.22.0-3D`)** 3D commutation, active braking, and fast recovery suite:

- [ ] Open the **[Bluejay3D Configurator](configurator/)** and click the **Block B** preset button matching your quad size (or load the matching `.bin` from [`presets/`](presets/)):

| Setting | 🐝 Block B: 1S/2S Whoop (`0702–1002`) | ⚡ Block B: 3"–4" Toothpick (`1204–1404`) | 🚁 Block B: 5" 3D Acro (`2207–2306`) |
|---|---|---|---|
| **Preset button / `.bin`** | `Block B: 1S/2S 3D Whoop` / [`BlockB_1S_2S_Whoop.bin`](presets/BlockB_1S_2S_Whoop.bin) | `Block B: 3"-4" Toothpick` / [`BlockB_3_4_Toothpick.bin`](presets/BlockB_3_4_Toothpick.bin) | `Block B: 5" 3D Acro` / [`BlockB_5inch_Acro.bin`](presets/BlockB_5inch_Acro.bin) |
| `Commutation Timing` | `Medium (15°)` | `Medium (15°)` | `Medium (15°)` |
| `Demag Compensation` | `High` | `High` | `High` |
| `Startup Power (Min / Max)` | `1.25x` (`33` / `29`) | `1.125x` (`29` / `25`) | `1.00x` (`25` / `21`) |
| `3D Brake Strength` | `8` (`37.6%` limit) | `8` (`37.6%` limit) | `6` (`28.2%` limit) |
| `3D Brake Speed (Handover)` | `7` (`~6.7k eRPM`) | `5` (`~5.0k eRPM`) | `4` (`~4.0k eRPM`) |
| `3D Min Duty Floor` | `4` (`3.14%`) | `3` (`2.35%`) | `3` (`2.35%`) |
| `3D Rev Boost` | `ON` | `ON` | `ON` |
| `3D Fast Restart` | `ON (1 ms)` | `ON (1 ms)` | `ON (1 ms)` |
| `3D Fast Track` | `ON (1:1)` | `ON (1:1)` | `ON (1:1)` |
| `3D Glitch Filter` | `1 (2 frames)` | `1 (2 frames)` | `2 (3 frames)` |

*(Note: Because `v0.22.0-3D` already ships with the Toothpick / All-Rounder Block B defaults in the `.hex`, flashing the stock `v0.22.0-3D` `.hex` also gives you Block B out of the box!)*

- [ ] Click **Write Settings to ESC** (or **Download Customized `.HEX`** and flash in esc-configurator.com), keeping the same motor directions as Block A.
- [ ] **Bench check again with props OFF** (Step 5): verify all 4 motors reverse crisply and cleanly.

## 8. Fly pack 3 and pack 4 (Block B)

- [ ] Erase Blackbox flash before each pack, fly the **exact same routine** as Step 6 with the same battery placement.
- [ ] Save the Blackbox logs as `YourCallsign_pack3_BlockB_BlueJay3D.BBL` and `YourCallsign_pack4_BlockB_BlueJay3D.BBL`.

## 9. Send your logs

### 👉 [Upload your logs and report here (Google Form)](https://docs.google.com/forms/d/e/1FAIpQLSfmN5fuS82CXPKGCXlqQAUPCoa6tT8LgZesW7zxZt6WFHSnpw/viewform)

- [ ] Upload all 4 `.BBL` files in one go (up to 10 files, 100 MB each), plus a screenshot of your Bluejay3D Configurator settings.
- [ ] Note which packs were Block A and Block B, which ESC target you flew (e.g. `O_H_5 48 kHz`), and how reversals felt.

Uploading files on Google Forms requires a Google sign-in. **No Google account?** Zip your `.BBL` logs and drag-and-drop them into our **[GitHub Log Upload Form](https://github.com/BlindingBright/Drones/issues/new?template=bluejay3d_log_upload.yml)**.

---

## Troubleshooting

| Problem | What to do |
|---|---|
| **A motor spins the wrong direction** | In Bluejay3D Configurator / esc-configurator.com, toggle that motor between `Bidirectional 3D` and `Bidirectional 3D Rev`. *(Avoid using Betaflight's built-in motor direction wizard in 3D mode — use the ESC configurator or Betaflight CLI.)* |
| **Motor stutters near stick center** | Increase `3D Min Duty Floor` by `+1` (e.g. from `3` = `2.35%` to `4` = `3.14%` or `5` = `3.92%`). |
| **Motors or ESCs get warm on 5-inch / heavy props** | Use `24 kHz` PWM frequency and lower `3D Brake Strength` from `8` (`37.6%`) to `5` or `6` (`23.5%–28.2%`). |
| **Harsh jolt on high-speed reversals** | Lower `3D Brake Speed (Handover)` by `1–2` steps so the motor brakes to a lower RPM before flipping phase sequence. |
| **Won't arm after flashing** | Verify `dshot_bidir = ON` in Betaflight CLI and that your throttle stick is centered (`1500`, inside `3d_deadband_low`..`3d_deadband_high`). |

## Pairing with BetaFlight 3D Edition

**BlueJay3D (`v0.22.0-3D`)** and **[BetaFlight 3D Edition (`v0.3.1-test`)](../BetaFlight%203D%20Edition/)** are designed to work together:
- **BlueJay3D** fixes the ESC-side commutation, active braking, 1 ms desync recovery, and 10-bit eRPM telemetry accuracy during the flip.
- **BetaFlight 3D Edition** remembers the upright and inverted I-term trims across the flip, gates anti-gravity during reversals, enables 3D dynamic idle, and releases the I-term hold as soon as BlueJay3D's bidirectional DShot eRPM telemetry confirms all 4 motors have restarted!

## No blackbox on your board?

Some 1S/2S AIOs (such as the DarwinFPV TinyApe `DARWINF4SX1280HD` or certain 1S BetaFPV boards) have no onboard flash chip. You can still help: fly the same 4-pack Block A vs Block B test, record **DVR**, and submit a written report in the [form](https://docs.google.com/forms/d/e/1FAIpQLSfmN5fuS82CXPKGCXlqQAUPCoa6tT8LgZesW7zxZt6WFHSnpw/viewform) describing whether desyncs or stutters changed between Packs 1–2 and Packs 3–4.
