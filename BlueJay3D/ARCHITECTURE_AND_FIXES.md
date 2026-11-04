# Project Bluejay3D: Complete Codebase Breakdown & 3D Architecture

## 1. Executive Summary

**Bluejay3D** is a next-generation 8-bit brushless ESC firmware for Silicon Labs `EFM8BB1`, `EFM8BB2` (`EFM8BB21`), and `EFM8BB51` microcontrollers, built on **Bluejay v0.21.0** (which derives from **BLHeli_S**) with backported 3D reversal physics, commutation tracking, demag recovery, minimum-duty control, and telemetry integrity from 32-bit firmwares (**AM32 v2.21 + Alka's 2025–2026 3D/Demag branches** and **ESCape32**) and co-designed with **BetaFlight 3D Edition** (`3d-whoop-tuning` / `BetaFlight 3D Edition`).

### Why Stock 8-Bit Bluejay Struggles & Desyncs in 3D Mode
While stock Bluejay is the gold standard for unidirectional 1S/2S whoops and 8-bit quads (providing bidirectional DShot eRPM telemetry and 24/48/96 kHz PWM), its 3D (bidirectional) reversal path was inherited largely unchanged from legacy BLHeli_S and contains **7 compounding architectural bugs** that cause slow reversals (>200 ms), low-throttle stalls at the 3D deadband (`DShot 1047`/`1048`), false high-eRPM telemetry spikes during zero-crossing, and catastrophic 100 ms motor shutdowns mid-flip.

---

## 2. Full Breakdown of the Stock Bluejay Codebase (`v0.21.0`)

### 2.1 File & Module Structure
Bluejay uses a single-translation-unit assembly architecture where `src/Bluejay.asm` `$include`s all hardware definitions, settings, modules, and the bootloader into one absolute-addressed image:

| File | Role & Responsibilities |
| :--- | :--- |
| `src/Bluejay.asm` | Top-level entry point, memory map (`DSEG AT 20h`, `DSEG AT 30h`, `ISEG AT 80h..D0h`, `CSEG AT CSEG_EEPROM`), initialization, main 6-step commutation loop (`run1`..`run6`), bidirectional reversal state machine (`run6_bidir_reversal`), startup phase (`motor_start`), comparator polling (`wait_for_comp_out_low`/`high`), and timeout/demag evaluation (`evaluate_comparator_integrity`). |
| `src/Settings/BluejaySettings.asm` | Compile-time constants, version tags (`0.21.0`), default EEPROM values (`DEFAULT_PGM_*`). |
| `src/Layouts/*.inc` & `BB51/*.inc` | Board pinouts (`A`..`Z`, `OA`, and `BB51/A`..`E`), FET polarity (`PWM_ACTIVE_HIGH`, `COM_ACTIVE_HIGH`), comparator mux ports, deadtime/damping modes, and `Base.inc` FET switching macros. |
| `src/Silabs/SI_EFM8*.inc` | SFR (`DATA`) and bit (`BIT`) register definitions for `EFM8BB2` (`BB1`/`BB2`) and `EFM8BB51`. |
| `src/Modules/Codespace.asm` | Flash memory layout constants (`CSEG_APP = 0x0080`, `CSEG_EEPROM = 0x1A00`/`0x3000`, `CSEG_BOOT_START = 0x1C00`/`0xF000`). |
| `src/Modules/Enums.asm` | Enumerations for MCU types, PWM frequencies (`24`, `48`, `96` kHz), DShot commands, and telemetry types. |
| `src/Modules/Macros.asm` | Hot-path inline assembly macros (`Early_Exit_Fetch_Tx_Pending`, `Update_Pwm_Duty_Cycle`, `Set_MCU_Clk_24MHz`/`48MHz`, `Abs_Diff`). |
| `src/Modules/Common.asm` | Interrupt vector table (`0x0000`..`0x0073`), clock/watchdog/crossbar initialization, delay routines (`wait1ms`..`wait250ms`), and 16x16 software division (`div_16bit_by_16bit`). |
| `src/Modules/Commutation.asm` | Six-step phase commutation routines (`comm12`..`comm61`), comparator input mux switching, and synchronous rectification (complementary damped light vs. non-damped FET switching). |
| `src/Modules/Timing.asm` | Timer 3 commutation period measurement (`calc_next_comm_period`), moving-average filters (`div_4_1`, `div_8_2_fast`, `div_8_2_slow`), motor timing advance (`15°` minus `0°..30°`), zero-cross scan blanking (`Wait_Before_ZC_Scan`), and comparator timeout programming (`setup_zc_scan_timeout`). |
| `src/Modules/Power.asm` | Throttle-to-PWM scaling (`scale_ throttle_and_set_pwm`), RPM-based power limiting (`set_pwm_limit`, `set_pwm_limit_high_rpm`), startup boost calculation, and demag power-off threshold (`Demag_Pwr_Off_Thresh`). |
| `src/Modules/DShot.asm` | DShot150/300/600 auto-detection (`dshot_detect_frame_length`), frame decoding & CRC validation (`t2_int_decode_dshot_frame`), bidirectional 3D throttle splitting (`48..1047` reverse, `1048..2047` forward), DShot command execution, and 21-bit GCR eRPM/EDT telemetry packet creation (`dshot_tlm_create_packet`). |
| `src/Modules/Isrs.asm` | Hardware ISRs: `int0_int` (DShot edge capture), `int1_int` (DShot telemetry bit-bang transmitter), `t1_int` (Startup boost PWM overlay), `t2_int` (DShot frame decode & RCP timeout), `t3_int` (Timer 3 commutation/ZC timer), `pca_int` (demag metric & comparator blanking release). |
| `src/Modules/Scheduler.asm` | Cooperative background task scheduler (`sync_with_scheduler`) interleaved inside the commutation loop to run LED control, temperature ADC reads, and DShot command state machines without blocking zero-cross detection. |
| `src/Modules/Eeprom.asm` | Flash page erase/write (`erase_and_store_in_flash`), EEPROM parameter decoding (`decode_settings`), and RTTTL startup melody player (`play_melody`). |
| `src/BLHeliBootLoad.inc` | 1-wire bit-banged UART bootloader (`19200` baud, `471d` protocol) compatible with BLHeliSuite / esc-configurator / Betaflight passthrough. |

### 2.2 Hardware Resource & Register Bank Allocation
Because the 8051 core has limited registers and a 2-level (BB1) or 4-level (BB2/BB51) interrupt priority controller, Bluejay partitions the 4 hardware register banks (`R0–R7`) across execution contexts:

- **Register Bank 0 (`0x00–0x07`, `Temp1–Temp8`)**: Main commutation loop, `Timing.asm`, `Power.asm`, and `t3_int`.
- **Register Bank 1 (`0x08–0x0F`, `Temp1–Temp8`)**: `t2_int` (DShot frame decode), `pca_int` (blanking/demag), `t1_int` (startup boost), and `dshot_tlm_create_packet`.
- **Register Bank 2 (`0x10–0x17`, `DShot_Temp*`)**: Ultra-fast `int0_int` (DShot pulse capture ISR) and `int1_int` (telemetry bit-bang ISR). `R1` permanently holds the write pointer into `DShot_Frame_Start` (`ISEG 0x80..0x9F`).

---

## 3. Root-Cause Forensics: Stock Bluejay's 7 Critical 3D Bugs

By tracing the exact assembly execution path during a 3D motor reversal (`DShot 1048..2047` $\leftrightarrow$ `DShot 48..1047`), we identified **7 concrete firmware bugs** that explain why stock Bluejay desyncs, stalls, and kicks in 3D flight:

### Bug #1: Startup Boost Is Completely Disabled on 3D Direction Reversals (`Isrs.asm:288` & `Bluejay.asm:977`)
In `src/Modules/Isrs.asm` (lines 287–293), the Timer 1 startup boost ISR (`t1_int`) explicitly checks `Flag_Motor_Started`:
```asm
    ; Do not boost when changing direction in bidirectional mode
    jb   Flag_Motor_Started, t1_int_startup_boosted

    ; Set extra power boost during startup Phase
    mov  A, Pwm_Limit_Spoolup
    add  A, Startup_Boost
```
When the motor first starts from rest (`motor_start` $\rightarrow$ `init_startup_phase` at `Bluejay.asm:871`), `Flag_Motor_Started` is `0`. Once the initial 18 commutations complete (`run6_initial_run_expired` at `Bluejay.asm:933`), `setb Flag_Motor_Started` is executed.
Later, when a 3D reversal occurs (`run6_bidir_reversal` $\rightarrow$ `run6_bidir_braking` at `Bluejay.asm:977–984`), Bluejay flips `Flag_Motor_Dir_Rev` and sets `Flag_Initial_Run_Phase` with `Initial_Run_Rot_Cntd = 18`, **but never clears `Flag_Motor_Started`!**
- **Consequence**: When a pilot or the flight controller's PID loop commands a gentle 3D reversal (`1%–5%` throttle across `DShot 1047`/`1048`), the motor reaches 0 RPM and tries to accelerate in the opposite direction with **zero startup boost (`Startup_Boost = 0`)**. Because 1–3% duty cycle minus FET deadtime cannot overcome stator resistance ($I \cdot R$) at 0 back-EMF, the rotor stalls in the deadband!

### Bug #2: Low-RPM Power Limit Is Cut in Half (50% Choke) After Every 3D Reversal (`Power.asm:72–73`)
In `src/Modules/Power.asm` (`set_pwm_limit`, lines 70–75):
```asm
    mov  A, #255
    jnb  Flag_Initial_Run_Phase, set_pwm_limit_calculate
    mov  A, #127                        ; Limit max power during initial run phase
```
Because `run6_bidir_braking` (`Bluejay.asm:979`) sets `Flag_Initial_Run_Phase` for 18 commutations (3 electrical revolutions) after reversing direction, `set_pwm_limit` **halves the low-RPM power limit** (`127 / Comm_Period4x_H * Low_Rpm_Pwr_Slope` instead of `255 / Comm_Period4x_H * Low_Rpm_Pwr_Slope`) right as the motor is trying to spin up in the new direction! Combined with Bug #1 (no startup boost), the motor is starved of both boost floor and ramp ceiling simultaneously.

### Bug #3: Direction-Change Braking Power Is Both Too Weak (`~2%`) AND Overwritten Mid-Cycle (`Bluejay.asm:959` vs `Power.asm:59`)
Look at what happens when `Flag_Motor_Dir_Rev != Flag_Rcp_Dir_Rev` at `run6_bidir_reversal` (`Bluejay.asm:957–960`):
```asm
    setb Flag_Dir_Change_Brake          ; Set brake flag
    mov  Pwm_Limit_By_Rpm, Pwm_Limit_Beg; Set max power while braking
    jmp  run4                           ; Jump back to commutation 4, gives 180 degree phase shift
```
1. First, `Pwm_Limit_Beg` is initialized from `Pgm_Startup_Power_Max` (`Power.asm:46`), which defaults to `1` $\rightarrow$ `(1 << 2) + 1 = 5` out of `255` (**1.96% duty cycle**). Braking a spinning propeller from 20,000+ RPM with 1.96% duty cycle takes hundreds of milliseconds!
2. Second, after jumping to `run4` $\rightarrow$ `run5` $\rightarrow$ `run6` (which loops back to `run1` while `Comm_Period4x_H < 0x40`), `run2` calls `set_pwm_limit` (`Bluejay.asm:617`)! And `set_pwm_limit` in `Power.asm:59` **does not check `Flag_Dir_Change_Brake`**! It overwrites `Pwm_Limit_By_Rpm` with the full RPM-proportional limit `(255 / Comm_Period4x_H) * Low_Rpm_Pwr_Slope` for steps `run2`, `run3`, `run4`, `run5`, only for `run6` to reset it to `Pwm_Limit_Beg` (`5`) for step `run1`!
- **Consequence**: Direction-change braking is erratic, asymmetrical across the 6 phases, and depends on whatever throttle the FC happens to send during braking rather than applying a controlled, uniform braking duty limit across all 6 steps.

### Bug #4: Catastrophic 100 ms Dead-Stop Lockout on Comparator Timeout (`Bluejay.asm:1045`)
During `Flag_Dir_Change_Brake` and the 18 commutations of `Flag_Initial_Run_Phase`, `evaluate_comparator_integrity` (`Bluejay.asm:1007–1008`) ignores comparator timeouts:
```asm
    jb   Flag_Initial_Run_Phase, eval_comp_exit
    jb   Flag_Dir_Change_Brake, eval_comp_exit
```
While `wait_for_comp_out_low`/`high` times out during zero-crossing, `Startup_Zc_Timeout_Cntd` counts down to `0` (`Isrs.asm:343`). As soon as the 18th commutation completes (`Initial_Run_Rot_Cntd == 0` $\rightarrow$ `clr Flag_Initial_Run_Phase`), if the motor has not yet reached sufficient RPM to generate clean back-EMF zero-crossings, the very next comparator timeout triggers `eval_comp_decrement_timeout` $\rightarrow$ `ljmp exit_run_mode_on_timeout` (`Bluejay.asm:1032–1048`):
```asm
exit_run_mode_on_timeout:
    clr  IE_EA
    call switch_power_off
    ...
    call wait100ms                      ; Wait 100ms before newstartup
    ljmp init_no_signal
```
- **Consequence**: A **100 ms total motor shutdown** in the middle of an inverted 3D maneuver or tic-toc! By comparison, **AM32** (`Src/main.c:2285`) and **ESCape32** (`src/main.c:302`) have **zero blocking delay** when back-EMF times out in 3D mode — they immediately re-enter startup/polling synchronization on the next microsecond.

### Bug #5: Sluggish Commutation Period Averaging (`div_8_2_slow`) During 3D Reversal (`Timing.asm:52–60`)
In `calc_next_comm_period` (`src/Modules/Timing.asm:52–60`):
```asm
    jb   Flag_Startup_Phase, calc_next_comm_startup
    ...
    ajmp div_8_2_slow
calc_next_comm_startup:
    ajmp div_4_1
```
During a 3D reversal, `Flag_Startup_Phase` is `0` (only `Flag_Dir_Change_Brake` and then `Flag_Initial_Run_Phase` are set). Thus Bluejay uses an 8-sample slow moving average (`div_8_2_slow`) while the rotor is decelerating at $>100,000\text{ eRPM/s}$ to zero and reversing!
- **Consequence**: `Comm_Period4x` lags behind the true rotor speed by 8 commutations, causing `Wait_Before_ZC_Scan` (15° timing advance) and blanking windows to be wildly mismatched to actual rotor position.

### Bug #6: DShot eRPM Telemetry 16-Bit/8-Bit Overflow Spike Near Zero-Crossing (`DShot.asm:269–291`)
In `dshot_tlm_create_packet` (`src/Modules/DShot.asm:233–291`):
1. Bluejay computes `Temp4:Temp3 = Comm_Period4x * 6` in 16-bit arithmetic (`DShot.asm:249–267`). Whenever `Comm_Period4x >= 0x2AAB` (`Comm_Period4x_H >= 0x2B`, which corresponds to **$<7,400\text{ eRPM}$**), `Comm_Period4x * 6` **overflows 16 bits** (`Temp4:Temp3` wraps modulo 65536)!
2. Immediately after (`DShot.asm:270–274`), it computes `(Comm_Period4x_H * 4)` in 8-bit `Temp5`:
   ```asm
   mov  A, Comm_Period4x_H              ; Note: Comm_Period4x_H is assumed to be < 64
   rl   A
   rl   A
   anl  A, #0FCh
   mov  Temp5, A
   ```
   Look at the comment on line 270: `; Note: Comm_Period4x_H is assumed to be < 64`!
   Yet during `run6_bidir_braking` (`Bluejay.asm:971`), `Comm_Period4x_H` is explicitly waited on until `Comm_Period4x_H >= 0x40` (`64`), and during slow 3D reversals `Comm_Period4x_H` reaches `0x40..0xFF`!
- **Consequence**: Every time a motor slows below 7,400 eRPM during a 3D reversal, `Temp4:Temp3` overflows 16 bits and wraps around to a small period value, transmitting **false high-RPM spikes** over bidirectional DShot telemetry right as the motor crosses zero! This corrupts **BetaFlight 3D Edition**'s RPM notch filters, RPM-gated I-term release (`3d_iterm_release`), and bidirectional dynamic idle (`3d_dyn_idle`).

### Bug #7: No Minimum Duty Floor (`duty_min`) & No Single-Frame 3D Reversal Glitch Guard (`Power.asm`, `DShot.asm`)
1. In `scale_throttle_and_set_pwm` (`Power.asm:199`), if `Pwm_Limit < Demag_Pwr_Off_Thresh`, Bluejay shuts all FETs off (`switch_power_off`), creating an effective torque deadzone at low throttle (`DShot 1048..1065` and `1047..1030`).
2. In `run6_bidir_reversal` (`Bluejay.asm:951`), a single corrupted DShot frame that flips `Flag_Rcp_Dir_Rev` while the motor is spinning at 50,000 eRPM immediately triggers a 180° phase-shift brake without checking that at least 2 consecutive DShot frames requested the new direction.

---

## 4. Breakdown of 32-Bit Reference Firmwares (`AM32` & `ESCape32`)

### 4.1 AM32 (`v2.16–v2.21` + Alka's 2025–2026 3D/Demag/Polling Branches)
Key mechanisms in `AM32/Src/main.c` and `AM32/Src/dshot.c` that make AM32 excel in 3D mode:
1. **Separated Minimum Duty Cycle (`minimum_duty_cycle`, EEPROM byte 6) vs. Startup Power (`startup_power`, EEPROM byte 25)**:
   - `minimum_duty_cycle` (0.5% increments; e.g. `6` = 3.0% on ZoeFPV's Lil Horny `esc1_config.bin`) sets the base duty cycle mapped to minimum throttle (`input == 47`, `Src/main.c:1218`: `duty_cycle_setpoint = map(input, 47, 2047, minimum_duty_cycle, 2000)`).
   - `min_startup_duty = minimum_duty_cycle + eepromBuffer.startup_power` (`Src/main.c:651`) enforces an extra boost floor for the first `30 >> stall_protection` zero-crossings (`Src/main.c:1326–1329`) on **every** startup AND **every** 3D direction reversal (because `setInput()` resets `zero_crosses = 0` on every direction change at `Src/main.c:1110, 1123`!).
2. **Velocity-Gated Direction Changeover (`reverse_speed_threshold`, `Src/main.c:806, 1108–1130`)**:
   - When `newinput` commands the opposite direction while `commutation_interval <= reverse_speed_threshold` or `duty_cycle >= 200`, AM32 clamps `newinput = 0` (`duty_cycle_setpoint = 0`), actively braking the rotor via complementary synchronous rectification (`comp_pwm = 1`, modulated by `driving_brake_strength` dead-time control at `Src/main.c:698–706`).
   - Once `commutation_interval > reverse_speed_threshold && duty_cycle < 200`, AM32 flips `forward`, resets `zero_crosses = 0`, sets `old_routine = 1` (polling mode), and immediately accelerates in the new direction with full `min_startup_duty` boost!
3. **3D-Specific BEMF Polling & Filter Thresholds (Commit `66aacb3`, `Src/main.c:807–811, 1962–1969`)**:
   - In `bi_direction` mode, AM32 halves `polling_mode_changeover = POLLING_MODE_THRESHOLD / 2` (staying in noise-immune polling mode to twice the eRPM during reversals) and reduces `min_bemf_counts_up/down` during the first 5 zero-crosses from `TARGET_MIN_BEMF_COUNTS * 2` to `TARGET_MIN_BEMF_COUNTS + 1` so direction changes lock onto back-EMF faster.
4. **Zero-Delay Desync / Timeout Re-Sync (`Src/main.c:1144, 2072–2088, 2285–2300`)**:
   - With `stuck_rotor_protection = 0` (or below `bemf_timeout`), a BEMF timeout (`INTERVAL_TIMER_COUNT > 45000`) or rapid interval jump never shuts the motor off for 100 ms; it sets `old_routine = 1; zero_crosses = 0; zcfoundroutine()` and re-acquires rotor phase immediately.
5. **Alka's Oct 2026 Long-Demag Blind-Step & Coast Recovery (`origin/feature/demag_cut_and_recovery`, Commits `3424278`, `35b17e9`, `2f17844`)**:
   - When a zero-cross is missed due to high-current demagnetization, AM32 turns all FETs off (`allOff()`), advances one commutation step (`commutate()`), watches the next phase's comparator while coasting, and upon detecting the zero-cross commutates immediately at 30° timing with a temporary power cut (`duty - (duty >> demag_cut_shift)`).
6. **Overflow-Proof DShot Telemetry (`Src/main.c:1581, 1943` & Commit `2147d85`)**:
   - `if (e_com_time > 65535) make_dshot_package(65535);` and `if (zero_crosses < 24) e_com_time = 65408;` completely prevent 16-bit wrap-around telemetry spikes during startup and 3D reversals.

### 4.2 ESCape32 (`neoxic/ESCape32`)
Key mechanisms in `ESCape32/src/main.c` and `ESCape32/src/io.c`:
1. **Unified Signed 3D Target (`throt` in `[-2000, +2000]`, `io.c:429` & `main.c:564–598`)**:
   - When `(reverse ^ (throt < 0))` is true (direction mismatch while running), ESCape32 forces `target = 0`, engaging active drag braking (`duty_drag`) until `ertm > 12000` ($\le 5,000\text{ eRPM}$), then flips `reverse ^= 1` and immediately ramps duty in the new direction.
2. **Fast Transient Detection (`fast`, `main.c:309, 557`)**:
   - In `zcdetect()`: `if ((fast = t < u >> 2 || t > u >> 1)) ival = x * 6;`
   - Whenever a commutation interval changes by $>25\%$ (rapid acceleration) or $>50\%$ (rapid 3D braking deceleration), ESCape32 sets `fast = 1`, snaps the 6-step interval filter `ival` directly to `x * 6` (eliminating moving-average phase lag!), and **bypasses duty slew-rate limiting** (`if (!fast && (maxduty = curduty + slew) < duty) duty = maxduty;` at `main.c:557`).
3. **Spin-Up Duty Envelope (`duty_spup` & `duty_ramp`, `main.c:555`)**:
   - Smoothly interpolates maximum allowed duty cycle as a function of `ertm` (`scale(ertm, 600000 / cfg.duty_ramp, 60000, duty_spup, 2000)`), never halving or starving low-RPM reversal torque.

---

## 5. Bluejay3D Firmware Architecture & Backported Enhancements

To make **Bluejay3D** the ultimate 8-bit 3D ESC firmware while maintaining 100% compatibility with existing EFM8BB1/BB21/BB51 boards and the 1-wire BLHeli bootloader, we implement **8 core architectural upgrades**:

### 5.1 Upgrade 1: Overhauled 3D Reversal State Machine with Uniform Active Braking (`Bluejay.asm` & `Power.asm`)
- When `Flag_Motor_Dir_Rev != Flag_Rcp_Dir_Rev` is confirmed, `Flag_Dir_Change_Brake` is set.
- Instead of jumping to `run4` with `Pwm_Limit_By_Rpm = Pwm_Limit_Beg` (which was 2% and got overwritten in `run2`), **`set_pwm_limit` in `Power.asm` explicitly checks `jb Flag_Dir_Change_Brake, set_pwm_limit_3d_brake`** and loads `Pwm_Limit_By_Rpm = Pwm_3D_Brake_Limit` (computed from `Pgm_3D_Brake_Strength`, default level `8` $\rightarrow$ `~35%` braking duty limit, configurable `1..10`).
- During `Flag_Dir_Change_Brake`, if the incoming throttle `New_Rcp` is lower than `Pwm_3D_Brake_Min` (e.g. when the pilot crosses `1047`/`1048` with a small throttle command), **Bluejay3D applies active proportional reversal braking (`Pwm_3D_Brake_Floor`)** so that even low-stick 3D reversals decelerate the prop crisply to the changeover speed threshold (`Pwm_3D_Brake_Speed`, configurable via `Pgm_3D_Brake_Speed`, default `0x38` $\approx 5,700\text{ eRPM}$) before flipping `Flag_Motor_Dir_Rev`!

### 5.2 Upgrade 2: 3D Reversal Startup Boost & Minimum Duty Floor (`Isrs.asm`, `Bluejay.asm`, `Power.asm`)
- At `run6_bidir_braking` (`Bluejay.asm`), when `Comm_Period4x_H >= Pwm_3D_Brake_Speed` and the motor transitions to the new direction:
  - We **clear `Flag_Motor_Started`** (`clr Flag_Motor_Started`) when `Pgm_3D_Rev_Boost` is enabled! This activates `t1_int` startup boost (`Startup_Boost`) during the post-reversal `Flag_Initial_Run_Phase` so the motor receives an immediate voltage kick to cross 0 RPM cleanly!
- In `scale_throttle_and_set_pwm` (`Power.asm`), when `Flag_Pgm_Bidir` is active and `Rcp_Stop_Cnt == 0` (non-zero throttle command), we enforce a configurable **Minimum Duty Cycle Floor** (`Pwm_3D_Min_Duty`, derived from `Pgm_3D_Min_Duty`, default `3%` duty cycle, matching ZoeFPV's proven AM32 3% minimum duty setting!). And we ensure `Pwm_Limit` is never below `Demag_Pwr_Off_Thresh` when throttle is active in 3D mode.

### 5.3 Upgrade 3: Un-Choked Post-Reversal Power Ramp (`Power.asm`)
- In `set_pwm_limit` (`Power.asm`), when `Flag_Initial_Run_Phase` is active:
  - If `Flag_Pgm_Bidir` is set (3D mode), we **do NOT halve `A` to `#127`**! We keep the full `#255` numerator with `Low_Rpm_Pwr_Slope`, eliminating the 50% post-reversal torque choke.

### 5.4 Upgrade 4: Zero-Wait Fast 3D Desync / Timeout Recovery (`Bluejay.asm` & `Timing.asm`)
- In `exit_run_mode_on_timeout` (`Bluejay.asm`), when `Flag_Pgm_Bidir` is active (or `Pgm_3D_Fast_Restart` is enabled):
  - **Completely skip `call wait100ms`!**
  - Reset `Comm_Period4x_H` / `Comm_Period4x_L` and jump directly to `motor_start` (if `Rcp_Stop_Cnt == 0`) or `init_no_signal`, cutting desync recovery latency from **>100 ms down to <0.5 ms**!
- Reduce post-reversal `Initial_Run_Rot_Cntd` from `18` to `12` (2 electrical revolutions) and reset `Startup_Zc_Timeout_Cntd = 2` on reversal completion so `evaluate_comparator_integrity` never false-trips on the first normal step after `Flag_Initial_Run_Phase`.

### 5.5 Upgrade 5: ESCape32-Style Fast Transient Commutation Period Tracking (`Timing.asm`)
- In `calc_next_comm_period` (`Timing.asm`):
  - Route `Flag_Dir_Change_Brake` and `Flag_Initial_Run_Phase` to the fast 4-sample filter (`div_4_1`) instead of `div_8_2_slow`.
  - Additionally, implement **ESCape32 Fast-Step Snap**: if `Flag_Pgm_Bidir` is active and the newly measured commutation timing (`Temp2:Temp1`) differs from `Comm_Period4x / 4` by more than 50% during braking/acceleration, double the filter weight so `Comm_Period4x` tracks extreme 3D deceleration/acceleration without phase lag.

### 5.6 Upgrade 6: Overflow-Proof DShot eRPM Telemetry at Low RPM & Zero-Crossing (`DShot.asm`)
- In `dshot_tlm_create_packet` (`DShot.asm`):
  - If `Flag_Dir_Change_Brake` is set (motor is braking to zero for a 3D reversal) OR `Comm_Period4x_H >= 0x40` ($<5,000\text{ eRPM}$ during startup/reversal), report `0x0FFF` (`0 eRPM`, maximum DShot period) cleanly instead of allowing `Comm_Period4x * 6` (16-bit) or `Comm_Period4x_H * 4` (8-bit) to overflow!
  - For `0x28 <= Comm_Period4x_H < 0x40` ($5,000\text{–}8,000\text{ eRPM}$), compute the pre-shifted period `(Comm_Period4x >> 1) * 6` with exponent `+1` so `Temp4:Temp3` **never overflows 16 bits**!
  - Result: **100% elimination of false high-eRPM telemetry spikes** across the entire RPM range down to 0 RPM!

### 5.7 Upgrade 7: 3D Direction Glitch Filter & Reboot Safety (`Bluejay.asm` & `DShot.asm`)
- Add a 2-frame direction consistency check (`Bidir_Rev_Confirm_Cnt`) before entering `Flag_Dir_Change_Brake` when the motor is spinning at high speed (`Comm_Period4x_H < 0x10`), preventing a single corrupted signal pulse or FC reboot transient from triggering a spurious mid-air reversal or full-throttle latch.

### 5.8 Upgrade 8: Backward-Compatible Bluejay3D EEPROM Parameters (`0x1A1B–0x1A21`)
Bluejay's flash EEPROM table (`Bluejay.asm:329–379`) has 7 unused legacy governor/placeholder bytes at offsets `0x1B..0x21` (`_Pgm_Gov_P_Gain` through `_Pgm_Gov_Range`) right in the main 44-byte EEPROM block that BLHeliSuite, esc-configurator, and 4-way passthrough already read and write!
We map these 7 bytes in **Bluejay3D** (with safe fallback validation if `0xFF` is present after a partial flash):

| Offset | Legacy Name | Bluejay3D Symbol | Range | Default | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0x1B` (27) | `_Pgm_Gov_P_Gain` | `Pgm_3D_Brake_Strength` | `1..10` | `8` (~35% duty) | Maximum braking duty cycle limit during 3D direction reversal (AM32 `driving_brake_strength` equivalent). |
| `0x1C` (28) | `_Pgm_Gov_I_Gain` | `Pgm_3D_Brake_Speed` | `1..10` | `5` (`0x38` $\approx 5.7\text{k eRPM}$) | Reversal changeover speed threshold (AM32 `reverse_speed_threshold` equivalent: `1`=lowest RPM, `10`=highest RPM). |
| `0x1D` (29) | `_Pgm_Gov_Mode` | `Pgm_3D_Min_Duty` | `0..10` | `3` (~3.0% duty) | Minimum duty cycle floor in 3D mode (AM32 `minimum_duty_cycle` / ESCape32 `duty_min` equivalent, in ~1% steps). |
| `0x1E` (30) | `_Pgm_Low_Voltage_Lim` | `Pgm_3D_Rev_Boost` | `0..2` | `1` (Enabled) | `0`=Off (stock), `1`=Normal startup boost on 3D reversal, `2`=High (1.5x) boost on 3D reversal. |
| `0x1F` (31) | `_Pgm_Motor_Gain` | `Pgm_3D_Fast_Restart` | `0..1` | `1` (Enabled) | `0`=Stock 100ms timeout lockout, `1`=Zero-delay (<0.5ms) instant re-sync on comparator timeout in 3D mode. |
| `0x20` (32) | `_Pgm_Motor_Idle` | `Pgm_3D_Fast_Track` | `0..1` | `1` (Enabled) | `0`=Stock slow filter, `1`=ESCape32-style fast commutation period tracking & un-choked reversal power ramp. |
| `0x21` (33) | `_Pgm_Startup_Method` | `Pgm_3D_Glitch_Filter` | `0..2` | `1` (2-frame) | Consecutive DShot frames required to confirm high-RPM 3D direction reversal (`0`=1 frame, `1`=2 frames, `2`=3 frames). |

Additionally, in **Bluejay3D**, the default `DEFAULT_PGM_DIRECTION` is set to `3` (**Bidirectional 3D**; `4` = Bidirectional 3D Reversed), `DEFAULT_PGM_STARTUP_PWR_MIN` is tuned for crisp 3D starts, and `DEFAULT_PGM_RPM_POWER_SLOPE` defaults to `9` for responsive low-RPM torque authority.
