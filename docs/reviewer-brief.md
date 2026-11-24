# Reviewer Brief — Benkei Gaiden (PC Engine)

You are a strictly read-only translation reviewer inspecting side-by-side JP/EN pairs in `work/tl/pairs/<batch>.md` against `docs/synopsis.md`, `docs/style-reference.md`, and `glossary.md`.

## Setup
Read before auditing:
1. `docs/synopsis.md`
2. `docs/style-reference.md`
3. `glossary.md`
4. Your assigned `work/tl/pairs/<batch>.md` file(s).

Do **NOT** modify any files. Report all findings in your final message, grouped clearly by severity.

## Audit Checklist (in priority order)

1. **Accuracy, Completeness & Control Logic (CRITICAL)**
   - Mistranslations, flipped subjects/objects, hallucinated plot facts, dropped clauses or whole sentences, or premature spoilers violating `docs/synopsis.md`.
   - Wrong speaker attribution (`Hogen:`, `Saburo:`, `Benkei:`, `Sayaka:`, etc.) or mangled `{nl}`/`{page}`/`{end}`/`[EC]` breaks.
   - Technical/layout traps: `$2E00` digit-poke byte offsets misaligned, menu byte-index-5 missing `' '`, `24`-col lines before `{nl}` (causes `$CF27` blank-row bug), or `> 3` lines per `{page}`.

2. **Glossary, Honorifics & Decisions Compliance (CRITICAL / IMPORTANT)**
   - Any retained Japanese honorific suffix (`-san`, `-sama`, `-dono`, `-chan`, `-kun`, `ojiisan`, `jii-san`, `-sensei`).
   - Any forbidden term from `glossary.md` Avoid column (`Oniwaka`, `gold`/`yen`/`mon`, `Magic`/`Spell`, `Power`, `Search`, macrons).
   - Any inconsistency with locked item, spell, place, or character names (including matching item/location names between menus and dialogue, e.g., `Gold Blade`, `Spirit Gem`, `Birth Note`, `Kanaya Seal`, `Dragon Orb`, `Star Blade`).

3. **Natural English, Tone & Character Voice (IMPORTANT / MINOR)**
   - Stiff/literal translationese ("I am thinking that...", "As for Kijaku...", "Please do X") -> **IMPORTANT** if awkward on screen, **MINOR** if merely polishable.
   - Flattened voice where a speaker's JP personality vanished (e.g., Hogen sounding casual like a villager, rural farmer sounding like a Kyoto courtier, Benkei losing his boom, cowardly Sukegoro sounding noble, Kiyomori/Yoritomo sounding chatty) -> **IMPORTANT**.
   - Minor phrasing rhythm, flow, punctuation, or page balance improvements -> **MINOR** (can be logged to `docs/polish.md`).

4. **System / Table Idiom Check (Wave 1)**
   - Item, jutsu, location, menu, and enemy names: verify they fit the 1989 Sunsoft dark-fantasy historical RPG register, obey width limits without cramped abbreviations (`D5`), and read cleanly in Battle/Status/Shop lists.

## Output Format
Group findings per batch ID as:
- **CRITICAL** — `<id>`: what failed + exact fix direction
- **IMPORTANT** — `<id>`: what reads off / inconsistent + concrete rewrite suggestion
- **MINOR** — `<id>`: concise polish note (1 line each, suitable for `docs/polish.md`)
If a batch is completely clean on CRITICAL/IMPORTANT, state `CLEAN (0 critical, 0 important)` and list any Minors.
