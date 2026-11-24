# Status

Updated at the end of every session/phase. Keep it to what the next session needs; history is in git.

- **Phase:** Step 0, **Phase 1 (Reverse Engineering)**, & **Phase 2 (Cold-Boot Debug Warp Tool & Capture Harness) COMPLETE** -> Phase 3 (Identity Build) next.
- **Done:**
  - Verified base ROM (`rom/Benkei Gaiden (Japan).pce`, 393,216 B / 48 × 8 KiB banks, SHA-1 `4bc46592f3707a7c3e514abc23e640e3194879ad`) and booted cleanly in MesenCE 2.2.1 (`tools/run_emu.py`).
  - Audited all 48 banks, text routines (`$FDEF`/`$FE2A`/`$FE08`), 4 planes (`r74` = `$00`/`$20`/`$FD`/`$1D`), and `BG[34]` overlay; built `tbl/jp_{base,ef,ed,fd,bg34_ed,bg34_fd}.tbl`, `tools/pce_text.py` (1,213 ROM strings round-trip verified), `tests/test_text.py`, and `docs/re/text_engine.md`.
  - Documented HuCard 48-bank mapping & built/smoke-tested 1 MiB expansion layout (`384 KiB` free in `$30..$3F` & `$60..$7F`, 2,600 frames verified in MesenCE) in `docs/re/rom_map.md`.
  - Audited all 36 `BG` & 25 `SPR` assets (`$D4A9`/`$D62A`); cataloged all tile-drawn Japanese graphics (`BG[23]`, `SPR[21]`, `SPR[24]`, `BG[15]`, `BG[16]`) and `BG[34]` font-rendered screens in `docs/re/graphics_text.md`; documented `$2000–$3FFF` WRAM (including shared `$2300` consumable & `$2310` equipment bags), Password, and BRAM `$F7` formats in `docs/re/ram_map.md`.
  - Built cold-boot debug warp & QA harness (`tools/debug/{scenes.lua,warp.lua,warp.py}` + `tests/test_debug.py`) supporting `GOD`/`NOENC`/`NOCLIP`/`FAST` and 25 cold-boot scenes (`splash`, `title_credits`, `title_logo`, `title_menu`, `bram_menu`, `password`, `test_mode`, `rinsho_intro`, `overworld`, `field_menu`, `status_full`, `items_menu`, `jutsu_menu`, `equip_menu`, `tsukumo_town`, `shop_item`, `kyoto`, `kamakura`, `nagasaki`, `dungeon`, `battle_spider`, `battle_party`, `game_over`, `ending_slideshow`, `ending_credits`), all 25/25 passing `--smoke` and visual sheet inspection with savestates exported to `work/states/*.mss`.
  - Updated `glossary.md` with verified Phase 1 characters, locations, currency (`sen`), and UI terms.
- **Next:** Phase 3 — Identity Build (`build/benkei_test.pce` 1 MiB byte-identical rebuild via `wla-huc6280` / `wlalink` / Python builder) & Phase 4 (Text Extraction).
- **Open bugs:** None.
- **Waiting on the user:** Nothing (pre-approved per D7).
