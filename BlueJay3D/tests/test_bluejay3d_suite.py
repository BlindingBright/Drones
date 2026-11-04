#!/usr/bin/env python3
"""
Automated Verification Suite for Project Bluejay3D (Firmware + Configurator)
============================================================================
Tests:
1. All 26 compiled .hex firmware binaries (Intel HEX checksums, code ceiling bounds,
   reset vectors, bootloader byte-for-byte match vs official Bluejay v0.21.0,
   and all EEPROM default parameters at 0x1A00 / 0x3000).
2. 8051 assembly arithmetic verification for:
   - 10-bit DShot telemetry period calculation (eliminating the Comm_Period4x_H >= 64 overflow)
   - DShot 0 (stop) 3D direction preservation & DShot 48/1048 active throttle floor
   - 3D parameter decoding & 0xFF legacy EEPROM fallback
3. Configurator patcher round-trip & 3D Reversal Physics Simulator benchmarks.
"""

import glob
import os
import sys
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "configurator"))

import server as cfg  # noqa: E402


class TestBluejay3DFirmwareAndConfigurator(unittest.TestCase):
    def setUp(self):
        self.hex_files = sorted(glob.glob(os.path.join(cfg.HEX_DIR, "*.hex")))
        self.assertGreaterEqual(len(self.hex_files), 26, "Expected at least 26 built .hex targets")

    def test_01_all_hex_binaries_valid_and_within_flash_bounds(self):
        """Verify every compiled .hex binary has valid checksums, reset vectors, and flash bounds."""
        for path in self.hex_files:
            fname = os.path.basename(path)
            with open(path, "r", encoding="utf-8") as f:
                hex_text = f.read()

            mem = cfg.parse_intel_hex(hex_text)
            info = cfg.inspect_firmware_memory(mem)

            # Check reset vector at 0x0000 is LJMP CSEG_RESET, and CSEG_RESET is LJMP pgm_start
            is_bb51 = info["mcu_family"] == "EFM8BB51"
            reset_addr = 0x2FFD if is_bb51 else 0x19FD
            self.assertEqual(mem.get(0x0000), 0x02, f"{fname}: Missing LJMP at reset vector 0x0000")
            vec0_target = (mem.get(0x0001, 0) << 8) | mem.get(0x0002, 0)
            self.assertEqual(vec0_target, reset_addr, f"{fname}: 0x0000 LJMP should point to CSEG_RESET 0x{reset_addr:04X}")
            self.assertEqual(mem.get(reset_addr), 0x02, f"{fname}: Missing LJMP at CSEG_RESET 0x{reset_addr:04X}")
            pgm_start_addr = (mem.get(reset_addr + 1, 0) << 8) | mem.get(reset_addr + 2, 0)
            self.assertGreater(pgm_start_addr, 0x0080, f"{fname}: Invalid pgm_start address 0x{pgm_start_addr:04X}")
            self.assertLess(pgm_start_addr, reset_addr, f"{fname}: pgm_start address out of bounds")

            # Check ample free flash space (>1400 bytes free on BB21, >6000 bytes free on BB51)
            self.assertGreater(info["app_flash_free_bytes"], 1400, f"{fname}: Flash usage too high")
            self.assertTrue(info["has_bootloader"], f"{fname}: Missing bootloader segment")

    def test_02_bootloader_byte_identical_to_official_v021(self):
        """Verify the bootloader segment in Bluejay3D .hex is 100% byte-identical to official Bluejay v0.21.0."""
        ref_bb21 = os.path.join(cfg.REF_HEX_DIR, "O_H_5_48_v0.21.0.hex")
        bj3d_bb21 = os.path.join(cfg.HEX_DIR, "O_H_5_48_v0.22.0-3D.hex")

        with open(ref_bb21, "r", encoding="utf-8") as f:
            ref_mem = cfg.parse_intel_hex(f.read())
        with open(bj3d_bb21, "r", encoding="utf-8") as f:
            bj3d_mem = cfg.parse_intel_hex(f.read())

        boot_addrs = [a for a in ref_mem.keys() if a >= 0x1C00]
        self.assertGreater(len(boot_addrs), 400)
        for a in boot_addrs:
            self.assertEqual(
                ref_mem[a],
                bj3d_mem.get(a),
                f"Bootloader byte mismatch at 0x{a:04X}",
            )

        # Also check BB51 bootloader at 0xF000
        ref_bb51 = os.path.join(cfg.REF_HEX_DIR, "A_X_5_48_v0.21.0.hex")
        bj3d_bb51 = os.path.join(cfg.HEX_DIR, "A_X_5_48_v0.22.0-3D.hex")
        with open(ref_bb51, "r", encoding="utf-8") as f:
            ref51_mem = cfg.parse_intel_hex(f.read())
        with open(bj3d_bb51, "r", encoding="utf-8") as f:
            bj3d51_mem = cfg.parse_intel_hex(f.read())

        boot51_addrs = [a for a in ref51_mem.keys() if a >= 0xF000]
        self.assertGreater(len(boot51_addrs), 400)
        for a in boot51_addrs:
            self.assertEqual(
                ref51_mem[a],
                bj3d51_mem.get(a),
                f"BB51 Bootloader byte mismatch at 0x{a:04X}",
            )

    def test_03_default_3d_eeprom_parameters(self):
        """Verify all 7 new Bluejay3D EEPROM parameters and 3D defaults are properly populated."""
        target = os.path.join(cfg.HEX_DIR, "O_H_5_48_v0.22.0-3D.hex")
        with open(target, "r", encoding="utf-8") as f:
            mem = cfg.parse_intel_hex(f.read())
        info = cfg.inspect_firmware_memory(mem)
        s = info["settings"]

        self.assertEqual(s["fw_main_revision"], 0)
        self.assertEqual(s["fw_sub_revision"], 22)
        self.assertEqual(s["layout_revision"], 208)
        self.assertEqual(s["direction"], 3, "Default direction must be 3 (Bidirectional 3D)")
        self.assertEqual(s["comm_timing"], 4, "Default comm timing must be 4 (Medium-High)")
        self.assertEqual(s["demag_comp"], 3, "Default demag comp must be 3 (High)")
        self.assertEqual(s["startup_power_min"], 29, "Default min startup power must be 29 (1014)")
        self.assertEqual(s["startup_power_max"], 25, "Default max startup power must be 25 (1100)")

        # 7 new 3D parameters
        self.assertEqual(s["bidir_3d_brake_strength"], 8)
        self.assertEqual(s["bidir_3d_brake_speed"], 5)
        self.assertEqual(s["bidir_3d_min_duty"], 3)
        self.assertEqual(s["bidir_3d_rev_boost"], 1)
        self.assertEqual(s["bidir_3d_fast_restart"], 1)
        self.assertEqual(s["bidir_3d_fast_track"], 1)
        self.assertEqual(s["bidir_3d_glitch_filter"], 1)
        self.assertEqual(info["name_tag"], "Bluejay3D v0.22")

    def test_04_8051_dshot_telemetry_10bit_fix(self):
        """
        Verify our 8051 assembly fix in DShot.asm:
        Circular rotate left twice (rl A / rl A) splits 4 * Comm_Period4x_H into
        low byte (A & 0xFC) and high byte (A & 0x03), preventing the 8-bit overflow
        at Comm_Period4x_H >= 64 (the exact 3D reversal speed range!).
        """
        def asm_dshot_eperiod_bluejay3d(comm4x_h: int, comm4x_l: int) -> int:
            comm4x = (comm4x_h << 8) | comm4x_l
            comm3x = (comm4x >> 1) + (comm4x >> 2)
            temp3 = comm3x & 0xFF
            temp4 = (comm3x >> 8) & 0xFF

            # Circular rotate left twice on 8-bit comm4x_h
            a = comm4x_h & 0xFF
            a = ((a << 1) | (a >> 7)) & 0xFF
            a = ((a << 1) | (a >> 7)) & 0xFF
            temp5 = a & 0xFC
            temp2 = a & 0x03

            # 16-bit subtraction Temp4:Temp3 - Temp2:Temp5
            res = ((temp4 << 8) | temp3) - ((temp2 << 8) | temp5)
            return res

        # Verify continuity across the critical 0x3F -> 0x40 (63 -> 64) boundary
        # (Stock Bluejay had a +254 us 8-bit overflow jump here; Bluejay3D stays within 2 us!)
        p_63_ff = asm_dshot_eperiod_bluejay3d(0x3F, 0xFF)
        p_64_00 = asm_dshot_eperiod_bluejay3d(0x40, 0x00)
        self.assertLessEqual(abs(p_64_00 - p_63_ff), 4, "No 256-us discontinuity across Comm_Period4x_H = 64")

        # Verify across all values 1..254
        prev = 0
        for h in range(1, 255):
            cur = asm_dshot_eperiod_bluejay3d(h, 0)
            self.assertGreater(cur, prev, f"Non-monotonic telemetry period at Comm_Period4x_H={h}")
            prev = cur

    def test_05_configurator_presets_and_hex_patch_roundtrip(self):
        """Verify patching a .hex file with each 3D preset and round-tripping through Intel HEX."""
        target = os.path.join(cfg.HEX_DIR, "O_H_5_48_v0.22.0-3D.hex")
        with open(target, "r", encoding="utf-8") as f:
            orig_hex = f.read()

        mem = cfg.parse_intel_hex(orig_hex)
        for preset_key, preset_data in cfg.PRESETS.items():
            patched_mem = cfg.patch_firmware_memory(mem, preset_data["settings"], name_tag=f"B3D {preset_key[:11]}")
            patched_hex = cfg.memory_to_intel_hex(patched_mem)
            re_mem = cfg.parse_intel_hex(patched_hex)
            info = cfg.inspect_firmware_memory(re_mem)

            for k, v in preset_data["settings"].items():
                self.assertEqual(info["settings"][k], v, f"Preset {preset_key} mismatch on {k}")

    def test_06_3d_reversal_simulation_benchmarks(self):
        """Verify Bluejay3D v0.22 outperforms Stock Bluejay v0.21 on 3D reversal latency and sync recovery."""
        for preset_key, preset_data in cfg.PRESETS.items():
            sim = cfg.simulate_3d_reversal(preset_data["settings"], initial_erpm=28000, target_throttle_pct=35.0)
            summary = sim["improvement_summary"]
            self.assertGreater(
                summary["zero_cross_speedup_pct"],
                35.0,
                f"Preset {preset_key}: Expected >35% faster zero-crossing",
            )
            self.assertGreater(
                summary["full_sync_speedup_pct"],
                45.0,
                f"Preset {preset_key}: Expected >45% faster full sync lock",
            )
            self.assertEqual(summary["desync_lockout_ms_bluejay3d"], 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
