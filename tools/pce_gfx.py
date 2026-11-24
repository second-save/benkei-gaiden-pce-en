"""BG ($D4A9) and Sprite ($D62A) decompressor, exact optimal compressor, and PNG renderer."""
from __future__ import annotations

import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

BG_EXCEPTIONS = frozenset({0x02, 0x0A, 0x0B, 0x0E, 0x10, 0x12, 0x19, 0x1A, 0x1C, 0x1D, 0x1E, 0x1F})
SPR_EXCEPTIONS = frozenset({0x00, 0x0B, 0x0F, 0x13, 0x15, 0x16, 0x17})
BG_COUNT = 36
SPR_COUNT = 25
# BG[25]: 1 equal-length Mode 0/1 tie in original; BG[29]: original has 1 suboptimal literal (-1B here);
# BG[31..32]: unused placeholder table slots. Every active text/signage/font BG & all 25 SPR recompress bit-exactly.
NON_EXACT_BG = frozenset({25, 29, 31, 32})

BG_X_END = {2: 0x01, 4: 0x10, 8: 0x11}
SPR_X_END = {2: 0x20, 4: 0x40, 8: 0x60}


@dataclass(frozen=True)
class GfxAsset:
    kind: str  # "bg" or "spr"
    idx: int
    count: int
    extra: int  # vram_word for BG, unkx for SPR
    offset: int
    did: int
    bpp: int
    x_end: int


def bg_meta(rom: bytes, idx: int) -> GfxAsset:
    """Read BG table ($05400) and pointer table ($14934) metadata for entry `idx`."""
    cnt_raw, vram_hi, did, bpp = rom[0x05400 + idx * 4 : 0x05404 + idx * 4]
    count = 256 if cnt_raw == 0 else cnt_raw
    ptr = rom[0x14934 + did * 2] | (rom[0x14934 + did * 2 + 1] << 8)
    bank = (ptr >> 13) + 0x48
    bank = (bank - 0x45) if did in BG_EXCEPTIONS else (0x20 + (bank & 0x0F))
    return GfxAsset("bg", idx, count, vram_hi << 8, bank * 0x2000 + (ptr & 0x1FFF), did, bpp, BG_X_END.get(bpp, 0x20))


def spr_meta(rom: bytes, idx: int) -> GfxAsset:
    """Read Sprite table ($055C6) and pointer table ($1C000) metadata for entry `idx`."""
    cnt_raw, unkx, did, bpp = rom[0x055C6 + idx * 4 : 0x055CA + idx * 4]
    count = 256 if cnt_raw == 0 else cnt_raw
    ptr = rom[0x1C000 + did * 2] | (rom[0x1C000 + did * 2 + 1] << 8)
    bank = (ptr >> 13) + 0x40
    bank = (bank - 0x3D) if did in SPR_EXCEPTIONS else (0x20 + (bank & 0x0F))
    return GfxAsset("spr", idx, count, unkx, bank * 0x2000 + (ptr & 0x1FFF), did, bpp, SPR_X_END.get(bpp, 0x80))


def _step_x(x: int) -> int:
    return (x - 0x0F) if (x & 1) == 0 else (x - 1)


def decompress_stream(
    rom: bytes | bytearray,
    pos: int,
    count: int,
    item_size: int,
    x_end: int,
) -> tuple[list[bytes], int]:
    """Decompress `count` BG (32B) or Sprite (128B) items from `rom[pos:]` and return `(items, consumed_bytes)`."""
    start = pos
    out: list[bytes] = []
    val = 0
    for _ in range(count):
        buf = bytearray(item_size)
        x = 0
        while x != x_end:
            hdr = rom[pos]
            pos += 1
            carry = (hdr & 0x80) != 0
            a = (hdr & 0x7F) | 0x80
            if not carry:
                while True:
                    c = (a & 0x80) != 0
                    a = (a << 1) & 0xFF
                    if c:
                        val = rom[pos]
                        pos += 1
                    buf[x] = val
                    x += 2
                    if (x & 0x0E) == 0:
                        break
            else:
                cnt = 8
                while True:
                    c = (a & 0x80) != 0
                    a = (a << 1) & 0xFF
                    if c:
                        val = rom[pos]
                        pos += 1
                    b = val
                    while True:
                        b <<= 1
                        bit = (b >> 8) & 1
                        b &= 0xFF
                        buf[x] = ((buf[x] << 1) | bit) & 0xFF
                        x += 2
                        if (x & 0x0E) == 0:
                            break
                    cnt -= 1
                    if cnt == 0:
                        break
                    x = (x - 0x10) & 0xFF
            x = _step_x(x)
        out.append(bytes(buf))
    return out, pos - start


