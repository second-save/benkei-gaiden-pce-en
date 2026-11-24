"""ROM build entry point (identity and 1 MiB expanded identity builds)."""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import check_rom  # noqa: E402
import pce_gfx  # noqa: E402
import pce_text  # noqa: E402
import romdiff  # noqa: E402

ORIG_ROM = ROOT / "rom" / "Benkei Gaiden (Japan).pce"
EXP_SIZE = 0x100000


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
        end = off + len(data)
        if off < 0 or end > len(self.buf):
            raise ValueError(f"write out of bounds: {off:#x}..{end:#x} (len {len(self.buf):#x})")
        orig_slice = self.orig[off:min(end, len(self.orig))]
        if len(orig_slice) < len(data):
            orig_slice = orig_slice + b"\xff" * (len(data) - len(orig_slice))
        self.writes.append((off, orig_slice, bytes(data), writer))
        self.buf[off:end] = data

    def write_log(self, path: Path) -> None:
        write_writes_log(path, self.writes)


def assemble_bank(asm_path: Path, work_dir: Path) -> bytes:
    """Assemble one 8 KiB HuC6280 bank with `wla-huc6280` + `wlalink` and trim trailing `$FF` pad."""
    work_dir.mkdir(parents=True, exist_ok=True)
    stem = asm_path.stem
    obj_path = work_dir / f"{stem}.o"
    link_path = work_dir / f"{stem}.link"
    bin_path = work_dir / f"{stem}.bin"

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
    end = len(raw)
    while end > 0 and raw[end - 1] == 0xFF:
        end -= 1
    return raw[:end]


def _write_u16_le(buf: bytearray, off: int, val: int) -> None:
    buf[off] = val & 0xFF
    buf[off + 1] = (val >> 8) & 0xFF


def build_identity(orig: bytes) -> bytes:
    """Unpack every text string and compressed GFX stream, repack them with no edits, and assert exact identity."""
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


def _default_out(cmd: str, lang: str) -> Path:
    suffix = "" if lang == "en" else f"_{lang}"
    if cmd == "identity":
        return ROOT / "build" / f"benkei_identity{suffix}.pce"
    return ROOT / "build" / f"benkei_1m_identity{suffix}.pce"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", choices=("identity", "expand"), help="Build mode")
    ap.add_argument("--lang", default="en", help="Target language code (default: en)")
    ap.add_argument("--out", type=Path, default=None, help="Output .pce path")
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

    built, writes = build_expanded_identity(orig, ROOT / "work" / "asm")
    out_path.write_bytes(built)
    writes_path = out_path.parent / "writes.txt"
    write_writes_log(writes_path, writes)
    sha1 = hashlib.sha1(built).hexdigest()
    print(f"expand ok: {out_path} ({len(built)} B, {len(writes)} writes, sha1={sha1})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
