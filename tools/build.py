"""ROM build entry point (identity, 1 MiB expanded identity, marker, and translated builds)."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import check_rom  # noqa: E402
import font_en  # noqa: E402
import pce_gfx  # noqa: E402
import pce_text  # noqa: E402
import romdiff  # noqa: E402

ORIG_ROM = ROOT / "rom" / "Benkei Gaiden (Japan).pce"
EXP_SIZE = 0x100000
FAR_BANK_FIRST = 0x61
FAR_BANK_LAST = 0x7E

SYM_LABEL_RE = re.compile(r"^[0-9A-Fa-f]{2}:([0-9A-Fa-f]{4})\s+(\S+)$")


def write_writes_log(path: Path, writes: list[tuple[int, bytes, bytes, str]]) -> None:
    """Write a `romdiff.py --writes`-compatible mutation log."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"{off:X} {orig_b.hex()} {new_b.hex()} {by}\n" for off, orig_b, new_b, by in writes]
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.writelines(lines)


class RomBuilder:
    """Tracks every ROM mutation against clean `orig` for `romdiff.py --writes` verification."""

    def __init__(self, orig: bytes, size: int) -> None:
        if size < len(orig):
            raise ValueError(f"target size {size} < orig {len(orig)}")
        self.orig = orig
        self.buf = bytearray(orig) + bytearray([0xFF] * (size - len(orig)))
        self.writes: list[tuple[int, bytes, bytes, str]] = []

    def put(self, off: int, data: bytes, writer: str) -> None:
        """Write `data` at ROM offset `off` and record original vs new slice."""
        end = off + len(data)
        if off < 0 or end > len(self.buf):
            raise ValueError(f"write out of bounds: {off:#x}..{end:#x} (len {len(self.buf):#x})")
        orig_slice = self.orig[off:min(end, len(self.orig))]
        if len(orig_slice) < len(data):
            orig_slice = orig_slice + b"\xff" * (len(data) - len(orig_slice))
        self.writes.append((off, orig_slice, bytes(data), writer))
        self.buf[off:end] = data

    def patch_assert(self, off: int, expected: bytes, repl: bytes, writer: str) -> None:
        """Assert exact original bytes at `off` before replacing them with equal-length `repl`."""
        if len(expected) != len(repl):
            raise ValueError(f"{writer}: replacement len {len(repl)} != expected {len(expected)}")
        actual = self.orig[off : off + len(expected)]
        if actual != expected:
            raise AssertionError(
                f"{writer} at {off:#x}: expected {expected.hex(' ')}, got {actual.hex(' ')}"
            )
        self.put(off, repl, writer)

    def write_log(self, path: Path) -> None:
        write_writes_log(path, self.writes)


class FarPacker:
    """Packs translated text across expansion banks `$61..$7E` (`MPR2` `$4000..$5FFF` + `MPR3`)."""

    def __init__(self, first_bank: int = FAR_BANK_FIRST, last_bank: int = FAR_BANK_LAST) -> None:
        self.first_bank = first_bank
        self.last_bank = last_bank
        self.bank = first_bank
        self.cursor = 0
        self.banks: dict[int, bytearray] = {}

    def alloc(self, data: bytes) -> tuple[int, int]:
        """Allocate `data` (<= 8 KiB) spanning `MPR2` into `MPR3` if needed; return `(bank, cpu_addr)`."""
        n = len(data)
        if n > 0x2000:
            raise ValueError(f"far string exceeds 8 KiB ({n} B)")
        max_bytes = (self.last_bank - self.first_bank + 1) * 0x2000
        used_before = (self.bank - self.first_bank) * 0x2000 + self.cursor
        if used_before + n > max_bytes:
            raise OverflowError(f"far string banks ${self.first_bank:02X}..${self.last_bank:02X} full")

        start_bank = self.bank
        start_addr = 0x4000 + self.cursor

        first_part = min(n, 0x2000 - self.cursor)
        buf0 = self.banks.setdefault(start_bank, bytearray([0xFF] * 0x2000))
        buf0[self.cursor : self.cursor + first_part] = data[:first_part]
        if first_part < n:
            buf1 = self.banks.setdefault(start_bank + 1, bytearray([0xFF] * 0x2000))
            buf1[: n - first_part] = data[first_part:]

        pos = self.cursor + n
        self.bank += pos // 0x2000
        self.cursor = pos % 0x2000
        return start_bank, start_addr

    def flush(self, rb: RomBuilder) -> None:
        """Emit all non-empty far banks into `rb`."""
        for bank, buf in sorted(self.banks.items()):
            end = len(buf)
            while end > 0 and buf[end - 1] == 0xFF:
                end -= 1
            if end:
                rb.put(bank * 0x2000, bytes(buf[:end]), f"far_b{bank:02x}")