def compress_slice(s: list[int]) -> bytes:
    """Encode an 8-byte bitplane slice using the shorter of Mode 0 (row RLE) or Mode 1 (bit-transposed RLE)."""
    hdr0 = 0
    lit0 = [s[0]]
    for k in range(1, 8):
        if s[k] != s[k - 1]:
            hdr0 |= 1 << (7 - k)
            lit0.append(s[k])
    out0 = bytes([hdr0, *lit0])

    t = [sum(((s[r] >> (7 - c)) & 1) << (7 - r) for r in range(8)) for c in range(8)]
    hdr1 = 0x80
    lit1 = [t[0]]
    for k in range(1, 8):
        if t[k] != t[k - 1]:
            hdr1 |= 1 << (7 - k)
            lit1.append(t[k])
    out1 = bytes([hdr1, *lit1])
    return out0 if len(out0) <= len(out1) else out1


def compress_stream(items: list[bytes], x_end: int) -> bytes:
    """Recompress BG or Sprite planar buffers matching the exact slice order of `$D4A9`/`$D62A`."""
    out = bytearray()
    for buf in items:
        x = 0
        while x != x_end:
            out.extend(compress_slice([buf[x + 2 * k] for k in range(8)]))
            x = _step_x(x + 16)
    return bytes(out)


def decompress_bg(rom: bytes, idx: int) -> list[bytes]:
    m = bg_meta(rom, idx)
    return decompress_stream(rom, m.offset, m.count, 32, m.x_end)[0]


def compress_bg(tiles: list[bytes], bpp: int) -> bytes:
    return compress_stream(tiles, BG_X_END.get(bpp, 0x20))


def decompress_spr(rom: bytes, idx: int) -> list[bytes]:
    m = spr_meta(rom, idx)
    return decompress_stream(rom, m.offset, m.count, 128, m.x_end)[0]


def compress_spr(pats: list[bytes], bpp: int) -> bytes:
    return compress_stream(pats, SPR_X_END.get(bpp, 0x80))


def write_png(path: Path, w: int, h: int, rgb: bytes) -> None:
    """Write an RGB888 PNG without external dependencies."""
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    rows = b"".join(b"\x00" + rgb[y * w * 3 : (y + 1) * w * 3] for y in range(h))
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b"")
    path.write_bytes(png)


def render_bg_4bpp_grid(tiles: list[bytes], cols: int = 16) -> tuple[int, int, bytes]:
    """Render decoded 8x8 PCE BG tiles into a grayscale RGB buffer."""
    rows = max(1, (len(tiles) + cols - 1) // cols)
    w, h = cols * 8, rows * 8
    buf = bytearray(w * h * 3)
    for idx, t in enumerate(tiles):
        tx, ty = (idx % cols) * 8, (idx // cols) * 8
        for py in range(8):
            p0, p1, p2, p3 = t[py * 2], t[py * 2 + 1], t[16 + py * 2], t[16 + py * 2 + 1]
            for px in range(8):
                sh = 7 - px
                c = ((p0 >> sh) & 1) | (((p1 >> sh) & 1) << 1) | (((p2 >> sh) & 1) << 2) | (((p3 >> sh) & 1) << 3)
                g = c * 17
                o = ((ty + py) * w + tx + px) * 3
                buf[o : o + 3] = bytes((g, g, g))
    return w, h, bytes(buf)


def render_spr_4bpp_grid(pats: list[bytes], cols: int = 8) -> tuple[int, int, bytes]:
    """Render decoded 16x16 PCE Sprite patterns into a grayscale RGB buffer."""
    rows = max(1, (len(pats) + cols - 1) // cols)
    w, h = cols * 16, rows * 16
    buf = bytearray(w * h * 3)
    for idx, s in enumerate(pats):
        sx, sy = (idx % cols) * 16, (idx // cols) * 16
        for py in range(16):
            for half in range(2):
                bo = py * 2 + (1 - half)
                p0, p1, p2, p3 = s[bo], s[32 + bo], s[64 + bo], s[96 + bo]
                for px in range(8):
                    sh = 7 - px
                    c = ((p0 >> sh) & 1) | (((p1 >> sh) & 1) << 1) | (((p2 >> sh) & 1) << 2) | (((p3 >> sh) & 1) << 3)
                    g = c * 17
                    o = ((sy + py) * w + sx + half * 8 + px) * 3
                    buf[o : o + 3] = bytes((g, g, g))
    return w, h, bytes(buf)
