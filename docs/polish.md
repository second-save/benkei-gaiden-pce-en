# Polish Log — Benkei Gaiden (PC Engine)

Minor style, rhythm, and flavor notes logged by `pce_reviewer` and story-review passes for post-merge pass consideration. Critical and Important items are resolved directly before batch merge and must not wait here.

## Wave 1 (System, Credits, Enemies, Locations, Equip, Items, Jutsu, Battle)

- **`b0a_menus_004_150E9`**: Verify during Phase 6/7 `B$09` password-grid work that `[EC]` in `Up[EC]Dn[EC] Rt[EC]Lt[EC] Del End` renders strictly as blank icon spacers (`Up/Down/Right/Left`).
- **`b0e_jutsu_000`/`001`**: Consider `Demon Break` / `Demon Surge` or `Bane Blast` / `Bane Surge` (`魔破`/`魔破過`) over `Soul Break`/`Soul Surge` if revisiting jutsu flavor.
- **`b0e_jutsu_019`**: Verify `B$08` effect of `豪昇` (Defense vs Attack boost -> `Raise Guard`/`Fortify` vs `Raise Might`).
- **`b0e_items_007`**: `Demon Blade` (`斬魔刀`) vs `Demonbane` (`9/11`) to clarify anti-demon weapon intent.
- **`b0e_items_008`/`015`/`016`**: Unify `Naginata` vs `Glaive` across `War Glaive`, `Apex Glaive` (`True Glaive`), and `Naginata`.
- **`b0e_items_042`/`043`**: Unify `Bamboo Mail` / `Cane Bracer` -> `Bamboo Cuff` (`11/11`).
- **`b0e_items_048`**: Check `月影の鎧` (`Moon Armor`) vs `Shadow Mail` once `b11_dialogue` locks `月影`.
- **`b0e_battle_011`**: ` damage taken!` (`14/24`) wraps `!` onto line 2 for 3-digit hits on 6-char party members (`Kijaku: 120 damage taken!`).
- **`b0d_enemy_kanji_011`/`024`/`091..093`**: Optional darker polish for `Monster Frog` (`Demon Toad`) and `Pale Skeleton` (`Death Skeleton`); keep `Earth/Stone/Bronze Golem` synchronized with `魔人` dialogue lines (`b11_dialogue_074`, `277`).
- **`b11_bg34_credits` Phase 7 Layout**: Shift `0x1376E` (`C20` `Motomiya Kikaku`) `x=8 -> x=2` before `C19` (`H. Motomiya` at `x=18`), and verify ending card `0x1386C`/`0x13873` (`C01`/`C07`) alignment + `tbl/jp_bg34_fd.tbl` `30=籏` doc note.

## Wave 2 (Dialogue Act 1)

- **`b11_dialogue_013`/`031`/`047`/`056`/`063`/`069`** (`b003`): Line-balance/phrasing polish (`Oh, you folks the new{nl}officials?{nl}Eh, you're not?`, `their keep` to echo `Kasumi Keep`, `is at our main shop`).
- **`b11_dialogue_094`/`104`/`116`/`117`/`138`/`143`/`158`** (`b004`): Optional `Lady Seira` consistency (`179`), `sorcery!` for Western `魔法` (`104`), `a comrade of Benkei` (`138`), consistent bare `Murakumo` (`143` vs `211`/`246`), differentiate Benkei's `Aye` from Hogen's (`158`: `Right, got it!` + uniform party-join `!` on `182`), varied rumor tags (`117`: `so they say.`).
- **`b11_dialogue_167`/`171`/`179`/`184`/`193`/`208`/`241`** (`b005`): Avoid repeated `must` (`167`), Dewa verse page-break balance (`171`), `Lady Seira` register parity (`179`), colon before `Overlord of Conquest` appositive (`184`), trim lone outer quotes on `193`, smoother passive cleanup (`208`, `241`).
- **`b11_dialogue_244`/`247`/`271`/`276`/`294`/`315`/`319`/`320`** (`b006`): Consolidate `247` onto 1 page (`the Yata{nl}Mirror and Yasakani`), Emperor gravitas (`244`, `320`), `fella`/`man` over `guy` (`294`), rural idiom (`315`), `fortune teller` vs `seer` across `044`/`134`/`277`.

## Wave 3 (Dialogue Act 2 & Finale)

- **`b11_dialogue_325`/`328`/`342`/`346`/`364`/`378`/`383`/`389`/`400`** (`b007`): Minor phrasing/register polish (`ancient tome` for `Prism Diary` `329`, `traveling with` on `346`, `Out at sea` `364`, `suspicious folk` `378`, continuous `Though guards stood watch... How could anyone...` `383`, `dead quite a while!` `389`, `Kindly show respect.` `400`).
- **`b11_dialogue_418`/`426`/`433`/`442`/`449`/`457`/`462`** (`b008`): `Yakkun` (`D2` diminutive nickname), `out there` (`426`), `anything, please tell us!` & keep `Yoshitsune Mound` unsplit (`433`), `lead them astray` (`442`), trim `alive` (`449`), ` is cured!` vs `'s poison faded!` (`457`), match Gedo's `I'll` contraction (`462`).
- **`b11_dialogue_476`/`478`/`484`/`501`/`502`/`503`/`522..524`/`541`/`548`/`560`/`565`** (`b009`): `How I've missed you...` (`476`), `bounced back!` (`478`), tighten `then or now!` (`484`), break `restore / light` (`501`), `grant you all` (`502`), `restore your strength` (`503`), `in just a few years` echo of `028` (`522..524`), poised Sayaka voice (`541` `really`/`truly`, `565`), polite Kanaya clerk (`548`), lowercase `Seven-Star power` consistency (`560` vs `412`/`444`).
- **`b11_dialogue_570`/`584`/`599`/`608`/`611`/`625`/`639`** (`b010`): `Drat! Caught off guard!` margin if `X=5` (`570`), orphan balance (`584`, `599`, `611`), `This is the Waking Fire!` (`608`), `this instant!` (`625`), tense match (`639` `was of help`).
- **Phase 7/8 Runtime Coordinates to Verify in QA**: `$FDEF` offsets `0x12F66` (`b11_dialogue_424` `,` + `$2C00` spacing), `0x11DBB` (`478`), `0x11F01` (`488`), `0x11B4A` (`570`), `0x37956`/`0x3795D` (`646`+`636`), and `0x379B5` (`647`).
