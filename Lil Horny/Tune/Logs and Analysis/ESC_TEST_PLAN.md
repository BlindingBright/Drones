# AM32 switching-speed test (Alka's plan)

Goal: faster 3D direction switching on the Lucid AIO (AM32 2.21) via **Minimum Duty Cycle** and the **Motor KV** slider.
Betaflight stays on `whoop3d_master.txt` for every log, with **no CLI changes during this test**, so the ESC is the only variable.

## What the existing logs already show
Plot: `reports/esc_compare_history.png`

| Run | Firmware / setting | Switch time (to 100k eRPM in new direction), median | p90 |
|---|---|---|---|
| Pass 1 | factory AM32 (2.03) | **136 ms** | 169 |
| Pass 3 | 2.21, 15° | 146 ms | 175 |
| Pass 5 | 2.21, startup power 120 | 144 ms | 162 |
| Pass 6 | 2.21, startup power 100 | 148 ms | 177 |

On 2.21 the motors sit in a rough **30–60k eRPM range for ~80 ms** after the switch before climbing.
On the factory firmware they dip cleanly through zero at ~60 ms and climb straight out.
This matches Alka: 2.03 had a higher min duty, and the KV slider caps throttle at low rpm.
(Caveat: different days and props, and my stick technique varies; the A/B/C logs below fix that.)

## Steps (same props, full packs, similar flying with LOTS of throttle reversals)

Before each step: in the Multi ESC Config Tool, set **all four ESCs (M1–M4)** the same, click **Save Settings**,
then **Save Config File** with the step name. Bench test props off: flick through center 10+ times.
Any stutter, twitch, or a motor that doesn't restart means stop, back off a step, and report it.

| Step | Change | Config file name | Log name |
|---|---|---|---|
| **A: default** | Current settings (timing 15, startup 100, KV 10220, min duty default). Pass 6 counts as A if props haven't changed | `am32_A_default` | `ESC A default.BBL` |
| **B: min duty** | **Minimum Duty Cycle → 3** (Alka: 3 or 4) | `am32_B_minduty3` | `ESC B minduty3.BBL` |
| **C: + low KV** | Keep min duty 3, **Motor KV 10220 → ~5100** (half) | `am32_C_minduty3_kv5100` | `ESC C kv5100.BBL` |
| D (optional) | Alka's tip: higher min duty (4) **with lower startup power** (e.g. 80) for a strong but smooth start | `am32_D_...` | `ESC D ....BBL` |

**Finding the setting:** Multi ESC Config Tool 1.86 (per the screenshot) doesn't show Minimum Duty Cycle.
Check for a newer version of the tool or esc-configurator.com. If neither exposes it for 2.21, ask Alka where it lives.

After each flight: feel the motors (more low-rpm power = more heat), and note the feel at center stick.

## Analyze

```
.\.venv\Scripts\python.exe tools\esc_compare.py reports\esc_test.png "A default=ESC A default.BBL" "B minduty3=ESC B minduty3.BBL" "C kv5100=ESC C kv5100.BBL"
```
(set `$env:PYTHONPATH="C:\Users\Admin\Documents\Tuning\orangebox-0.5.0;tools"` first; trim crashes with `@0-55`)

Columns: `stop` / `restart` / `total` switch times (ms, lower = faster), `spread` between motors, `slow>200` count,
`err pk` attitude kick during the switch, `lowRPM rough` (eRPM ripple below 150k, the "rough transition" feel),
`low-thr wob` (wobble at <20% output).

## Results so far (2026-10-08)
Plot: `reports/esc_test_A_vs_B.png`. A = Pass 7 (2 packs, impact at 70 s trimmed), B = Pass 8 log 3 (impact at 79 s trimmed).

| | A default (P7, n=36) | **B min duty 3 (P8, n=23)** |
|---|---|---|
| Switch time median / p90 | 155 / 193 ms | **147 / 172 ms** |
| Slow switches (>200 ms) | 14 of 36 (39%) | **1 of 23 (4%)** |
| Motor spread | 73 ms | **49 ms** |
| Low-rpm roughness (eRPM ripple) | 3.5k | **1.8k (halved)** |
| Low-throttle wobble | 2.8 | 2.4 |
| Idle eRPM | 68k | **92k (+35%)** |
| Attitude kick during switch median / p90 | 74 / 147 | 85 / 173 (slightly worse) |

