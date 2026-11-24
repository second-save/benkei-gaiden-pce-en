"""Stateful text codec and canonical string table inventory for Benkei Gaiden (PCE).

Hardware text architecture (Bank $02 $CE45/$CF27):
- r74 ($74) selects the active character plane (reset to $00 at string start):
    $00: jp_base.tbl  - 8x16 halfwidth kana/digits/ASCII/punct + 18 2-byte kanji pairs (VRAM $0400)
    $20: jp_ef.tbl    - 16x16 high-frequency kanji (VRAM $0400, pal $E/$F; toggled by $EF)
    $FD: jp_ed.tbl    - 16x16 kanji (VRAM $0100 BG[17], pal $C/$D; toggled by $ED)
    $1D: jp_fd.tbl    - 16x16 kanji (VRAM $0100 BG[17], pal $E/$F; toggled by $FD)
- During the Title, Save/BRAM menu, and Ending Credits, BG[34] temporarily overwrites
  VRAM $0120..$0177 ($ED/$FD bytes $20..$77) with specialized kanji/names (`bg34=True`).
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TBL_DIR = ROOT / "tbl"
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

from tbl import Table  # noqa: E402

TOKEN_RE = re.compile(r"\{(\w+)(?::([0-9A-Fa-f]*))?\}|\[([0-9A-Fa-f]{2})\]")

# Toggle byte -> (XOR mask on r74, control token name)
TOGGLE_BYTES = {0xEF: (0x20, "ef"), 0xED: (0xFD, "ed"), 0xFD: (0x1D, "fd")}
TOGGLE_NAMES = {name: (byte, mask) for byte, (mask, name) in TOGGLE_BYTES.items()}


@dataclass(frozen=True)
class RomString:
    group: str
    index: int
    offset: int
    length: int | None  # None = $FF-terminated; int = fixed/adjacent-pointer byte length
    bg34: bool = False


@dataclass(frozen=True)
class PtrTable:
    group: str
    ptr_offset: int
    count: int
    has_sentinel: bool
    rom_base: int
    cpu_base: int
    is_len_table: bool = False


PTR_TABLES: tuple[PtrTable, ...] = (
    PtrTable("b09_password", 0x12609, 5, False, 0x12000, 0xC000),
    PtrTable("b0a_menus", 0x1505E, 31, False, 0x14000, 0x4000),
    PtrTable("b0a_locations", 0x15268, 13, False, 0x14000, 0x4000),
    PtrTable("b0d_enemy_kanji", 0x1BA06, 112, True, 0x1A000, 0xA000, True),
    PtrTable("b0d_enemy_kana", 0x1BD12, 112, True, 0x1A000, 0xA000, True),
    PtrTable("b0e_jutsu", 0x1C032, 32, False, 0x1C000, 0x4000),
    PtrTable("b0e_items", 0x1C13A, 128, False, 0x1C000, 0x4000),
    PtrTable("b11_dialogue", 0x2397F, 648, False, 0x1C000, 0x4000),
    PtrTable("b1b_staff", 0x37A3D, 41, False, 0x36000, 0xC000),
)


class PceCodec:
    """Loads jp_*.tbl files via tbl.Table and handles stateful $74 decoding/encoding."""

    def __init__(self, tbl_dir: Path = TBL_DIR) -> None:
        self.base = Table.load(tbl_dir / "jp_base.tbl")
        self.ef = Table.load(tbl_dir / "jp_ef.tbl")
        self.ed = Table.load(tbl_dir / "jp_ed.tbl")
        self.fd = Table.load(tbl_dir / "jp_fd.tbl")
        self.bg34_ed = Table.load(tbl_dir / "jp_bg34_ed.tbl")
        self.bg34_fd = Table.load(tbl_dir / "jp_bg34_fd.tbl")

        # BG[34] overwrites VRAM $0120..$0177 (bytes $20..$77); only bytes >= $78 remain from BG[17].
        self._bg34_ed_dec = {
            **{k: v for k, v in self.ed.dec.items() if k[0] >= 0x78},
            **self.bg34_ed.dec,
        }
        self._bg34_fd_dec = {
            **{k: v for k, v in self.fd.dec.items() if k[0] >= 0x78},
            **self.bg34_fd.dec,
        }
        self._bg34_ed_enc = {
            **{v: k for k, v in self._bg34_ed_dec.items()},
        }
        self._bg34_fd_enc = {
            **{v: k for k, v in self._bg34_fd_dec.items()},
        }

        # Lookup order when auto-switching out of current plane for plain-text encoding
        self._plane_order = (0x00, 0x20, 0xFD, 0x1D)
        self._state_to_open_byte = {0x20: 0xEF, 0xFD: 0xED, 0x1D: 0xFD}

    def _dec_for_state(self, r74: int, byte: int, bg34: bool) -> str | None:
        code = bytes((byte,))
        if r74 == 0x20:
            return self.ef.dec.get(code)
        if r74 == 0xFD:
            return (self._bg34_ed_dec if bg34 else self.ed.dec).get(code)
        if r74 == 0x1D:
            return (self._bg34_fd_dec if bg34 else self.fd.dec).get(code)
        return None

    def _enc_tables_for_state(self, r74: int, bg34: bool) -> tuple[dict[str, bytes], ...]:
        if r74 == 0x00:
            return (self.base.enc,)
        if r74 == 0x20:
            return (self.ef.enc,)
        if r74 == 0xFD:
            return (self._bg34_ed_enc if bg34 else self.ed.enc,)
        if r74 == 0x1D:
            return (self._bg34_fd_enc if bg34 else self.fd.enc,)
        return ()

    def decode(
        self,
        data: bytes | bytearray,
        pos: int = 0,
        length: int | None = None,
        *,
        bg34: bool = False,
        preserve_toggles: bool = False,
        maxlen: int = 4096,
    ) -> tuple[str, int]:
        """Decode one string from `data[pos:]`. Returns `(text, consumed_bytes)`."""
        start = pos
        stop = len(data) if length is None else pos + length
        r74 = 0
        out: list[str] = []

        while pos < stop:
            if length is None and pos - start >= maxlen:
                raise ValueError(f"no {{end}} within {maxlen} bytes of {start:#x}")
            b = data[pos]
            if b in TOGGLE_BYTES:
                mask, name = TOGGLE_BYTES[b]
                r74 ^= mask
                pos += 1
                if preserve_toggles:
                    out.append(f"{{{name}}}")
                continue
            if r74 == 0x00:
                matched = False
                for k in range(min(self.base.keylen, stop - pos), 0, -1):
                    code = bytes(data[pos : pos + k])
                    if code in self.base.ctrl:
                        name, argc = self.base.ctrl[code]
                        if name in TOGGLE_NAMES:
                            continue  # already handled above
                        pos += k + argc
                        out.append(f"{{{name}}}")
                        if name == "end" and length is None:
                            return "".join(out), pos - start
                        matched = True
                        break
                    val = self.base.dec.get(code)
                    if val is not None:
                        out.append(val)
                        pos += k
                        matched = True
                        break
                if not matched:
                    out.append(f"[{b:02X}]")
                    pos += 1
            else:
                if b in (0xEE, 0xFE, 0xFF):
                    name = self.base.ctrl[bytes((b,))][0]
                    pos += 1
                    out.append(f"{{{name}}}")
                    if name == "end" and length is None:
                        return "".join(out), pos - start
                    continue
                val = self._dec_for_state(r74, b, bg34)
                pos += 1
                if val is not None:
                    out.append(val)
                else:
                    tag = {0x20: "EF", 0xFD: "ED", 0x1D: "FD"}.get(r74, f"M{r74:02X}")
                    out.append(f"[{tag}:{b:02X}]")

        if length is None:
            raise ValueError(f"ran off end of data decoding from {start:#x}")
        return "".join(out), pos - start

    def encode(self, text: str, *, bg34: bool = False) -> bytes:
        """Encode `text` back to ROM bytes (handles both explicit toggles and plain Unicode)."""
        out = bytearray()
        r74 = 0
        i = 0

        while i < len(text):
            m = TOKEN_RE.match(text, i)
            if m:
                if m[3]:
                    out.append(int(m[3], 16))
                else:
                    name = m[1]
                    if name in TOGGLE_NAMES:
                        b, mask = TOGGLE_NAMES[name]
                        out.append(b)
                        r74 ^= mask
                    elif name in self.base.ctrl_enc:
                        code, argc = self.base.ctrl_enc[name]
                        out.extend(code)
                        if argc:
                            out.extend(bytes.fromhex(m[2]))
                    else:
                        raise KeyError(f"unknown control token {{{name}}}")
                i = m.end()
                continue

            # Try matching in currently active plane first
            encoded = self._match_in_state(text, i, r74, bg34)
            if encoded is not None:
                code, consumed = encoded
                out.extend(code)
                i += consumed
                continue

            # Otherwise auto-switch to the first plane containing a match
            for target_r74 in self._plane_order:
                if target_r74 == r74:
                    continue
                encoded = self._match_in_state(text, i, target_r74, bg34)
                if encoded is not None:
                    if r74 != 0x00:
                        out.append(self._state_to_open_byte[r74])
                    if target_r74 != 0x00:
                        out.append(self._state_to_open_byte[target_r74])
                    code, consumed = encoded
                    out.extend(code)
                    r74 = target_r74
                    i += consumed
                    break
            else:
                raise KeyError(f"unencodable character {text[i]!r} at index {i} of {text!r}")

        return bytes(out)

    def _match_in_state(self, text: str, idx: int, r74: int, bg34: bool) -> tuple[bytes, int] | None:
        for enc_map in self._enc_tables_for_state(r74, bg34):
            maxlen = max((len(k) for k in enc_map), default=1)
            for k in range(min(maxlen, len(text) - idx), 0, -1):
                sub = text[idx : idx + k]
                if sub in enc_map:
                    return enc_map[sub], k
        return None


def _read_u16(rom: bytes, off: int) -> int:
    return rom[off] | (rom[off + 1] << 8)


def iter_all_rom_strings(rom: bytes) -> list[RomString]:
    """Return every discovered string location across the Japanese Benkei Gaiden (PCE) ROM."""
    items: list[RomString] = []

    # 1. B$00 build timestamp (Test Mode)
    items.append(RomString("b00_timestamp", 0, 0x01B75, None))

    # 2. B$02 $DE36..$DFBB system / menus / status / battle summary / Test Mode
    off = 0x05E36
    idx = 0
    while off < 0x05FBC:
        nxt = rom.index(0xFF, off) + 1
        items.append(RomString("b02_sys", idx, off, None))
        off = nxt
        idx += 1

    # 3. B$09 $C609 password entry kana rows (5 rows)
    for k in range(5):
        ptr = _read_u16(rom, 0x12609 + k * 2)
        items.append(RomString("b09_password", k, 0x12000 + (ptr - 0xC000), None))

    # 4. B$0A $505E BRAM/Name-entry/Title menus (31) + $5268 locations (13)
    for k in range(31):
        ptr = _read_u16(rom, 0x1505E + k * 2)
        o = 0x14000 + (ptr - 0x4000)
        items.append(RomString("b0a_menus", k, o, None, bg34=(0x15159 <= o < 0x151A6)))
    for k in range(13):
        ptr = _read_u16(rom, 0x15268 + k * 2)
        items.append(RomString("b0a_locations", k, 0x14000 + (ptr - 0x4000), None))

    # 5. B$0D $BA06 enemy kanji (112) & $BD12 enemy kana (112) - length = next_ptr - cur_ptr
    for gname, ptbl in (("b0d_enemy_kanji", 0x1BA06), ("b0d_enemy_kana", 0x1BD12)):
        for k in range(112):
            p0 = _read_u16(rom, ptbl + k * 2)
            p1 = _read_u16(rom, ptbl + k * 2 + 2)
            items.append(RomString(gname, k, 0x1A000 + (p0 - 0xA000), p1 - p0))

    # 6. B$0E..$11 jutsu (32), items (128), battle templates (13), dialogue (648), ending credits/narration
    for k in range(32):
        ptr = _read_u16(rom, 0x1C032 + k * 2)
        items.append(RomString("b0e_jutsu", k, 0x1C000 + (ptr - 0x4000), None))
    for k in range(128):
        ptr = _read_u16(rom, 0x1C13A + k * 2)
        items.append(RomString("b0e_items", k, 0x1C000 + (ptr - 0x4000), None))
    off = 0x1C524
    idx = 0
    while off < 0x1C571:
        nxt = rom.index(0xFF, off) + 1
        items.append(RomString("b0e_battle", idx, off, None))
        off = nxt
        idx += 1
    for k in range(648):
        ptr = _read_u16(rom, 0x2397F + k * 2)
        items.append(RomString("b11_dialogue", k, 0x1C000 + (ptr - 0x4000), None))

    # B$11 $BE8F..$BF24 (23 Title / Ending credit labels & names rendered with BG[34] loaded at $1200)
    off = 0x23E8F
    idx = 0
    while off < 0x23F25:
        nxt = rom.index(0xFF, off) + 1
        items.append(RomString("b11_bg34_credits", idx, off, None, bg34=True))
        off = nxt
        idx += 1
    items.append(RomString("b11_ending_nar", 0, 0x23F25, None))
    items.append(RomString("b11_ending_nar", 1, 0x23F47, None))

    # 7. B$1B $DA3D ending staff names (41)
    for k in range(41):
        ptr = _read_u16(rom, 0x37A3D + k * 2)
        items.append(RomString("b1b_staff", k, 0x36000 + (ptr - 0xC000), None))

    return items
