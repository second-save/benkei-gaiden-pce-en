# Translator Brief — Benkei Gaiden (PC Engine)

Translate your assigned batch file(s) `work/tl/<batch>.in.tsv` into `work/tl/<batch>.out.tsv`, line by line, in natural, distinctive English matching `docs/style-reference.md`.

## Files & Context to Read First
1. `docs/synopsis.md` — complete story arc so foreshadowing, reveals, and stakes land cleanly.
2. `docs/style-reference.md` — tone, voice register table, and approved pilot slice.
3. `glossary.md` — canonical names, terms, UI labels, and Avoid list.
4. `work/tl/<batch>.in.tsv` — your assigned batch (columns: `id`, `box`, `max`, `terms`, `jp`, `en`, `notes`).

## Output Rules (Strict)
1. **Format:** Write `work/tl/<batch>.out.tsv` directly using `write_file`. Keep the exact TSV header (`id\ten`) or the full columns from `<batch>.in.tsv`, with **every ID in exact order** and every `en` cell populated. Never leave blank `en`, `TODO`, or untranslated Japanese characters (`hiragana`, `katakana`, or `kanji`).
2. **Craft each line by hand:** Never use scripts, regexes, or bulk find/replace to mass-rewrite prose. Translate faithfully with zero dropped clauses, zero invented plot details, and distinct character voices.
3. **Read-only shared files:** Do **NOT** edit `script/*.json`, `glossary.md`, `tools/*`, `docs/*`, or any other batch file.
4. **Control Codes & Tokens:**
   - Preserve exact control semantics (`{nl}`, `{page}`, `{end}`, `[EC]`).
   - `{end}` must appear at the very end **iff** it appears in `jp` (`b0d_enemy_kanji` entries have **no** `{end}`; keep none).
   - `[EC]` count and placement must match any palette/control requirements noted in the row (`b0a_menus[4]`, `b11_bg34_credits`).
5. **Character Set (`tbl/en.tbl`):** Only characters in the 84-glyph ASCII subset (`A-Z`, `a-z`, `0-9`, space, `?"!:-_/.,;+*\'()[]&%#~`) plus `{nl}`, `{page}`, `{end}`, `[EC]`. Use straight quotes `'` and `"`, no curly quotes, no em-dashes (`--` or ` - ` or `-`), and no non-ASCII characters.
6. **Box Width & `$CF27` Auto-Wrap Rule:**
   - For dialogue (`24x3` lines per `{page}`): **`{nl}` must follow lines of at most `23` columns** (`24` chars before `{nl}` triggers `$CF27` auto-wrap plus `{nl}`, creating an unintended blank row!). A final line before `{page}` or `{end}` may use all `24` columns. At most **`3` lines per `{page}`**.
   - Check the `max` column and `notes` column on every row:
     - **Two-column menus** (`b02_sys[0..2]`, `b02_sys[17..18]`): **byte index `5` MUST be `' '`** (space) so the cursor pearl lands between columns cleanly (max 5 cols left + space + max 5 cols right).
     - **Equippable & Key Items** (`b0e_items[0..85]`): hard cap **`11` columns**. Do not abbreviate awkwardly (`Kanaya Seal`, `Birth Note`, `Siren Tear`, `Dream Lens`).
     - **First-line shop prompt** (`b11_dialogue_050_1CE27`): line 1 max **`14` columns** (`Sen` box overlaps top-right).
     - **Runtime digit pokes (`$2E00`):** Leave exact `' '` (or `'0'`) placeholders in the byte slots noted in `notes`:
       - `b02_sys_053_05F87`: 5 spaces at offset `7..11` (`"Gained       EXP!{end}"`, digits printed at screen col `$0B`).
       - `b02_sys_054_05F99`: 5+ spaces starting at offset `5` (`"Got        sen!{end}"`, digits printed at screen col `$0B`).
       - `b11_dialogue_237_1F0BD`: 3 spaces at byte offsets `4..6` (`"Cost   sen to stay?{nl}Rest tonight?{end}"`).
       - `b11_dialogue_566_22EA9`: 3 spaces at offsets `3..5` + `'0'` at offset `6` (`"Got   0 sen!{end}"`).
       - `b11_dialogue_601_23289`: 5 spaces at offsets `3..7` (`"For     sen, I can..."`).
7. **Rulings (`docs/decisions.md`):**
   - Drop Japanese honorifics (`-san`, `-sama`, `-dono`, `-chan`, `-kun`, `ojisan`, `jii-san`).
   - Standard Hepburn without macrons; `Kijaku` (never `Oniwaka`); `sen` (lowercase in prose, `Sen` HUD).
   - No ugly abbreviations (`Stats`, `Items`, `Equip`, `Check`, `Jutsu`, `Password`, `Save RAM`).

## Self-Check Before Finishing
Run:
```sh
python3 -X utf8 tools/batches.py check <batch>
```
Fix every error (`width`, `charset`, `tokens`, `glossary`, `honorifics`, `pokes`, `cursor`) until it prints `OK` with exit code `0`. If you notice a genuinely recurring term missing from `glossary.md`, report it in your completion message rather than editing `glossary.md`.
