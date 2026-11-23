# Text Engine & Font Architecture — Benkei Gaiden (PCE)

Verified against `rom/Benkei Gaiden (Japan).pce` (`CRC32 e1a73797`) and live MesenCE VRAM/VCE dumps (`work/recon/ng_run/`, `work/recon/text_probe/`).

## 1. 4-Plane 1bpp Packed VRAM Font & Palettes

Because PC Engine BG tiles are 4bpp (32 bytes = planes `p0,p1` in bytes `0..15`, `p2,p3` in bytes `16..31`), *Benkei Gaiden* packs **four independent 1bpp font layers** into each 4bpp VRAM region using VCE palettes `$0C..$0F` (set by `B$02` / `B$00`):

- Palette `$0C`: bitplane 0 = `#666/$FFF` (`$1B6`), all other bits transparent/black (`$000`).
- Palette `$0D`: bitplane 1 = `#666/$FFF`, all other bits `$000`.
- Palette `$0E`: bitplane 2 = `#666/$FFF`, all other bits `$000`.
- Palette `$0F`: bitplane 3 = `#666/$FFF`, all other bits `$000`.

### Loaded Font Assets

| Asset | ROM Offset | Decomp Size | VRAM Word | Tiles | Contents |
| --- | --- | --- | --- | --- | --- |
| `BG[1]` (`$D404`, ID `$01`) | `0x51824` (`B$28`) | `253` tiles (`8,096 B`) | `$4000` | `$400..$4FC` | `p0/p1` (`$74=$00`): 8×16 halfwidth digits, `A..F`, kana, punct + 18 2-byte kanji pairs (`撃岩身経験値宿防具走体調査素早会話装備`); `p2/p3` (`$74=$20`, `$EF`): 16×16 kanji |
| `BG[17]` (`$D444`, ID `$15`) | `0x5B5EF` (`B$2D`) | `220` tiles (`7,040 B`) | `$1200` | `$120..$1FB` | `p0/p1` (`$74=$FD`, `$ED`): 16×16 kanji `$20..$FA`; `p2/p3` (`$74=$1D`, `$FD`): 16×16 kanji `$20..$FA` |
| `BG[34]` (`$D488`, ID `$1E`) | `0x0E9AC` (`B$07`) | `88` tiles (`2,816 B`) | `$1200` | `$120..$177` | Temporary Title / BRAM / Ending Credits kanji overlay (`$20..$77`); bytes `>= $78` remain from `BG[17]` |

> Note: Every 8×16 halfwidth glyph in `BG[1]` uses tile `t & $EF` (`pal $C`) for the top 8 rows and `t | $10` (`pal $C`) for the bottom 8 rows when bit 4 is `0`, OR `(t & $EF)` / `(t | $10)` with `pal $D` (`p1`) when bit 4 is `1`. 16×16 kanji always sit at **even** indices (`b` left, `b+1` right; `top = t & $EF`, `bot = t | $10`).

---

## 2. State Machine & Control Codes (`$74`)

Both `B$02:$CE45` and `B$02:$CF27` initialize `r74` (ZP `$74`) to `$00` at the start of every string (`STZ $74`):

| Byte | Action | Meaning |
| --- | --- | --- |
| `$FF` | Terminate string | `{end}` |
| `$FE` | Clear box / wait for input & reset cursor (`$CF27`) | `{page}` |
| `$EE` | Advance to next line of `24` tiles (`$CF27`) | `{nl}` |
| `$EF` | `r74 ^= $20` | Switch `$00 <-> $20` (`tbl/jp_ef.tbl`) |
| `$ED` | `r74 ^= $FD` | Switch `$00 <-> $FD` (`tbl/jp_ed.tbl` / `tbl/jp_bg34_ed.tbl`) |
| `$FD` | `r74 ^= $1D` | Switch `$00 <-> $1D` (`tbl/jp_fd.tbl` / `tbl/jp_bg34_fd.tbl`) |

Valid active states observed across all 1,213 strings in the ROM are strictly `{$00, $20, $FD, $1D}`. Notice some strings end with an open toggle right before `$FF` (e.g., `B$02:$DE60` `ed 36 ed fd 26 ff`); the printer resets `$74 = 0` on the next call (`preserve_toggles=True` in `tools/pce_text.py` guarantees bit-exact roundtrip).

