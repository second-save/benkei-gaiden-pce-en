# UI Window Budgets & Text Layout Rules — Benkei Gaiden (PCE)

Measured pixel-by-pixel on live MesenCE 2.2.1 captures (`work/qa/p5_marker/`, `work/qa/p5_torture/`, `work/qa/p5_verify/`) using the 8×16 halfwidth ASCII font (`BG[01]`, `32` halfwidth columns × `14` tile-pair rows on `256×224` px).

## 1. Core Rendering & Word-Wrap Rules

- **Dialogue auto-wrap (`B$02:$CF27`):**
  - Standard dialogue boxes hold **24 columns × 3 lines per page** (`$18`, `$30`, `$48`).
  - Writing **24 printable glyphs** on a line *already* advances `$00` to `$18`/`$30`/`$48` and wraps to the next line. Following a 24-character line with `{nl}` (`$EE`) advances an *extra* row, leaving an unwanted blank line.
  - **Rule:** Either keep lines with explicit `{nl}` to **`<= 23` characters**, or omit `{nl}` after exact `24`-character lines. Never combine 24 printable chars + `{nl}`.
- **Clearance before right-aligned numbers:**
  - Stat, price, HP/MP, EXP, and sen fields overwrite fixed BAT columns from the right. Every label column limit below preserves `>= 1` blank space before maximum runtime digit width (`999`, `999/999`, `99999` sen, `999999` EXP).
- **Fixed `$2E00` digit-poke templates (`STA $2E0x`):**
  - Three strings are copied into `$2E00` via `$F90C` and then patched in-place with ASCII digit bytes before printing:
    - `b11_dialogue_237_1F0BD` (`B$01:$CA8D..$CA97`): writes 3-digit Inn price into byte offsets **`+4..+6`** (`$2E04..$2E06`). Put `3` placeholder spaces at bytes `+4..+6` (e.g. `Stay   ...` -> `"Stay 50..."`).
    - `b11_dialogue_601_23289` (`B$01:$CDBF..$CDD3`): writes 5-digit pawn/sale price into byte offsets **`+3..+7`** (`$2E03..$2E07`). Keep 5 spaces at `+3..+7`.
    - `b11_dialogue_566_22EA9` (`B$1B:$C965..$C96F`): writes 3-digit sen (`×10`, literal `'0'` at `+6`) into byte offsets **`+3..+5`** (`$2E03..$2E05`). Keep 3 spaces at `+3..+5`.

---

## 2. Measured Window Budgets by Screen / Group

