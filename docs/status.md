# Status

Updated at the end of every session/phase. Keep it to what the next session needs; history is in git.

- **Phase:** Step 0, **Phase 1 (RE)**, **Phase 2 (Debug)**, **Phase 3 (Identity)**, & **Phase 4 (Extract) COMPLETE** -> Phase 5 (Engine Spike & Marker Build) next.
- **Done:**
  - Verified base ROM (`rom/Benkei Gaiden (Japan).pce`, 393,216 B / 48 × 8 KiB banks, SHA-1 `4bc46592f3707a7c3e514abc23e640e3194879ad`) and booted cleanly in MesenCE 2.2.1 (`tools/run_emu.py`).
  - Audited all 48 banks, text routines (`$FDEF`/`$FE2A`/`$FE08`), 4 planes (`r74` = `$00`/`$20`/`$FD`/`$1D`), and `BG[34]` overlay; built `tbl/jp_{base,ef,ed,fd,bg34_ed,bg34_fd}.tbl`, `tools/pce_text.py` (all 1,217 ROM strings across 14 groups + pointer tables `PTR_TABLES`, `CREDITS_PTR_TABLE`, `CHAR_NAME_PTR_TABLE`), `tests/test_text.py`, and `docs/re/text_engine.md`.
  - Documented HuCard 48-bank mapping & built/smoke-tested 1 MiB expansion layout (`384 KiB` free in `$30..$3F` & `$60..$7F`) in `docs/re/rom_map.md`.
  - Audited all 36 `BG` & 25 `SPR` assets (`$D4A9`/`$D62A`); cataloged all tile-drawn Japanese graphics (`BG[23]`, `SPR[21]`, `SPR[24]`, `BG[15]`, `BG[16]`) and `BG[34]` font-rendered screens in `docs/re/graphics_text.md`; documented `$2000–$3FFF` WRAM, Password, and BRAM `$F7` formats in `docs/re/ram_map.md`.
  - Built cold-boot debug warp & QA harness (`tools/debug/{scenes.lua,warp.lua,warp.py}` + `tests/test_debug.py`) reaching 25 cold-boot scenes with savestates exported to `work/states/*.mss`.
  - Built Phase 3 Identity pipeline (`tools/pce_gfx.py`, `asm/identity.asm`, `tools/build.py`, `tests/test_identity.py`): byte-identical 384 KiB rebuild, 1 MiB WLA-DX expansion (`sha1=0f2460be25a8c372b728866e71a8aeaac2bd632e`), and 25/25 pixel-identical cold-boot scenes in MesenCE.
  - Built Phase 4 extractor (`tools/extract.py` + `tests/test_extract.py`) generating `script/*.json` (`1,217` total: `1,151 todo`, `6 keep`, `60 data`) with full pointer/code slot tracking, overwrite refusal without `--force`, byte-exact roundtrip, and 100% zero-gap coverage across all 9 text regions (`0x1C032..0x23F92` in `B$0E..$11`) and all 299 `$FDEF`/`$FE2A`/`$FE08` calls.
  - Updated `glossary.md` with verified Phase 1 characters, locations, currency (`sen`), and UI terms.
- **Next:** Phase 5 — Engine Spike, 8×16 ASCII Font (`BG[01]`), Bank-$60..$7F Extended Dialogue Relocation, Marker Build, & Width Gate across all box variants.
- **Open bugs:** None.
- **Waiting on the user:** Nothing (pre-approved per D7).
