;**** **** **** **** ****
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
; Settings
;
;**** **** **** **** **** **** **** **** **** **** **** **** ****

; Sets default programming parameters
set_default_parameters:
    mov  Temp1, #_Pgm_Gov_P_Gain
    mov  @Temp1, #0FFh                  ; _Pgm_Gov_P_Gain
    imov Temp1, #DEFAULT_PGM_STARTUP_POWER_MIN ; Pgm_Startup_Power_Min
    imov Temp1, #DEFAULT_PGM_STARTUP_BEEP ; Pgm_Startup_Beep
    imov Temp1, #0FFh                   ; _Pgm_Dithering
    imov Temp1, #DEFAULT_PGM_STARTUP_POWER_MAX ; Pgm_Startup_Power_Max
    imov Temp1, #0FFh                   ; _Pgm_Rampup_Slope
    imov Temp1, #DEFAULT_PGM_RPM_POWER_SLOPE ; Pgm_Rpm_Power_Slope
    imov Temp1, #(24 SHL PWM_FREQ)      ; Pgm_Pwm_Freq
    imov Temp1, #DEFAULT_PGM_DIRECTION  ; Pgm_Direction
    imov Temp1, #0FFh                   ; _Pgm_Input_Pol

    inc  Temp1                          ; Skip Initialized_L_Dummy
    inc  Temp1                          ; Skip Initialized_H_Dummy

    imov Temp1, #0FFh                   ; _Pgm_Enable_TX_Program
    imov Temp1, #DEFAULT_PGM_BRAKING_STRENGTH ; Pgm_Braking_Strength
    imov Temp1, #DEFAULT_PGM_3D_BRAKE_STRENGTH ; Pgm_3D_Brake_Strength
    imov Temp1, #DEFAULT_PGM_3D_BRAKE_SPEED ; Pgm_3D_Brake_Speed
    imov Temp1, #DEFAULT_PGM_3D_MIN_DUTY ; Pgm_3D_Min_Duty
    imov Temp1, #DEFAULT_PGM_3D_REV_BOOST ; Pgm_3D_Rev_Boost
    imov Temp1, #DEFAULT_PGM_COMM_TIMING ; Pgm_Comm_Timing
    imov Temp1, #DEFAULT_PGM_3D_FAST_RESTART ; Pgm_3D_Fast_Restart
    imov Temp1, #DEFAULT_PGM_3D_FAST_TRACK ; Pgm_3D_Fast_Track
    imov Temp1, #DEFAULT_PGM_3D_GLITCH_FILTER ; Pgm_3D_Glitch_Filter
    imov Temp1, #0FFh                   ; _Pgm_Min_Throttle
    imov Temp1, #0FFh                   ; _Pgm_Max_Throttle
    imov Temp1, #DEFAULT_PGM_BEEP_STRENGTH ; Pgm_Beep_Strength
    imov Temp1, #DEFAULT_PGM_BEACON_STRENGTH ; Pgm_Beacon_Strength
    imov Temp1, #DEFAULT_PGM_BEACON_DELAY ; Pgm_Beacon_Delay
    imov Temp1, #0FFh                   ; _Pgm_Throttle_Rate
    imov Temp1, #DEFAULT_PGM_DEMAG_COMP ; Pgm_Demag_Comp
    imov Temp1, #0FFh                   ; _Pgm_BEC_Voltage_High
    imov Temp1, #0FFh                   ; _Pgm_Center_Throttle
    imov Temp1, #0FFh                   ; _Pgm_Main_Spoolup_Time
    imov Temp1, #DEFAULT_PGM_ENABLE_TEMP_PROT ; Pgm_Enable_Temp_Prot
    imov Temp1, #0FFh                   ; _Pgm_Enable_Power_Prot
    imov Temp1, #0FFh                   ; _Pgm_Enable_Pwm_Input
    imov Temp1, #0FFh                   ; _Pgm_Pwm_Dither
    imov Temp1, #DEFAULT_PGM_BRAKE_ON_STOP ; Pgm_Brake_On_Stop
    imov Temp1, #DEFAULT_PGM_LED_CONTROL ; Pgm_LED_Control
    imov Temp1, #DEFAULT_PGM_POWER_RATING ; Pgm_Power_Rating
    imov Temp1, #DEFAULT_PGM_SAFETY_ARM ; Pgm_Safety_Arm

    ret

