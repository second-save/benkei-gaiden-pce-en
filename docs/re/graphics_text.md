# Tile-Drawn Japanese Graphics & Font Asset Inventory

*Benkei Gaiden* (PC Engine HuCard, 1989). All compressed 4bpp BG and Sprite graphics in the ROM are unpacked through two centralized Bank `$02` decompression routines (`$D4A9` for BG tiles, `$D62A` for 16×16 hardware sprites). Both decompressors were replicated in `work/recon/decode_all_gfx.py` and verified byte-for-byte against live MesenCE VRAM dumps (`explore`, `ng_run`, `splash_dump`, `shop_run3`).

---

## 1. Graphics Tables & Hardware Formats

| System | Index Table | Data Pointer Table | Bank Rule | Decompressor | Target Layout |
|---|---|---|---|---|---|
| **BG Tiles** (`0..35`) | `B$02:$D400` (`0x05400`, 4 B/entry: `cnt, vram_hi, did, bpp`) | `0x14934` (`did * 2`) | `(ptr >> 13) + $48`; `- $45` if `did` in `{02,0A,0B,0E,10,12,19,1A,1C,1D,1E,1F}`, else `$20 + (bank & $0F)` | `B$02:$D3E5 -> $D4A9` | 8×8 4bpp PCE BG tiles (32 B/tile, bitplanes 0/1 interleaved then 2/3) |
| **Sprites** (`0..24`) | `B$02:$D5C6` (`0x055C6`, 4 B/entry: `cnt, unk, did, bpp`) | `0x1C000` (`did * 2`) | `(ptr >> 13) + $40`; `- $3D` if `did` in `{00,0B,0F,13,15,16,17}`, else `$20 + (bank & $0F)` | `B$02:$D5AE -> $D62A` | 16×16 4bpp PCE sprites (128 B/pat, 4 planar 32 B blocks; word order `s[py*2]` = right px 8..15, `s[py*2+1]` = left px 0..7) |

---

## 2. Tile-Drawn Japanese Graphics Replaced in English Build (Decision D3)

Every decoded asset across all 36 `BG` entries (`32` unique `did` streams) and 25 `SPR` entries was visually inspected (`work/recon/gfx_catalog/`). Only **five** compressed graphic assets contain baked-in Japanese artwork/signage; all five are redrawn within original compressed budgets in `tools/gfx_en.py`:

| Asset ID | `did` | ROM Offset (Bank) | Codec | VRAM Target | Size / BPP | Shipped English Redraw & Verification |
|---|---|---|---|---|---|---|
| **`BG[23]`** | `0x1B` | `0x5FD5A` (`B$2F:$BD5A`) | `$D4A9` | `$2000` | `65` tiles, `bpp=8` | **`SUNSOFT®`** preserved (tiles `0x00..0x0B, 0x11..0x1A, 0x20..0x2D`) + hairline (`0x0F`) + **`DREAMS - CREATION - SUNSOFT`** (`621/648 B`), plus `0x160DD` 5×18 BAT tagline map (`splash/final.png` visually verified). |
| **`SPR[21]`** | `0x15` | `0x09CB6` (`B$04:$BCB6`) | `$D62A` | `$5000` | `62` pats (16×16), `bpp=4` | Bold two-tone crimson brush title **`BENKEI`** + **`GAIDEN`** (`1576/2388 B`) + Scene `$CF` OAM placements/lists (`0x17D73`, `0x17412`, `0x1742B`, `0x1747D`; `title_logo` & `title_menu` visually verified). |
| **`SPR[24]`** | `0x18` | `0x4FEBE` (`B$27:$BEBE`) | `$D62A` | `$6000` | `9` pats (16×16), `bpp=4` | Crimson accent brush rules above & below **`GAIDEN`** (`148/302 B`) placed via Scene `$CF` object `0x6B` (`0x17D73`, `0x1747D`; `title_logo` & `title_menu` visually verified). |
| **`BG[15]`** | `0x13` | `0x58D80` (`B$2C:$AD80`) | `$D4A9` | `$2000` | `256` tiles, `bpp=16` | Interior/Town Armor Shop sign (`防`, tiles `46,47 / 62,63`) redrawn as crisp 2-row **`AR / MR`** (`ARMR`) inside original wood frame (`5048/5052 B`, preview PNG & lossless budget/preserve test verified). |
| **`BG[16]`** | `0x14` | `0x5A13C` (`B$2D:$A13C`) | `$D4A9` | `$3000` | `227` tiles, `bpp=16` | Town tileset **4 signs** (`5211/5299 B`): **`Inn`** (`宿`, tiles `64,65 / 80,81`), **`WE / AP`** (`武`, `66,67 / 82,83`), **`IT / EM`** (`道`, `162,163 / 178,179`), and **`KANAYA`** (`金屋`, `207..214`, 32×16 px). `Inn`, `IT/EM`, and `KANAYA` verified live in MesenCE (`tsukumo_town`, `shop_item`, `p8_kyoto_mkt`, `p8_kamakura6`); `WE/AP` verified via preview PNG & `test_gfx_en.py`. |

