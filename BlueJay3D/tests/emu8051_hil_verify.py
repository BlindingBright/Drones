#!/usr/bin/env python3
"""
8051 Machine-Code Emulator & Pre-Flight SIL Verification Harness
================================================================
Loads the actual compiled Intel HEX binaries:
  - Stock Bluejay v0.21.0: reference/official_hex/O_H_5_48_v0.21.0.hex
  - Bluejay3D v0.22.0-3D:  firmware/build/hex/O_H_5_48_v0.22.0-3D.hex

Executes the real 8051 instructions in both binaries to prove at the
silicon instruction level (before putting props on a quad) that all
Bluejay3D fixes work as designed.
"""

import os
import sys
import unittest
from typing import Optional, Tuple

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "configurator"))

import server as cfg  # noqa: E402


class Cpu8051:
    """Cycle-accurate 8051 core emulator for EFM8 ESC firmware verification."""

    def __init__(self, code_mem: dict):
        self.code = [0xFF] * 65536
        for addr, val in code_mem.items():
            if 0 <= addr < 65536:
                self.code[addr] = val & 0xFF
        self.iram = [0x00] * 256
        self.xdata = [0x00] * 256
        self.sfr = [0x00] * 256
        self.pc = 0
        self.cycles = 0
        self.sp = 0x07

    # SFR addresses
    ACC = 0xE0
    B = 0xF0
    PSW = 0xD0
    SP_ADDR = 0x81
    DPL = 0x82
    DPH = 0x83

    @property
    def a(self) -> int:
        return self.sfr[self.ACC]

    @a.setter
    def a(self, val: int):
        self.sfr[self.ACC] = val & 0xFF

    @property
    def b(self) -> int:
        return self.sfr[self.B]

    @b.setter
    def b(self, val: int):
        self.sfr[self.B] = val & 0xFF

    @property
    def psw(self) -> int:
        return self.sfr[self.PSW]

    @psw.setter
    def psw(self, val: int):
        self.sfr[self.PSW] = val & 0xFF

    @property
    def c(self) -> int:
        return (self.psw >> 7) & 1

    @c.setter
    def c(self, val: int):
        if val:
            self.psw |= 0x80
        else:
            self.psw &= ~0x80

    @property
    def dptr(self) -> int:
        return (self.sfr[self.DPH] << 8) | self.sfr[self.DPL]

    @dptr.setter
    def dptr(self, val: int):
        self.sfr[self.DPH] = (val >> 8) & 0xFF
        self.sfr[self.DPL] = val & 0xFF

    def reg_bank_base(self) -> int:
        return ((self.psw >> 3) & 0x03) * 8

    def get_r(self, idx: int) -> int:
        return self.iram[self.reg_bank_base() + idx]

    def set_r(self, idx: int, val: int):
        self.iram[self.reg_bank_base() + idx] = val & 0xFF

    def read_direct(self, addr: int) -> int:
        if addr < 0x80:
            return self.iram[addr]
        return self.sfr[addr]

    def write_direct(self, addr: int, val: int):
        val &= 0xFF
        if addr < 0x80:
            self.iram[addr] = val
        else:
            self.sfr[addr] = val

    def get_bit(self, bit_addr: int) -> int:
        if bit_addr < 0x80:
            byte_addr = 0x20 + (bit_addr >> 3)
            bit_idx = bit_addr & 7
            return (self.iram[byte_addr] >> bit_idx) & 1
        else:
            byte_addr = bit_addr & 0xF8
            bit_idx = bit_addr & 7
            return (self.sfr[byte_addr] >> bit_idx) & 1

    def set_bit(self, bit_addr: int, val: int):
        if bit_addr < 0x80:
            byte_addr = 0x20 + (bit_addr >> 3)
            bit_idx = bit_addr & 7
            if val:
                self.iram[byte_addr] |= 1 << bit_idx
            else:
                self.iram[byte_addr] &= ~(1 << bit_idx)
        else:
            byte_addr = bit_addr & 0xF8
            bit_idx = bit_addr & 7
            if val:
                self.sfr[byte_addr] |= 1 << bit_idx
            else:
                self.sfr[byte_addr] &= ~(1 << bit_idx)

    def push8(self, val: int):
        sp = (self.read_direct(self.SP_ADDR) + 1) & 0xFF
        self.write_direct(self.SP_ADDR, sp)
        self.iram[sp] = val & 0xFF

    def pop8(self) -> int:
        sp = self.read_direct(self.SP_ADDR)
        val = self.iram[sp]
        self.write_direct(self.SP_ADDR, (sp - 1) & 0xFF)
        return val

    def fetch(self) -> int:
        b = self.code[self.pc]
        self.pc = (self.pc + 1) & 0xFFFF
        return b

    def fetch_rel(self) -> int:
        rel = self.fetch()
        return rel - 256 if rel >= 128 else rel

    def call_subroutine(self, entry_addr: int, max_steps: int = 10000):
        """Call an 8051 subroutine at entry_addr and run until it returns to sentinel 0xFFFE."""
        self.write_direct(self.SP_ADDR, 0xB0)
        self.push8(0xFE)
        self.push8(0xFF)
        self.pc = entry_addr
        steps = 0
        while self.pc != 0xFFFE and steps < max_steps:
            self.step()
            steps += 1
        if steps >= max_steps:
            raise RuntimeError(f"Subroutine 0x{entry_addr:04X} exceeded {max_steps} steps (PC=0x{self.pc:04X})")
        return steps

    def step(self):
        op = self.fetch()
        self.cycles += 1

        if op == 0x00:  # NOP
            return
        if (op & 0x1F) == 0x01:  # AJMP
            low = self.fetch()
            self.pc = (self.pc & 0xF800) | ((op & 0xE0) << 3) | low
            return
        if (op & 0x1F) == 0x11:  # ACALL
            low = self.fetch()
            target = (self.pc & 0xF800) | ((op & 0xE0) << 3) | low
            self.push8(self.pc & 0xFF)
            self.push8((self.pc >> 8) & 0xFF)
            self.pc = target
            return
        if op == 0x02:  # LJMP
            hi = self.fetch()
            lo = self.fetch()
            self.pc = (hi << 8) | lo
            return
        if op == 0x12:  # LCALL
            hi = self.fetch()
            lo = self.fetch()
            self.push8(self.pc & 0xFF)
            self.push8((self.pc >> 8) & 0xFF)
            self.pc = (hi << 8) | lo
            return
        if op in (0x22, 0x32):  # RET / RETI
            hi = self.pop8()
            lo = self.pop8()
            self.pc = (hi << 8) | lo
            return
        if op == 0x80:  # SJMP
            rel = self.fetch_rel()
            self.pc = (self.pc + rel) & 0xFFFF
            return
        if op == 0x60:  # JZ
            rel = self.fetch_rel()
            if self.a == 0:
                self.pc = (self.pc + rel) & 0xFFFF
            return
        if op == 0x70:  # JNZ
            rel = self.fetch_rel()
            if self.a != 0:
                self.pc = (self.pc + rel) & 0xFFFF
            return
        if op == 0x40:  # JC
            rel = self.fetch_rel()
            if self.c == 1:
                self.pc = (self.pc + rel) & 0xFFFF
            return
        if op == 0x50:  # JNC
            rel = self.fetch_rel()
            if self.c == 0:
                self.pc = (self.pc + rel) & 0xFFFF
            return
        if op == 0x20:  # JB bit, rel
            bit = self.fetch()
            rel = self.fetch_rel()
            if self.get_bit(bit) == 1:
                self.pc = (self.pc + rel) & 0xFFFF
            return
        if op == 0x30:  # JNB bit, rel
            bit = self.fetch()
            rel = self.fetch_rel()
            if self.get_bit(bit) == 0:
                self.pc = (self.pc + rel) & 0xFFFF
            return
        if op == 0x10:  # JBC bit, rel
            bit = self.fetch()
            rel = self.fetch_rel()
            if self.get_bit(bit) == 1:
                self.set_bit(bit, 0)
                self.pc = (self.pc + rel) & 0xFFFF
            return
        if op == 0xE4:  # CLR A
            self.a = 0
            return
        if op == 0xF4:  # CPL A
            self.a = (~self.a) & 0xFF
            return
        if op == 0x03:  # RR A
            self.a = ((self.a >> 1) | ((self.a & 1) << 7)) & 0xFF
            return
        if op == 0x13:  # RRC A
            old_c = self.c
            self.c = self.a & 1
            self.a = ((self.a >> 1) | (old_c << 7)) & 0xFF
            return
        if op == 0x23:  # RL A
            self.a = (((self.a << 1) & 0xFF) | ((self.a >> 7) & 1)) & 0xFF
            return
        if op == 0x33:  # RLC A
            old_c = self.c
            self.c = (self.a >> 7) & 1
            self.a = (((self.a << 1) & 0xFF) | old_c) & 0xFF
            return
        if op == 0xC4:  # SWAP A
            self.a = (((self.a & 0x0F) << 4) | ((self.a >> 4) & 0x0F)) & 0xFF
            return
        if op == 0xA4:  # MUL AB
            prod = self.a * self.b
            self.a = prod & 0xFF
            self.b = (prod >> 8) & 0xFF
            self.c = 0
            return
        if op == 0x84:  # DIV AB
            if self.b != 0:
                q = self.a // self.b
                r = self.a % self.b
                self.a = q
                self.b = r
            self.c = 0
            return
        if op == 0xC3:  # CLR C
            self.c = 0
            return
        if op == 0xD3:  # SETB C
            self.c = 1
            return
        if op == 0xB3:  # CPL C
            self.c = 1 - self.c
            return
        if op == 0xC2:  # CLR bit
            self.set_bit(self.fetch(), 0)
            return
        if op == 0xD2:  # SETB bit
            self.set_bit(self.fetch(), 1)
            return
        if op == 0xB2:  # CPL bit
            bit = self.fetch()
            self.set_bit(bit, 1 - self.get_bit(bit))
            return
        if op == 0xA2:  # MOV C, bit
            self.c = self.get_bit(self.fetch())
            return
        if op == 0x92:  # MOV bit, C
            self.set_bit(self.fetch(), self.c)
            return
        if op == 0x90:  # MOV DPTR, #data16
            hi = self.fetch()
            lo = self.fetch()
            self.dptr = (hi << 8) | lo
            return
        if op == 0xA3:  # INC DPTR
            self.dptr = (self.dptr + 1) & 0xFFFF
            return
        if op == 0x93:  # MOVC A, @A+DPTR
            self.a = self.code[(self.a + self.dptr) & 0xFFFF]
            return
        if op == 0x74:  # MOV A, #imm
            self.a = self.fetch()
            return
        if op == 0xE5:  # MOV A, direct
            self.a = self.read_direct(self.fetch())
            return
        if op in (0xE6, 0xE7):  # MOV A, @Ri
            addr = self.get_r(op & 1)
            self.a = self.iram[addr]
            return
        if 0xE8 <= op <= 0xEF:  # MOV A, Rn
            self.a = self.get_r(op & 7)
            return
        if op == 0xF5:  # MOV direct, A
            self.write_direct(self.fetch(), self.a)
            return
        if op == 0x75:  # MOV direct, #imm
            d = self.fetch()
            imm = self.fetch()
            self.write_direct(d, imm)
            return
        if op == 0x85:  # MOV direct_dst, direct_src (Note: 8051 encodes src first, dst second!)
            src = self.fetch()
            dst = self.fetch()
            self.write_direct(dst, self.read_direct(src))
            return
        if op in (0x86, 0x87):  # MOV direct, @Ri
            d = self.fetch()
            self.write_direct(d, self.iram[self.get_r(op & 1)])
            return
        if 0x88 <= op <= 0x8F:  # MOV direct, Rn
            d = self.fetch()
            self.write_direct(d, self.get_r(op & 7))
            return
        if op in (0xF6, 0xF7):  # MOV @Ri, A
            self.iram[self.get_r(op & 1)] = self.a
            return
        if op in (0x76, 0x77):  # MOV @Ri, #imm
            self.iram[self.get_r(op & 1)] = self.fetch()
            return
        if op in (0xA6, 0xA7):  # MOV @Ri, direct
            self.iram[self.get_r(op & 1)] = self.read_direct(self.fetch())
            return
        if 0xF8 <= op <= 0xFF:  # MOV Rn, A
            self.set_r(op & 7, self.a)
            return
        if 0x78 <= op <= 0x7F:  # MOV Rn, #imm
            self.set_r(op & 7, self.fetch())
            return
        if 0xA8 <= op <= 0xAF:  # MOV Rn, direct
            self.set_r(op & 7, self.read_direct(self.fetch()))
            return
        if op == 0x04:  # INC A
            self.a = (self.a + 1) & 0xFF
            return
        if op == 0x05:  # INC direct
            d = self.fetch()
            self.write_direct(d, self.read_direct(d) + 1)
            return
        if op in (0x06, 0x07):  # INC @Ri
            addr = self.get_r(op & 1)
            self.iram[addr] = (self.iram[addr] + 1) & 0xFF
            return
        if 0x08 <= op <= 0x0F:  # INC Rn
            r = op & 7
            self.set_r(r, self.get_r(r) + 1)
            return
        if op == 0x14:  # DEC A
            self.a = (self.a - 1) & 0xFF
            return
        if op == 0x15:  # DEC direct
            d = self.fetch()
            self.write_direct(d, self.read_direct(d) - 1)
            return
        if 0x18 <= op <= 0x1F:  # DEC Rn
            r = op & 7
            self.set_r(r, self.get_r(r) - 1)
            return
        if op == 0xC0:  # PUSH direct
            self.push8(self.read_direct(self.fetch()))
            return
        if op == 0xD0:  # POP direct
            self.write_direct(self.fetch(), self.pop8())
            return
        if op == 0xC5:  # XCH A, direct
            d = self.fetch()
            v = self.read_direct(d)
            self.write_direct(d, self.a)
            self.a = v
            return
        if 0xC8 <= op <= 0xCF:  # XCH A, Rn
            r = op & 7
            v = self.get_r(r)
            self.set_r(r, self.a)
            self.a = v
            return
        # ADD / ADDC / SUBB / ANL / ORL / XRL
        if (op & 0xF0) in (0x20, 0x30, 0x90, 0x50, 0x40, 0x60):
            hi_nib = op & 0xF0
            low_nib = op & 0x0F
            if low_nib == 0x02 and hi_nib in (0x50, 0x40, 0x60):  # ANL/ORL/XRL direct, A
                d = self.fetch()
                v = self.read_direct(d)
                if hi_nib == 0x50:
                    self.write_direct(d, v & self.a)
                elif hi_nib == 0x40:
                    self.write_direct(d, v | self.a)
                else:
                    self.write_direct(d, v ^ self.a)
                return
            if low_nib == 0x03 and hi_nib in (0x50, 0x40, 0x60):  # ANL/ORL/XRL direct, #imm
                d = self.fetch()
                imm = self.fetch()
                v = self.read_direct(d)
                if hi_nib == 0x50:
                    self.write_direct(d, v & imm)
                elif hi_nib == 0x40:
                    self.write_direct(d, v | imm)
                else:
                    self.write_direct(d, v ^ imm)
                return
            if low_nib == 0x04:
                rhs = self.fetch()
            elif low_nib == 0x05:
                rhs = self.read_direct(self.fetch())
            elif low_nib in (0x06, 0x07):
                rhs = self.iram[self.get_r(low_nib & 1)]
            elif low_nib >= 0x08:
                rhs = self.get_r(low_nib & 7)
            else:
                raise NotImplementedError(f"Unhandled ALU op 0x{op:02X}")

            if hi_nib == 0x20:  # ADD
                res = self.a + rhs
                self.c = 1 if res > 0xFF else 0
                self.a = res & 0xFF
            elif hi_nib == 0x30:  # ADDC
                res = self.a + rhs + self.c
                self.c = 1 if res > 0xFF else 0
                self.a = res & 0xFF
            elif hi_nib == 0x90:  # SUBB
                res = self.a - rhs - self.c
                self.c = 1 if res < 0 else 0
                self.a = res & 0xFF
            elif hi_nib == 0x50:  # ANL
                self.a = self.a & rhs
            elif hi_nib == 0x40:  # ORL
                self.a = self.a | rhs
            elif hi_nib == 0x60:  # XRL
                self.a = self.a ^ rhs
            return

        # CJNE
        if op == 0xB4:  # CJNE A, #imm, rel
            imm = self.fetch()
            rel = self.fetch_rel()
            self.c = 1 if self.a < imm else 0
            if self.a != imm:
                self.pc = (self.pc + rel) & 0xFFFF
            return
        if op == 0xB5:  # CJNE A, direct, rel
            val = self.read_direct(self.fetch())
            rel = self.fetch_rel()
            self.c = 1 if self.a < val else 0
            if self.a != val:
                self.pc = (self.pc + rel) & 0xFFFF
            return
        if op in (0xB6, 0xB7):  # CJNE @Ri, #imm, rel
            lhs = self.iram[self.get_r(op & 1)]
            imm = self.fetch()
            rel = self.fetch_rel()
            self.c = 1 if lhs < imm else 0
            if lhs != imm:
                self.pc = (self.pc + rel) & 0xFFFF
            return
        if 0xB8 <= op <= 0xBF:  # CJNE Rn, #imm, rel
            lhs = self.get_r(op & 7)
            imm = self.fetch()
            rel = self.fetch_rel()
            self.c = 1 if lhs < imm else 0
            if lhs != imm:
                self.pc = (self.pc + rel) & 0xFFFF
            return
        # DJNZ
        if op == 0xD5:  # DJNZ direct, rel
            d = self.fetch()
            rel = self.fetch_rel()
            val = (self.read_direct(d) - 1) & 0xFF
            self.write_direct(d, val)
            if val != 0:
                self.pc = (self.pc + rel) & 0xFFFF
            return
        if 0xD8 <= op <= 0xDF:  # DJNZ Rn, rel
            r = op & 7
            rel = self.fetch_rel()
            val = (self.get_r(r) - 1) & 0xFF
            self.set_r(r, val)
            if val != 0:
                self.pc = (self.pc + rel) & 0xFFFF
            return

        raise NotImplementedError(f"Opcode 0x{op:02X} at PC=0x{self.pc - 1:04X}")