When `r74 == $00`, byte `$EC` in `B$0A:$50E9` (`うえ[EC]した[EC]...`) writes empty `BG[1]` tile `$04EC/$04FC` as a 1-tile spacer slot for directional icons on the name entry screen.

---

## 3. Text Rendering Entry Points & Buffers

- **RAM Buffers:**
  - `$2E00..$2FFF` (`$2E00`): General string assembly buffer filled by `B$00:$F90C` (`$D8/$D9` copy) and `B$00:$F908` (`DEC $DC` append), plus enemy names from `B$02:$D9CF`/`$DA01` (`$BA06`/`$BD12`).
  - `$2C00..$2CFF`: Secondary scratch buffer used by `B$09:$C792` / `B$09:$D49D` (password / BRAM menus) and `B$02:$D50B` (GFX decompression).
- **Trampolines in `B$00` (mapping `B$02` into `MPR6` `$C000..$DFFF`):**
  - `$FDEF`: Instant string print at inline `(x, y)` + 16-bit pointer (`B$02:$CE45` wrapper).
  - `$FE2A`: Instant dialogue/status box print at inline 16-bit pointer (`B$02:$CE45` via `$FE24`).
  - `$FE08`: Indirect pointer print (reads 16-bit address stored at inline pointer -> `B$02`).
- **Printer Routines in `B$02`:**
  - `$CE45`: Instant printer (`MPR2..5 = B$0E..$11` via `$F935`). Writes 2× 8×8 BAT rows per character, toggling ZP `$01` (`1 -> 0`) and adding `$40` (64 columns) to BAT address (`$0F/$10`). BAT high byte is `($C4 + $74)` or `($D4 + $74)`.
  - `$CF27`: Typewriter dialogue box printer (`24` tiles = `$18` per line, 3 lines `$18 / $30 / $48` before `$D060` page wait & clear; calls `$E2C0` frame delay between characters).
  - `$CD62`: Window border/frame drawer using `B$0A:$60DD` (`18×5` BAT blocks).
  - `$DD80`: Overworld top/bottom HUD layout (`7×32` BAT strips from `B$0A:$4A16`, VRAM `$0180` & `$0340`).
  - `$D9CF` / `$DA01`: Enemy kanji / kana name copier (`B$0D:$BA06` / `B$0D:$BD12`); computes `len = ptr[i+1] - ptr[i]`, copies into `$2E00`, appends `$FF`.

---

## 4. Complete Text Table Inventory (`1,213` strings)

