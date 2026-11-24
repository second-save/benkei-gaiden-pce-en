# Status

Updated at the end of every session/phase. Keep it to what the next session needs; history is in git.

- **Phase:** Steps 0–5 & **Phase 6 (Translation Pipeline, Glossary, 1,029-Entry Translation, Line + Story Reviews & Merge) COMPLETE** -> Phase 7 (Password/Name Entry ASCII Grid, Ending/Menu Coordinate Polish, 5 Tile Graphics, Full English Insertion & MesenCE QA) next.
- **Done:**
  - Verified base ROM (`rom/Benkei Gaiden (Japan).pce`, 393,216 B / 48 × 8 KiB banks, SHA-1 `4bc46592f3707a7c3e514abc23e640e3194879ad`) and booted cleanly in MesenCE 2.2.1 (`tools/run_emu.py`).
  - Audited all 48 banks, text routines (`$FDEF`/`$FE2A`/`$FE08`), 4 planes (`r74` = `$00`/`$20`/`$FD`/`$1D`), and `BG[34]` overlay; built `tbl/jp_{base,ef,ed,fd,bg34_ed,bg34_fd}.tbl`, `tools/pce_text.py` (all 1,217 ROM strings across 14 groups + pointer tables `PTR_TABLES`, `CREDITS_PTR_TABLE`, `CHAR_NAME_PTR_TABLE`), `tests/test_text.py`, and `docs/re/text_engine.md`.
  - Documented HuCard 48-bank mapping & built/smoke-tested 1 MiB expansion layout (`384 KiB` free in `$30..$3F` & `$60..$7F`) in `docs/re/rom_map.md`.
  - Audited all 36 `BG` & 25 `SPR` assets (`$D4A9`/`$D62A`); cataloged all tile-drawn Japanese graphics (`BG[23]`, `SPR[21]`, `SPR[24]`, `BG[15]`, `BG[16]`) and `BG[34]` font-rendered screens in `docs/re/graphics_text.md`; documented `$2000–$3FFF` WRAM, Password, and BRAM `$F7` formats in `docs/re/ram_map.md`.
  - Built cold-boot debug warp & QA harness (`tools/debug/{scenes.lua,warp.lua,warp.py}` + `tests/test_debug.py`) reaching 25 cold-boot scenes with savestates exported to `work/states/*.mss`.
  - Built Phase 3 Identity pipeline (`tools/pce_gfx.py`, `asm/identity.asm`, `tools/build.py`, `tests/test_identity.py`): byte-identical 384 KiB rebuild, 1 MiB WLA-DX expansion (`sha1=0f2460be25a8c372b728866e71a8aeaac2bd632e`), and 25/25 pixel-identical cold-boot scenes in MesenCE.
  - Built Phase 4 extractor (`tools/extract.py` + `tests/test_extract.py`) generating `script/*.json` (`1,217` total: `1,151 todo`, `6 keep`, `60 data`) with full pointer/code slot tracking, overwrite refusal without `--force`, byte-exact roundtrip, and 100% zero-gap coverage across all 9 text regions (`0x1C032..0x23F92` in `B$0E..$11`) and all 299 `$FDEF`/`$FE2A`/`$FE08` calls.
  - Completed Phase 5 Engine Spike (`tbl/en.tbl`, `tools/font_en.py`, `tools/pce_text.py` `EnCodec`, `asm/engine_{b00,b02,b09}.asm`, `tools/build.py` `marker`/`translate`, `tools/windows.json`, `docs/re/windows.md`, `tests/test_engine.py`): 84-glyph CC0 8×16 font patched into `BG[01]` (`6277 B <= 6481 B`), `$FC <bank> <lo> <hi>` far-string hooks into Banks `$61..$7E`, dedicated `B$60` enemy table (furigana skipped cleanly), `SafeWait_E2C0`/`SafeWait_EF33` MPR guards, `Hook_F915` in fixed `B$00`, horizontal Title/Continue/BRAM menus (`B$09:$D28E`/`$D2BD`), and 3-char `shop_item` Sen label (`Inc11By3`); all 25/25 marker scenes and 84/84 live PCE glyphs visually verified in MesenCE.
  - Completed Phase 6 Translation (`glossary.md`, `docs/{synopsis,style-reference,translator-brief,reviewer-brief,story-reviewer-brief,polish}.md`, `tools/fit.py`, `tools/batches.py`, `tests/test_batches.py`): split, hand-translated, line-reviewed, story-reviewed, fixed, and merged all 10 batches (`b001`–`b010`: `1,028` `script/*.json` entries + synthetic `b02_sys_026_mid` = `1,029` entries marked `done`); verified `tools/batches.py check --script` (`OK`) and `tools/check.py` (29 tests `OK`), and updated `tools/build.py` to compile both `todo` and `done` entries plus `en_mid` and bypassed `b0a_menus[21..29]`.
- **Next (Phase 7):**
  - Convert Password / Name Entry grid (`b09_password` 5 rows, `b0a_menus[0..3]` 4 rows) + `B$09:$C5DF`/`$C8E8` ASCII decode for player naming & password entry.
  - Adjust ending/menu `$FDEF` X-coordinates (`0x1376E` `C20` `Motomiya Kikaku` `x=8->2` before `C19` `H. Motomiya` at `x=18`; check `0x1386C`/`0x13873` `C01`/`C07` on ending card and `0x12F66` `b11_dialogue_424` `$2C00` spacing after comma).
  - Translate & redraw all 5 tile-drawn Japanese graphics (`BG[23]`, `SPR[21]`, `SPR[24]`, `BG[15]`, `BG[16]`).
  - Run full `tools/build.py translate` + MesenCE 25-scene visual QA, minor polish pass (`docs/polish.md`), and IPS/release packaging.
- **Open bugs:** None.
- **Waiting on the user:** Nothing (pre-approved per D7).