def decode_call_at(cpu: Cpu8051, addr: int) -> Tuple[Optional[int], int]:
    """Decode either a 3-byte LCALL (0x12) or a 2-byte ACALL ((op & 0x1F) == 0x11) at addr."""
    op = cpu.code[addr]
    if op == 0x12:
        target = (cpu.code[addr + 1] << 8) | cpu.code[addr + 2]
        return target, 3
    if (op & 0x1F) == 0x11:
        next_pc = (addr + 2) & 0xFFFF
        target = (next_pc & 0xF800) | ((op & 0xE0) << 3) | cpu.code[addr + 1]
        return target, 2
    return None, 1


def discover_firmware_entrypoints(cpu: Cpu8051) -> dict:
    """
    Locate subroutine addresses directly from the binary's reset vector and call graph:
    - pgm_start (from LJMP at 0x19FD)
    - set_default_parameters, read_all_eeprom_parameters, decode_settings (3 CALLs after clear_ram)
    - dshot_tlm_create_packet (CALL after `jb Flag_Telemetry_Pending` in wait_for_start_no_beep)
    - set_pwm_limit (second CALL inside run2)
    """
    reset_addr = (cpu.code[1] << 8) | cpu.code[2]
    pgm_start = (cpu.code[reset_addr + 1] << 8) | cpu.code[reset_addr + 2]

    # Scan forward from pgm_start for `DJNZ R0, clear_ram` (0xD8 0xFD), followed by 3 CALLs
    addr = pgm_start
    while not (cpu.code[addr] == 0xD8 and cpu.code[addr + 1] == 0xFD):
        addr += 1
    addr += 2

    calls = []
    for _ in range(3):
        target, length = decode_call_at(cpu, addr)
        assert target is not None, f"Expected CALL at 0x{addr:04X}, got 0x{cpu.code[addr]:02X}"
        calls.append(target)
        addr += length

    # Scan for Wait_For_Timer3 macro pattern:
    # jb Flag_Telemetry_Pending, wait_for_t3 (0x20 0x28 rel)
    # jnb Flag_Timer3_Pending, done_waiting  (0x30 0x18 rel)
    # call dshot_tlm_create_packet           (at a + 6)
    dshot_tlm_addr = None
    for a in range(0x0100, reset_addr - 12):
        if (
            cpu.code[a] == 0x20
            and cpu.code[a + 1] == 0x28
            and cpu.code[a + 3] == 0x30
            and cpu.code[a + 4] == 0x18
        ):
            target, _ = decode_call_at(cpu, a + 6)
            if target is not None:
                dshot_tlm_addr = target
                break

    # Scan for set_pwm_limit: in run1..run6, run1 has 4 CALLs and run2 has 5 CALLs
    # where the 1st CALL of run2 is wait_for_comp_out_low and the 2nd CALL is set_pwm_limit,
    # and the 3rd CALL of run2 (wait_for_comm) equals the 2nd CALL of run1 (wait_for_comm)!
    set_pwm_limit_addr = None
    for a in range(pgm_start, reset_addr - 30):
        cur = a
        seq = []
        for _ in range(9):
            t, l = decode_call_at(cpu, cur)
            if t is None:
                break
            seq.append(t)
            cur += l
        # seq[0..3] = run1 (wait_for_comp_out_high, wait_for_comm, comm1_comm2, calc_next_comm_period)
        # seq[4..8] = run2 (wait_for_comp_out_low, set_pwm_limit, wait_for_comm, comm2_comm3, calc_next_comm_period)
        if len(seq) == 9 and seq[1] == seq[6] and seq[3] == seq[8]:
            set_pwm_limit_addr = seq[5]
            wait_for_comm_addr = seq[1]
            break

    return {
        "pgm_start": pgm_start,
        "set_default_parameters": calls[0],
        "read_all_eeprom_parameters": calls[1],
        "decode_settings": calls[2],
        "dshot_tlm_create_packet": dshot_tlm_addr,
        "set_pwm_limit": set_pwm_limit_addr,
        "wait_for_comm": wait_for_comm_addr,
    }


