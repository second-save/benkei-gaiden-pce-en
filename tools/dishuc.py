"""HuC6280 (PC Engine CPU) disassembler — pure stdlib Python 3."""
from __future__ import annotations

import argparse
from pathlib import Path

# Addressing modes:
# imp: implied, acc: A, imm: #xx, zp: $xx, zpx: $xx,X, zpy: $xx,Y,
# zpi: ($xx), zpix: ($xx,X), zpiy: ($xx),Y, rel: branch target,
# abs: $xxxx, absx: $xxxx,X, absy: $xxxx,Y, absi: ($xxxx), absix: ($xxxx,X),
# zprel: $xx,rel (BBR/BBS), tst_zp: #xx,$xx, tst_abs: #xx,$xxxx,
# tst_zpx: #xx,$xx,X, tst_absx: #xx,$xxxx,X, blk: $ssss,$dddd,$llll (TII/TDD/TIN/TIA/TAI)
OPCODES: dict[int, tuple[str, str]] = {
    0x00: ("BRK", "imm"), 0x01: ("ORA", "zpix"), 0x02: ("SXY", "imp"), 0x03: ("ST0", "imm"),
    0x04: ("TSB", "zp"), 0x05: ("ORA", "zp"), 0x06: ("ASL", "zp"), 0x07: ("RMB0", "zp"),
    0x08: ("PHP", "imp"), 0x09: ("ORA", "imm"), 0x0A: ("ASL", "acc"), 0x0C: ("TSB", "abs"),
    0x0D: ("ORA", "abs"), 0x0E: ("ASL", "abs"), 0x0F: ("BBR0", "zprel"),
    0x10: ("BPL", "rel"), 0x11: ("ORA", "zpiy"), 0x12: ("ORA", "zpi"), 0x13: ("ST1", "imm"),
    0x14: ("TRB", "zp"), 0x15: ("ORA", "zpx"), 0x16: ("ASL", "zpx"), 0x17: ("RMB1", "zp"),
    0x18: ("CLC", "imp"), 0x19: ("ORA", "absy"), 0x1A: ("INC", "acc"), 0x1C: ("TRB", "abs"),
    0x1D: ("ORA", "absx"), 0x1E: ("ASL", "absx"), 0x1F: ("BBR1", "zprel"),
    0x20: ("JSR", "abs"), 0x21: ("AND", "zpix"), 0x22: ("SAX", "imp"), 0x23: ("ST2", "imm"),
    0x24: ("BIT", "zp"), 0x25: ("AND", "zp"), 0x26: ("ROL", "zp"), 0x27: ("RMB2", "zp"),
    0x28: ("PLP", "imp"), 0x29: ("AND", "imm"), 0x2A: ("ROL", "acc"), 0x2C: ("BIT", "abs"),
    0x2D: ("AND", "abs"), 0x2E: ("ROL", "abs"), 0x2F: ("BBR2", "zprel"),
    0x30: ("BMI", "rel"), 0x31: ("AND", "zpiy"), 0x32: ("AND", "zpi"), 0x34: ("BIT", "zpx"),
    0x35: ("AND", "zpx"), 0x36: ("ROL", "zpx"), 0x37: ("RMB3", "zp"), 0x38: ("SEC", "imp"),
    0x39: ("AND", "absy"), 0x3A: ("DEC", "acc"), 0x3C: ("BIT", "absx"), 0x3D: ("AND", "absx"),
    0x3E: ("ROL", "absx"), 0x3F: ("BBR3", "zprel"),
    0x40: ("RTI", "imp"), 0x41: ("EOR", "zpix"), 0x42: ("SAY", "imp"), 0x43: ("TMA", "imm"),
    0x44: ("BSR", "rel"), 0x45: ("EOR", "zp"), 0x46: ("LSR", "zp"), 0x47: ("RMB4", "zp"),
    0x48: ("PHA", "imp"), 0x49: ("EOR", "imm"), 0x4A: ("LSR", "acc"), 0x4C: ("JMP", "abs"),
    0x4D: ("EOR", "abs"), 0x4E: ("LSR", "abs"), 0x4F: ("BBR4", "zprel"),
    0x50: ("BVC", "rel"), 0x51: ("EOR", "zpiy"), 0x52: ("EOR", "zpi"), 0x53: ("TAM", "imm"),
    0x54: ("CSL", "imp"), 0x55: ("EOR", "zpx"), 0x56: ("LSR", "zpx"), 0x57: ("RMB5", "zp"),
    0x58: ("CLI", "imp"), 0x59: ("EOR", "absy"), 0x5A: ("PHY", "imp"), 0x5D: ("EOR", "absx"),
    0x5E: ("LSR", "absx"), 0x5F: ("BBR5", "zprel"),
    0x60: ("RTS", "imp"), 0x61: ("ADC", "zpix"), 0x62: ("CLA", "imp"), 0x64: ("STZ", "zp"),
    0x65: ("ADC", "zp"), 0x66: ("ROR", "zp"), 0x67: ("RMB6", "zp"), 0x68: ("PLA", "imp"),
    0x69: ("ADC", "imm"), 0x6A: ("ROR", "acc"), 0x6C: ("JMP", "absi"), 0x6D: ("ADC", "abs"),
    0x6E: ("ROR", "abs"), 0x6F: ("BBR6", "zprel"),
    0x70: ("BVS", "rel"), 0x71: ("ADC", "zpiy"), 0x72: ("ADC", "zpi"), 0x73: ("TII", "blk"),
    0x74: ("STZ", "zpx"), 0x75: ("ADC", "zpx"), 0x76: ("ROR", "zpx"), 0x77: ("RMB7", "zp"),
    0x78: ("SEI", "imp"), 0x79: ("ADC", "absy"), 0x7A: ("PLY", "imp"), 0x7C: ("JMP", "absix"),
    0x7D: ("ADC", "absx"), 0x7E: ("ROR", "absx"), 0x7F: ("BBR7", "zprel"),
    0x80: ("BRA", "rel"), 0x81: ("STA", "zpix"), 0x82: ("CLX", "imp"), 0x83: ("TST", "tst_zp"),
    0x84: ("STY", "zp"), 0x85: ("STA", "zp"), 0x86: ("STX", "zp"), 0x87: ("SMB0", "zp"),
    0x88: ("DEY", "imp"), 0x89: ("BIT", "imm"), 0x8A: ("TXA", "imp"), 0x8C: ("STY", "abs"),
    0x8D: ("STA", "abs"), 0x8E: ("STX", "abs"), 0x8F: ("BBS0", "zprel"),
    0x90: ("BCC", "rel"), 0x91: ("STA", "zpiy"), 0x92: ("STA", "zpi"), 0x93: ("TST", "tst_abs"),
    0x94: ("STY", "zpx"), 0x95: ("STA", "zpx"), 0x96: ("STX", "zpy"), 0x97: ("SMB1", "zp"),
    0x98: ("TYA", "imp"), 0x99: ("STA", "absy"), 0x9A: ("TXS", "imp"), 0x9C: ("STZ", "abs"),
    0x9D: ("STA", "absx"), 0x9E: ("STZ", "absx"), 0x9F: ("BBS1", "zprel"),
    0xA0: ("LDY", "imm"), 0xA1: ("LDA", "zpix"), 0xA2: ("LDX", "imm"), 0xA3: ("TST", "tst_zpx"),
    0xA4: ("LDY", "zp"), 0xA5: ("LDA", "zp"), 0xA6: ("LDX", "zp"), 0xA7: ("SMB2", "zp"),
    0xA8: ("TAY", "imp"), 0xA9: ("LDA", "imm"), 0xAA: ("TAX", "imp"), 0xAC: ("LDY", "abs"),
    0xAD: ("LDA", "abs"), 0xAE: ("LDX", "abs"), 0xAF: ("BBS2", "zprel"),
    0xB0: ("BCS", "rel"), 0xB1: ("LDA", "zpiy"), 0xB2: ("LDA", "zpi"), 0xB3: ("TST", "tst_absx"),
    0xB4: ("LDY", "zpx"), 0xB5: ("LDA", "zpx"), 0xB6: ("LDX", "zpy"), 0xB7: ("SMB3", "zp"),
    0xB8: ("CLV", "imp"), 0xB9: ("LDA", "absy"), 0xBA: ("TSX", "imp"), 0xBC: ("LDY", "absx"),
    0xBD: ("LDA", "absx"), 0xBE: ("LDX", "absy"), 0xBF: ("BBS3", "zprel"),
    0xC0: ("CPY", "imm"), 0xC1: ("CMP", "zpix"), 0xC2: ("CLY", "imp"), 0xC3: ("TDD", "blk"),
    0xC4: ("CPY", "zp"), 0xC5: ("CMP", "zp"), 0xC6: ("DEC", "zp"), 0xC7: ("SMB4", "zp"),
    0xC8: ("INY", "imp"), 0xC9: ("CMP", "imm"), 0xCA: ("DEX", "imp"), 0xCC: ("CPY", "abs"),
    0xCD: ("CMP", "abs"), 0xCE: ("DEC", "abs"), 0xCF: ("BBS4", "zprel"),
    0xD0: ("BNE", "rel"), 0xD1: ("CMP", "zpiy"), 0xD2: ("CMP", "zpi"), 0xD3: ("TIN", "blk"),
    0xD4: ("CSH", "imp"), 0xD5: ("CMP", "zpx"), 0xD6: ("DEC", "zpx"), 0xD7: ("SMB5", "zp"),
    0xD8: ("CLD", "imp"), 0xD9: ("CMP", "absy"), 0xDA: ("PHX", "imp"), 0xDD: ("CMP", "absx"),
    0xDE: ("DEC", "absx"), 0xDF: ("BBS5", "zprel"),
    0xE0: ("CPX", "imm"), 0xE1: ("SBC", "zpix"), 0xE3: ("TIA", "blk"), 0xE4: ("CPX", "zp"),
    0xE5: ("SBC", "zp"), 0xE6: ("INC", "zp"), 0xE7: ("SMB6", "zp"), 0xE8: ("INX", "imp"),
    0xE9: ("SBC", "imm"), 0xEA: ("NOP", "imp"), 0xEC: ("CPX", "abs"), 0xED: ("SBC", "abs"),
    0xEE: ("INC", "abs"), 0xEF: ("BBS6", "zprel"),
    0xF0: ("BEQ", "rel"), 0xF1: ("SBC", "zpiy"), 0xF2: ("SBC", "zpi"), 0xF3: ("TAI", "blk"),
    0xF4: ("SET", "imp"), 0xF5: ("SBC", "zpx"), 0xF6: ("INC", "zpx"), 0xF7: ("SMB7", "zp"),
    0xF8: ("SED", "imp"), 0xF9: ("SBC", "absy"), 0xFA: ("PLX", "imp"), 0xFD: ("SBC", "absx"),
    0xFE: ("INC", "absx"), 0xFF: ("BBS7", "zprel"),
}