| Group | Bank / Offset | Ptr Table / Endianness | Count | Notes |
| --- | --- | --- | --- | --- |
| `b00_timestamp` | `B$00` `0x01B75` (`$FB75`) | Direct ref at `B$1B:$C3DD` | `1` | Build timestamp (`1989/08/25  10:31:18`) in Test Mode |
| `b02_sys` | `B$02` `0x05E36..0x05FBB` (`$DE36`) | Direct `$FF`-terminated refs (`B$00/$01/$02/$08/$1B`) | `56` | Menus, status labels, battle summary, unused Test Mode (`$DF42`) |
| `b09_password` | `B$09` `0x12611..0x12682` | `0x12609` (`$C609`, 5× LE16 `MPR6`) | `5` | Password entry hiragana grid (`$C683+` is non-string tile data) |
| `b0a_menus` | `B$0A` `0x1509C..0x151AE` | `0x1505E` (`$505E`, 27× LE16 `MPR2`); box specs `0x151AF` | `27` | Name entry (`うえ/した...`), BRAM save/load/delete, & `BG[34]` vertical menus (`$5159..$51A0`: `冒頭/継続`, `バックアップ/旅の記録`, `弁慶 1..3 / やめる`) |
| `b0a_locations` | `B$0A` `0x15282..0x152C8` | `0x15268` (`$5268`, 13× LE16 `MPR2`) | `13` | Fast-travel / location names (`林省寺` .. `リウモ村`) |
| `b0d_enemy_kanji` | `B$0D` `0x1BAE8..0x1BD10` | `0x1BA06` (`$BA06`, 112 ptrs + sentinel `$BD11`) | `112` | No `$FF`; len = `ptr[i+1] - ptr[i]`. Slots `105..109` are 0 bytes |
| `b0d_enemy_kana` | `B$0D` `0x1BDF4..0x1BFE7` | `0x1BD12` (`$BD12`, 112 ptrs + sentinel `$BFE8`) | `112` | Matched hiragana readings (`B$02:$DA01`) |
| `b0e_jutsu` | `B$0E` `0x1C072..0x1C139` | `0x1C032` (`$4032`, 32× LE16 `MPR2`) | `32` | Jutsu (spell) names (`魔破` .. `極無転`) |
| `b0e_items` | `B$0E` `0x1C23C..0x1C523` | `0x1C13A` (`$413A`, 128× LE16 `MPR2`) | `128` | Unified IDs: `0..31` weapons, `32..63` armor, `64..95` key items, `96..127` consumables (unused slots -> `$423A` `"0{end}"`) |
| `b0e_battle` | `B$0E` `0x1C524..0x1C570` (`$4524`) | Direct refs (`B$00/$01/$08/$0E..$11`) | `13` | Battle action & damage templates (`の 攻撃`, `を たおした`, `に .. の ダメージ...`) |
| `b11_dialogue` | `B$0E..$11` `0x1C571..0x2397E` | `0x2397F..0x23E8E` (`$B97F`, 648× LE16 `MPR2..5`) | `648` | Master dialogue & prologue/battle script indexed via `B$01:$C096` (plus direct ending `$B784/$B7FC..` calls in `B$1B:$D950`) |
| `b11_bg34_credits` | `B$11` `0x23E8F..0x23F24` (`$BE8F`) | Direct `$FDEF`/`$FE2A` refs (`B$02:$C61D`, `B$09:$D562`) | `23` | Rendered with `BG[34]`: `協力/本宮ひろ志/著作/制作/本宮企画`, ending role headings & staff kanji (`脚本/制作/.../平成 元年`) |
| `b11_ending_nar` | `B$11` `0x23F25..0x23F60` (`$BF25/$BF47`) | Direct `$FDEF` refs (`B$09:$DA2C/$DA42`) | `2` | Final epilogue narration lines |
| `b1B_staff` | `B$1B` `0x37A8F..0x37C2C` | `0x37A3D` (`$DA3D`, 41× LE16 `MPR6`) | `41` | Padded hiragana ending staff roll (`のむら まさひと` ..) |

> Verification: `tools/pce_text.py` + `tests/test_text.py` decode and re-encode all **1,213 strings** with 100% byte-exact fidelity.

---

## 5. English Localization Strategy

1. **8×16 Halfwidth ASCII Font:** Every single-byte glyph (`r74=$00`) already renders as 1 byte per 8×16 halfwidth column! Replacing `BG[1]` Plane 0/1 tiles (`0x51824`) with a crisp 8×16 ASCII/Latin set (`A-Z, a-z, 0-9`, punctuation, quotes, apostrophes) lets English text use `$74 == $00` throughout with zero toggle overhead, fitting 24 characters per line × 3 lines (`72` chars/page) in standard dialogue boxes without even changing window dimensions!
2. **Word-Wrap & Box Expansion:** In `B$0E..$11` (`b11_dialogue`, moved cleanly into the `B$60..$7F` expansion banks or repointed via `$B97F`), we will wrap cleanly at word boundaries inside `24` columns (or `32`/`28` if widened) and add `EN`-width padding for `b0e_items` / `b0d_enemy_*` / `b02_sys` menus where needed.
3. **Title & Credits (`BG[34]`):** Both `冒頭 / 継続` (`New Game / Continue`), `本宮ひろ志 / 本宮企画` (`Hiroshi Motomiya / Motomiya Kikaku`), `旅の記録 / バックアップ` (`Save Log / Backup`), and Ending headings (`脚本 / 制作 / 美術...`) are printed via `$CE45` (`B$0A:$5159` and `B$11:$BE8F`), so translating their strings directly with the ASCII 8×16 font translates them cleanly without needing custom kanji tiles!