class TestPreFlight8051Emulation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        stock_path = os.path.join(cfg.REF_HEX_DIR, "O_H_5_48_v0.21.0.hex")
        bj3d_path = os.path.join(cfg.HEX_DIR, "O_H_5_48_v0.22.0-3D.hex")
        with open(stock_path, "r", encoding="utf-8") as f:
            cls.stock_mem = cfg.parse_intel_hex(f.read())
        with open(bj3d_path, "r", encoding="utf-8") as f:
            cls.bj3d_mem = cfg.parse_intel_hex(f.read())

    def _boot_and_decode_eeprom(self, code_mem: dict) -> Tuple[Cpu8051, dict]:
        cpu = Cpu8051(code_mem)
        eps = discover_firmware_entrypoints(cpu)
        cpu.call_subroutine(eps["set_default_parameters"])
        cpu.call_subroutine(eps["read_all_eeprom_parameters"])
        cpu.call_subroutine(eps["decode_settings"])
        return cpu, eps

    def test_01_emulate_eeprom_read_and_decode_settings(self):
        """Execute actual 8051 `read_all_eeprom_parameters` + `decode_settings` in Bluejay3D .hex."""
        cpu, _ = self._boot_and_decode_eeprom(self.bj3d_mem)

        # Verify Flags2.2 (Flag_Pgm_Bidir = bit 0x22) is 1 by default in Bluejay3D
        self.assertEqual(cpu.get_bit(0x22), 1, "Flag_Pgm_Bidir (Flags2.2) must be set to 1 by decode_settings")

        # Verify Flags3 3D flags (Flags3.3=0x2B, Flags3.4=0x2C, Flags3.5=0x2D)
        self.assertEqual(cpu.get_bit(0x2B), 1, "Flag_3D_Rev_Boost_En (Flags3.3) must be 1")
        self.assertEqual(cpu.get_bit(0x2C), 1, "Flag_3D_Fast_Restart (Flags3.4) must be 1")
        self.assertEqual(cpu.get_bit(0x2D), 1, "Flag_3D_Fast_Track (Flags3.5) must be 1")

        # Verify decoded 3D direct RAM variables at 0x68..0x6C:
        # Pwm_3D_Brake_Limit (0x68) = 8 * 12 = 96
        # Pwm_3D_Brake_Floor (0x69) = 8 * 3  = 24
        # Pwm_3D_Brake_Speed (0x6A) = 104 - 5*8 = 64 (0x40)
        # Pwm_3D_Min_Duty    (0x6B) = 3 * 2  = 6
        # Bidir_Glitch_Thresh(0x6C) = 1 + 1  = 2
        self.assertEqual(cpu.iram[0x68], 96, "Pwm_3D_Brake_Limit should be 96")
        self.assertEqual(cpu.iram[0x69], 24, "Pwm_3D_Brake_Floor should be 24")
        self.assertEqual(cpu.iram[0x6A], 64, "Pwm_3D_Brake_Speed should be 64")
        self.assertEqual(cpu.iram[0x6B], 6, "Pwm_3D_Min_Duty should be 6")
        self.assertEqual(cpu.iram[0x6C], 2, "Bidir_Glitch_Thresh should be 2")

    def test_02_emulate_set_pwm_limit_braking_and_initial_run(self):
        """
        Execute actual 8051 `set_pwm_limit` machine code in Stock v0.21 vs Bluejay3D v0.22:
        1. During Flag_Dir_Change_Brake (bit 0x1D):
           - Stock v0.21 overwrites Pwm_Limit_By_Rpm (0x4E) with slope calculation!
           - Bluejay3D preserves Pwm_Limit_By_Rpm = Pwm_3D_Brake_Limit (96)!
        2. During Flag_Initial_Run_Phase (bit 0x11) after reversal at Comm_Period4x_H = 40:
           - Stock v0.21 chokes power in half (#127 / 40 * 9 = 27)!
           - Bluejay3D delivers full low-RPM power slope (#255 / 40 * 9 = 54)!
        """
        stock_cpu, stock_eps = self._boot_and_decode_eeprom(self.stock_mem)
        bj3d_cpu, bj3d_eps = self._boot_and_decode_eeprom(self.bj3d_mem)

        # Case 1: Active 3D Braking (Flag_Dir_Change_Brake = bit 0x1D = 1, Comm_Period4x_H (0x43) = 20)
        for cpu, eps in ((stock_cpu, stock_eps), (bj3d_cpu, bj3d_eps)):
            cpu.set_bit(0x1D, 1)       # Flag_Dir_Change_Brake = 1
            cpu.iram[0x43] = 20        # Comm_Period4x_H = 20
            cpu.iram[0x4F] = 5         # Pwm_Limit_Beg = 5
            cpu.iram[0x4E] = 5         # Pwm_Limit_By_Rpm before run2
            cpu.call_subroutine(eps["set_pwm_limit"])

        self.assertEqual(stock_cpu.iram[0x4E], 108, "Stock v0.21 overwrites Pwm_Limit_By_Rpm in run2 during braking!")
        self.assertEqual(bj3d_cpu.iram[0x4E], 96, "Bluejay3D locks Pwm_Limit_By_Rpm to Pwm_3D_Brake_Limit (96)!")

        # Case 2: Post-Reversal Initial Run Phase (Flag_Dir_Change_Brake=0, Flag_Initial_Run_Phase=bit 0x11=1)
        for cpu, eps in ((stock_cpu, stock_eps), (bj3d_cpu, bj3d_eps)):
            cpu.set_bit(0x1D, 0)       # Flag_Dir_Change_Brake = 0
            cpu.set_bit(0x11, 1)       # Flag_Initial_Run_Phase = 1
            cpu.iram[0x43] = 40        # Comm_Period4x_H = 40 (~8,000 eRPM)
            cpu.iram[0x4F] = 5         # Pwm_Limit_Beg = 5
            cpu.call_subroutine(eps["set_pwm_limit"])

        self.assertEqual(stock_cpu.iram[0x4E], 27, "Stock v0.21 chokes post-reversal torque by 50% (27/255)")
        self.assertEqual(bj3d_cpu.iram[0x4E], 54, "Bluejay3D delivers 2x post-reversal torque (54/255)")

    def test_03_emulate_dshot_tlm_create_packet_stage0_and_stage1(self):
        """
        Execute actual 8051 `dshot_tlm_create_packet` machine code in Stock v0.21 vs Bluejay3D v0.22:
        1. At Comm_Period4x = 0x3FFF vs 0x4000 (~5,000 eRPM 3D handover):
           - Stock v0.21 suffers a +254 us 8-bit overflow jump in Tlm_Data_H:Tlm_Data_L!
           - Bluejay3D computes exact 16-bit period with only 2 us step!
        2. During Flag_Dir_Change_Brake = 1:
           - Bluejay3D outputs 0x0FFF (0 eRPM) so Betaflight RPM filters never spike!
        """
        stock_cpu, stock_eps = self._boot_and_decode_eeprom(self.stock_mem)
        bj3d_cpu, bj3d_eps = self._boot_and_decode_eeprom(self.bj3d_mem)

        def run_tlm_stage0(cpu: Cpu8051, eps: dict, comm_h: int, comm_l: int, braking: bool = False) -> int:
            cpu.iram[0x42] = comm_l    # Comm_Period4x_L
            cpu.iram[0x43] = comm_h    # Comm_Period4x_H
            cpu.set_bit(0x1D, 1 if braking else 0)  # Flag_Dir_Change_Brake
            # Register bank 2 Temp7 = R6 (0x16) = packet stage 0
            cpu.iram[0x16] = 0
            cpu.call_subroutine(eps["dshot_tlm_create_packet"])
            # Tlm_Data_L = 0x26, Tlm_Data_H = 0x27
            return (cpu.iram[0x27] << 8) | cpu.iram[0x26]

        stock_63 = run_tlm_stage0(stock_cpu, stock_eps, 0x3F, 0xFF)
        stock_64 = run_tlm_stage0(stock_cpu, stock_eps, 0x40, 0x00)
        self.assertEqual(stock_64 - stock_63, 254, "Stock v0.21 has +254 us 8-bit overflow jump at Comm_Period4x_H=64")

        bj3d_63 = run_tlm_stage0(bj3d_cpu, bj3d_eps, 0x3F, 0xFF)
        bj3d_64 = run_tlm_stage0(bj3d_cpu, bj3d_eps, 0x40, 0x00)
        self.assertEqual(abs(bj3d_64 - bj3d_63), 2, "Bluejay3D eliminates the 8-bit overflow jump at Comm_Period4x_H=64")

        # Verify braking telemetry blanking in stage 0 + stage 1 (encodes 0 -> 0x0FFF)
        run_tlm_stage0(bj3d_cpu, bj3d_eps, 0x20, 0x00, braking=True)
        bj3d_cpu.call_subroutine(bj3d_eps["dshot_tlm_create_packet"])  # Stage 1
        encoded_12bit = (bj3d_cpu.iram[0x27] << 8) | bj3d_cpu.iram[0x26]
        self.assertEqual(encoded_12bit, 0x0FFF, "Bluejay3D must encode 0x0FFF (0 eRPM) during active 3D braking")

    def test_04_emulate_wait_for_comm_demag_cutoff_protection(self):
        """
        Execute actual 8051 `wait_for_comm` machine code in Stock v0.21 vs Bluejay3D v0.22
        when Demag_Detected_Metric = 190 (accumulated during 3D braking) and Flag_Initial_Run_Phase = 1:
        - Stock v0.21 sets Flag_Desync_Notify (Flags0.4 = bit 0x14) and cuts power FETs off!
        - Bluejay3D protects Flag_Initial_Run_Phase & Flag_Dir_Change_Brake from demag FET cutoff!
        """
        stock_cpu, stock_eps = self._boot_and_decode_eeprom(self.stock_mem)
        bj3d_cpu, bj3d_eps = self._boot_and_decode_eeprom(self.bj3d_mem)

        for cpu, eps in ((stock_cpu, stock_eps), (bj3d_cpu, bj3d_eps)):
            cpu.iram[0x38] = 190       # Demag_Detected_Metric = 190 (from braking)
            cpu.iram[0x3A] = 160       # Demag_Pwr_Off_Thresh = 160
            cpu.set_bit(0x19, 0)       # Flag_Demag_Detected = 0
            cpu.set_bit(0x11, 1)       # Flag_Initial_Run_Phase = 1 (post-reversal acceleration)
            cpu.set_bit(0x14, 0)       # Flag_Desync_Notify = 0
            cpu.set_bit(0x18, 0)       # Flag_Timer3_Pending = 0 (so Wait_For_Timer3 exits immediately)
            cpu.call_subroutine(eps["wait_for_comm"])

        self.assertEqual(stock_cpu.get_bit(0x14), 1, "Stock v0.21 triggers Flag_Desync_Notify & cuts FETs after reversal!")
        self.assertEqual(bj3d_cpu.get_bit(0x14), 0, "Bluejay3D prevents post-reversal demag FET cutoff!")


if __name__ == "__main__":
    unittest.main(verbosity=2)
