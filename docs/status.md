# Status

Updated at the end of every session/phase. Keep it to what the next session needs; history is in git.

- **Phase:** Step 0 (Repo setup) & **Phase 1 (Reverse Engineering & Recon) COMPLETE** -> Phase 2 (Cold-Boot Debug Warp Tool & Capture Harness) next.
- **Done:**
  - Verified base ROM (`rom/Benkei Gaiden (Japan).pce`, 393,216 B / 48 × 8 KiB banks, SHA-1 `4bc46592f3707a7c3e514abc23e640e3194879ad`) and booted cleanly in MesenCE 2.2.1 (`tools/run_emu.py`).
  - Audited all 48 banks, text routines (`$FDEF`/`$FE2A`/`$FE08`), 4 planes (`r74` = `$00`/`$20`/`$FD`/`$1D`), and `BG[34]` overlay; built `tbl/jp_{base,ef,ed,fd,bg34_ed,bg34_fd}.tbl`, `tools/pce_text.py` (1,213 ROM strings round-trip verified), `tests/test_text.py`, and `docs/re/text_engine.md`.
  - Documented HuCard 48-bank mapping & built/smoke-tested 1 MiB expansion layout (`384 KiB` free in `$30..$3F` & `$60..$7F`, 2,600 frames verified in MesenCE) in `docs/re/rom_map.md`.
  - Captured live Rinsho-ji Temple, Overworld, Battle (`大ぐも`), Tsukumo Village (`九十九村(つくもむら)`), Field Menu, Full Status UI, Item Shop Menu, Sunsoft Splash, and Title states; documented `$2000–$3FFF` WRAM, Password, and BRAM `$F7` formats in `docs/re/ram_map.md`.
  - Audited all 36 `BG` & 25 `SPR` assets (`$D4A9`/`$D62A`); cataloged all tile-drawn Japanese graphics (`BG[23]` `SUNSOFT® 夢・創造・サンソフト`, `SPR[21]` `弁慶`, `SPR[24]` `ー外伝ー`, `BG[15]` `防`, `BG[16]` `宿`/`武`/`道`/`金屋`) and `BG[34]` font-rendered screens in `docs/re/graphics_text.md`.
  - Updated `glossary.md` with verified Phase 1 characters (`鬼若 -> Kijaku`, `法眼 -> Hogen`, etc.), locations (`林省寺 -> Rinsho-ji Temple`, `九十九村 -> Tsukumo Village`), currency (`銭 -> sen`), and UI terms.
- **Next:** Phase 2 — Build cold-boot debug warp tool & scripted/savestate capture harness (`Overworld`, `Town/Shop`, `Status`, `Battle`, `Save/Title/Credits`).
- **Open bugs:** None.
- **Waiting on the user:** Nothing (pre-approved per D7).
