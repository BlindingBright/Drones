# BetaFlight 3D Edition: firmware for every board

**v0.3.1-test**: 89 flight controllers, all built from the same commit (`161e867a9`, Betaflight 4.5.1 base).
After flashing, the CLI `version` command shows `4.5.1 ... (161e867a9)`. All files are on the
[v0.3.1-test release page](https://github.com/BlindingBright/betaflight/releases/tag/v0.3.1-3d-test).
Then follow the **[testing guide](TESTING_GUIDE.md)**.

> **Most of these builds have not been flown yet.** The Lucid AIO is the board the change was developed and flight-tested on.
> Fly carefully, and please [send your logs](https://forms.gle/Vfq3c2W7Lp5FE36t5): that's how a board gets confirmed.
> Board not listed? **[Request a build](https://forms.gle/1p93ZjiqDp1PLWA96).**

**New in v0.3.1 (requested boards):** DarwinFPV F435 AIO `DARWINF435`, JHEMCU H743 AIO `JHEH743_AIO`,
Flywoo GOKU F722 Pro V1 / Mini `FLYWOOF722PRO`.

**Added in v0.3.0 (requested boards):** DarwinFPV TinyApe `DARWINF4SX1280HD`, Flywoo GOKU F722 Pro V2 `FLYWOOF722PROV2`,
Sequre H7 V2 `SEQUREH7V2`.

**Already on Betaflight 2026.6?** The 3D Edition is built on 4.5.1; flashing it means going back to 4.5.1 (back up `diff all`
first; a few newer settings won't paste back). An older v0.1 build on the 2026.6.2 base exists for the Hobbywing XRotor F7 Conv
([release](https://github.com/BlindingBright/betaflight/releases/tag/v0.1.0-3d-test-2026.6)); it does **not** have the v0.2 features
(learned-trim memory upgrades, RPM release). A port of the current version to 2026.6 is planned.

**Older versions:** [v0.3.0-test](https://github.com/BlindingBright/betaflight/releases/tag/v0.3.0-3d-test),
[v0.2.2-test](https://github.com/BlindingBright/betaflight/releases/tag/v0.2.2-3d-test) and
[v0.1.0-test](https://github.com/BlindingBright/betaflight/releases/tag/v0.1.0-3d-test) files stay on their release pages.
Use v0.3.1 for new tests.

## Pick your board
Find your board name: Betaflight Configurator → CLI → `version`. The name at the end of that line must match the
**Betaflight target** column exactly. Flashing the wrong target can leave motors or the gyro on the wrong pins.

| Board | Betaflight target | MCU | Download (v0.3.1, 4.5.1 base) |
|---|---|---|---|
| **Whoop / AIO** | | | |
| TBS Lucid AIO 1-2S | `TBS_LUCID_AIO` | AT32F435M | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_TBS_LUCID_AIO.hex) |
| Happymodel CrazyBee F4 SX1280 (ELRS) | `CRAZYBEEF4SX1280` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_CRAZYBEEF4SX1280.hex) |
| Happymodel CrazyBee F4 DX | `CRAZYBEEF4DX` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_CRAZYBEEF4DX.hex) |
| Happymodel CrazyBee F4 FR | `CRAZYBEEF4FR` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_CRAZYBEEF4FR.hex) |
| BetaFPV F4 1S/2S AIO SX1280 (ELRS) | `BETAFPVF4SX1280` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_BETAFPVF4SX1280.hex) |
| BetaFPV F411 AIO | `BETAFPVF411` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_BETAFPVF411.hex) |
| GEPRC F411 SX1280 AIO (ELRS) | `GEPRCF411SX1280` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_GEPRCF411SX1280.hex) |
| iFlight F4 SX1280 AIO (ELRS) | `IFLIGHT_F4SX1280` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_IFLIGHT_F4SX1280.hex) |
| T-Motor F4 SX1280 AIO (ELRS) | `TMOTORF4SX1280` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_TMOTORF4SX1280.hex) |
| JHE F411 | `JHEF411` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_JHEF411.hex) |
| Matek F411 | `MATEKF411` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_MATEKF411.hex) |
| Flywoo F411 5-in-1 AIO | `FLYWOOF411_5IN1_AIO` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_FLYWOOF411_5IN1_AIO.hex) |
| DarwinFPV TinyApe 2S ELRS AIO (no blackbox flash) | `DARWINF4SX1280HD` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_DARWINF4SX1280HD.hex) |
| DarwinFPV F435 AIO | `DARWINF435` | AT32F435G | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_DARWINF435.hex) |
| JHEMCU H743 AIO | `JHEH743_AIO` | STM32H743 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_JHEH743_AIO.hex) |
| Fractal Engineering SP8 1S AIO (AM32 8A, built-in ELRS) | `FRACSP8AIO` | AT32F435G | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_FRACSP8AIO.hex) |
| BetaFPV G473 AIO | `BETAFPVG473` | STM32G47x | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_BETAFPVG473.hex) |
| BetaFPV F435 AIO | `BETAFPVF435` | AT32F435G | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_BETAFPVF435.hex) |
| iFlight BLITZ F435 | `IFLIGHT_BLITZ_F435` | AT32F435G | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_IFLIGHT_BLITZ_F435.hex) |
| iFlight F411 AIO (32-bit ESC) | `IFLIGHT_F411_AIO32` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_IFLIGHT_F411_AIO32.hex) |
| iFlight F745 AIO V2 | `IFLIGHT_F745_AIO_V2` | STM32F745 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_IFLIGHT_F745_AIO_V2.hex) |
| iFlight H743 AIO V2 | `IFLIGHT_H743_AIO_V2` | STM32H743 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_IFLIGHT_H743_AIO_V2.hex) |
| GEPRC F722 AIO | `GEPRC_F722_AIO` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_GEPRC_F722_AIO.hex) |
| GEPRC TAKER G4 AIO | `TAKERG4AIO` | STM32G47x | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_TAKERG4AIO.hex) |
| GEPRC F411 AIO | `GEPRCF411_AIO` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_GEPRCF411_AIO.hex) |
| HGLRC F722 AIO | `HGLRCF722AIO` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_HGLRCF722AIO.hex) |
| HGLRC Zeus F722 AIO | `ZEUSF722_AIO` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_ZEUSF722_AIO.hex) |
| HGLRC F411 SX1280 AIO (ELRS) | `HGLRCF411SX1280` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_HGLRCF411SX1280.hex) |
| NewBeeDrone Infinity AIO V2 Pro | `NBD_INFINITYAIOV2PRO` | STM32F745 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_NBD_INFINITYAIOV2PRO.hex) |
| NeutronRC G4 AIO | `NEUTRONRCG4AIO` | STM32G47x | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_NEUTRONRCG4AIO.hex) |
| LUX Micro AIO | `LUXMICROAIO` | STM32G47x | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_LUXMICROAIO.hex) |
| Airbot G4 AIO | `AIRBOTG4AIO` | STM32G47x | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_AIRBOTG4AIO.hex) |
| Holybro Kakute G4 AIO | `KAKUTEG4AIO` | STM32G47x | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_KAKUTEG4AIO.hex) |
| Foxeer F745 AIO V4 | `FOXEERF745V4_AIO` | STM32F745 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_FOXEERF745V4_AIO.hex) |
| SpeedyBee F745 AIO | `SPEEDYBEE_F745_AIO` | STM32F745 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_SPEEDYBEE_F745_AIO.hex) |
| Flywoo GOKU GN745 AIO | `FLYWOOF745AIO` | STM32F745 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_FLYWOOF745AIO.hex) |
| Axisflying Argus F7 AIO | `ARGUSF7AIO` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_ARGUSF7AIO.hex) |
| Skystars F405 AIO | `SKYSTARSF405AIO` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_SKYSTARSF405AIO.hex) |
| JHEMCU F435 | `JHEF435` | AT32F435G | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_JHEF435.hex) |
| CCRC F435 AIO | `CCRCF435AIO` | AT32F435G | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_CCRCF435AIO.hex) |
| BAYCK Dolphin Mini | `BAYCK_DOLPHIN_MINI` | AT32F435G | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_BAYCK_DOLPHIN_MINI.hex) |
| EMAX F405 ELRS AIO | `EMAX_F405_ELRS_AIO` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_EMAX_F405_ELRS_AIO.hex) |
| EMAX Tinyhawk F4 SX1280 AIO (ELRS) | `EMAX_TINYHAWKF4SX1280` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_EMAX_TINYHAWKF4SX1280.hex) |
| BetaFPV F411 RX AIO | `BETAFPVF411RX` | STM32F411 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_BETAFPVF411RX.hex) |
| **5-inch / stack** | | | |
| TBS Lucid FC | `TBS_LUCID_FC` | AT32F435M | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_TBS_LUCID_FC.hex) |
| TBS Lucid H7 | `TBS_LUCID_H7` | STM32H743 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_TBS_LUCID_H7.hex) |
| Hobbywing XRotor F7 Conv (ZoeFPV's 5-inch 3D quad) | `HOBBYWING_XROTORF7CONV` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_HOBBYWING_XROTORF7CONV.hex) · [2026.6.2 base, v0.1 only](https://github.com/BlindingBright/betaflight/releases/download/v0.1.0-3d-test-2026.6/BetaFlight3DEdition_v0.1.0-test-2026.6_HOBBYWING_XROTORF7CONV.hex) |
| SpeedyBee F405 V3 | `SPEEDYBEEF405V3` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_SPEEDYBEEF405V3.hex) |
| SpeedyBee F405 V4 | `SPEEDYBEEF405V4` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_SPEEDYBEEF405V4.hex) |
| SpeedyBee F405 Mini | `SPEEDYBEEF405MINI` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_SPEEDYBEEF405MINI.hex) |
| SpeedyBee F405 AIO | `SPEEDYBEEF405AIO` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_SPEEDYBEEF405AIO.hex) |
| SpeedyBee F7 V3 | `SPEEDYBEEF7V3` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_SPEEDYBEEF7V3.hex) |
| Diatone Mamba F405 (2022B) | `MAMBAF405_2022B` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_MAMBAF405_2022B.hex) |
| Diatone Mamba F722 (2022B) | `MAMBAF722_2022B` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_MAMBAF722_2022B.hex) |
| Matek F405-SE | `MATEKF405SE` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_MATEKF405SE.hex) |
| Matek F405-TE | `MATEKF405TE` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_MATEKF405TE.hex) |
| Matek F722-SE | `MATEKF722SE` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_MATEKF722SE.hex) |
| Matek H743 | `MATEKH743` | STM32H743 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_MATEKH743.hex) |
| Holybro Kakute F7 V2 | `KAKUTEF7V2` | STM32F745 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_KAKUTEF7V2.hex) |
| Holybro Kakute H7 | `KAKUTEH7` | STM32H743 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_KAKUTEH7.hex) |
| Holybro Kakute H7 V2 | `KAKUTEH7V2` | STM32H743 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_KAKUTEH7V2.hex) |
| Foxeer F722 V4 | `FOXEERF722V4` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_FOXEERF722V4.hex) |
| Foxeer H743 | `FOXEERH743` | STM32H743 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_FOXEERH743.hex) |
| iFlight BLITZ F722 | `IFLIGHT_BLITZ_F722` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_IFLIGHT_BLITZ_F722.hex) |
| iFlight BLITZ F7 AIO | `IFLIGHT_BLITZ_F7_AIO` | STM32F745 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_IFLIGHT_BLITZ_F7_AIO.hex) |
| JHE F7 Dual | `JHEF7DUAL` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_JHEF7DUAL.hex) |
| JHE F405 Pro | `JHEF405PRO` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_JHEF405PRO.hex) |
| GEPRC F405 | `GEPRCF405` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_GEPRCF405.hex) |
| GEPRC F722 | `GEPRCF722` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_GEPRCF722.hex) |
| T-Motor F7 V2 | `TMOTORF7V2` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_TMOTORF7V2.hex) |
| Flywoo F405S AIO | `FLYWOOF405S_AIO` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_FLYWOOF405S_AIO.hex) |
| BetaFPV F405 | `BETAFPVF405` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_BETAFPVF405.hex) |
| BetaFPV F722 | `BETAFPVF722` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_BETAFPVF722.hex) |
| Flywoo GOKU F722 Pro V2 (incl. Pro Mini V2 20x20 stack, ICM42688 gyro) | `FLYWOOF722PROV2` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_FLYWOOF722PROV2.hex) |
| Flywoo GOKU F722 Pro (V1, incl. Mini 20x20 stack, MPU6000 gyro) | `FLYWOOF722PRO` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_FLYWOOF722PRO.hex) |
| Sequre H7 V2 | `SEQUREH7V2` | STM32H743 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_SEQUREH7V2.hex) |
| Diatone Mamba F722 | `MAMBAF722` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_MAMBAF722.hex) |
| Diatone Mamba F405 (US) | `MAMBAF405US` | STM32F405 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_MAMBAF405US.hex) |
| SpeedyBee F7 Mini V2 | `SPEEDYBEEF7MINIV2` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_SPEEDYBEEF7MINIV2.hex) |
| Holybro Kakute H7 Mini | `KAKUTEH7MINI` | STM32H743 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_KAKUTEH7MINI.hex) |
| Holybro Kakute F7 Mini V3 | `KAKUTEF7MINIV3` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_KAKUTEF7MINIV3.hex) |
| GEPRC TAKER F722 SE | `TAKERF722SE` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_TAKERF722SE.hex) |
| Foxeer F722 V3 | `FOXEERF722V3` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_FOXEERF722V3.hex) |
| Matek F722 | `MATEKF722` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_MATEKF722.hex) |
| T-Motor Velox F7 V2 | `TMOTORVELOXF7V2` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_TMOTORVELOXF7V2.hex) |
| T-Motor F7 (BMI270; tested stack ships with AM32 ESC `TMOTOR_G071`) | `TMOTORF7` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_TMOTORF7.hex) |
| Axisflying F7 Pro | `AXISFLYINGF7PRO` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_AXISFLYINGF7PRO.hex) |
| iFlight BLITZ F7 Pro | `IFLIGHT_BLITZ_F7_PRO` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_IFLIGHT_BLITZ_F7_PRO.hex) |
| Skystars F7 HD Pro | `SKYSTARSF7HDPRO` | STM32F722 | [⬇ hex](https://github.com/BlindingBright/betaflight/releases/download/v0.3.1-3d-test/BetaFlight3DEdition_v0.3.1-test_SKYSTARSF7HDPRO.hex) |

## How to test
The [testing guide](TESTING_GUIDE.md) works for every board in this list: back up, flash, paste Block A, fly 2 packs,
paste Block B, fly 2 packs, upload. The only board-specific choice is in step 8: use `3d_iterm_release = RPM` and `3d_dyn_idle` only if your
ESCs give RPM telemetry (`dshot_bidir = ON`: AM32, Bluejay, BLHeli_32). Stock BLHeli_S has none (v0.3.1 then falls back to the
250 ms timer by itself).

Notes on requested boards:
- **Fractal Engineering SP8 (`FRACSP8AIO`)**: 1S AIO with AM32 8A ESCs and built-in ELRS. There is no official Betaflight
  target for it; this build uses Fractal's own target definition (FractalEngineer/config, branch `SP8-AIO`). Not flown on the
  3D Edition yet: bench-check props off first. AM32 settings: [am32.ca/configurator](https://am32.ca/configurator), ESC target `SP8AIO`.
- **Boards added in bulk (v0.3.1)**: common AIOs (many with 32-bit ESCs that run AM32) and popular 5-inch FCs. Built from the
  official Betaflight 4.5 targets but not flown with the 3D Edition yet. Make sure the target matches what `version` shows on
  your board today.
- **DarwinFPV TinyApe (`DARWINF4SX1280HD`)**: built-in SPI ExpressLRS is enabled on the 4.5.1 target. Coming from
  Betaflight 4.4.2, re-bind after flashing, check the binding phrase, and check that your transmitter's ELRS version matches. The board has **no blackbox flash**, so it can't record
  logs; DVR plus a written report still helps (see the guide's "No blackbox" note).
- **Flywoo GOKU F722 Mini stacks**: two versions with different gyros. Check the board name your current Betaflight shows
  (CLI `version`): `FLYWOOF722PROV2` (ICM42688, current Pro Mini V2) or `FLYWOOF722PRO` (MPU6000, V1). Flash the matching file.
- **DarwinFPV F435 AIO (`DARWINF435`)**: AT32F435, 16 MB blackbox flash.
- **JHEMCU H743 AIO (`JHEH743_AIO`)**: only 2 MB blackbox flash; on a 5-inch use `set blackbox_sample_rate = 1/16`, erase before
  every pack, and expect a short log (fly the flips early in the pack).
- **Flywoo GOKU F722 Pro V2 / Sequre H7 V2**: 16 MB flash; on a 5-inch at 8 kHz, `set blackbox_sample_rate = 1/4` or `1/8`
  helps a full pack fit.
