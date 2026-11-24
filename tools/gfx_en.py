"""Deterministic English pixel-art replacements for all 5 tile-drawn JP graphics."""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import pce_gfx  # noqa: E402

# Crisp proportional pixel fonts for BG[23] tagline and BG[15]/BG[16] shop plaques.
FONT_5X7: dict[str, tuple[str, ...]] = {
    "A": (".##.", "#..#", "#..#", "####", "#..#", "#..#", "#..#"),
    "C": (".###", "#...", "#...", "#...", "#...", "#...", ".###"),
    "D": ("###.", "#..#", "#..#", "#..#", "#..#", "#..#", "###."),
    "E": ("####", "#...", "#...", "###.", "#...", "#...", "####"),
    "F": ("####", "#...", "#...", "###.", "#...", "#...", "#..."),
    "I": ("###", ".#.", ".#.", ".#.", ".#.", ".#.", "###"),
    "M": ("#...#", "##.##", "#.#.#", "#...#", "#...#", "#...#", "#...#"),
    "N": ("#..#", "##.#", "#.##", "#..#", "#..#", "#..#", "#..#"),
    "O": (".##.", "#..#", "#..#", "#..#", "#..#", "#..#", ".##."),
    "R": ("###.", "#..#", "#..#", "###.", "#.#.", "#..#", "#..#"),
    "S": (".###", "#...", "#...", ".##.", "...#", "...#", "###."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#..#", "#..#", "#..#", "#..#", "#..#", "#..#", ".##."),
    "-": ("...", "...", "...", "###", "...", "...", "..."),
    " ": ("..", "..", "..", "..", "..", "..", ".."),
}

SIGN_FONT_3X7: dict[str, tuple[str, ...]] = {
    "A": (".#.", "#.#", "#.#", "###", "#.#", "#.#", "#.#"),
    "I": ("#", "#", "#", "#", "#", "#", "#"),
    "K": ("#..#", "#.#.", "##..", "##..", "#.#.", "#..#", "#..#"),
    "N": ("#.#", "##.", "###", ".##", "#.#", "#.#", "#.#"),
    "Y": ("#.#", "#.#", "#.#", ".#.", ".#.", ".#.", ".#."),
}

SIGN_FONT_N4: dict[str, tuple[str, ...]] = {
    "N": ("#..#", "##.#", "#.##", "#..#", "#..#", "#..#", "#..#"),
}

SIGN_FONT_5: dict[str, tuple[str, ...]] = {
    "A": (".###.", "##.##", "#####", "#...#", "#...#"),
    "E": ("###", "#..", "###", "#..", "###"),
    "I": ("###", ".#.", ".#.", ".#.", "###"),
    "M": ("#...#", "##.##", "#.#.#", "#...#", "#...#"),
    "n": ("###", "#.#", "#.#", "#.#", "#.#"),
    "P": ("###", "#.#", "###", "#..", "#.."),
    "R": ("###", "#.#", "##.", "#.#", "#.#"),
    "T": ("#####", "..#..", "..#..", "..#..", "..#.."),
    "W": ("#...#", "#...#", "#.#.#", "##.##", ".#.#."),
}

BG23_TAGLINE_TILES: tuple[int, ...] = (
    0x0C, 0x0D, 0x0E, 0x10, 0x1B, 0x1C, 0x1D, 0x1E, 0x1F,
    0x2E, 0x2F, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35,
)
BG23_UNUSED_CLEAR: tuple[int, ...] = tuple(range(0x36, 0x41))


def _bg_px_grid(tiles: list[bytes], grid: list[list[int]]) -> list[list[int]]:
    h = len(grid) * 8
    w = len(grid[0]) * 8
    out = [[0] * w for _ in range(h)]
    for gr, row_ids in enumerate(grid):
        for gc, tid in enumerate(row_ids):
            t = tiles[tid]
            for py in range(8):
                p0, p1, p2, p3 = t[py * 2], t[py * 2 + 1], t[16 + py * 2], t[16 + py * 2 + 1]
                for px in range(8):
                    sh = 7 - px
                    c = ((p0 >> sh) & 1) | (((p1 >> sh) & 1) << 1) | (((p2 >> sh) & 1) << 2) | (((p3 >> sh) & 1) << 3)
                    out[gr * 8 + py][gc * 8 + px] = c
    return out


def _encode_bg_tile(px_rows: list[list[int]], x0: int, y0: int) -> bytes:
    buf = bytearray(32)
    for py in range(8):
        p0 = p1 = p2 = p3 = 0
        for px in range(8):
            c = px_rows[y0 + py][x0 + px]
            sh = 7 - px
            p0 |= ((c >> 0) & 1) << sh
            p1 |= ((c >> 1) & 1) << sh
            p2 |= ((c >> 2) & 1) << sh
            p3 |= ((c >> 3) & 1) << sh
        buf[py * 2] = p0
        buf[py * 2 + 1] = p1
        buf[16 + py * 2] = p2
        buf[16 + py * 2 + 1] = p3
    return bytes(buf)


def _set_bg_grid(tiles: list[bytes], grid: list[list[int]], canvas: list[list[int]]) -> None:
    for gr, row_ids in enumerate(grid):
        for gc, tid in enumerate(row_ids):
            tiles[tid] = _encode_bg_tile(canvas, gc * 8, gr * 8)


def _encode_spr_pat(px_rows: list[list[int]], x0: int, y0: int) -> bytes:
    buf = bytearray(128)
    for py in range(16):
        for half in range(2):
            bo = py * 2 + (1 - half)
            p0 = p1 = p2 = p3 = 0
            for px in range(8):
                c = px_rows[y0 + py][x0 + half * 8 + px]
                sh = 7 - px
                p0 |= ((c >> 0) & 1) << sh
                p1 |= ((c >> 1) & 1) << sh
                p2 |= ((c >> 2) & 1) << sh
                p3 |= ((c >> 3) & 1) << sh
            buf[bo] = p0
            buf[32 + bo] = p1
            buf[64 + bo] = p2
            buf[96 + bo] = p3
    return bytes(buf)


def _draw_glyph(
    canvas: list[list[int]],
    glyph: tuple[str, ...],
    x: int,
    y: int,
    color: int,
) -> int:
    for gy, row in enumerate(glyph):
        for gx, ch in enumerate(row):
            if ch != ".":
                canvas[y + gy][x + gx] = color
    return len(glyph[0])


def _draw_text(
    canvas: list[list[int]],
    text: str,
    font: dict[str, tuple[str, ...]],
    x: int,
    y: int,
    color: int,
    spacing: int = 1,
) -> None:
    cx = x
    for ch in text:
        g = font[ch]
        w = _draw_glyph(canvas, g, cx, y, color)
        cx += w + spacing


def _text_width(text: str, font: dict[str, tuple[str, ...]], spacing: int = 1) -> int:
    if not text:
        return 0
    return sum(len(font[ch][0]) for ch in text) + spacing * (len(text) - 1)


def _clear_wood_sign(canvas: list[list[int]], width: int) -> None:
    """Keep authentic frame (outer 3px left, 2px right, top 3 rows, bottom 2 rows) and reset interior wood."""
    for y in range(3, 14):
        for x in range(3, width - 2):
            if y == 3:
                canvas[y][x] = 7
            elif y <= 11:
                canvas[y][x] = 5
            elif y == 12:
                canvas[y][x] = 4
            else:
                canvas[y][x] = 5 if (x % 3) else 4


def patch_bg23(rom: bytes) -> tuple[bytes, int, bytes]:
    """Redraw `BG[23]` tagline row cleanly while preserving `SUNSOFT(R)` tiles 00..0B, 11..1A, 20..2D."""
    m = pce_gfx.bg_meta(rom, 23)
    tiles, orig_len = pce_gfx.decompress_stream(rom, m.offset, m.count, 32, m.x_end)

    # Clear unused tagline slots so compression stays compact.
    for tid in BG23_UNUSED_CLEAR:
        tiles[tid] = bytes(32)

    # Tile 0x0F holds the pure 1px hairline at y=2 (used across columns 0..16 of r3).
    hairline = [[0] * 8 for _ in range(8)]
    hairline[2] = [2] * 8
    tiles[0x0F] = _encode_bg_tile(hairline, 0, 0)

    # 17-tile x 8px tagline row (136px wide) centered under SUNSOFT(R).
    text = "DREAMS - CREATION - SUNSOFT"
    canvas = [[0] * (len(BG23_TAGLINE_TILES) * 8) for _ in range(8)]
    tw = _text_width(text, FONT_5X7, spacing=1)
    x0 = (len(canvas[0]) - tw) // 2
    _draw_text(canvas, text, FONT_5X7, x0, 1, color=2, spacing=1)
    for idx, tid in enumerate(BG23_TAGLINE_TILES):
        tiles[tid] = _encode_bg_tile(canvas, idx * 8, 0)

    comp = pce_gfx.compress_bg(tiles, m.bpp)
    if len(comp) > orig_len:
        raise OverflowError(f"BG[23] compressed to {len(comp)} B > budget {orig_len} B")

    new_map = bytearray(rom[0x160DD : 0x160DD + 90])
    # Rows 3 and 4 (offsets 54..71 and 72..89).
    new_map[54:72] = bytes([0x0F] * 17 + [0x00])
    new_map[72:90] = bytes(list(BG23_TAGLINE_TILES) + [0x00])
    return comp, orig_len, bytes(new_map)


def patch_bg15(rom: bytes) -> tuple[bytes, int]:
    """Redraw `BG[15]` Armor Shop sign (`防`, tiles 46,47 / 62,63) -> `AR/MR`."""
    m = pce_gfx.bg_meta(rom, 15)
    tiles, orig_len = pce_gfx.decompress_stream(rom, m.offset, m.count, 32, m.x_end)
    grid = [[46, 47], [62, 63]]
    canvas = _bg_px_grid(tiles, grid)
    _clear_wood_sign(canvas, 16)
    _draw_text(canvas, "AR", SIGN_FONT_5, x=4, y=3, color=0, spacing=1)
    _draw_text(canvas, "MR", SIGN_FONT_5, x=4, y=9, color=0, spacing=1)
    _set_bg_grid(tiles, grid, canvas)

    comp = pce_gfx.compress_bg(tiles, m.bpp)
    if len(comp) > orig_len:
        raise OverflowError(f"BG[15] compressed to {len(comp)} B > budget {orig_len} B")
    return comp, orig_len


def patch_bg16(rom: bytes) -> tuple[bytes, int]:
    """Redraw `BG[16]` 4 town signs: `INN`, `WE/AP`, `IT/EM`, and `KANAYA`."""
    m = pce_gfx.bg_meta(rom, 16)
    tiles, orig_len = pce_gfx.decompress_stream(rom, m.offset, m.count, 32, m.x_end)

    # 1. `宿` (64,65 / 80,81) -> Inn (9px centered at x=4..12, keeping x=3,13 clear)
    g_inn = [[64, 65], [80, 81]]
    c_inn = _bg_px_grid(tiles, g_inn)
    _clear_wood_sign(c_inn, 16)
    _draw_text(c_inn, "I", SIGN_FONT_3X7, x=4, y=5, color=0, spacing=1)
    _draw_text(c_inn, "nn", SIGN_FONT_5, x=6, y=7, color=0, spacing=1)
    _set_bg_grid(tiles, g_inn, c_inn)

    # 2. `武` (66,67 / 82,83) -> 2-row WEAP
    g_wpn = [[66, 67], [82, 83]]
    c_wpn = _bg_px_grid(tiles, g_wpn)
    _clear_wood_sign(c_wpn, 16)
    _draw_text(c_wpn, "WE", SIGN_FONT_5, x=4, y=3, color=0, spacing=1)
    _draw_text(c_wpn, "AP", SIGN_FONT_5, x=4, y=9, color=0, spacing=1)
    _set_bg_grid(tiles, g_wpn, c_wpn)

    # 3. `道` (162,163 / 178,179) -> 2-row ITEM
    g_item = [[162, 163], [178, 179]]
    c_item = _bg_px_grid(tiles, g_item)
    _clear_wood_sign(c_item, 16)
    _draw_text(c_item, "IT", SIGN_FONT_5, x=4, y=3, color=0, spacing=1)
    _draw_text(c_item, "EM", SIGN_FONT_5, x=4, y=9, color=0, spacing=1)
    _set_bg_grid(tiles, g_item, c_item)

    # 4. `金屋` (207..210 / 211..214) -> KANAYA
    g_kan = [[207, 208, 209, 210], [211, 212, 213, 214]]
    c_kan = _bg_px_grid(tiles, g_kan)
    _clear_wood_sign(c_kan, 32)
    kan_font = {**SIGN_FONT_3X7, **SIGN_FONT_N4}
    kw = _text_width("KANAYA", kan_font, spacing=1)  # 25 px
    _draw_text(c_kan, "KANAYA", kan_font, x=3 + (27 - kw) // 2, y=5, color=0, spacing=1)
    _set_bg_grid(tiles, g_kan, c_kan)

    comp = pce_gfx.compress_bg(tiles, m.bpp)
    if len(comp) > orig_len:
        raise OverflowError(f"BG[16] compressed to {len(comp)} B > budget {orig_len} B")
    return comp, orig_len


# ---------------------------------------------------------------------------
# Hand-crafted calligraphic brushwork helpers for SPR[21] (BENKEI / GAIDEN)
# ---------------------------------------------------------------------------

def _fill_rect(c: list[list[int]], x0: int, y0: int, x1: int, y1: int, val: int) -> None:
    h, w = len(c), len(c[0])
    for y in range(max(0, y0), min(h, y1 + 1)):
        for x in range(max(0, x0), min(w, x1 + 1)):
            c[y][x] = val


def _draw_brush_line(
    c: list[list[int]],
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    r0: float,
    r1: float,
    val: int = 3,
) -> None:
    h, w = len(c), len(c[0])
    steps = max(int(max(abs(x1 - x0), abs(y1 - y0)) * 2), 1)
    for s in range(steps + 1):
        t = s / steps
        cx = x0 + (x1 - x0) * t
        cy = y0 + (y1 - y0) * t
        r = r0 + (r1 - r0) * t
        r2 = r * r
        for y in range(max(0, int(cy - r - 1)), min(h, int(cy + r + 2))):
            for x in range(max(0, int(cx - r - 1)), min(w, int(cx + r + 2))):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                    c[y][x] = val


def _apply_crimson_shadow(c: list[list[int]], fg: int = 3, shadow: int = 2) -> None:
    """Add dark-crimson chiseled edge depth (`color 2`) down-right of bright strokes (`color 3`)."""
    h, w = len(c), len(c[0])
    orig = [row[:] for row in c]
    for y in range(h):
        for x in range(w):
            if orig[y][x] == fg:
                for dy, dx in ((1, 1), (1, 0), (0, 1), (2, 1)):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h and 0 <= nx < w and orig[ny][nx] != fg:
                        c[ny][nx] = shadow


def _render_benkei_canvas() -> list[list[int]]:
    """Draw dramatic 128x64 crimson calligraphy `BENKEI` across x=0..127, y=0..63."""
    c = [[0] * 128 for _ in range(64)]
    top, mid, bot = 9, 31, 53
    # B (x=4..20)
    _draw_brush_line(c, 5, top - 2, 5, bot + 2, 2.4, 2.1)
    _draw_brush_line(c, 2, top - 1, 13, top, 1.8, 2.0)
    _draw_brush_line(c, 13, top, 17, top + 6, 1.9, 2.1)
    _draw_brush_line(c, 17, top + 6, 16, mid - 4, 2.1, 1.8)
    _draw_brush_line(c, 16, mid - 4, 6, mid - 1, 1.8, 1.7)
    _draw_brush_line(c, 6, mid - 1, 17, mid + 3, 1.8, 2.1)
    _draw_brush_line(c, 17, mid + 3, 18, bot - 5, 2.2, 2.0)
    _draw_brush_line(c, 18, bot - 5, 13, bot + 1, 2.0, 1.9)
    _draw_brush_line(c, 3, bot + 1, 13, bot + 1, 1.7, 2.0)

    # E (x=24..40)
    _draw_brush_line(c, 26, top - 1, 26, bot + 1, 2.3, 2.1)
    _draw_brush_line(c, 24, top, 39, top - 1, 1.9, 2.3)
    _draw_brush_line(c, 39, top - 1, 40, top + 4, 1.5, 0.9)
    _draw_brush_line(c, 26, mid, 36, mid - 1, 1.8, 1.7)
    _draw_brush_line(c, 24, bot + 1, 40, bot + 1, 1.9, 2.4)
    _draw_brush_line(c, 40, bot + 1, 41, bot - 4, 1.5, 0.8)

    # N (x=45..63)
    _draw_brush_line(c, 47, top - 2, 47, bot + 3, 2.2, 1.9)
    _draw_brush_line(c, 47, top - 1, 61, bot + 2, 2.3, 2.4)
    _draw_brush_line(c, 61, top - 3, 61, bot + 2, 2.2, 2.1)
    _draw_brush_line(c, 44, top - 2, 49, top - 2, 1.5, 1.4)
    _draw_brush_line(c, 58, top - 3, 64, top - 3, 1.5, 1.5)

    # K (x=68..86)
    _draw_brush_line(c, 70, top - 2, 70, bot + 2, 2.4, 2.1)
    _draw_brush_line(c, 84, top - 2, 71, mid + 1, 2.1, 1.8)
    _draw_brush_line(c, 72, mid - 1, 86, bot + 3, 2.2, 2.4)
    _draw_brush_line(c, 86, bot + 3, 89, bot + 5, 1.6, 0.7)

    # E (x=92..108)
    _draw_brush_line(c, 94, top - 1, 94, bot + 1, 2.3, 2.1)
    _draw_brush_line(c, 92, top, 107, top - 1, 1.9, 2.3)
    _draw_brush_line(c, 107, top - 1, 108, top + 4, 1.4, 0.8)
    _draw_brush_line(c, 94, mid, 104, mid - 1, 1.8, 1.7)
    _draw_brush_line(c, 92, bot + 1, 108, bot + 1, 1.9, 2.3)
    _draw_brush_line(c, 108, bot + 1, 109, bot - 4, 1.4, 0.8)

    # I (x=114..125)
    _draw_brush_line(c, 119, top - 2, 119, bot + 2, 2.4, 2.2)
    _draw_brush_line(c, 114, top - 1, 125, top - 1, 1.7, 1.8)
    _draw_brush_line(c, 114, bot + 1, 125, bot + 1, 1.7, 1.8)

    _apply_crimson_shadow(c, fg=3, shadow=2)
    return c


def _render_gaiden_canvas() -> list[list[int]]:
    """Draw dramatic 128x32 crimson calligraphy `GAIDEN` across x=0..127, y=0..31."""
    c = [[0] * 128 for _ in range(32)]
    top, mid, bot = 5, 15, 25
    # G (x=4..22)
    _draw_brush_line(c, 19, top + 1, 14, top, 1.4, 1.6)
    _draw_brush_line(c, 14, top, 8, top + 1, 1.6, 1.7)
    _draw_brush_line(c, 8, top + 1, 6, mid, 1.7, 1.8)
    _draw_brush_line(c, 6, mid, 8, bot - 1, 1.8, 1.7)
    _draw_brush_line(c, 8, bot - 1, 18, bot, 1.7, 1.6)
    _draw_brush_line(c, 18, bot, 19, mid + 1, 1.6, 1.5)
    _draw_brush_line(c, 13, mid + 1, 20, mid + 1, 1.5, 1.5)

    # A (x=25..43)
    _draw_brush_line(c, 34, top - 1, 26, bot + 1, 1.6, 1.5)
    _draw_brush_line(c, 34, top - 1, 42, bot + 1, 1.6, 1.8)
    _draw_brush_line(c, 29, mid + 3, 39, mid + 3, 1.4, 1.4)

    # I (x=47..56)
    _draw_brush_line(c, 51, top, 51, bot + 1, 1.7, 1.6)
    _draw_brush_line(c, 47, top, 55, top, 1.3, 1.3)
    _draw_brush_line(c, 47, bot + 1, 55, bot + 1, 1.3, 1.3)

    # D (x=61..78)
    _draw_brush_line(c, 63, top, 63, bot + 1, 1.7, 1.6)
    _draw_brush_line(c, 61, top, 72, top + 1, 1.4, 1.6)
    _draw_brush_line(c, 72, top + 1, 77, mid, 1.6, 1.7)
    _draw_brush_line(c, 77, mid, 72, bot, 1.7, 1.6)
    _draw_brush_line(c, 61, bot + 1, 72, bot, 1.4, 1.6)

    # E (x=83..99)
    _draw_brush_line(c, 85, top, 85, bot + 1, 1.7, 1.6)
    _draw_brush_line(c, 84, top, 98, top, 1.4, 1.6)
    _draw_brush_line(c, 85, mid, 94, mid, 1.4, 1.4)
    _draw_brush_line(c, 84, bot + 1, 98, bot + 1, 1.4, 1.6)

    # N (x=104..122)
    _draw_brush_line(c, 106, top, 106, bot + 1, 1.7, 1.6)
    _draw_brush_line(c, 106, top, 120, bot + 1, 1.7, 1.7)
    _draw_brush_line(c, 120, top, 120, bot + 1, 1.7, 1.6)

    _apply_crimson_shadow(c, fg=3, shadow=2)
    return c


def _render_rule_canvas() -> list[list[int]]:
    """Draw tapered horizontal crimson brush rule (`96x16`, color `1` for SPR pal 10)."""
    c = [[0] * 96 for _ in range(16)]
    _draw_brush_line(c, 4, 8, 91, 8, 0.8, 0.8, val=1)
    _fill_rect(c, 14, 7, 81, 8, 1)
    return c


def _write_spr_block(
    pats: list[bytes],
    base_pat: int,
    cols_32: int,
    rows_16: int,
    canvas: list[list[int]],
) -> None:
    stride = rows_16 * 2
    for c in range(cols_32):
        for r in range(rows_16):
            p = base_pat + c * stride + r * 2
            pats[p] = _encode_spr_pat(canvas, c * 32, r * 16)
            pats[p + 1] = _encode_spr_pat(canvas, c * 32 + 16, r * 16)


def patch_spr21_and_24(rom: bytes) -> tuple[bytes, int, bytes, int]:
    """Redraw `SPR[21]` (`BENKEI` + `GAIDEN`) and `SPR[24]` (accent brush bar) within original budgets."""
    m21 = pce_gfx.spr_meta(rom, 21)
    _, orig21 = pce_gfx.decompress_stream(rom, m21.offset, m21.count, 128, m21.x_end)
    pats21 = [bytes(128)] * m21.count
    _write_spr_block(pats21, 0, cols_32=4, rows_16=4, canvas=_render_benkei_canvas())
    _write_spr_block(pats21, 32, cols_32=4, rows_16=2, canvas=_render_gaiden_canvas())
    comp21 = pce_gfx.compress_spr(pats21, m21.bpp)
    if len(comp21) > orig21:
        raise OverflowError(f"SPR[21] compressed to {len(comp21)} B > budget {orig21} B")

    m24 = pce_gfx.spr_meta(rom, 24)
    _, orig24 = pce_gfx.decompress_stream(rom, m24.offset, m24.count, 128, m24.x_end)
    pats24 = [bytes(128)] * m24.count
    _write_spr_block(pats24, 0, cols_32=3, rows_16=1, canvas=_render_rule_canvas())
    comp24 = pce_gfx.compress_spr(pats24, m24.bpp)
    if len(comp24) > orig24:
        raise OverflowError(f"SPR[24] compressed to {len(comp24)} B > budget {orig24} B")

    return comp21, orig21, comp24, orig24


def title_oam_patches() -> dict[int, tuple[bytes, str]]:
    """Return exact ROM offsets and payloads for Scene $CF Title Screen sprite placements and OAM lists."""
    # Scene $CF objects: (0x68 @ 56,48), (0x69 @ 56,124), (0x6B @ 56,112).
    scene_cf = bytes((0x68, 56, 48, 0x69, 56, 124, 0x6B, 56, 112))

    # obj 0x68 (6 sprites at 0x17412..0x17429, terminated by 0x90 at 0x1742A):
    # 4 x 32x64 BENKEI + 2 dummy offscreen sprites (pat=61, dy=127, 16x16).
    oam_68 = bytes(
        [
            0, 0, 0, 0x31,
            32, 0, 8, 0x31,
            64, 0, 16, 0x31,
            96, 0, 24, 0x31,
            0, 127, 61, 0x00,
            0, 127, 61, 0x00,
        ]
    )

    # obj 0x69 (13 sprites at 0x1742B..0x1745E, terminated by 0x90 at 0x1745F):
    # 4 x 32x32 GAIDEN + 9 dummy offscreen sprites.
    oam_69 = bytes(
        [
            0, 0, 32, 0x11,
            32, 0, 36, 0x11,
            64, 0, 40, 0x11,
            96, 0, 44, 0x11,
        ]
        + [0, 127, 61, 0x00] * 9
    )

    # obj 0x6B (6 sprites at 0x1747D..0x17494, terminated by 0x90 at 0x17495):
    # 3 x 32x16 bar above GAIDEN (dy=0) + 3 x 32x16 bar below GAIDEN (dy=46).
    oam_6b = bytes(
        [
            16, 0, 0, 0x01,
            48, 0, 2, 0x01,
            80, 0, 4, 0x01,
            16, 46, 0, 0x01,
            48, 46, 2, 0x01,
            80, 46, 4, 0x01,
        ]
    )

    return {
        0x17D73: (scene_cf, "title_scene_cf_objs"),
        0x17412: (oam_68, "title_oam_0x68_benkei"),
        0x1742B: (oam_69, "title_oam_0x69_gaiden"),
        0x1747D: (oam_6b, "title_oam_0x6b_rule"),
    }


def _canvas_to_png(path: Path, canvas: list[list[int]], pal: dict[int, tuple[int, int, int]]) -> None:
    h, w = len(canvas), len(canvas[0])
    rgb = bytearray(w * h * 3)
    for y, row in enumerate(canvas):
        for x, idx in enumerate(row):
            r, g, b = pal.get(idx, (idx * 17, idx * 17, idx * 17))
            o = (y * w + x) * 3
            rgb[o : o + 3] = bytes((r, g, b))
    pce_gfx.write_png(path, w, h, bytes(rgb))


def export_previews(rom: bytes, out_dir: Path) -> None:
    """Export legible PNG previews of all 5 redrawn assets into `out_dir`."""
    out_dir.mkdir(parents=True, exist_ok=True)
    comp23, orig23, map23 = patch_bg23(rom)
    tiles23, _ = pce_gfx.decompress_stream(comp23, 0, 65, 32, 0x11)
    bg23_grid = [list(map23[r * 18 : (r + 1) * 18]) for r in range(5)]
    c23 = _bg_px_grid(tiles23, bg23_grid)
    _canvas_to_png(
        out_dir / "bg23_sunsoft.png",
        c23,
        {0: (0, 0, 0), 1: (216, 216, 252), 2: (216, 216, 216), 3: (180, 180, 180), 4: (144, 144, 144), 5: (108, 108, 108), 6: (72, 72, 108)},
    )

    comp15, orig15 = patch_bg15(rom)
    tiles15, _ = pce_gfx.decompress_stream(comp15, 0, 256, 32, 0x20)
    sign_pal = {0: (16, 16, 16), 1: (48, 36, 24), 2: (96, 68, 40), 3: (136, 96, 56), 4: (172, 128, 72), 5: (212, 164, 96), 6: (120, 120, 120), 7: (248, 212, 144)}
    _canvas_to_png(out_dir / "bg15_arm.png", _bg_px_grid(tiles15, [[46, 47], [62, 63]]), sign_pal)

    comp16, orig16 = patch_bg16(rom)
    tiles16, _ = pce_gfx.decompress_stream(comp16, 0, 227, 32, 0x20)
    _canvas_to_png(out_dir / "bg16_inn.png", _bg_px_grid(tiles16, [[64, 65], [80, 81]]), sign_pal)
    _canvas_to_png(out_dir / "bg16_wpn.png", _bg_px_grid(tiles16, [[66, 67], [82, 83]]), sign_pal)
    _canvas_to_png(out_dir / "bg16_item.png", _bg_px_grid(tiles16, [[162, 163], [178, 179]]), sign_pal)
    _canvas_to_png(out_dir / "bg16_kanaya.png", _bg_px_grid(tiles16, [[207, 208, 209, 210], [211, 212, 213, 214]]), sign_pal)

    comp21, orig21, comp24, orig24 = patch_spr21_and_24(rom)
    pats21, _ = pce_gfx.decompress_stream(comp21, 0, 62, 128, 0x40)
    pats24, _ = pce_gfx.decompress_stream(comp24, 0, 9, 128, 0x40)
    spr_pal = {0: (24, 16, 16), 1: (180, 0, 0), 2: (108, 0, 0), 3: (216, 0, 0)}

    # Assemble title lockup preview (128x128).
    lockup = [[0] * 128 for _ in range(128)]
    for y in range(64):
        c_row = _render_benkei_canvas()[y]
        lockup[y][:128] = c_row
    # Rule at y=64 (dx=16..111 -> 96x16 relative to X=56, obj 0x6B at y=112 -> 112-48=64).
    rc = _render_rule_canvas()
    for ry in range(16):
        for rx in range(96):
            if rc[ry][rx]:
                lockup[64 + ry][16 + rx] = rc[ry][rx]
                lockup[64 + 46 + ry][16 + rx] = rc[ry][rx]
    gc = _render_gaiden_canvas()
    for gy in range(32):
        for gx in range(128):
            if gc[gy][gx]:
                lockup[76 + gy][gx] = gc[gy][gx]
    # Note validate roundtrip decoding from pats21 & pats24 too!
    w21, h21, rgb21 = pce_gfx.render_spr_4bpp_grid(pats21[:48], cols=8)
    pce_gfx.write_png(out_dir / "spr21_grid.png", w21, h21, rgb21)
    w24, h24, rgb24 = pce_gfx.render_spr_4bpp_grid(pats24, cols=3)
    pce_gfx.write_png(out_dir / "spr24_grid.png", w24, h24, rgb24)
    _canvas_to_png(out_dir / "title_lockup.png", lockup, spr_pal)

    print(
        f"BG[23]: {len(comp23)}/{orig23} B | BG[15]: {len(comp15)}/{orig15} B | "
        f"BG[16]: {len(comp16)}/{orig16} B | SPR[21]: {len(comp21)}/{orig21} B | SPR[24]: {len(comp24)}/{orig24} B"
    )


def main() -> int:
    rom = (ROOT / "rom" / "Benkei Gaiden (Japan).pce").read_bytes()
    export_previews(rom, ROOT / "work" / "qa" / "gfx_preview")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
