# ROM Map & 1 MiB Expansion — Benkei Gaiden (PCE)

Verified against `rom/Benkei Gaiden (Japan).pce` (`393,216` bytes = `48` × 8 KiB banks `$00..$2F`, `CRC32 e1a73797`, `SHA-1 4bc46592f3707a7c3e514abc23e640e3194879ad`) and live MesenCE execution (`work/test_expand_1m.pce`).

## 1. Reset / Interrupt Vectors & Bank Architecture

Bank `$00` (`0x00000..0x01FFF`) is permanently mapped in `MPR7` (`$E000..$FFFF`):
- Vectors: `IRQ2/BRK = $E2E7`, `IRQ1/VDC = $E2E8`, `TIMER = $E34E`, `NMI = $E2E7`, `RESET = $E000`.
- Boot (`$E000..`): `MPR0 = $FF` (HW I/O), `MPR1 = $F8` (8 KiB Work RAM `$2000..$3FFF`), `MPR7 = $00`, `MPR6 = $01`.
- Inline `MPR6` Far-Call Trampolines via `$F176` (`JSR <trampoline>; .dw target_addr`):
  - `$EC89` -> `B$02` (`57` calls)
  - `$ECAE` -> `B$09` (`7` calls)
  - `$ECBE` -> `B$08` (`11` calls)
  - `$ECCE` -> `B$1F` (`8` calls)
  - `$ECDE` -> `B$1B` (`43` calls)
  - `$ECEE` -> `B$1A` (`3` calls)
- 4-Bank `MPR2..MPR5` (`$4000..$BFFF`) Window Mappers:
  - `$F929`: `B$0A..$0D` (`0x14000..0x1BFFF`)
  - `$F92D`: `B$1C..$1F` (`0x38000..0x3FFFF`)
  - `$F931`: `B$15..$18` (`0x2A000..0x31FFF`)
  - `$F935`: `B$0E..$11` (`0x1C000..0x23FFF`)
  - `$EF76` (`A2` = `0/1/2` -> `$EF87`): maps 3/4 consecutive banks starting at `$12`, `$15`, or `$18`.
  - `B$09:$DF35`: maps `MPR4` (`TAM #$10`) to `$F7` (2 KiB BRAM) during save/load.

---

## 2. Complete 48-Bank Inventory (`$00..$2F`)