MODE_LEN = {
    "imp": 1, "acc": 1,
    "imm": 2, "zp": 2, "zpx": 2, "zpy": 2, "zpi": 2, "zpix": 2, "zpiy": 2, "rel": 2,
    "abs": 3, "absx": 3, "absy": 3, "absi": 3, "absix": 3, "zprel": 3, "tst_zp": 3, "tst_zpx": 3,
    "tst_abs": 4, "tst_absx": 4,
    "blk": 7,
}


def dis_one(data: bytes, off: int, pc: int) -> tuple[int, str, str]:
    op = data[off]
    if op not in OPCODES:
        return 1, f"{op:02X}", f".db ${op:02X}"
    mnem, mode = OPCODES[op]
    size = MODE_LEN[mode]
    if off + size > len(data):
        return 1, f"{op:02X}", f".db ${op:02X}"
    raw = data[off:off + size]
    hex_s = raw.hex(" ")
    if mode == "imp":
        arg = ""
    elif mode == "acc":
        arg = "A"
    elif mode == "imm":
        arg = f"#${raw[1]:02X}"
    elif mode == "zp":
        arg = f"${raw[1]:02X}"
    elif mode == "zpx":
        arg = f"${raw[1]:02X},X"
    elif mode == "zpy":
        arg = f"${raw[1]:02X},Y"
    elif mode == "zpi":
        arg = f"(${raw[1]:02X})"
    elif mode == "zpix":
        arg = f"(${raw[1]:02X},X)"
    elif mode == "zpiy":
        arg = f"(${raw[1]:02X}),Y"
    elif mode == "rel":
        d = raw[1] - 0x100 if raw[1] >= 0x80 else raw[1]
        arg = f"${(pc + 2 + d) & 0xFFFF:04X}"
    elif mode == "abs":
        arg = f"${raw[1] | (raw[2] << 8):04X}"
    elif mode == "absx":
        arg = f"${raw[1] | (raw[2] << 8):04X},X"
    elif mode == "absy":
        arg = f"${raw[1] | (raw[2] << 8):04X},Y"
    elif mode == "absi":
        arg = f"(${raw[1] | (raw[2] << 8):04X})"
    elif mode == "absix":
        arg = f"(${raw[1] | (raw[2] << 8):04X},X)"
    elif mode == "zprel":
        d = raw[2] - 0x100 if raw[2] >= 0x80 else raw[2]
        arg = f"${raw[1]:02X},${(pc + 3 + d) & 0xFFFF:04X}"
    elif mode == "tst_zp":
        arg = f"#${raw[1]:02X},${raw[2]:02X}"
    elif mode == "tst_zpx":
        arg = f"#${raw[1]:02X},${raw[2]:02X},X"
    elif mode == "tst_abs":
        arg = f"#${raw[1]:02X},${raw[2] | (raw[3] << 8):04X}"
    elif mode == "tst_absx":
        arg = f"#${raw[1]:02X},${raw[2] | (raw[3] << 8):04X},X"
    elif mode == "blk":
        src = raw[1] | (raw[2] << 8)
        dst = raw[3] | (raw[4] << 8)
        ln = raw[5] | (raw[6] << 8)
        arg = f"${src:04X},${dst:04X},${ln:04X}"
    else:
        arg = ""
    txt = f"{mnem} {arg}".rstrip()
    return size, hex_s, txt


def disassemble(data: bytes, start_off: int, base_pc: int, count: int) -> list[str]:
    lines = []
    off = start_off
    pc = base_pc
    for _ in range(count):
        if off >= len(data):
            break
        size, hex_s, txt = dis_one(data, off, pc)
        lines.append(f"${pc:04X} (0x{off:05X}): {hex_s:<21s} {txt}")
        off += size
        pc = (pc + size) & 0xFFFF
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("rom")
    ap.add_argument("off", type=lambda x: int(x, 16), help="file offset (hex)")
    ap.add_argument("count", nargs="?", type=int, default=60)
    ap.add_argument("--pc", type=lambda x: int(x, 16), help="CPU PC of off (default: bank 0=$E000+(off&1FFF) else $C000+(off&1FFF))")
    args = ap.parse_args()
    data = Path(args.rom).read_bytes()
    pc = args.pc if args.pc is not None else ((0xE000 if args.off < 0x2000 else 0xC000) + (args.off & 0x1FFF))
    for line in disassemble(data, args.off, pc, args.count):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
