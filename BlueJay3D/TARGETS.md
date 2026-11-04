# BlueJay3D: Firmware for Every 8-Bit ESC & AIO Board

**`v0.22.0-3D`**: **63 ESC target layouts (135 `.hex` firmware files)** across `EFM8BB21` (`_H_`) and `EFM8BB51` (`_X_`) at **24 kHz**, **48 kHz**, and **96 kHz**, all built from the same source tree.
After flashing, the ESC firmware tag reads **`Bluejay3D v0.22`** (version code `22.0`, EEPROM layout `v208`).
Once flashed, follow the **[pilot testing guide](TESTING_GUIDE.md)**.

> **Fly carefully and bench-check with props off first.** Please **[send your blackbox logs](https://docs.google.com/forms/d/e/1FAIpQLSfmN5fuS82CXPKGCXlqQAUPCoa6tT8LgZesW7zxZt6WFHSnpw/viewform)** (or via [GitHub Issue](https://github.com/BlindingBright/Drones/issues/new?template=bluejay3d_log_upload.yml)): that's how an ESC target gets flight-confirmed.
> ESC layout or board not listed? **[Request a build](https://docs.google.com/forms/d/e/1FAIpQLSegPRjFi6s6WUmWW0QfRsDMLYOeNchlNj9iVQxU-3Z2g0Upxw/viewform)** *(or [open a Target Request issue](https://github.com/BlindingBright/Drones/issues/new?template=bluejay3d_target_request.yml)).*

---

## How to find your ESC target code (takes 10 seconds)

⚠️ **Never guess your ESC layout!** Flashing the wrong letter (e.g. `O_H_5` vs `Z_H_30`) puts the FET gate drivers on the wrong pins and can damage the ESC.

1. Take **props OFF** and plug in USB + battery.
2. Open **[esc-configurator.com](https://esc-configurator.com)** (or the local **[Bluejay3D Configurator](configurator/)**) in Chrome/Edge and click **Connect** → **Read Settings**.
3. Look at the 5-character code printed under **ESC 1 – ESC 4** (for example: **`O_H_5`**, **`Z_H_30`**, **`S_H_50`**, **`G_H_30`**, or **`A_X_5`**).
   - **1st letter (`A`–`Z`)**: Pinout layout of the board. **Must match exactly.**
   - **2nd letter (`H` or `X`)**: MCU family (`H` = Silicon Labs `EFM8BB21` 48 MHz; `X` = `EFM8BB51` 48 MHz). **Must match.**
   - **Number (`0`–`90`)**: FET switching deadtime. **Must match.**
4. Pick your **PWM Frequency**:
   - **48 kHz**: Recommended for **1S/2S 3D whoops** (`0702–1103`) and **3"–4" toothpicks** (`1204–1404`). Best balance of braking authority and cool motors.
   - **24 kHz**: Recommended for **5-inch 3D quads** (`2207–2306`) and heavy props where maximum low-end braking torque is needed.
   - **96 kHz**: Optional for ultra-light 1S indoor whoops.

---

## Quick Lookup: Popular AIO Flight Controllers & 4-in-1 ESCs

*(Always verify the target code in `Read Settings` before flashing — manufacturers occasionally change ESC layouts between board revisions!)*

| Board / ESC Model | Typical ESC Target | MCU | Recommended Download (`v0.22.0-3D`) |
|---|---|---|---|
| **1S / 2S Whoop & Toothpick AIOs** | | | |
| **BetaFPV F4 1S 5A / 1S 12A / 2S 15A AIO** (Meteor65/75/85, Cetus Pro, Air65/75 BB21) | `O_H_5` | EFM8BB21 | **[⬇ 48 kHz](firmware/hex/O_H_5_48_v0.22.0-3D.hex)** · [⬇ 24 kHz](firmware/hex/O_H_5_24_v0.22.0-3D.hex) · [⬇ 96 kHz](firmware/hex/O_H_5_96_v0.22.0-3D.hex) |
| **Happymodel CrazyBee F4 SX1280 / Lite / Pro** (Mobula6, Mobula7, Mobula8, Mobeetle6) | `O_H_5` *(or `S_H_50`)* | EFM8BB21 | **[⬇ O_H_5 48k](firmware/hex/O_H_5_48_v0.22.0-3D.hex)** · **[⬇ S_H_50 48k](firmware/hex/S_H_50_48_v0.22.0-3D.hex)** |
| **Happymodel X12 5-in-1 1-2S 12A AIO** (Mobula7 1S HD, Crux35, Bassline) | `O_H_5` *(or `Z_H_30`)* | EFM8BB21 | **[⬇ O_H_5 48k](firmware/hex/O_H_5_48_v0.22.0-3D.hex)** · **[⬇ Z_H_30 48k](firmware/hex/Z_H_30_48_v0.22.0-3D.hex)** |
| **Happymodel CrazyF411 / CrazyF405 HD 12A–20A AIO** (Crux3, Larva X) | `S_H_50` *(or `O_H_15`)* | EFM8BB21 | **[⬇ S_H_50 48k](firmware/hex/S_H_50_48_v0.22.0-3D.hex)** · [⬇ O_H_15 48k](firmware/hex/O_H_15_48_v0.22.0-3D.hex) |
| **HGLRC Zeus 12A / 13A / 25A / 35A AIO** (Draknight, Petrel, Rekon) | `Z_H_30` | EFM8BB21 | **[⬇ 48 kHz](firmware/hex/Z_H_30_48_v0.22.0-3D.hex)** · [⬇ 24 kHz](firmware/hex/Z_H_30_24_v0.22.0-3D.hex) · [⬇ 96 kHz](firmware/hex/Z_H_30_96_v0.22.0-3D.hex) |
| **Flywoo Goku F411 / F405 / F722 1S–4S AIO (8-bit BLS)** (Firefly, Explorer) | `Z_H_30` *(or `O_H_5`)* | EFM8BB21 | **[⬇ Z_H_30 48k](firmware/hex/Z_H_30_48_v0.22.0-3D.hex)** · [⬇ O_H_5 48k](firmware/hex/O_H_5_48_v0.22.0-3D.hex) |
| **GEPRC Taker F411 12A / GEP-F411-35A AIO (8-bit BLS)** (TinyGO, Cinelog, Smart) | `Z_H_30` *(or `J_H_15`)* | EFM8BB21 | **[⬇ Z_H_30 48k](firmware/hex/Z_H_30_48_v0.22.0-3D.hex)** · [⬇ J_H_15 48k](firmware/hex/J_H_15_48_v0.22.0-3D.hex) |
| **DarwinFPV TinyApe 1-3S 15A ELRS AIO** (`DARWINF4SX1280HD`) | `O_H_5` *(or `B_X_30`)* | BB21 / BB51 | **[⬇ O_H_5 48k](firmware/hex/O_H_5_48_v0.22.0-3D.hex)** · **[⬇ B_X_30 48k](firmware/hex/B_X_30_48_v0.22.0-3D.hex)** |
| **EMAX Tinyhawk II / III / Freestyle AIO** | `A_H_5` *(or `M_H_5`)* | EFM8BB21 | **[⬇ A_H_5 48k](firmware/hex/A_H_5_48_v0.22.0-3D.hex)** · [⬇ M_H_5 48k](firmware/hex/M_H_5_48_v0.22.0-3D.hex) |
| **NewBeeDrone AcroBee / BeeBrain BLV4 AIO** | `M_H_5` *(or `O_H_5`)* | EFM8BB21 | **[⬇ M_H_5 48k](firmware/hex/M_H_5_48_v0.22.0-3D.hex)** · [⬇ O_H_5 48k](firmware/hex/O_H_5_48_v0.22.0-3D.hex) |
| **JHEMCU GHF411AIO / GHF405AIO / Play F4 (12A–40A BLS)** | `J_H_15` *(or `J_H_20`)* | EFM8BB21 | **[⬇ J_H_15 48k](firmware/hex/J_H_15_48_v0.22.0-3D.hex)** · [⬇ J_H_20 48k](firmware/hex/J_H_20_48_v0.22.0-3D.hex) |
| **BetaFPV Air / Meteor 2024+ 1S 5A AIO (EFM8BB51)** | `A_X_5` | EFM8BB51 | **[⬇ 48 kHz](firmware/hex/A_X_5_48_v0.22.0-3D.hex)** · [⬇ 24 kHz](firmware/hex/A_X_5_24_v0.22.0-3D.hex) · [⬇ 96 kHz](firmware/hex/A_X_5_96_v0.22.0-3D.hex) |
| **Happymodel SuperX HD / ELRS AIO (EFM8BB51)** | `B_X_30` *(or `A_X_5`)* | EFM8BB51 | **[⬇ B_X_30 48k](firmware/hex/B_X_30_48_v0.22.0-3D.hex)** · [⬇ A_X_5 48k](firmware/hex/A_X_5_48_v0.22.0-3D.hex) |
| **5-Inch / 20x20 & 30x30 4-in-1 Stack ESCs** | | | |
| **SpeedyBee F405 V3 / V4 BLS 50A / 55A / 60A 4-in-1** | `G_H_30` *(or `J_H_40`)* | EFM8BB21 | **[⬇ G_H_30 24k](firmware/hex/G_H_30_24_v0.22.0-3D.hex)** · [⬇ G_H_30 48k](firmware/hex/G_H_30_48_v0.22.0-3D.hex) · [⬇ J_H_40 24k](firmware/hex/J_H_40_24_v0.22.0-3D.hex) |
| **SpeedyBee F405 Mini BLS 35A 4-in-1 (20x20)** | `J_H_25` *(or `G_H_30`)* | EFM8BB21 | **[⬇ J_H_25 24k](firmware/hex/J_H_25_24_v0.22.0-3D.hex)** · [⬇ J_H_25 48k](firmware/hex/J_H_25_48_v0.22.0-3D.hex) · [⬇ G_H_30 24k](firmware/hex/G_H_30_24_v0.22.0-3D.hex) |
| **Diatone Mamba F40 / F50 / F55 / F60 BLS 4-in-1** | `G_H_30` *(or `J_H_50`)* | EFM8BB21 | **[⬇ G_H_30 24k](firmware/hex/G_H_30_24_v0.22.0-3D.hex)** · [⬇ J_H_50 24k](firmware/hex/J_H_50_24_v0.22.0-3D.hex) |
| **iFlight SucceX-E 45A / Blitz E45S / E55S 4-in-1 BLS** | `Q_H_20` *(or `Q_H_25`)* | EFM8BB21 | **[⬇ Q_H_20 24k](firmware/hex/Q_H_20_24_v0.22.0-3D.hex)** · [⬇ Q_H_20 48k](firmware/hex/Q_H_20_48_v0.22.0-3D.hex) · [⬇ Q_H_25 24k](firmware/hex/Q_H_25_24_v0.22.0-3D.hex) |
| **Hobbywing XRotor Micro 40A / 60A BLHeli_S 4-in-1** | `H_H_30` *(or `H_H_40`)* | EFM8BB21 | **[⬇ H_H_30 24k](firmware/hex/H_H_30_24_v0.22.0-3D.hex)** · [⬇ H_H_30 48k](firmware/hex/H_H_30_48_v0.22.0-3D.hex) · [⬇ H_H_40 24k](firmware/hex/H_H_40_24_v0.22.0-3D.hex) |
| **Foxeer Reaper F4 45A / 60A / Mini BLS 4-in-1** | `H_H_30` *(or `G_H_30`)* | EFM8BB21 | **[⬇ H_H_30 24k](firmware/hex/H_H_30_24_v0.22.0-3D.hex)** · [⬇ G_H_30 24k](firmware/hex/G_H_30_24_v0.22.0-3D.hex) |
| **T-Motor Velox V2 45A / 50A BLS 4-in-1** | `J_H_30` *(or `G_H_30`)* | EFM8BB21 | **[⬇ J_H_30 24k](firmware/hex/J_H_30_24_v0.22.0-3D.hex)** · [⬇ G_H_30 24k](firmware/hex/G_H_30_24_v0.22.0-3D.hex) |
| **Skystars Kramam /KO45 / KO55 / KM50 BLS 4-in-1** | `J_H_30` *(or `B_X_30`)* | BB21 / BB51 | **[⬇ J_H_30 24k](firmware/hex/J_H_30_24_v0.22.0-3D.hex)** · [⬇ B_X_30 24k](firmware/hex/B_X_30_24_v0.22.0-3D.hex) |
| **GEPRC SPAN F405 / Taker G50A BLS 4-in-1** | `Q_H_25` *(or `G_H_30`)* | EFM8BB21 | **[⬇ Q_H_25 24k](firmware/hex/Q_H_25_24_v0.22.0-3D.hex)** · [⬇ G_H_30 24k](firmware/hex/G_H_30_24_v0.22.0-3D.hex) |

---

## All 63 Built ESC Layouts (135 Firmware Files)

### Silicon Labs `EFM8BB21` Targets (`_H_`)

| ESC Target Code | Deadtime | 24 kHz Download | 48 kHz Download | 96 kHz Download |
|---|---|---|---|---|
| **`A_H_0`** | 0 | [⬇ 24 kHz](firmware/hex/A_H_0_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/A_H_0_48_v0.22.0-3D.hex) | [⬇ 96 kHz](firmware/hex/A_H_0_96_v0.22.0-3D.hex) |
| **`A_H_5`** | 5 | [⬇ 24 kHz](firmware/hex/A_H_5_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/A_H_5_48_v0.22.0-3D.hex) | [⬇ 96 kHz](firmware/hex/A_H_5_96_v0.22.0-3D.hex) |
| **`A_H_10`** | 10 | [⬇ 24 kHz](firmware/hex/A_H_10_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/A_H_10_48_v0.22.0-3D.hex) | — |
| **`A_H_15`** | 15 | [⬇ 24 kHz](firmware/hex/A_H_15_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/A_H_15_48_v0.22.0-3D.hex) | — |
| **`A_H_20`** | 20 | [⬇ 24 kHz](firmware/hex/A_H_20_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/A_H_20_48_v0.22.0-3D.hex) | — |
| **`A_H_25`** | 25 | [⬇ 24 kHz](firmware/hex/A_H_25_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/A_H_25_48_v0.22.0-3D.hex) | — |
| **`A_H_30`** | 30 | [⬇ 24 kHz](firmware/hex/A_H_30_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/A_H_30_48_v0.22.0-3D.hex) | — |
| **`B_H_10`** | 10 | [⬇ 24 kHz](firmware/hex/B_H_10_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/B_H_10_48_v0.22.0-3D.hex) | — |
| **`C_H_15`** | 15 | [⬇ 24 kHz](firmware/hex/C_H_15_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/C_H_15_48_v0.22.0-3D.hex) | — |
| **`C_H_25`** | 25 | [⬇ 24 kHz](firmware/hex/C_H_25_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/C_H_25_48_v0.22.0-3D.hex) | — |
| **`C_H_40`** | 40 | [⬇ 24 kHz](firmware/hex/C_H_40_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/C_H_40_48_v0.22.0-3D.hex) | — |
| **`D_H_20`** | 20 | [⬇ 24 kHz](firmware/hex/D_H_20_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/D_H_20_48_v0.22.0-3D.hex) | — |
| **`E_H_10`** | 10 | [⬇ 24 kHz](firmware/hex/E_H_10_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/E_H_10_48_v0.22.0-3D.hex) | — |
| **`F_H_40`** | 40 | [⬇ 24 kHz](firmware/hex/F_H_40_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/F_H_40_48_v0.22.0-3D.hex) | — |
| **`G_H_20`** | 20 | [⬇ 24 kHz](firmware/hex/G_H_20_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/G_H_20_48_v0.22.0-3D.hex) | — |
| **`G_H_30`** | 30 | [⬇ 24 kHz](firmware/hex/G_H_30_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/G_H_30_48_v0.22.0-3D.hex) | [⬇ 96 kHz](firmware/hex/G_H_30_96_v0.22.0-3D.hex) |
| **`H_H_15`** | 15 | [⬇ 24 kHz](firmware/hex/H_H_15_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/H_H_15_48_v0.22.0-3D.hex) | — |
| **`H_H_20`** | 20 | [⬇ 24 kHz](firmware/hex/H_H_20_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/H_H_20_48_v0.22.0-3D.hex) | — |
| **`H_H_30`** | 30 | [⬇ 24 kHz](firmware/hex/H_H_30_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/H_H_30_48_v0.22.0-3D.hex) | — |
| **`H_H_40`** | 40 | [⬇ 24 kHz](firmware/hex/H_H_40_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/H_H_40_48_v0.22.0-3D.hex) | — |
| **`H_H_50`** | 50 | [⬇ 24 kHz](firmware/hex/H_H_50_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/H_H_50_48_v0.22.0-3D.hex) | — |
| **`H_H_70`** | 70 | [⬇ 24 kHz](firmware/hex/H_H_70_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/H_H_70_48_v0.22.0-3D.hex) | — |
| **`J_H_15`** | 15 | [⬇ 24 kHz](firmware/hex/J_H_15_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/J_H_15_48_v0.22.0-3D.hex) | [⬇ 96 kHz](firmware/hex/J_H_15_96_v0.22.0-3D.hex) |
| **`J_H_20`** | 20 | [⬇ 24 kHz](firmware/hex/J_H_20_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/J_H_20_48_v0.22.0-3D.hex) | — |
| **`J_H_25`** | 25 | [⬇ 24 kHz](firmware/hex/J_H_25_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/J_H_25_48_v0.22.0-3D.hex) | — |
| **`J_H_30`** | 30 | [⬇ 24 kHz](firmware/hex/J_H_30_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/J_H_30_48_v0.22.0-3D.hex) | — |
| **`J_H_40`** | 40 | [⬇ 24 kHz](firmware/hex/J_H_40_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/J_H_40_48_v0.22.0-3D.hex) | — |
| **`J_H_50`** | 50 | [⬇ 24 kHz](firmware/hex/J_H_50_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/J_H_50_48_v0.22.0-3D.hex) | — |
| **`J_H_70`** | 70 | [⬇ 24 kHz](firmware/hex/J_H_70_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/J_H_70_48_v0.22.0-3D.hex) | — |
| **`J_H_90`** | 90 | [⬇ 24 kHz](firmware/hex/J_H_90_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/J_H_90_48_v0.22.0-3D.hex) | — |
| **`K_H_20`** | 20 | [⬇ 24 kHz](firmware/hex/K_H_20_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/K_H_20_48_v0.22.0-3D.hex) | — |
| **`L_H_10`** | 10 | [⬇ 24 kHz](firmware/hex/L_H_10_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/L_H_10_48_v0.22.0-3D.hex) | — |
| **`L_H_20`** | 20 | [⬇ 24 kHz](firmware/hex/L_H_20_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/L_H_20_48_v0.22.0-3D.hex) | — |
| **`M_H_5`** | 5 | [⬇ 24 kHz](firmware/hex/M_H_5_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/M_H_5_48_v0.22.0-3D.hex) | [⬇ 96 kHz](firmware/hex/M_H_5_96_v0.22.0-3D.hex) |
| **`M_H_20`** | 20 | [⬇ 24 kHz](firmware/hex/M_H_20_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/M_H_20_48_v0.22.0-3D.hex) | — |
| **`N_H_20`** | 20 | [⬇ 24 kHz](firmware/hex/N_H_20_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/N_H_20_48_v0.22.0-3D.hex) | — |
| **`O_H_5`** | 5 | [⬇ 24 kHz](firmware/hex/O_H_5_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/O_H_5_48_v0.22.0-3D.hex) | [⬇ 96 kHz](firmware/hex/O_H_5_96_v0.22.0-3D.hex) |
| **`O_H_10`** | 10 | [⬇ 24 kHz](firmware/hex/O_H_10_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/O_H_10_48_v0.22.0-3D.hex) | — |
| **`O_H_15`** | 15 | [⬇ 24 kHz](firmware/hex/O_H_15_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/O_H_15_48_v0.22.0-3D.hex) | — |
| **`O_H_20`** | 20 | [⬇ 24 kHz](firmware/hex/O_H_20_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/O_H_20_48_v0.22.0-3D.hex) | — |
| **`O_H_30`** | 30 | [⬇ 24 kHz](firmware/hex/O_H_30_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/O_H_30_48_v0.22.0-3D.hex) | — |
| **`P_H_20`** | 20 | [⬇ 24 kHz](firmware/hex/P_H_20_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/P_H_20_48_v0.22.0-3D.hex) | — |
| **`Q_H_15`** | 15 | [⬇ 24 kHz](firmware/hex/Q_H_15_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/Q_H_15_48_v0.22.0-3D.hex) | — |
| **`Q_H_20`** | 20 | [⬇ 24 kHz](firmware/hex/Q_H_20_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/Q_H_20_48_v0.22.0-3D.hex) | [⬇ 96 kHz](firmware/hex/Q_H_20_96_v0.22.0-3D.hex) |
| **`Q_H_25`** | 25 | [⬇ 24 kHz](firmware/hex/Q_H_25_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/Q_H_25_48_v0.22.0-3D.hex) | — |
| **`Q_H_30`** | 30 | [⬇ 24 kHz](firmware/hex/Q_H_30_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/Q_H_30_48_v0.22.0-3D.hex) | — |
| **`Q_H_40`** | 40 | [⬇ 24 kHz](firmware/hex/Q_H_40_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/Q_H_40_48_v0.22.0-3D.hex) | — |
| **`Q_H_50`** | 50 | [⬇ 24 kHz](firmware/hex/Q_H_50_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/Q_H_50_48_v0.22.0-3D.hex) | — |
| **`R_H_20`** | 20 | [⬇ 24 kHz](firmware/hex/R_H_20_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/R_H_20_48_v0.22.0-3D.hex) | — |
| **`S_H_20`** | 20 | [⬇ 24 kHz](firmware/hex/S_H_20_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/S_H_20_48_v0.22.0-3D.hex) | — |
| **`S_H_30`** | 30 | [⬇ 24 kHz](firmware/hex/S_H_30_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/S_H_30_48_v0.22.0-3D.hex) | — |
| **`S_H_40`** | 40 | [⬇ 24 kHz](firmware/hex/S_H_40_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/S_H_40_48_v0.22.0-3D.hex) | — |
| **`S_H_50`** | 50 | [⬇ 24 kHz](firmware/hex/S_H_50_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/S_H_50_48_v0.22.0-3D.hex) | [⬇ 96 kHz](firmware/hex/S_H_50_96_v0.22.0-3D.hex) |
| **`T_H_20`** | 20 | [⬇ 24 kHz](firmware/hex/T_H_20_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/T_H_20_48_v0.22.0-3D.hex) | — |
| **`U_H_20`** | 20 | [⬇ 24 kHz](firmware/hex/U_H_20_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/U_H_20_48_v0.22.0-3D.hex) | — |
| **`W_H_30`** | 30 | [⬇ 24 kHz](firmware/hex/W_H_30_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/W_H_30_48_v0.22.0-3D.hex) | — |
| **`Z_H_30`** | 30 | [⬇ 24 kHz](firmware/hex/Z_H_30_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/Z_H_30_48_v0.22.0-3D.hex) | [⬇ 96 kHz](firmware/hex/Z_H_30_96_v0.22.0-3D.hex) |

### Silicon Labs `EFM8BB51` Targets (`_X_`)

| ESC Target Code | Deadtime | 24 kHz Download | 48 kHz Download | 96 kHz Download |
|---|---|---|---|---|
| **`A_X_5`** | 5 | [⬇ 24 kHz](firmware/hex/A_X_5_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/A_X_5_48_v0.22.0-3D.hex) | [⬇ 96 kHz](firmware/hex/A_X_5_96_v0.22.0-3D.hex) |
| **`B_X_30`** | 30 | [⬇ 24 kHz](firmware/hex/B_X_30_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/B_X_30_48_v0.22.0-3D.hex) | [⬇ 96 kHz](firmware/hex/B_X_30_96_v0.22.0-3D.hex) |
| **`C_X_30`** | 30 | [⬇ 24 kHz](firmware/hex/C_X_30_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/C_X_30_48_v0.22.0-3D.hex) | — |
| **`D_X_30`** | 30 | [⬇ 24 kHz](firmware/hex/D_X_30_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/D_X_30_48_v0.22.0-3D.hex) | — |
| **`E_X_30`** | 30 | [⬇ 24 kHz](firmware/hex/E_X_30_24_v0.22.0-3D.hex) | [⬇ 48 kHz](firmware/hex/E_X_30_48_v0.22.0-3D.hex) | — |

Full SHA-256 checksums for all 135 files: **[`firmware/SHA256SUMS.txt`](firmware/SHA256SUMS.txt)**.

---

## Need another layout or deadtime?

Any `(LAYOUT, MCU, DEADTIME, PWM)` combination supported by Bluejay can be built in 2 seconds with [BUILD_FROM_SOURCE.md](BUILD_FROM_SOURCE.md), or **[request a build](https://docs.google.com/forms/d/e/1FAIpQLSegPRjFi6s6WUmWW0QfRsDMLYOeNchlNj9iVQxU-3Z2g0Upxw/viewform)** *(or [open a GitHub Target Request](https://github.com/BlindingBright/Drones/issues/new?template=bluejay3d_target_request.yml))* and we'll build it and add it to this table.
