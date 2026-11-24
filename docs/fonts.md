# Fonts

## English 8×16 Halfwidth Bitmap Font (`tools/font_en.py`, `tbl/en.tbl`, 84 glyphs)

- **License / Provenance:** Original CC0 pixel-art 8×16 glyph bitmaps authored directly in `tools/font_en.py` for this project (no external copyrighted font files bundled or redistributed).
- **Geometry & Baseline:**
  - `8×16` cell per character, `1 px` right-side spacing (`bit 0` always `0`, max `7 px` glyph ink width so adjacent characters never touch).
  - Uppercase letters and digits occupy rows `3..12` (10 px cap height, matching the row-12 baseline of *Benkei Gaiden*'s native digits).
  - Lowercase bodies occupy rows `6..12` with ascenders at rows `3..12` and descenders (`g, j, p, q, y`) extending to rows `13..14` while keeping row `15` clear.
- **VRAM & Plane Mapping (`BG[01]`, `0x51824`):**
  - Stored in Planes 0 (`codes $00..$0F, $20..$29, $40..$4F`) and 1 (`codes $10..$1F, $30..$39, $50..$5F`) of `BG[01]` (`VRAM $4000`, `253` tiles), using the native single-byte `r74 == $00` text path.
  - Top 8 rows map to tile `code & $EF`, bottom 8 rows to tile `code | $10`, selecting Plane 0 (`(code & $10) == 0`) or Plane 1 (`(code & $10) != 0`).
  - Plane 2/3 (`$EF` kanji) and all tile indices `>= $60` (box borders `$CA..$FB`, cursors, remaining kana/kanji) are preserved verbatim.
