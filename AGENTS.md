# Benkei Gaiden (PC Engine) English translation

Skill: translate-retro-game (`~/.agents/skills/translate-retro-game/SKILL.md`; `python3 -X utf8 tools/skill.py`). Read it before ROM, text or QA work.
Hooks setup on fresh clone: `git config core.hooksPath tools/hooks`.

## Commands (run from repo root)
- Check: `python3 -X utf8 tools/check.py` (pre-commit hook runs this)
- Smoke: `python3 -X utf8 tools/run_emu.py "rom/Benkei Gaiden (Japan).pce" --out work/qa/smoke --route tools/routes/boot.txt --shot-every 60 --smoke --sheet`

## Paths
- Original ROM: `rom/Benkei Gaiden (Japan).pce` (gitignored; SHA-1 `4bc46592f3707a7c3e514abc23e640e3194879ad` in `rom.sha1`).
- Emulator: `tools/mesen/Mesen.app/Contents/MacOS/Mesen` (MesenCE 2.2.1 macOS ARM64). Assembler: `wla-huc6280` / `wlalink` (wla-dx 10.7).
- Rulings: `docs/decisions.md`. Glossary: `glossary.md`. RE notes index: `docs/re/README.md`.

## Rules
- Edit source files (`.py .lua .asm .s .tbl .json`) only with the file-edit tool; never shell heredocs or `sed -i`.
- Use `python3 -X utf8` for scripts; `python3.14` when Pillow/numpy/capstone are needed.
- Always run `tools/run_emu.py` against a `.txt` route file (never an inline string).

## Status
`docs/status.md`: done, next, open bugs. Update at the end of every phase/session.