---

## 3. Text Engine Font & Kanji Tile Sheets (Not Raw Graphic Art)

These four `BG` streams hold font/glyph tiles used directly by the runtime text engine (`$FDEF`/`$FE2A`), not static baked artwork:

| Asset ID | `did` | ROM Offset (Bank) | VRAM Target | Tiles / BPP | Role |
|---|---|---|---|---|---|
| **`BG[01]`** | `0x01` | `0x51824` (`B$28:$B824`) | `$4000` (`$0400` tile base) | `253` (`bpp=16`) | Plane `$00` 8×16 halfwidth kana/ASCII/digits & 18 2-byte kanji + Plane `$20` (`$EF`) 16×16 high-frequency kanji + window borders |
| **`BG[17]`** | `0x15` | `0x5B5EF` (`B$2D:$B5EF`) | `$1200` (`$0120` tile base) | `220` (`bpp=16`) | Standard gameplay Planes `$FD`/`$1D` (`$ED`/`$FD`) kanji sheet (`bytes $20..$FA`) |
| **`BG[34]`** | `0x1E` | `0x0E9AC` (`B$07:$A9AC`) | `$1200` (`$0120` tile base) | `88` (`bpp=16`) | Temporary overlay during **Title**, **BRAM Save/Load**, and **Ending Credits** (`$ED`/`$FD` bytes `$20..$77`) |
| **`BG[33]`** | `0x1A` | `0x0E8AE` (`B$07:$A8AE`) | `$2000` | `48` (`bpp=2`) | ASCII + `SUNSOFT` thin-font 1bpp/2bpp utility glyph sheet |

### Screens Rendered via Text Engine (`BG[34]` + `BG[01]`), NOT Tile Art
Confirmed in `tools/pce_text.py` & live `ng_run`/`world_run` captures — all translated via standard script insertion (zero redraw needed):
- **Credits Intro**: `協力 本宮ひろ志 / 本宮企画 / 著作 制作` (`b11_bg34_credits`, plus `BG[23]` `SUNSOFT®` tile graphic below it — see `world_run/sheet.png` tile 3)
- **Title Menu**: `冒頭` / `継続` (`b0a_menus` vertical rows `0x15159..0x15166`, `bg34=True`)
- **BRAM Save/Load Menu**: `旅の記録`, `バックアップ`, `弁慶 1`–`弁慶 3`, `とりけし`, confirmation prompts (`0x150FF..0x1518E`)
- **Ending Credits**: `脚本`, `制作`, `美術`, `音楽`, `進行`, `協力`, `監修`, `題字`, staff kanji names `中村一朗`..`吉田喜春`, `平成 元年` (`0x23E8F..0x23F24`)

---

## 4. Clean Non-Text Graphics Audit Summary

All remaining assets were visually verified to contain **zero Japanese text**:
- **Field & Overworld Tilesets (`BG[00]`, `BG[02..14]`, `BG[18..20]`)**: Terrain, mountains, caves, shrines, town rooftops, and castle interiors (`map_tilesets_all.png`). Zero kanji signs outside `BG[15]` and `BG[16]`.
- **Battle Backgrounds & Title Scenery (`BG[21..22]`, `BG[30]`, `BG[31..32]`, `BG[35]`)**: Horizon silhouettes, title sunset torii backdrop (`BG[30]`), and village/credits scenery (`BG[35]`). Zero text.
- **Character Portraits (`BG[24..29]`)**: Six 4-expression animated character portrait sheets (`Kijaku`, `Sayaka`, `Saburo`, `Benkei`, `Hogen`, `Yoshitsune`). Zero text.
- **Character, Monster, VFX, and Cloud Sprites (`SPR[00..20]`, `SPR[22..23]`)**: Walk cycles, battle enemy/spell VFX, and title mist/clouds (`spr_summary.png`). Zero text.
