# Status

Updated at the end of every session/phase. Keep it to what the next session needs; history is in git.

- **Phase:** **Phase 8 (Polish Pass, Remaining Live QA Spot-Checks, Docs Sync & Release Packaging) COMPLETE — Ready for release.**
- **Done:**
  - Verified base ROM (`rom/Benkei Gaiden (Japan).pce`, 393,216 B / 48 × 8 KiB banks, CRC32 `e1a73797`, SHA-1 `4bc46592f3707a7c3e514abc23e640e3194879ad`) and booted cleanly in MesenCE 2.2.1 (`tools/run_emu.py`).
  - Audited all 48 banks, text routines (`$FDEF`/`$FE2A`/`$FE08`), 4 planes (`r74` = `$00`/`$20`/`$FD`/`$1D`), and `BG[34]` overlay; built `tbl/jp_{base,ef,ed,fd,bg34_ed,bg34_fd}.tbl`, `tools/pce_text.py` (all 1,217 ROM strings across 14 groups + pointer tables `PTR_TABLES`, `CREDITS_PTR_TABLE`, `CHAR_NAME_PTR_TABLE`), `tests/test_text.py`, and `docs/re/text_engine.md`.
  - Documented HuCard 48-bank mapping & built/smoke-tested 1 MiB expansion layout (`384 KiB` free in `$30..$3F` & `$60..$7F`) in `docs/re/rom_map.md`.
  - Audited all 36 `BG` & 25 `SPR` assets (`$D4A9`/`$D62A`); updated `docs/re/graphics_text.md` with all 5 shipped English tile/sprite redraws (`BG[23]`, `SPR[21]`, `SPR[24]`, `BG[15]`, `BG[16]`); documented `$2000–$3FFF` WRAM, Password, and BRAM `$F7` formats in `docs/re/ram_map.md`.
  - Built cold-boot debug warp & QA harness (`tools/debug/{scenes.lua,warp.lua,warp.py}` + `tests/test_debug.py`) reaching 25 cold-boot scenes with savestates exported to `work/states/*.mss`.
  - Built Phase 3 Identity pipeline (`tools/pce_gfx.py`, `asm/identity.asm`, `tools/build.py`, `tests/test_identity.py`): byte-identical 384 KiB rebuild, 1 MiB WLA-DX expansion (`sha1=0f2460be25a8c372b728866e71a8aeaac2bd632e`), and 25/25 pixel-identical cold-boot scenes in MesenCE.
  - Built Phase 4 extractor (`tools/extract.py` + `tests/test_extract.py`) generating `script/*.json` (`1,217` extracted entries: `1,037` translated `done` + `1` synthetic `en_mid`, `114` bypassed `todo` in `b0a_menus[21..25,27..29]` / `b0d_enemy_kana`, `6 keep`, `60 data`) with full pointer/code slot tracking and byte-exact roundtrip.
  - Completed Phase 5 Engine Spike (`tbl/en.tbl`, `tools/font_en.py`, `tools/pce_text.py` `EnCodec`, `asm/engine_{b00,b02,b09}.asm`, `tools/build.py`, `tools/windows.json`, `docs/re/windows.md`, `tests/test_engine.py`): 84-glyph CC0 8×16 font in `BG[01]`, `$FC <bank> <lo> <hi>` far-string hooks (`$61..$7E`), dedicated `B$60` enemy table, horizontal Title/Continue/BRAM menus (`B$09:$D28E`/`$D2BD`), and 25/25 marker scenes verified in MesenCE.
  - Completed Phase 6 Translation (`glossary.md`, `docs/{synopsis,style-reference,translator-brief,reviewer-brief,story-reviewer-brief,polish}.md`, `tools/fit.py`, `tools/batches.py`, `tests/test_batches.py`): translated, line-reviewed, story-reviewed, and merged all 10 batches (`b001`–`b010`).
  - Completed Phase 7 (`tools/gfx_en.py`, `tests/test_gfx_en.py`, `tools/build.py` translate mode): ASCII Travel Log (`b0a_menus[0..3]`, 77 B at `0x1509C`, no `'0'`) & Test Mode (`b09_password`, 112 B at `0x12613`) grids, secret passwords (`SOUNDTEST`, `DEBUGMODE`), `$FDEF` coordinate shifts (`0x1376E`, `0x1386D`, `0x13874`, `0x12F66`), Battle Command & Enemy List layout fix (`Jutsu Item`, 10 cols), and all 5 graphics redrawn within budget (`BG[23]` 621/648 B, `BG[15]` 5048/5052 B, `BG[16]` 5211/5299 B, `SPR[21]` 1576/2388 B, `SPR[24]` 148/302 B); 25/25 cold-boot scenes passed (`warp.py --all`).
  - Completed Phase 8 Polish, Spot-Checks & Release Packaging:
    - Applied `docs/polish.md` fixes (`b0e_battle_011_1C559` -> `" damage!{end}"`, `b0e_items_043_1C342` -> `"Bamboo Cuff{end}"`) and ticked all items `- [x]` in `docs/polish.md`.
    - Live-verified in MesenCE: passive cold-boot prologue crawl (`b11_dialogue_512..528`, `work/qa/p8_prologue`), Test Mode 5-row `b09_password` ASCII grid (`work/qa/p8_testpw`), and `KANAYA` (`work/qa/p8_kyoto_mkt/f000630.png`, `work/qa/p8_kamakura6/f001440.png`), `Inn`, and `IT/EM` town signs (while `WE/AP` and `AR/MR` are verified via preview PNGs and `tests/test_gfx_en.py`).
    - Added `tools/release.py` and `tests/test_release.py`, synced `README.md` and `docs/re/graphics_text.md`, and built/verified `build/benkei_en.pce` (`1,048,576` B, `CRC32=d99929aa`, `SHA1=9e6ffc62d11803408dfceb9ad96cfcd32cbafcee`) + `release/benkei-gaiden-pce-en.bps` (`336,813` B, `CRC32=2144df1c`, `SHA1=bfb3ae7ec6b32afe43dfd965f26012fab357c2d1`) + `release/benkei-gaiden-pce-en.zip`.
- **Next:**
  - Complete. Optional follow-ups only if requested by the user (e.g., publishing GitHub repo/release or capturing trailer screenshots).
- **Open bugs:** None.
- **Waiting on the user:** Nothing (ready for handoff).
