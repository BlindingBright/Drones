# Drones

Frames, mounts, tunes and flight-log analysis for my FPV builds. Each project lives in its own folder.

## Latest project: Lil Horny (3D whoop)

**[Lil Horny](Lil%20Horny/)** is a 65 mm 3D (reversible-motor) whoop built around a DJI O4 Lite and a
TBS Lucid AIO. It can fly upright and inverted, flipping motor direction mid-air. The folder includes
the printable mounts, the Fusion 360 design, a Betaflight tune and the AM32 ESC configs that go with it,
plus all the blackbox logs and analysis from tuning it.

The frame is based on the **Fractal 65** by Fractal Engineering, and all credit for the frame goes to them.
I tested the prints on a cut-down Fractal 65 and a cut-down Pavo Pico, and they fit both.

### Build list

| Part | Notes |
|---|---|
| Frame | Fractal 65 (or Pavo Pico), cut down |
| Flight controller / ESC | TBS Lucid AIO 1-2S (AM32). The battery mount is shaped to fit around its plugs |
| Video | DJI O4 Lite. The camera mount is made for it |
| Motors | 0802, 16000 kv |
| Props | Gemfan 123D (31 mm) |
| Battery | 2S, 200–300 mAh. Both sizes fit the same battery mount ([example 1](https://www.amazon.com/dp/B0D3F5YF9L), [example 2](https://www.amazon.com/dp/B0GXZCW923)) |

### What's in the folder

```
Lil Horny/
├── Frame Files/          Printable mounts (.obj / .stl), Fusion 360 design (.f3d + script), Lucid AIO .step
│   └── stl/              TPU standoffs (several heights)
├── Tune/
│   ├── Lil Horny 3D Master Tune.txt   Betaflight 4.5.1 CLI "diff all" — the current tune
│   ├── esc1-4_config.bin              AM32 settings for each ESC
│   └── Logs and Analysis/             Blackbox logs, plots, TUNING_NOTES.md, ESC_TEST_PLAN.md
├── README.md              Project info and build list
└── Lil Horny - Lisence Info Please Read.txt
```

### Setting it up

1. **Print the mounts** from `Frame Files/`. The standoffs are meant to be printed in TPU.
2. **ESCs (AM32 2.21):** load the `Tune/esc*_config.bin` files with [esc-configurator.com](https://esc-configurator.com)
   (props off, battery plugged in). The key settings are: bidirectional ON, 12 motor poles, timing 15°,
   startup power 100, min duty 3, motor KV 2200 (stock is fine), complementary PWM ON and running brake 10.
   Updating AM32 can reset these values (it changed timing to 22.5° on mine), so check them again after any flash.
3. **Betaflight 4.5.1:** paste `Tune/Lil Horny 3D Master Tune.txt` into the CLI and it will `save`.
   It turns on 3D mode (1496 low / 1500 neutral / 1504 high, with a deadband of 3), sets
   `motor_poles = 12` and enables bidirectional DShot.
   Before the first flight, check in the Motors tab (props off) that all four motors spin the right way in both directions.

The full pass-by-pass story of the tune — what was changed, why, and what the logs showed — is in
[`Tune/Logs and Analysis/TUNING_NOTES.md`](Lil%20Horny/Tune/Logs%20and%20Analysis/TUNING_NOTES.md).

## How to get the files

**Download everything (easiest):** click the green **Code** button at the top of this page, then **Download ZIP**.

**Clone with git:**

```bash
git clone https://github.com/BlindingBright/Drones.git
```

**Download only the Lil Horny folder** (skips the other projects):

```bash
git clone --filter=blob:none --sparse https://github.com/BlindingBright/Drones.git
cd Drones
git sparse-checkout set "Lil Horny"
```

**Single files:** open the file on GitHub and click the download (↓) button at the top right of the file view.

The project is also updated regularly on
[Google Drive](https://drive.google.com/drive/folders/10FEdRLiF6wVrJK5k8aDCwKiYdItE1z3n?usp=drive_link).

## License

Lil Horny is released under
**[Creative Commons BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode.en)**.
You're free to print, build, change and share it **for non-commercial use**, as long as you give credit and share
any changes under the same license. See `Lil Horny - Lisence Info Please Read.txt` for the full text.
