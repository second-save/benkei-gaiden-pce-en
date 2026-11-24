# Benkei Gaiden (PC Engine) — English Translation

Unofficial archival and historical English fan translation of ***Benkei Gaiden*** (*弁慶外伝*, PC Engine / TurboGrafx-16 HuCard, Sunsoft, 1989).

> **Players:** Download `benkei-gaiden-pce-en.zip` and apply `benkei-gaiden-pce-en.bps` to your own clean unheadered Japanese dump of *Benkei Gaiden*. No ROMs or copyrighted game data are included.

## Translation Status

| Part | Status | Notes |
|---|---|---|
| Dialogue & story (`b11_dialogue`, `b11_ending_nar`) | 100% translated | All `1,037` translated script/table entries (plus `MP` HUD label = `1,038` translated items) reviewed & merged |
| Menus, items, equipment, jutsu, enemies, locations, UI | 100% translated | Custom CC0 8×16 ASCII font in `BG[01]`, `1 MiB` HuCard expansion (`$60–$7E`), horizontal Title/Continue/BRAM menus, adjusted Battle Command & Enemy List layout |
| Tile-drawn graphics (`BG[23]`, `SPR[21]`, `SPR[24]`, `BG[15]`, `BG[16]`) | 100% translated | `DREAMS - CREATION - SUNSOFT` splash slogan, crimson brush `BENKEI GAIDEN` logo & bars, and wooden town shop signs (`Inn`, `WE/AP`, `IT/EM`, `AR/MR`, `KANAYA`) |
| Ending staff credits roll & opening story crawl | 100% translated | Dynamic opening prologue (`b11_dialogue_512..528`), ending slideshow captions, and full staff credits (`b11_bg34_credits`, `b1b_staff`) |
| Password & Backup RAM ASCII grids | 100% translated | Full English ASCII entry grids (`b0a_menus[0..3]`, `b09_password`), Backup RAM save slots, and secret passwords (`SOUNDTEST`, `DEBUGMODE`) |

Known issues: none known.

## Required Japanese Base ROM

Verify your dump before patching:

- **Filename:** `Benkei Gaiden (Japan).pce` (No-Intro unheadered HuCard)
- **Size:** `393,216` bytes (`0x60000`)
- **CRC32:** `e1a73797`
- **SHA-1:** `4bc46592f3707a7c3e514abc23e640e3194879ad`

If your dump has a 512-byte copier header (`393,728` bytes), strip the first 512 bytes before applying the `.bps` patch.

## How to Patch & Play

Apply `benkei-gaiden-pce-en.bps` to your clean unheadered Japanese `.pce` file using any standard BPS patcher:

- **GUI / Web:** [Flips](https://github.com/Alcaro/Flips) or [RomPatcher.js](https://www.marcrobledo.com/RomPatcher.js/)
- **Command line (from this repo):**
  ```sh
  python3 -X utf8 tools/bps.py apply "rom/Benkei Gaiden (Japan).pce" release/benkei-gaiden-pce-en.bps benkei-en.pce
  ```

| File | Size | CRC32 | SHA-1 |
|---|---:|---|---|
| `benkei-gaiden-pce-en.bps` | `336,813` B | `2144df1c` | `bfb3ae7ec6b32afe43dfd965f26012fab357c2d1` |
| Patched `.pce` (`1 MiB` HuCard) | `1,048,576` B | `d99929aa` | `9e6ffc62d11803408dfceb9ad96cfcd32cbafcee` |

> **Emulator & Save Notes:** Tested in **MesenCE 2.2.1** across cold-boot startup (`splash`, `title_credits`, `title_logo`, `title_menu`), opening story crawl & Rinsho-ji cutscene, field/status/item/jutsu/equip/shop/battle menus, Backup RAM saves, Travel Log & Test Mode passwords, ending slideshow, ending staff credits, and 25 cold-boot scenes (not yet tested on real PC Engine hardware or flashcart). Always start from a **cold boot**; savestates from the unpatched Japanese ROM are incompatible.

### Controls & Helpful Tips

- **Title Menu (`New Game` / `Continue`):** Choose **Continue** for Backup RAM save slots (`Benkei 1`–`3`) or Travel Log **Password** entry (`ASCII` grid).
- **Secret Passwords:** Entering **`SOUNDTEST`** on the Password / Name grid opens the Sound Test; **`DEBUGMODE`** enables Test Mode (`Pause`, `Enemies`, `NPC Clip`, `Map Clip`, `Speed`, `Password`, `Sound`).

## What's Here (Source Repository)

| Path | What it is |
|---|---|
| `tools/build.py` | Master ROM builder (`identity`, `expand`, `marker`, `translate` modes) |
| `asm/` | WLA-DX HuC6280 1 MiB bank expansion, far-string hook, and horizontal menu patches |
| `script/` | Extracted Japanese & translated English text tables (`14` groups, `1,217` extracted entries) |
| `tbl/` | Character tables (`en.tbl`, `jp_base.tbl`, `jp_ef/ed/fd.tbl`, `jp_bg34_ed/fd.tbl`) |
| `tools/` | Pure-Python stdlib tooling: extract, lint/fit checks, `BG[01]` font, translated graphics (`gfx_en.py`), BPS patcher, release packager (`release.py`), MesenCE debug harness (`tools/debug/`) |
| `tests/` | `unittest` suite covering ROM integrity, text codec/batch checks, identity rebuild, engine hooks, graphics, and release packaging |
| `docs/` | Reverse-engineering notes (`docs/re/`), design rulings (`docs/decisions.md`), status & polish logs |
| `glossary.md` | Binding names, historical spellings, and UI/terminology rules |

## Build From Source

Requires Python 3.12+ (pure stdlib; optional `pillow` / `numpy` for PNG sheet tools) and your own verified Japanese dump at `rom/Benkei Gaiden (Japan).pce`:

```sh
python3 -X utf8 tools/check.py                                   # verify base ROM hash, batch lint, and unit tests
python3 -X utf8 tools/batches.py check --script                  # validate merged script/*.json directly
python3 -X utf8 tools/build.py translate --out build/benkei_en.pce
python3 -X utf8 tools/release.py --force                         # run release gates, build & verify .bps and .zip
```

## Credits & Licence

- **Archival Translation, Engineering & AI Assistance:** `second-save` (assisted by AI translation and reverse-engineering workflows; all scripts, layouts, and builds verified programmatically and visually in MesenCE).
- **Original Game:** *Benkei Gaiden* © 1989 Sunsoft (with Hiroshi Motomiya / Motomiya Kikaku). This project is an unofficial, non-commercial fan translation for archival and historical preservation and is not affiliated with Sunsoft.
- **Licence:** Build tools and original English translation text are released under the MIT Licence ([`LICENSE`](LICENSE)). Original Japanese script data in `script/` belongs to Sunsoft and is included solely to verify extraction and translation accuracy. Do not distribute copyrighted ROMs.
