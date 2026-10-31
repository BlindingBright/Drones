# BetaFlight 3D Edition: firmware for every board

**v0.2.2-test**: 44 flight controllers, all built from the same commit (`b5fa258ef`, Betaflight 4.5.1 base).
After flashing, the CLI `version` command shows `4.5.1 ... (b5fa258ef)`. All files are on the
[v0.2.2-test release page](https://github.com/BlindingBright/betaflight/releases/tag/v0.2.2-3d-test).
Then follow the **[testing guide](TESTING_GUIDE.md)**.

> **Most of these builds have not been flown yet.** The Lucid AIO is the board the change was developed and flight-tested on.
> Fly carefully, and please [send your logs](https://forms.gle/Vfq3c2W7Lp5FE36t5): that's how a board gets confirmed.
> Board not listed? **[Request a build](https://forms.gle/1p93ZjiqDp1PLWA96).**

**New in this release (requested boards):** DarwinFPV TinyApe `DARWINF4SX1280HD`, Flywoo GOKU F722 Pro V2 `FLYWOOF722PROV2`,
Sequre H7 V2 `SEQUREH7V2`.

**Already on Betaflight 2026.6?** The 3D Edition is built on 4.5.1; flashing it means going back to 4.5.1 (back up `diff all`
first; a few newer settings won't paste back). An older v0.1 build on the 2026.6.2 base exists for the Hobbywing XRotor F7 Conv
([release](https://github.com/BlindingBright/betaflight/releases/tag/v0.1.0-3d-test-2026.6)); it does **not** have the v0.2 features
(learned-trim memory upgrades, RPM release). A v0.2.2 port to 2026.6 is planned.

**Older version:** v0.1.0-test files for 41 boards stay on the [v0.1.0-test release](https://github.com/BlindingBright/betaflight/releases/tag/v0.1.0-3d-test).
Use v0.2.2 for new tests.

## Pick your board
Find your board name: Betaflight Configurator → CLI → `version`. The name at the end of that line must match the
**Betaflight target** column exactly. Flashing the wrong target can leave motors or the gyro on the wrong pins.

| Board | Betaflight target | MCU | Download (v0.2.2, 4.5.1 base) |
|---|---|---|---|
| **Whoop / AIO** | | | |
| TBS Lucid AIO 1-2S | `TBS_LUCID_AIO` | AT32F435M | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_TBS_LUCID_AIO.hex) |
| Happymodel CrazyBee F4 SX1280 (ELRS) | `CRAZYBEEF4SX1280` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_CRAZYBEEF4SX1280.hex) |
| Happymodel CrazyBee F4 DX | `CRAZYBEEF4DX` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_CRAZYBEEF4DX.hex) |
| Happymodel CrazyBee F4 FR | `CRAZYBEEF4FR` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_CRAZYBEEF4FR.hex) |
| BetaFPV F4 1S/2S AIO SX1280 (ELRS) | `BETAFPVF4SX1280` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_BETAFPVF4SX1280.hex) |
| BetaFPV F411 AIO | `BETAFPVF411` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_BETAFPVF411.hex) |
| GEPRC F411 SX1280 AIO (ELRS) | `GEPRCF411SX1280` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_GEPRCF411SX1280.hex) |
| iFlight F4 SX1280 AIO (ELRS) | `IFLIGHT_F4SX1280` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_IFLIGHT_F4SX1280.hex) |
| T-Motor F4 SX1280 AIO (ELRS) | `TMOTORF4SX1280` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_TMOTORF4SX1280.hex) |
| JHE F411 | `JHEF411` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_JHEF411.hex) |
| Matek F411 | `MATEKF411` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_MATEKF411.hex) |
| Flywoo F411 5-in-1 AIO | `FLYWOOF411_5IN1_AIO` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_FLYWOOF411_5IN1_AIO.hex) |
| DarwinFPV TinyApe 2S ELRS AIO (no blackbox flash) | `DARWINF4SX1280HD` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_DARWINF4SX1280HD.hex) |
| **5-inch / stack** | | | |
| TBS Lucid FC | `TBS_LUCID_FC` | AT32F435M | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_TBS_LUCID_FC.hex) |
| TBS Lucid H7 | `TBS_LUCID_H7` | STM32H743 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_TBS_LUCID_H7.hex) |
| Hobbywing XRotor F7 Conv (ZoeFPV's 5-inch 3D quad) | `HOBBYWING_XROTORF7CONV` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_HOBBYWING_XROTORF7CONV.hex) · [2026.6.2 base, v0.1 only](https://github.com/BlindingBright/betaflight/releases/download/v0.1.0-3d-test-2026.6/BetaFlight3DEdition_v0.1.0-test-2026.6_HOBBYWING_XROTORF7CONV.hex) |
| SpeedyBee F405 V3 | `SPEEDYBEEF405V3` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_SPEEDYBEEF405V3.hex) |
| SpeedyBee F405 V4 | `SPEEDYBEEF405V4` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_SPEEDYBEEF405V4.hex) |
| SpeedyBee F405 Mini | `SPEEDYBEEF405MINI` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_SPEEDYBEEF405MINI.hex) |
| SpeedyBee F405 AIO | `SPEEDYBEEF405AIO` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_SPEEDYBEEF405AIO.hex) |
| SpeedyBee F7 V3 | `SPEEDYBEEF7V3` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_SPEEDYBEEF7V3.hex) |
| Diatone Mamba F405 (2022B) | `MAMBAF405_2022B` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_MAMBAF405_2022B.hex) |
| Diatone Mamba F722 (2022B) | `MAMBAF722_2022B` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_MAMBAF722_2022B.hex) |
| Matek F405-SE | `MATEKF405SE` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_MATEKF405SE.hex) |
| Matek F405-TE | `MATEKF405TE` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_MATEKF405TE.hex) |
| Matek F722-SE | `MATEKF722SE` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_MATEKF722SE.hex) |
| Matek H743 | `MATEKH743` | STM32H743 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_MATEKH743.hex) |
| Holybro Kakute F7 V2 | `KAKUTEF7V2` | STM32F745 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_KAKUTEF7V2.hex) |
| Holybro Kakute H7 | `KAKUTEH7` | STM32H743 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_KAKUTEH7.hex) |
| Holybro Kakute H7 V2 | `KAKUTEH7V2` | STM32H743 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_KAKUTEH7V2.hex) |
| Foxeer F722 V4 | `FOXEERF722V4` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_FOXEERF722V4.hex) |
| Foxeer H743 | `FOXEERH743` | STM32H743 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_FOXEERH743.hex) |
| iFlight BLITZ F722 | `IFLIGHT_BLITZ_F722` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_IFLIGHT_BLITZ_F722.hex) |
| iFlight BLITZ F7 AIO | `IFLIGHT_BLITZ_F7_AIO` | STM32F745 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_IFLIGHT_BLITZ_F7_AIO.hex) |
| JHE F7 Dual | `JHEF7DUAL` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_JHEF7DUAL.hex) |
| JHE F405 Pro | `JHEF405PRO` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_JHEF405PRO.hex) |
| GEPRC F405 | `GEPRCF405` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_GEPRCF405.hex) |
| GEPRC F722 | `GEPRCF722` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_GEPRCF722.hex) |
| T-Motor F7 V2 | `TMOTORF7V2` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_TMOTORF7V2.hex) |
| Flywoo F405S AIO | `FLYWOOF405S_AIO` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_FLYWOOF405S_AIO.hex) |
| BetaFPV F405 | `BETAFPVF405` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_BETAFPVF405.hex) |
| BetaFPV F722 | `BETAFPVF722` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_BETAFPVF722.hex) |
| Flywoo GOKU F722 Pro V2 | `FLYWOOF722PROV2` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_FLYWOOF722PROV2.hex) |
| Sequre H7 V2 | `SEQUREH7V2` | STM32H743 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.2.2-3d-test/BetaFlight3DEdition_v0.2.2-test_SEQUREH7V2.hex) |

## How to test
The [testing guide](TESTING_GUIDE.md) works for every board in this list: back up, flash, paste Block A, fly 2 packs,
paste Block B, fly 2 packs, upload. The only board-specific choice is in step 8: use `3d_iterm_release = RPM` only if your
ESCs give RPM telemetry (`dshot_bidir = ON`: AM32, Bluejay, BLHeli_32). Stock BLHeli_S has none.

Notes on requested boards:
- **DarwinFPV TinyApe (`DARWINF4SX1280HD`)**: built-in SPI ExpressLRS is enabled on the 4.5.1 target. Coming from
  Betaflight 4.4.2, re-bind after flashing, check the binding phrase, and check that your transmitter's ELRS version matches. The board has **no blackbox flash**, so it can't record
  logs; DVR plus a written report still helps (see the guide's "No blackbox" note).
- **Flywoo GOKU F722 Pro V2 / Sequre H7 V2**: 16 MB flash; on a 5-inch at 8 kHz, `set blackbox_sample_rate = 1/4` or `1/8`
  helps a full pack fit.