;**** **** **** **** **** **** **** **** **** **** **** **** ****
;
; Decode settings
;
; Decodes programmed settings and set RAM variables accordingly
;
;**** **** **** **** **** **** **** **** **** **** **** **** ****
decode_settings:
    mov  Temp1, #Pgm_Direction          ; Load programmed direction
    mov  A, @Temp1
    dec  A
    mov  C, ACC.1                       ; Set bidirectional mode
    mov  Flag_Pgm_Bidir, C
    mov  C, ACC.0                       ; Set direction (Normal / Reversed)
    mov  Flag_Pgm_Dir_Rev, C

    ; Check startup power
    mov  Temp1, #Pgm_Startup_Power_Max
    mov  A, #80                         ; Limit to at most 80
    subb A, @Temp1
    jnc  decode_settings_check_low_rpm
    mov  @Temp1, #80

decode_settings_check_low_rpm:
    ; Check low rpm power slope
    mov  Temp1, #Pgm_Rpm_Power_Slope
    mov  A, #13                         ; Limit to at most 13
    subb A, @Temp1
    jnc  decode_settings_set_low_rpm
    mov  @Temp1, #13

decode_settings_set_low_rpm:
    mov  Low_Rpm_Pwr_Slope, @Temp1

    ; Decode demag compensation
    mov  Temp1, #Pgm_Demag_Comp
    mov  A, @Temp1
    mov  Demag_Pwr_Off_Thresh, #255     ; Set default

    cjne A, #2, decode_demag_high

    mov  Demag_Pwr_Off_Thresh, #160     ; Settings for demag comp low

decode_demag_high:
    cjne A, #3, decode_demag_done

    mov  Demag_Pwr_Off_Thresh, #130     ; Settings for demag comp high

decode_demag_done:
    ; Decode temperature protection limit
    mov  Temp_Prot_Limit, #0
    mov  Temp1, #Pgm_Enable_Temp_Prot
    mov  A, @Temp1
    mov  Temp2, A                       ; Temp2 = *Pgm_Enable_Temp_Prot;
    jz   decode_temp_done

;**** **** **** **** **** **** **** **** **** **** **** **** ****
;
; Power rating only applies to BB21 because voltage references behave diferently
; depending on if an external voltage regulator is used or not.
;
; NOTE: For BB51, the 1s power rating code path is mandatory
;
;**** **** **** **** **** **** **** **** **** **** **** **** ****
IF MCU_TYPE == MCU_BB2
    ; Read power rating and decode temperature limit
    mov  Temp1, #Pgm_Power_Rating
    cjne @Temp1, #01h, decode_temp_use_adc_use_vdd_3V3_vref
ENDIF

; Set A to temperature limit depending on power rating
decode_temp_use_adc_use_internal_1V65_vref:
    mov  A, #(TEMP_LIMIT_1S - TEMP_LIMIT_STEP)
    sjmp decode_temp_step
decode_temp_use_adc_use_vdd_3V3_vref:
    mov  A, #(TEMP_LIMIT_2S - TEMP_LIMIT_STEP)

; Increase A while Temp2-- != 0;
decode_temp_step:
    add  A, #TEMP_LIMIT_STEP
    djnz Temp2, decode_temp_step

; Set Temp_Prot_Limit to the temperature limit calculated in A
decode_temp_done:
    mov  Temp_Prot_Limit, A

    mov  Temp1, #Pgm_Beep_Strength      ; Read programmed beep strength setting
    mov  Beep_Strength, @Temp1          ; Set beep strength

    mov  Temp1, #Pgm_Braking_Strength   ; Read programmed braking strength setting
    mov  A, @Temp1
IF PWM_BITS_H == PWM_11_BIT             ; Scale braking strength to pwm resolution
    ; Note: Added for completeness
    ; Currently 11-bit pwm is only used on targets with built-in dead time insertion
    rl   A
    rl   A
    rl   A
    mov  Temp2, A
    anl  A, #07h
    mov  Pwm_Braking_H, A
    mov  A, Temp2
    anl  A, #0F8h
    mov  Pwm_Braking_L, A
ELSEIF PWM_BITS_H == PWM_10_BIT
    rl   A
    rl   A
    mov  Temp2, A
    anl  A, #03h
    mov  Pwm_Braking_H, A
    mov  A, Temp2
    anl  A, #0FCh
    mov  Pwm_Braking_L, A
ELSEIF PWM_BITS_H == PWM_9_BIT
    rl   A
    mov  Temp2, A
    anl  A, #01h
    mov  Pwm_Braking_H, A
    mov  A, Temp2
    anl  A, #0FEh
    mov  Pwm_Braking_L, A
ELSEIF PWM_BITS_H == PWM_8_BIT
    mov  Pwm_Braking_H, #0
    mov  Pwm_Braking_L, A
ENDIF
    cjne @Temp1, #0FFh, decode_3d_settings
    mov  Pwm_Braking_L, #0FFh           ; Apply full braking if setting is max

