3D whoop: TBS Lucid AIO (AT32F435 FC + AM32), 0802 16000kv (12-pole), Gemfan 31mm prototype 3D props,
2S 300mAh, DJI O4 Lite, ~30 g. Betaflight 4.5.1, 8k/8k, feature 3D, DShot600 bidirectional, 2 kHz blackbox.

AM32 settings common to all 2.21 logs: bidirectional ON, complementary PWM ON, variable PWM ON,
stuck rotor protection ON, sine startup OFF, stall protection OFF, brake on stop OFF, auto-timing OFF,
poles 12, running brake 10, stopped brake 10, sine range 15, sine power 6.
Only the values in each filename change.

Betaflight: tune evolved during 01-03. 04-07 all use the SAME Betaflight config
(dshot_idle_value 400 = 4%, thrust_linear 20), so 04-07 are a clean ESC-only comparison.

File  | Use                         | Notes
------+-----------------------------+--------------------------------------------------------------
01    | factory firmware reference  | AM32 still set to 14 poles, BF idle 2.8%. Cleanest reversals in eRPM.
02    | timing 22.5 (reset by 2.21) | 5 logs. Log 4: motor 1 (BF m0) stops at 0 rpm right after a
      |                             | reversal at ~37.1 s and never restarts, while commanded 2047 for 0.75 s, then crash.
      |                             | Log 1 end = prop came off (not ESC). Log 5 is the good flight.
03    | startup power 120           | Tree hit at 55.8 s; analyze 0-55.5 s.
04    | DEFAULT (A1)                | Log 4 is the flight (106 s, clean).
05    | DEFAULT (A2)                | 2 packs. Log 1 impact at 70.0 s; log 2 truncated (flash full).
06    | TEST B: min duty 3          | Log 3 is the flight; impact at 79 s.
07    | TEST C: min duty 3, KV 5100 | Crash at 88.6 s; analyze 0-88.4 s.
08    | TEST D: min duty 4, KV 2100 | Clean 86 s flight, no impacts. 126 ms median.
09    | TEST E: min duty 3, KV 2100 | Clean 94 s flight, no impacts. 126 ms median, most consistent. FINAL SETTING.

Plots: esc_test_ABCDE.png (A, C, D, E), esc_test_ABCD.png (A vs B vs C vs D), esc_test_ABC.png, esc_compare_history.png (all firmware/settings).
Switch time = from BF direction switch until eRPM >= 100k in the new direction (per motor, median).
