;**** **** **** **** **** **** **** **** **** **** **** **** ****
;
; Bluejay digital ESC firmware for controlling brushless motors in multirotors
;
; Copyleft  2022-2023 Daniel Mosquera
; Copyright 2020-2022 Mathias Rasmussen
; Copyright 2011-2017 Steffen Skaug
;
; This file is part of Bluejay.
;
; Bluejay is free software: you can redistribute it and/or modify
; it under the terms of the GNU General Public License as published by
; the Free Software Foundation, either version 3 of the License, or
; (at your option) any later version.
;
; Bluejay is distributed in the hope that it will be useful,
; but WITHOUT ANY WARRANTY; without even the implied warranty of
; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
; GNU General Public License for more details.
;
; You should have received a copy of the GNU General Public License
; along with Bluejay.  If not, see <http://www.gnu.org/licenses/>.
;
;**** **** **** **** **** **** **** **** **** **** **** **** ****
;
; Programming defaults
;
;**** **** **** **** **** **** **** **** **** **** **** **** ****

DEFAULT_PGM_RPM_POWER_SLOPE EQU 9       ; 0=Off,1..13 (Power limit factor in relation to rpm)
DEFAULT_PGM_COMM_TIMING EQU 4           ; 1=Low 2=MediumLow 3=Medium 4=MediumHigh 5=High
DEFAULT_PGM_DEMAG_COMP EQU 3            ; 1=Disabled 2=Low 3=High (High default for 3D reversals)
DEFAULT_PGM_DIRECTION EQU 3             ; 1=Normal 2=Reversed 3=Bidir 4=Bidir rev (3D Bidir default)
DEFAULT_PGM_BEEP_STRENGTH EQU 40        ; 0..255 (BLHeli_S is 1..255)
DEFAULT_PGM_BEACON_STRENGTH EQU 80      ; 0..255
DEFAULT_PGM_BEACON_DELAY EQU 4          ; 1=1m 2=2m 3=5m 4=10m 5=Infinite
DEFAULT_PGM_ENABLE_TEMP_PROT EQU 0      ; 0=Disabled 1=80C 2=90C 3=100C 4=110C 5=120C 6=130C 7=140C

DEFAULT_PGM_POWER_RATING EQU 2          ; 1=1S,2=2S+

DEFAULT_PGM_BRAKE_ON_STOP EQU 0         ; 1=Enabled 0=Disabled
DEFAULT_PGM_LED_CONTROL EQU 0           ; Byte for LED control. 2 bits per LED,0=Off,1=On

DEFAULT_PGM_STARTUP_POWER_MIN EQU 29    ; 0..255 => 1014 BLHeli min startup power for crisp 3D zero-crossings
DEFAULT_PGM_STARTUP_BEEP EQU 1          ; 0=Short beep,1=Melody

DEFAULT_PGM_STARTUP_POWER_MAX EQU 25    ; 0..255 => 1100 BLHeli max startup power for 3D authority
DEFAULT_PGM_BRAKING_STRENGTH EQU 255    ; 0..255 => 0..100 % Braking

DEFAULT_PGM_SAFETY_ARM EQU 0            ; EDT safety arm is disabled by default

; Bluejay3D (AM32 / ESCape32 Backported 3D Mode Parameters)
DEFAULT_PGM_3D_BRAKE_STRENGTH EQU 8     ; 1..10 => Max 3D direction-change braking power (8 = ~37.6%)
DEFAULT_PGM_3D_BRAKE_SPEED EQU 5        ; 1..10 => Zero-cross switchover speed threshold (5 = ~5000 eRPM)
DEFAULT_PGM_3D_MIN_DUTY EQU 3           ; 0..15 => Minimum 3D active duty floor (3 = ~2.35% floor)
DEFAULT_PGM_3D_REV_BOOST EQU 1          ; 0=Off, 1=On => Apply startup boost on 3D direction reversals
DEFAULT_PGM_3D_FAST_RESTART EQU 1       ; 0=Off, 1=On => 1ms fast desync recovery & 12-step initial run
DEFAULT_PGM_3D_FAST_TRACK EQU 1         ; 0=Off, 1=On => Fast 4-sample comm filter & full post-rev torque
DEFAULT_PGM_3D_GLITCH_FILTER EQU 1      ; 0..3 => High-RPM reversal confirmation frames (1 = 2 frames >20k eRPM)