| Group / Window (`box`) | Columns | Lines | Notes |
| --- | --- | --- | --- |
| `dialogue` (standard `$CF27`) | `24` | `3` / page | Multi-page `{page}` unlimited in `B$61..$7E`; use `<= 23` + `{nl}` |
| `dialogue` (`shop_item` prompt `b11_dialogue_050_1CE27`) | `14` (L1) / `24` (L2–3) | `3` | `[Sen   50]` window overlaps cols 17..29 of Line 1 |
| `field_menu` (`b02_sys[0..2]`) | `11` (`5 + 1 + 5`) | `1` each | Right-column cursor (`•`) lands on byte index `5`; `<= 5` left, `' '` at 5, `<= 5` right |
| `items_menu` list (`b0e_items` `96..127`) | `12` | `8` rows × 2 cols | 2-column bag list; col 13 touches divider/cursor |
| `items_menu` Use/Drop (`b02_sys[19..20]`) | `6` | `2` | Small action popup above items list |
| `equip_menu` items (`b0e_items` `0..95`) | `11` | `8` (list) / `3` (equipped) | Shared by `status_full` bottom-left (`11` cols) and `equip_menu` top-right (`14` cols minus `3`-col `"W: "`/`"A: "`/`"R: "` prefix) |
| `equip_menu` labels (`b02_sys[11..13]`) | `3` (`4` max) | `1` each | `"W: "`/`"A: "`/`"R: "` (`3` cols) leaves `11` cols for item name inside `14`-col top-right box |
| `equip_menu` stats (`b02_sys[29..30]`) | `7` | `1` each | Before right-aligned 3-digit ATK/DEF |
| `jutsu_menu` list (`b0e_jutsu`) | `11` | `1` each | 12th column touches right vertical border `\|` |
| `jutsu_menu` party (`b02_sys[6..9]`) | `7` | `4` | Party member selector (`Kijaku`, `Sayaka`, `Saburo`, `Benkei` = 6 cols) |
| `status_full` right panel (`14` cols total) | `2–14` (per slot) | `11` | `Name` (`8`) + `S24` Lv (`2–3`); `S25` HP (`<= 4`); `S26M` MP (`<= 4`); `S27..S30` STR/AGI/ATK/DEF (`<= 9` / `8` w/3-dig); `S31` EXP (`14`); `S32` Next (`14`); `S33` (`3` cols before 5-dig EXP) |
| `status_full` & `shop_item` Sen (`b02_sys[23]`) | `3` | `1` | Fixed to `3` cols (`"Sen"`) by `Inc11By3` patch at `B$01:$CD0E` (also fits `5`-col `status_full` Sen box) |
| `shop_item` Buy/Sell (`b02_sys[39..40]`) | `6` | `2` | Upper-left shop command box |
| `location` (`b0a_locations[0..12]`) | `12` | `1` | Warp/fast-travel destination window (`<= 12` cols cleanly inside box) |
| `battle_spider` / `battle_party` HUD (`b02_sys[6..9]`) | `7` | `2` rows | `4` members across `32` cols (`7` chars/name + `1` gap); `95/40`..`120/20` HP/MP row |
| `battle_tpl` command (`b02_sys[17..18]`) | `11` (`4–5 + 1 + 5`) | `2` | Left option `<= 4–5`, `' '` at index `5` for cursor2, right option `<= 5` |
| `enemy_kanji` (`b0d_enemy_kanji`) | `14` | `1` each | Battle enemy-name list (`<= 14` cols; Bank `$60` `$A000..$BFFF`, no `$FF` terminator) |
| `battle_tpl` templates (`b0e_battle[0..12]`) | `24` | `3` | `$CF27` battle message box (Note: `b0e_battle[6]` `"-{end}"` is 2 bytes in-place; `[8]` & `[10]` repointed via `B$11` tail) |
| `title_menu` horizontal (`b0a_menus[17..20]`) | `8` (`9` max) | `2` | Patched horizontal `B$09` box (`12×6`, `$D28E`), clear of `—外伝—` |
| `bram_menu` horizontal (`b0a_menus[8..11]`, `[30]`) | `8` (`10` max) / `20` (`[30]`) | `4` | Patched horizontal `B$09` box (`12×10`, `$D2BD`), printing `b0a_menus[8..11]`; prompt `[30]` above box up to `20` cols; `b0a_menus[21..29]` bypassed legacy slices |
| `credits_bg34` (`b11_bg34_credits`) | `5–20` | `1` | `title_credits`: `C05` (`cols 6..11`) = `5` cols before `C19` (`20` cols); `ending_slideshow`: top role `20` cols, bottom cast name `14` cols (`cols 18..31`); `ending_credits`: left role `10` cols before staff col |
| `ending_nar` (`b11_ending_nar`) | `28` | `1` each | Full-width bottom narration lines (`C` screen `ending_slideshow` / epilogue) |
| `staff_roll` (`b1b_staff[0..39]`) | `16` | `scrolling` | Starts at col `16` on 32-col screen (`cols 16..31`) |
| `password` (`b09_password`) & Name (`b0a_menus[0..4]`) | `20–24` | `5` / `4+1` | Kept in-place in Phase 5; convert to English picker grid in Phase 6/7 alongside `B$09` input decode adjustment |