def _run_wla(asm_path: Path, work_dir: Path) -> tuple[bytes, dict[str, int]]:
    """Assemble one `.asm` bank via `wla-huc6280` + `wlalink` and return `(8 KiB raw, labels)`."""
    work_dir.mkdir(parents=True, exist_ok=True)
    stem = asm_path.stem
    obj_path = work_dir / f"{stem}.o"
    link_path = work_dir / f"{stem}.link"
    bin_path = work_dir / f"{stem}.bin"
    sym_path = work_dir / f"{stem}.sym"

    r1 = subprocess.run(
        ["wla-huc6280", "-o", str(obj_path), str(asm_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r1.returncode != 0:
        raise RuntimeError(f"wla-huc6280 failed on {asm_path}:\n{r1.stdout}\n{r1.stderr}")

    link_path.write_text(f"[objects]\n{obj_path.name}\n", encoding="utf-8", newline="\n")
    r2 = subprocess.run(
        ["wlalink", "-r", "-S", link_path.name, bin_path.name],
        cwd=work_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if r2.returncode != 0:
        raise RuntimeError(f"wlalink failed on {link_path}:\n{r2.stdout}\n{r2.stderr}")

    raw = bin_path.read_bytes()
    if len(raw) != 0x2000:
        raise RuntimeError(f"expected 8 KiB bank binary from {asm_path}, got {len(raw)} bytes")

    labels: dict[str, int] = {}
    in_labels = False
    for line in sym_path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith(";"):
            continue
        if s.startswith("["):
            in_labels = s == "[labels]"
            continue
        if in_labels:
            m = SYM_LABEL_RE.match(s)
            if m:
                labels[m.group(2)] = int(m.group(1), 16)
    return raw, labels


def _trim_ff(raw: bytes) -> bytes:
    end = len(raw)
    while end > 0 and raw[end - 1] == 0xFF:
        end -= 1
    return raw[:end]


def assemble_bank(asm_path: Path, work_dir: Path) -> bytes:
    """Assemble one 8 KiB HuC6280 bank and trim trailing `$FF` pad."""
    raw, _ = _run_wla(asm_path, work_dir)
    return _trim_ff(raw)


def assemble_section(asm_path: Path, work_dir: Path, org_off: int, max_len: int) -> tuple[bytes, dict[str, int]]:
    """Assemble a bank tail section from `org_off`, assert `<= max_len`, and return `(bytes, labels)`."""
    raw, labels = _run_wla(asm_path, work_dir)
    payload = _trim_ff(raw[org_off:])
    if not (0 < len(payload) <= max_len):
        raise RuntimeError(
            f"{asm_path.name} payload {len(payload)} B out of allowed range (1..{max_len})"
        )
    return payload, labels


def _write_u16_le(buf: bytearray, off: int, val: int) -> None:
    buf[off] = val & 0xFF
    buf[off + 1] = (val >> 8) & 0xFF


def _u16_le(val: int) -> bytes:
    return bytes((val & 0xFF, (val >> 8) & 0xFF))


def _stub4(bank: int, addr: int) -> bytes:
    return bytes((0xFC, bank, addr & 0xFF, (addr >> 8) & 0xFF))


def _stub5(bank: int, addr: int) -> bytes:
    return _stub4(bank, addr) + b"\xff"


def build_identity(orig: bytes) -> bytes:
    """Unpack every text string and compressed GFX stream, repack with no edits, and assert exact identity."""
    buf = bytearray(orig)
    codec = pce_text.PceCodec()
    entries = pce_text.iter_all_rom_strings(orig)

    by_group: dict[str, dict[int, pce_text.RomString]] = defaultdict(dict)
    by_offset: dict[int, tuple[int, bytes]] = {}
    end_by_group: dict[str, int] = defaultdict(int)

    for entry in entries:
        by_group[entry.group][entry.index] = entry
        txt, used = codec.decode(orig, entry.offset, length=entry.length, bg34=entry.bg34, preserve_toggles=True)
        enc = codec.encode(txt, bg34=entry.bg34)
        assert enc == orig[entry.offset : entry.offset + used], f"text re-encode mismatch at {entry}"
        end_by_group[entry.group] = max(end_by_group[entry.group], entry.offset + used)
        prev = by_offset.get(entry.offset)
        if prev is None or used > prev[0]:
            by_offset[entry.offset] = (used, enc)

    for off, (used, enc) in by_offset.items():
        buf[off : off + used] = enc

    for pt in pce_text.PTR_TABLES:
        grp = by_group[pt.group]
        for idx in range(pt.count):
            ptr_val = pt.cpu_base + (grp[idx].offset - pt.rom_base)
            _write_u16_le(buf, pt.ptr_offset + idx * 2, ptr_val)
        if pt.has_sentinel:
            sent_val = pt.cpu_base + (end_by_group[pt.group] - pt.rom_base)
            _write_u16_le(buf, pt.ptr_offset + pt.count * 2, sent_val)

    seen_gfx: set[tuple[str, int]] = set()
    for idx in range(pce_gfx.BG_COUNT):
        m = pce_gfx.bg_meta(orig, idx)
        tiles, orig_len = pce_gfx.decompress_stream(orig, m.offset, m.count, 32, m.x_end)
        comp = pce_gfx.compress_bg(tiles, m.bpp)
        redec, _ = pce_gfx.decompress_stream(comp, 0, m.count, 32, m.x_end)
        assert redec == tiles, f"BG[{idx}] lossless roundtrip mismatch"
        assert len(comp) <= orig_len, f"BG[{idx}] grew {len(comp)} > {orig_len}"
        key = ("bg", m.offset)
        if idx not in pce_gfx.NON_EXACT_BG and key not in seen_gfx:
            seen_gfx.add(key)
            assert comp == orig[m.offset : m.offset + orig_len], f"BG[{idx}] bit-exact mismatch"
            buf[m.offset : m.offset + orig_len] = comp

    for idx in range(pce_gfx.SPR_COUNT):
        m = pce_gfx.spr_meta(orig, idx)
        pats, orig_len = pce_gfx.decompress_stream(orig, m.offset, m.count, 128, m.x_end)
        comp = pce_gfx.compress_spr(pats, m.bpp)
        redec, _ = pce_gfx.decompress_stream(comp, 0, m.count, 128, m.x_end)
        assert redec == pats, f"SPR[{idx}] lossless roundtrip mismatch"
        key = ("spr", m.offset)
        if key not in seen_gfx:
            seen_gfx.add(key)
            assert comp == orig[m.offset : m.offset + orig_len], f"SPR[{idx}] bit-exact mismatch"
            buf[m.offset : m.offset + orig_len] = comp

    built = bytes(buf)
    assert built == orig, "identity rebuild does not match original ROM byte-for-byte"
    errs, _ = romdiff.check(orig, built, set(), [])
    assert not errs, f"identity romdiff failed: {errs}"
    return built


def build_expanded_identity(orig: bytes, work_dir: Path) -> tuple[bytes, list[tuple[int, bytes, bytes, str]]]:
    """Build 1 MiB expanded identity ROM ($40/$50 mirror + bank-$30 WLA payload) with write log."""
    base = build_identity(orig)
    rb = RomBuilder(orig, EXP_SIZE)
    rb.buf[: len(base)] = base

    upper = base[0x40000:0x60000]
    rb.put(0x80000, upper, "mirror_40_4f")
    rb.put(0xA0000, upper, "mirror_50_5f")

    payload = assemble_bank(ROOT / "asm" / "identity.asm", work_dir)
    rb.put(0x60000, payload, "asm_identity")

    built = bytes(rb.buf)
    errs, _ = romdiff.check(orig, built, set(), rb.writes)
    assert not errs, f"expanded identity romdiff failed: {errs}"
    return built, rb.writes


_MARKER_PREFIX = {
    "b02_sys": ("S", 2),
    "b0a_menus": ("M", 2),
    "b0a_locations": ("L", 2),
    "b0e_jutsu": ("J", 2),
    "b0e_items": ("I", 3),
    "b0e_battle": ("B", 2),
    "b11_dialogue": ("D", 3),
    "b11_bg34_credits": ("C", 2),
    "b11_ending_nar": ("N", 2),
    "b1b_staff": ("T", 2),
}


def _resolve_entry_text(
    group: str,
    entry: dict,
    *,
    mode: str,
    lang: str,
    qa_overrides: dict[str, str],
) -> str:
    eid = entry["id"]
    idx = entry["index"]
    is_enemy = group == "b0d_enemy_kanji"

    if eid in qa_overrides:
        txt = qa_overrides[eid]
        if not is_enemy and not txt.endswith("{end}"):
            txt += "{end}"
        return txt

    if mode == "marker":
        if is_enemy:
            return f"E{idx:03d}"
        prefix, width = _MARKER_PREFIX[group]
        return f"{prefix}{idx:0{width}d}{{end}}"

    txt = entry.get(lang, "")
    if not txt:
        raise ValueError(f"missing '{lang}' translation for {eid}")
    if not is_enemy and not txt.endswith("{end}"):
        raise ValueError(f"{eid} '{lang}' must end with {{end}}: {txt!r}")
    return txt


def build_patched(
    orig: bytes,
    script_dir: Path,
    work_dir: Path,
    *,
    mode: str = "marker",
    lang: str = "en",
    qa_overrides: dict[str, str] | None = None,
) -> tuple[bytes, list[tuple[int, bytes, bytes, str]]]:
    """Build 1 MiB expanded English ROM with 8x16 font, far-string hooks, and packed strings/markers."""
    if mode not in ("marker", "translate"):
        raise ValueError(f"unsupported build_patched mode: {mode!r}")

    overrides = dict(qa_overrides or {})
    codec = pce_text.EnCodec(lang=lang)
    rb = RomBuilder(orig, EXP_SIZE)

    # 1. Patch BG[01] 8x16 English font BEFORE mirroring $40/$50 so mirrored copies stay consistent.
    bg01_meta = pce_gfx.bg_meta(orig, 1)
    bg01_comp, bg01_orig_len = font_en.patch_bg01(orig)
    rb.put(bg01_meta.offset, bg01_comp, "font_bg01")
    if len(bg01_comp) < bg01_orig_len:
        rb.put(
            bg01_meta.offset + len(bg01_comp),
            b"\xff" * (bg01_orig_len - len(bg01_comp)),
            "font_bg01_pad",
        )

    upper = bytes(rb.buf[0x40000:0x60000])
    rb.put(0x80000, upper, "mirror_40_4f")
    rb.put(0xA0000, upper, "mirror_50_5f")

    rb.put(0x60000, assemble_bank(ROOT / "asm" / "identity.asm", work_dir), "asm_identity")

    # 2. Assemble far-string engine hooks into free tails of B$00 and B$02, and B$09 menu driver.
    b00_bin, b00_sym = assemble_section(ROOT / "asm" / "engine_b00.asm", work_dir, 0x1F90, 80)
    b02_bin, b02_sym = assemble_section(ROOT / "asm" / "engine_b02.asm", work_dir, 0x1FBC, 68)
    b09_raw, b09_sym = _run_wla(ROOT / "asm" / "engine_b09.asm", work_dir)
    if (b09_sym.get("Menu2_Run"), b09_sym.get("Menu4_Run"), b09_sym.get("ClearCursor4")) != (
        0xD28E,
        0xD2BD,
        0xD35D,
    ):
        raise RuntimeError(f"unexpected engine_b09 symbols: {b09_sym}")
    rb.put(0x01F90, b00_bin, "asm_engine_b00")
    rb.put(0x05FBC, b02_bin, "asm_engine_b02")
    rb.put(0x1328E, b09_raw[0x128E:0x139B], "asm_engine_b09")

    # 3. Install verified code/layout hook patches.
    rb.patch_assert(
        0x04E48,
        bytes.fromhex("a6 00 a4 01"),
        b"\x20" + _u16_le(b02_sym["Hook_CE45"]) + b"\xea",
        "hook_ce45",
    )
    rb.patch_assert(
        0x04F32,
        bytes.fromhex("a6 87 a4 88"),
        b"\x20" + _u16_le(b02_sym["Hook_CF27"]) + b"\xea",
        "hook_cf27",
    )
    rb.patch_assert(
        0x04FFA,
        bytes.fromhex("20 c0 e2"),
        b"\x20" + _u16_le(b00_sym["SafeWait_E2C0"]),
        "hook_safewait_e2c0",
    )
    rb.patch_assert(
        0x050A3,
        bytes.fromhex("20 33 ef"),
        b"\x20" + _u16_le(b00_sym["SafeWait_EF33"]),
        "hook_safewait_ef33",
    )
    rb.patch_assert(
        0x01915,
        bytes.fromhex("a6 dc c2 b1 d8 9d 00 2e e8 c8 c9 ff d0 f5 86 dc"),
        b"\x20" + _u16_le(b00_sym["Hook_F915"]) + b"\xea" * 13,
        "hook_f915",
    )
    rb.patch_assert(0x0596D, bytes.fromhex("a2 3e a0"), bytes.fromhex("68 80 0f"), "skip_enemy_kana")
    rb.patch_assert(
        0x059D3,
        bytes.fromhex("98 0a a8"),
        b"\x20" + _u16_le(b02_sym["Hook_EnemyBank"]),
        "hook_enemy_bank",
    )
    rb.patch_assert(
        0x059D6,
        bytes.fromhex("b9 06 ba 85 d8 b9 07 ba 85 d9 b9 08 ba"),
        bytes.fromhex("b9 00 a0 85 d8 b9 01 a0 85 d9 b9 02 a0"),
        "hook_enemy_ptrs",
    )
    # 3b. Horizontal Title / Continue / BRAM menu frames, cursor coords, and B$0A spec rows.
    rb.patch_assert(0x12FBC, bytes.fromhex("03 0a 06 09"), bytes.fromhex("00 0c 0c 06"), "title_menu_box")
    rb.patch_assert(0x12FC9, bytes.fromhex("a0 0c"), bytes.fromhex("a0 0d"), "title_menu_cur_y")
    rb.patch_assert(0x12FE6, bytes.fromhex("03 09 06 0d"), bytes.fromhex("00 0c 0c 06"), "cont_menu_box")
    rb.patch_assert(0x12FEF, bytes.fromhex("a0 0b"), bytes.fromhex("a0 0d"), "cont_menu_cur_y")
    rb.patch_assert(0x13061, bytes.fromhex("02 05 06 15"), bytes.fromhex("00 07 0c 0a"), "bram_menu_box")
    rb.patch_assert(0x1306F, bytes.fromhex("a2 03 a0 07"), bytes.fromhex("a2 01 a0 08"), "bram_menu_cur_xy")
    rb.patch_assert(0x151AF, bytes.fromhex("04 0e 22 02"), bytes.fromhex("03 0d 22 02"), "b0a_title_rows")
    rb.patch_assert(0x151B3, bytes.fromhex("04 0d 26 04"), bytes.fromhex("03 0d 26 02"), "b0a_cont_rows")
    rb.patch_assert(0x151BB, bytes.fromhex("03 09 2e 07"), bytes.fromhex("03 08 10 04"), "b0a_bram_rows")
    # 3c. Shop Sen box (+3 col label so "Sen" fits cleanly before right-aligned amount).
    rb.patch_assert(0x02CFE, bytes.fromhex("1a 1a"), bytes.fromhex("1a ea"), "shop_sen_x")
    rb.patch_assert(
        0x02D0E,
        bytes.fromhex("e6 11 e6 11"),
        b"\x20" + _u16_le(b00_sym["Inc11By3"]) + b"\xea",
        "shop_sen_adv3",
    )
    rb.patch_assert(0x02D24, bytes.fromhex("af"), bytes.fromhex("b0"), "shop_sen_num_off")

    # 4. Load extracted script groups and encode/pack strings.
    manifest = json.loads((script_dir / "manifest.json").read_text(encoding="utf-8"))
    groups = {
        g: json.loads((script_dir / info["file"]).read_text(encoding="utf-8"))["entries"]
        for g, info in manifest["groups"].items()
    }

    far = FarPacker()
    b11_tail_base = 0x23F93
    b11_tail_buf = bytearray()

    def alloc_b11_tail(stub: bytes) -> int:
        off = b11_tail_base + len(b11_tail_buf)
        b11_tail_buf.extend(stub)
        if b11_tail_base + len(b11_tail_buf) > 0x24000:
            raise OverflowError("B$11 free tail ($BF93..$BFFF, 109 B) exhausted")
        return 0x4000 + (off - 0x1C000)

    # 4a. b0d_enemy_kanji -> Bank $60 ($A000..$BFFF), NO $FF terminators.
    ptrs60 = bytearray()
    strs60 = bytearray()
    base60 = 0xA000 + (112 + 1) * 2
    for e in groups["b0d_enemy_kanji"]:
        ptrs60.extend(_u16_le(base60 + len(strs60)))
        if e["status"] in ("todo", "done"):
            txt = _resolve_entry_text("b0d_enemy_kanji", e, mode=mode, lang=lang, qa_overrides=overrides)
            strs60.extend(codec.encode(txt))
    ptrs60.extend(_u16_le(base60 + len(strs60)))
    bank60 = bytes(ptrs60 + strs60)
    if len(bank60) > 0x2000:
        raise OverflowError(f"Bank $60 enemies overflowed 8 KiB ({len(bank60)} B)")
    rb.put(0xC0000, bank60, "bank60_enemies")

    # 4b. b02_sys (+ mid-string ref at 0x05EE1).
    for e in groups["b02_sys"]:
        if e["status"] not in ("todo", "done"):
            continue
        txt = _resolve_entry_text("b02_sys", e, mode=mode, lang=lang, qa_overrides=overrides)
        bk, ad = far.alloc(codec.encode(txt))
        stub = _stub4(bk, ad)
        off = int(e["offset"], 16)
        if e["raw_len"] >= 4:
            rb.put(off, stub, f"stub_{e['id']}")
        else:
            if not e["slots"]:
                raise ValueError(f"short b02_sys entry {e['id']} has no repointable slots")
            tail_cpu = alloc_b11_tail(stub)
            orig_cpu = _u16_le(0xC000 + (off - 0x04000))
            new_cpu = _u16_le(tail_cpu)
            for s in e["slots"]:
                rb.patch_assert(int(s["slot"], 16), orig_cpu, new_cpu, f"repoint_{e['id']}")

        if e["index"] == 26:
            mid_txt = (
                overrides.get("b02_sys_026_mid")
                or (e.get(f"{lang}_mid", e.get("en_mid", "")) if mode == "translate" else "")
                or ("S26M{end}" if mode == "marker" else "")
            )
            if not mid_txt and mode == "translate":
                raise ValueError("missing 'b02_sys_026_mid' MP label for translate mode")
            if not mid_txt.endswith("{end}"):
                mid_txt += "{end}"
            mbk, mad = far.alloc(codec.encode(mid_txt))
            rb.put(0x05EE1, _stub4(mbk, mad), "stub_b02_sys_026_mid")

    # 4c. b0a_menus[4..30] (preserve 0..3 name-entry grid & 26 empty spacer).
    menus_ptr_low = bytearray()
    menus_stub_low = bytearray()
    menus_ptr_high = bytearray()
    menus_stub_high = bytearray()
    for e in groups["b0a_menus"]:
        idx = e["index"]
        if idx < 4 or idx == 26:
            continue
        if e["status"] not in ("todo", "done"):
            raise ValueError(f"unexpected status on b0a_menus[{idx}]: {e['status']}")
        if mode == "translate" and 21 <= idx <= 29 and not e.get(lang, "") and e["id"] not in overrides:
            txt = "{end}"
        else:
            txt = _resolve_entry_text("b0a_menus", e, mode=mode, lang=lang, qa_overrides=overrides)
        bk, ad = far.alloc(codec.encode(txt))
        s5 = _stub5(bk, ad)
        if idx < 26:
            cpu = 0x4000 + (0x150E9 + len(menus_stub_low) - 0x14000)
            menus_stub_low.extend(s5)
            menus_ptr_low.extend(_u16_le(cpu))
        else:
            cpu = 0x4000 + (0x15194 + len(menus_stub_high) - 0x14000)
            menus_stub_high.extend(s5)
            menus_ptr_high.extend(_u16_le(cpu))
    assert 0x150E9 + len(menus_stub_low) <= 0x15193
    assert 0x15194 + len(menus_stub_high) <= 0x151AF
    rb.put(0x15066, bytes(menus_ptr_low), "ptrs_b0a_menus_low")
    rb.put(0x150E9, bytes(menus_stub_low), "stubs_b0a_menus_low")
    rb.put(0x15094, bytes(menus_ptr_high), "ptrs_b0a_menus_high")
    rb.put(0x15194, bytes(menus_stub_high), "stubs_b0a_menus_high")

    # 4d. b0a_locations (13 sequential 5-byte stubs).
    loc_ptrs = bytearray()
    loc_stubs = bytearray()
    for e in groups["b0a_locations"]:
        txt = _resolve_entry_text("b0a_locations", e, mode=mode, lang=lang, qa_overrides=overrides)
        bk, ad = far.alloc(codec.encode(txt))
        cpu = 0x4000 + (0x15282 + len(loc_stubs) - 0x14000)
        loc_stubs.extend(_stub5(bk, ad))
        loc_ptrs.extend(_u16_le(cpu))
    assert 0x15282 + len(loc_stubs) <= 0x152C9
    rb.put(0x15268, bytes(loc_ptrs), "ptrs_b0a_locations")
    rb.put(0x15282, bytes(loc_stubs), "stubs_b0a_locations")

    # 4e. In-place 4-byte stub groups in B$0E/$11.
    for g in ("b0e_jutsu", "b0e_items", "b11_bg34_credits", "b11_ending_nar"):
        for e in groups[g]:
            if e["status"] not in ("todo", "done"):
                continue
            txt = _resolve_entry_text(g, e, mode=mode, lang=lang, qa_overrides=overrides)
            bk, ad = far.alloc(codec.encode(txt))
            rb.put(int(e["offset"], 16), _stub4(bk, ad), f"stub_{e['id']}")

    # 4f. b0e_battle (index 6 fits 2 B in-place; indices 8 & 10 repointed to B$11 free tail).
    for e in groups["b0e_battle"]:
        if e["status"] not in ("todo", "done"):
            continue
        idx = e["index"]
        off = int(e["offset"], 16)
        if idx == 6:
            if "b0e_battle_006_1C542" in overrides or mode == "translate":
                txt = (
                    overrides["b0e_battle_006_1C542"]
                    if "b0e_battle_006_1C542" in overrides
                    else e.get(lang, "")
                )
                if not txt.endswith("{end}"):
                    txt += "{end}"
                enc = codec.encode(txt)
                if len(enc) != 2:
                    raise ValueError(f"b0e_battle[6] must encode to 2 bytes, got {len(enc)}")
                rb.put(off, enc, "b0e_battle_006")
            continue
        txt = _resolve_entry_text("b0e_battle", e, mode=mode, lang=lang, qa_overrides=overrides)
        bk, ad = far.alloc(codec.encode(txt))
        stub = _stub4(bk, ad)
        if e["raw_len"] >= 4:
            rb.put(off, stub, f"stub_{e['id']}")
        elif idx == 8:
            tail_cpu = alloc_b11_tail(stub)
            rb.patch_assert(
                0x11B65,
                bytes.fromhex("a2 46 a0 45"),
                bytes((0xA2, tail_cpu & 0xFF, 0xA0, (tail_cpu >> 8) & 0xFF)),
                "repoint_b0e_battle_8",
            )
        elif idx == 10:
            tail_cpu = alloc_b11_tail(stub)
            repl = bytes((0xA2, tail_cpu & 0xFF, 0xA0, (tail_cpu >> 8) & 0xFF))
            for slot_off in (0x0313B, 0x11A4B, 0x11A7B, 0x11B7F):
                rb.patch_assert(slot_off, bytes.fromhex("a2 56 a0 45"), repl, f"repoint_b0e_battle_10_{slot_off:x}")
        else:
            raise ValueError(f"unexpected short b0e_battle entry {e['id']}")

    # 4g. b11_dialogue (646 in-place 5-byte stubs; 2 short entries -> B$11 free tail + ptr update).
    for e in groups["b11_dialogue"]:
        if e["status"] not in ("todo", "done"):
            continue
        txt = _resolve_entry_text("b11_dialogue", e, mode=mode, lang=lang, qa_overrides=overrides)
        bk, ad = far.alloc(codec.encode(txt))
        s5 = _stub5(bk, ad)
        off = int(e["offset"], 16)
        if e["raw_len"] >= 5:
            rb.put(off, s5, f"stub_{e['id']}")
        else:
            tail_cpu = alloc_b11_tail(s5)
            rb.put(0x2397F + e["index"] * 2, _u16_le(tail_cpu), f"ptr_{e['id']}")

    # 4h. b1b_staff (40 sequential 5-byte stubs leaving [40] $FF sentinel intact).
    staff_ptrs = bytearray()
    staff_stubs = bytearray()
    for e in groups["b1b_staff"]:
        if e["status"] not in ("todo", "done"):
            continue
        txt = _resolve_entry_text("b1b_staff", e, mode=mode, lang=lang, qa_overrides=overrides)
        bk, ad = far.alloc(codec.encode(txt))
        cpu = 0xC000 + (0x37A8F + len(staff_stubs) - 0x36000)
        staff_stubs.extend(_stub5(bk, ad))
        staff_ptrs.extend(_u16_le(cpu))
    assert 0x37A8F + len(staff_stubs) <= 0x37C2C
    rb.put(0x37A3D, bytes(staff_ptrs), "ptrs_b1b_staff")
    rb.put(0x37A8F, bytes(staff_stubs), "stubs_b1b_staff")

    # 5. Flush B$11 tail stubs and far string banks, then validate every byte with romdiff.
    if b11_tail_buf:
        rb.put(b11_tail_base, bytes(b11_tail_buf), "b11_tail_stubs")
    far.flush(rb)

    built = bytes(rb.buf)
    errs, _ = romdiff.check(orig, built, set(), rb.writes)
    assert not errs, "build_patched romdiff failed:\n" + "\n".join(errs[:20])
    return built, rb.writes


def _parse_qa_overrides(items: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in items:
        key, sep, val = item.partition("=")
        if not sep or not key:
            raise SystemExit(f"--qa expects ID=TEXT, got {item!r}")
        out[key] = val
    return out


def _default_out(cmd: str, lang: str) -> Path:
    suffix = "" if lang == "en" else f"_{lang}"
    if cmd == "identity":
        return ROOT / "build" / f"benkei_identity{suffix}.pce"
    if cmd == "expand":
        return ROOT / "build" / f"benkei_1m_identity{suffix}.pce"
    if cmd == "marker":
        return ROOT / "build" / f"benkei_marker{suffix}.pce"
    return ROOT / "build" / f"benkei_{lang}.pce"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=("identity", "expand", "marker", "translate"), help="Build mode")
    ap.add_argument("--lang", default="en", help="Target language code (default: en)")
    ap.add_argument("--out", type=Path, default=None, help="Output .pce path")
    ap.add_argument("--qa", action="append", default=[], metavar="ID=TEXT", help="Override string by ID")
    args = ap.parse_args()

    check_rom.check()
    orig = ORIG_ROM.read_bytes()
    out_path = args.out or _default_out(args.cmd, args.lang)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.cmd == "identity":
        built = build_identity(orig)
        out_path.write_bytes(built)
        sha1 = hashlib.sha1(built).hexdigest()
        print(f"identity ok: {out_path} ({len(built)} B, sha1={sha1})")
        return 0

    work_dir = ROOT / "work" / "asm"
    if args.cmd == "expand":
        built, writes = build_expanded_identity(orig, work_dir)
    else:
        qa = _parse_qa_overrides(args.qa)
        built, writes = build_patched(
            orig,
            ROOT / "script",
            work_dir,
            mode=args.cmd,
            lang=args.lang,
            qa_overrides=qa,
        )

    out_path.write_bytes(built)
    writes_path = out_path.parent / "writes.txt"
    write_writes_log(writes_path, writes)
    sha1 = hashlib.sha1(built).hexdigest()
    print(f"{args.cmd} ok: {out_path} ({len(built)} B, {len(writes)} writes, sha1={sha1})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
