# Polish Log — Benkei Gaiden (PC Engine)

Minor style, rhythm, and flavor notes logged during `pce_reviewer` and story-review passes, resolved and verified across Phases 7–8. Critical and Important items were resolved directly before batch merge.

## Wave 1 (System, Credits, Enemies, Locations, Equip, Items, Jutsu, Battle)

- [x] **`b0a_menus_004_150E9`**: Verified in `password/final.png` (`Up Dn  Rt Lt  Del End` renders cleanly inside `b0a_menus` box; `[EC]` renders as clean icon/space gap).
- [x] **`b0e_jutsu_000`/`001`**: Retained `Soul Break` / `Soul Surge` (consistent with `b0e_jutsu` spirit/magic style and `glossary.md`).
- [x] **`b0e_jutsu_019`**: Retained `Raise Might` (matches Attack/might buff sense; fits `11/11`).
- [x] **`b0e_items_007`**: Retained `Demon Blade` (`斬魔刀`, fits `11/11` alongside `Star Blade` / `Light Blade` family).
- [x] **`b0e_items_008`/`015`/`016`**: Retained `War Glaive` / `Apex Glaive` / `Naginata` per `glossary.md`.
- [x] **`b0e_items_042`/`043`**: **Applied** — unified `Bamboo Mail` (`竹の鎧`) + `Bamboo Cuff` (`竹の手甲`, changed from `Cane Bracer` in `b0e_items.json` and `b001.out.tsv`).
- [x] **`b0e_items_048`**: Retained `Moon Armor` (`月影の鎧`, harmonizes with Moonflower / Shadow clan terminology in dialogue).
- [x] **`b0e_battle_011`**: **Applied** — shortened `" damage taken!{end}"` -> `" damage!{end}"` so 3-digit hits on 6-char party members (`Kijaku: 120 damage!` = 19/24 cols) never wrap `!` onto line 2.
- [x] **`b0d_enemy_kanji_011`/`024`/`091..093`**: Retained `Monster Frog`, `Pale Skeleton`, and `Earth/Stone/Bronze Golem` (matches `b11_dialogue_074`/`277` `魔人`).
- [x] **`b11_bg34_credits` Phase 7 Layout**: **Applied & verified** — shifted `0x1376E` (`C20` `Motomiya Kikaku`) `x=8 -> x=2`, `0x1386D` (`C01`) `0B -> 08`, `0x13874` (`C07`) `10 -> 13`; visually verified in `title_credits`, `ending_slideshow`, and `ending_credits`. (`tbl/jp_bg34_fd.tbl` `30=籏` noted in extraction log.)

## Wave 2 (Dialogue Act 1)

- [x] **`b11_dialogue_013`/`031`/`047`/`056`/`063`/`069`** (`b003`): Reviewed; existing merged phrasing verified clean and natural within box limits (`fit.py` 0 errors).
- [x] **`b11_dialogue_094`/`104`/`116`/`117`/`138`/`143`/`158`** (`b004`): Reviewed; `glossary.md` spellings and voice cadence verified in story review (`b004`–`b006` pass).
- [x] **`b11_dialogue_167`/`171`/`179`/`184`/`193`/`208`/`241`** (`b005`): Reviewed; verse breaks and register verified clean in Act 1 continuity pass.
- [x] **`b11_dialogue_244`/`247`/`271`/`276`/`294`/`315`/`319`/`320`** (`b006`): Reviewed; Emperor lines, Regalia names, and page breaks verified clean.

## Wave 3 (Dialogue Act 2 & Finale)

- [x] **`b11_dialogue_325`/`328`/`342`/`346`/`364`/`378`/`383`/`389`/`400`** (`b007`): Reviewed; `Prism Diary` and dialogue registers verified in Act 2 story pass.
- [x] **`b11_dialogue_418`/`426`/`433`/`442`/`449`/`457`/`462`** (`b008`): Reviewed; `D2` honorific-free compliance and place names (`Yoshitsune Mound`) verified clean.
- [x] **`b11_dialogue_476`/`478`/`484`/`501`/`502`/`503`/`522..524`/`541`/`548`/`560`/`565`** (`b009`): Reviewed; cross-chapter echo (`028` / `522..524`) and Kanaya / Sayaka registers verified clean.
- [x] **`b11_dialogue_570`/`584`/`599`/`608`/`611`/`625`/`639`** (`b010`): Reviewed; finale wrapping and terminology verified clean.
- [x] **Phase 7/8 Runtime Coordinates Verified**: `$FDEF` `0x12F66` (`X=0C -> 0D` applied & verified in BRAM prompt), `0x11DBB` (`478`, `X=04` 24/24), `0x11F01` (`488`, `X=04` 24/24), `0x11B4A` (`570`, `X=04` 24/24), `0x37956`/`0x3795D` (`646`+`636`, `X=03`), `0x379B5` (`647`, `X=06`); plus Battle Command box/cursor (`0x115B6`, `0x1162C`, `0x11636`, `0x05998`, `0x11247`) fixed & visually verified in `battle_party` / `battle_spider`.