| Bank(s) | ROM Offset | Free Tail | Role |
| --- | --- | --- | --- |
| `$00` | `0x00000..0x01FFF` | `0 B` | Fixed bank (`$E000..$FFFF`): vectors, trampolines, mappers, text callers, Test Mode timestamp `$FB75` |
| `$01` | `0x02000..0x03FFF` | `24 B` | Field / event / shop / menu logic; `B$01:$C096` dialogue loader |
| `$02` | `0x04000..0x05FFF` | `69 B` | Text printers (`$CD62/$CE45/$CF27/$D9CF/$DA01/$DD80`), Title prologue (`$C600`), BG/Sprite decompressors (`$D4A9/$D62A`), `$D494/$D4A1` chip tables, system/status/Test Mode strings (`$DE36..$DFBB`) |
| `$03..$04` | `0x06000..0x09FFF` | `0..1 B` | Exception compressed Sprite GFX (`$D4A1` entries `0x00, 0x0B, 0x0F, 0x13, 0x15, 0x16, 0x17`) |
| `$05` | `0x0A000..0x0BFFF` | `0 B` | Shared exception compressed Sprite GFX (`0x0A60A, 0x0B51A`) & BG GFX (`0x0B69C`) |
| `$06..$07` | `0x0C000..0x0FFFF` | `0 B` | Exception compressed BG GFX (`0x0C0A8..0x0F298`, incl. `BG[34]` Title/BRAM/Ending overlay at `0x0E9AC`) |
| `$08` | `0x10000..0x11FFF` | `11 B` | BG GFX overflow (`0x105FC`), plus battle/combat & menu logic (`$C600..$DFFF`) |
| `$09` | `0x12000..0x13FFF` | `39 B` | Password screen (`$C2C0/$C609`), BRAM `$F7` save/load (`$CF9C/$D4EB/$DF35`), ending slideshow (`$D50F..$DA80`) |
| `$0A` | `0x14000..0x15FFF` | `0 B` | BG GFX ptr table (`$4934`), HUD tilemap tables (`$4A16, $5E01, $60DD`), `!BM FORMAT!` (`$5043`), BRAM/name-entry/title menus (`$505E..$51DF`), location names (`$5268..$52C8`), ending helper (`$52C9..`) |
| `$0B..$0C` | `0x16000..0x19FFF` | `0 B` | Enemy encounter groups, world zone / NPC / map metadata |
| `$0D` | `0x1A000..0x1BFFF` | `23 B` | Enemy stats/AI/shop tables (`$A000..$B9FF`), Enemy kanji (`$BA06`) & kana (`$BD12`) 112-entry name tables |
| `$0E..$11` | `0x1C000..0x23FFF` | `109 B` (in `$11`) | `MPR2..5` 32 KiB text/data window: `$4000` Sprite GFX ptrs, `$4032` 32 jutsu, `$413A` 128 items, `$4524` 13 battle templates, `0x1C571..0x2397E` script, `B$11:$B97F` 648 dialogue ptrs, `$BE8F..$BF60` `BG[34]` credits & ending narration |
| `$12..$17` | `0x24000..0x2FFFF` | `0 B` | World, town, dungeon map tilemaps & collision (`$EF76`) |
| `$18..$1A` | `0x30000..0x35FFF` | `110 B` (in `$1A`) | Additional map/event/flag data & sub-routines (`B$1A:$DF0B..`) |
| `$1B` | `0x36000..0x37FFF` | `11 B` | Title / Game Over / Ending & Test Mode (`$C399`) flow controller, credits printer (`$D9C1`), 41 staff hiragana names (`$DA3D`) |
| `$1C..$1F` | `0x38000..0x3FFFF` | `28 B` (in `$1F`) | PSG sound driver init (`B$1C:$4000`), music/SFX sequences (`B$1C..$1E`), cutscene/event runner (`B$1F:$D6A6..`) |
| `$20..$27` | `0x40000..0x4FFFF` | `20 B` (in `$27`) | Compressed Sprite GFX (chip 1 low window, logical banks `$40..$47`) |
| `$28..$2F` | `0x50000..0x5FFFF` | `30 B` (in `$2F`) | Compressed BG GFX (chip 1 high window, logical banks `$48..$4F`, incl. `BG[1]` font `0x51824` & `BG[17]` kanji `0x5B5EF`) |

---

## 3. Verified 1 MiB (`0x100000`, 128-Bank) Expansion Layout

Because `$D4A9` (BG) and `$D62A` (Sprites) select banks using chip-split logic:
- `(ptr >> 13) + $48` (BG, `$48..$4F`, wrapping `$4F -> $50` on 2-bank reads)
- `(ptr >> 13) + $40` (Sprites, `$40..$47`)
while standard 384 KiB hardware mirrors the upper 128 KiB (`$20..$2F`) at `A20=1` (`$40..$4F`, `$50..$5F`, `$60..$6F`, `$70..$7F`), expanding directly to 1 MiB requires mirroring original upper banks `$20..$2F` across `$20..$2F`, `$40..$4F`, and `$50..$5F`:

| Physical Banks | ROM Offset | Size | Contents |
| --- | --- | --- | --- |
| `$00..$1F` | `0x00000..0x3FFFF` | `256 KiB` | Original banks `$00..$1F` (code, text, maps, sound, exceptions) |
| `$20..$2F` | `0x40000..0x5FFFF` | `128 KiB` | Original upper GFX banks `$20..$2F` (defensive mirror) |
| **`$30..$3F`** | `0x60000..0x7FFFF` | **`128 KiB`** | **Free expansion space (`$FF` fill) — Code / Graphics** |
| `$40..$4F` | `0x80000..0x9FFFF` | `128 KiB` | Mirror of original `$20..$2F` (preserves `$D4A9/$D62A` logical `$40..$4F`) |
| `$50..$5F` | `0xA0000..0xBFFFF` | `128 KiB` | Mirror of original `$20..$2F` (preserves `$4F+1 -> $50` bank wrap) |
| **`$60..$7F`** | `0xC0000..0xFFFFF` | **`256 KiB`** | **Free expansion space (`$FF` fill) — Expanded English Script / Tables** |

- **Total clean expansion space:** **`384 KiB`** (`$30..$3F` + `$60..$7F`).
- **Verification (`work/test_expand_1m.pce`):** Booted through Sunsoft logo, title screen, New Game prologue, and Rinsho-ji Temple over `2,600` frames in MesenCE (`smoke ok`). Frames `480..2160` matched `ng_run/` **100% pixel-for-pixel**, and `2400` rendered the identical Rinsho-ji Temple scene.