decode_3d_settings:
    ; 1. Decode Pgm_3D_Brake_Strength (1..10, default 8)
    ; Pwm_3D_Brake_Limit = val * 12 (12..120 on 0..255 scale)
    ; Pwm_3D_Brake_Floor = val * 3  (3..30 on 0..255 scale)
    mov  Temp1, #Pgm_3D_Brake_Strength
    mov  A, @Temp1
    jz   decode_3d_brake_str_default
    clr  C
    subb A, #11
    jc   decode_3d_brake_str_ok
decode_3d_brake_str_default:
    mov  @Temp1, #DEFAULT_PGM_3D_BRAKE_STRENGTH
decode_3d_brake_str_ok:
    mov  A, @Temp1
    mov  B, #3
    mul  AB
    mov  Pwm_3D_Brake_Floor, A          ; Floor = strength * 3
    rl   A
    rl   A
    mov  Pwm_3D_Brake_Limit, A          ; Limit = strength * 12

    ; 2. Decode Pgm_3D_Brake_Speed (1..10, default 5)
    ; Pwm_3D_Brake_Speed = 104 - (val * 8) => 96 (60h, ~3.3k eRPM) down to 24 (18h, ~13.3k eRPM)
    mov  Temp1, #Pgm_3D_Brake_Speed
    mov  A, @Temp1
    jz   decode_3d_brake_spd_default
    clr  C
    subb A, #11
    jc   decode_3d_brake_spd_ok
decode_3d_brake_spd_default:
    mov  @Temp1, #DEFAULT_PGM_3D_BRAKE_SPEED
decode_3d_brake_spd_ok:
    mov  A, @Temp1
    mov  B, #8
    mul  AB
    mov  Temp2, A
    clr  C
    mov  A, #104
    subb A, Temp2
    mov  Pwm_3D_Brake_Speed, A

    ; 3. Decode Pgm_3D_Min_Duty (0..15, default 3)
    ; Pwm_3D_Min_Duty = val * 2 (0..30 on 0..255 scale)
    mov  Temp1, #Pgm_3D_Min_Duty
    mov  A, @Temp1
    clr  C
    subb A, #16
    jc   decode_3d_min_duty_ok
    mov  @Temp1, #DEFAULT_PGM_3D_MIN_DUTY
decode_3d_min_duty_ok:
    mov  A, @Temp1
    clr  C
    rlc  A
    mov  Pwm_3D_Min_Duty, A

    ; 4. Decode Pgm_3D_Rev_Boost (0..1, default 1)
    mov  Temp1, #Pgm_3D_Rev_Boost
    mov  A, @Temp1
    clr  C
    subb A, #2
    jc   decode_3d_rev_boost_ok
    mov  @Temp1, #DEFAULT_PGM_3D_REV_BOOST
decode_3d_rev_boost_ok:
    mov  A, @Temp1
    mov  C, ACC.0
    mov  Flag_3D_Rev_Boost_En, C

    ; 5. Decode Pgm_3D_Fast_Restart (0..1, default 1)
    mov  Temp1, #Pgm_3D_Fast_Restart
    mov  A, @Temp1
    clr  C
    subb A, #2
    jc   decode_3d_fast_restart_ok
    mov  @Temp1, #DEFAULT_PGM_3D_FAST_RESTART
decode_3d_fast_restart_ok:
    mov  A, @Temp1
    mov  C, ACC.0
    mov  Flag_3D_Fast_Restart, C

    ; 6. Decode Pgm_3D_Fast_Track (0..1, default 1)
    mov  Temp1, #Pgm_3D_Fast_Track
    mov  A, @Temp1
    clr  C
    subb A, #2
    jc   decode_3d_fast_track_ok
    mov  @Temp1, #DEFAULT_PGM_3D_FAST_TRACK
decode_3d_fast_track_ok:
    mov  A, @Temp1
    mov  C, ACC.0
    mov  Flag_3D_Fast_Track, C

    ; 7. Decode Pgm_3D_Glitch_Filter (0..3, default 1)
    ; Bidir_Glitch_Thresh = val + 1 (1..4 frames at >20k eRPM)
    mov  Temp1, #Pgm_3D_Glitch_Filter
    mov  A, @Temp1
    clr  C
    subb A, #4
    jc   decode_3d_glitch_ok
    mov  @Temp1, #DEFAULT_PGM_3D_GLITCH_FILTER
decode_3d_glitch_ok:
    mov  A, @Temp1
    inc  A
    mov  Bidir_Glitch_Thresh, A

decode_end:
    ; Return
    ret