- Min duty **adds on top of** the Betaflight idle command (idle rpm +35% at the same `dshot_idle_value`).
- Much more consistent and smoother at low rpm, only ~8 ms faster on median.
- The ~40–110 ms rough 30–60k eRPM plateau after each switch is **unchanged**, so it isn't min duty.
  It looks like the low-rpm throttle limit, which is what step C (KV ~5100) targets.
- Slightly bigger attitude kick during switches is possibly the bigger thrust jump from +idle to −idle. Watch it in C.

### Step C added (Pass 9, impact at 88.6 s trimmed; pilot: "felt good in the air")
Plot: `reports/esc_test_ABC.png`. A now pools P6 + P7 (52 reversals).

| | A default | B min duty 3 | **C min duty 3 + KV 5100** |
|---|---|---|---|
| Switch time median / p90 | 153 / 183 ms | 147 / 172 | **142 / 172** |
| Restart phase (zero → 100k eRPM) | 45 ms | 42 | **39** |
| Slow switches (>200 ms) | 17 of 52 (33%) | 1 of 23 | **1 of 28 (4%)** |
| Motor spread | 70 ms | 49 | **45** |
| Per-motor median m0..m3 | 152 147 156 155 | 143 149 146 154 | **139 135 139 149** |
| Low-rpm roughness | 3.3k | **1.8k** | 3.5k |
| Attitude kick median / p90 | 60 / 136 | 85 / 173 | 68 / 172 |

- C is the fastest and most consistent 2.21 setup: −11 ms median, every motor faster, slow switches 33% → 4%.
  Still ~6 ms behind factory 2.03 (136 ms in Pass 1).
- Lower KV brought the low-rpm roughness back (B's smoothness gain gone).
- **The rough 30–60k eRPM window from ~40–110 ms after each switch is identical in A, B and C.**
  Neither setting moves it, so it's likely 2.21's reversal routine or telemetry not resolving low rpm. Factory 2.03
  (Pass 1) instead dips cleanly to ~10k at 60 ms. Question for Alka.
- Flight quality in C: pitch D-term and motor jitter slightly up (jitter 17 vs 14 in P6); could be the
  harder flying / prop wear. Watch it.
- Idle rpm at the idle command: A ~70–79k, B ~87–93k, C ~78–92k (rough in-flight measure).

### Step D: min duty 4 + KV 2100 (Pass 10; Alka suggested ~2200). Clean 86 s flight
Plot: `reports/esc_test_ABCD.png`

| | A | C | **D** |
|---|---|---|---|
| Switch median / p90 | 153 / 183 | 142 / 172 | **126 / 154 ms** |
| Per-motor m0..m3 | 152 147 156 155 | 139 135 139 149 | **125 128 126 130** |
| Motor spread | 70 | 45 | **38 ms** |
| Low-rpm roughness | 3.3k | 3.5k | **1.7k** |
| Slow >200 ms | 33% | 4% | 7% (2 of 30) |

- Fastest and smoothest config. Beats factory 2.03 (136 ms). The 30–60k plateau finally shrank (climbing by ~85 ms vs ~110).
- Side effect: pitch step overshoot 1.22 → 1.37 and steady error up slightly (roll/pitch 9.1/8.9 vs ~8 in C).
  More low-rpm authority from the ESC likely raises loop gain at low throttle. Betaflight candidate: `thrust_linear` 20 → 10.

### Step E: min duty 3 + KV 2100 (Pass 11, Alka's final recommendation). FINAL
Plot: `reports/esc_test_ABCDE.png`

| | D (duty 4) | **E (duty 3)** |
|---|---|---|
| Switch median / p90 | 126 / 154 | **126 / 148 ms** |
| Per-motor | 125 128 126 130 | 118 128 123 129 |
| Motor spread / slow | 38 / 2 | **34 / 1** |
| Low-rpm roughness | 1.7k | 1.8k |
| Pitch step peak | 1.37 | **1.22** |
| Inverted jitter | 19.2 | **16.6** |
| Reversal kick p90 | **149** | 185 |

D and E are near-identical; the pilot couldn't tell them apart either. Keeping E: same speed, slightly more consistent,
less pitch overshoot, and lower min duty = more desync margin (per Alka).

## Betaflight interaction to watch
Min duty puts a floor *under* Betaflight's `dshot_idle_value = 400` (4%): the lowest DShot value becomes ~3% duty,
so Betaflight's 4% idle now lands higher. Expect more thrust / float at center stick. If B/C switch faster but center
feels floaty, the follow-up is lowering `dshot_idle_value` (e.g. 400 → 300) to put the true idle back where it was.
That's a separate pass after the ESC test.
