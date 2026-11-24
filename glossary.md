# Benkei Gaiden (PC Engine) — Project Glossary

Core rulings from `docs/decisions.md` and `AGENTS.md`:
- **D2 Honorifics:** Drop all Japanese honorific suffixes (`-san`, `-sama`, `-dono`, `-chan`, `-kun`, `ojisan`, `ojiichan`); use English titles (`Priest`, `Master`, `Lord`, `Emperor`) or warm direct address only when social/feudal register demands it.
- **D3 Romanization & Historical Terms:** Standard Hepburn without macrons (`Hogen`, `Kijaku`, `Yoshitsune`, `Yoritomo`, `Kiyomori`, `Rinsho-ji`, `Dannoura`, `Koromogawa`, `sen`). Do not convert `鬼若` (Oniwaka) into `Benkei` or `Oniwaka`: he is strictly `Kijaku` in dialogue/UI (with the historical reading noted only in dialogue lines explaining the kanji, if at all; keep `Kijaku` consistent everywhere).
- **D5 No Abbreviations:** Write full terms/titles cleanly (`Items`, `Stats`, `Equip`, `Check`, `Jutsu`, `Continue`, `Save RAM`, `Password`). Only box-width caps in `tools/windows.json` dictate short forms when a field cannot expand.
- **Box Limits (`tools/windows.json`):** Dialogue boxes are `24` columns × `3` lines per `{page}`. `$CF27` auto-wraps at col `24`, so any line ended by `{nl}` must be **`<= 23` columns** (`nl_max_cols: 23`). Two-column menu pairs (`b02_sys[0..2]`, `[17..18]`) require `' '` at **byte index 5**. Equip/Key items (`b0e_items[0..85]`) are capped at **`11` columns**.

## Canonical Terms

| JP | EN | max | notes | Avoid |
| --- | --- | --- | --- | --- |
| 鬼若 | Kijaku | 7 | Protagonist; foundling of Rinsho-ji | Oniwaka |
| 弁慶 | Benkei | 7 | Musashibo Benkei, warrior monk | Musashi |
| 沙夜香 | Sayaka | 7 | Maiden of Dewa Sanzan | Sayoko |
| 三郎 | Saburo | 7 | Ise Saburo, chief of Kasumi Band | Saburou |
| 伊勢三郎 | Ise Saburo | - | Saburo's full name | Ise Saburou |
| 法眼 | Hogen | 7 | High priest of Rinsho-ji | Hogen-sama, Father Hogen |
| 義経 | Yoshitsune | - | Minamoto no Yoshitsune; check status box max if capped | Yoshi |
| 源義経 | Minamoto no Yoshitsune | - | Full name in formal/dramatic dialogue | Minamoto Yoshitsune |
| 頼朝 | Yoritomo | - | Minamoto no Yoritomo | Yoritomo-sama |
| 源頼朝 | Minamoto no Yoritomo | - | Full name in formal dialogue | Minamoto Yoritomo |
| 平清盛 | Taira no Kiyomori | - | Vengeful Heike spirit; final mastermind | Taira Kiyomori |
| 清盛 | Kiyomori | - | Short reference to Taira no Kiyomori | Kiyomori's |
| 平家 | Heike | - | Fallen Taira clan | Taira clan |
| 静 | Shizuka | - | Kijaku's mother, Yoshitsune's beloved | Shizuka-sama |
| おコト | O-Koto | - | Saburo's daughter; Yoichi cares for her at village | Okoto, Koto |
| 与市 | Yoichi | - | Tsukumo villager; Saburo's lieutenant | Yoichi-san |
| 吉次郎 | Kichijiro | - | Merchant head of Kanaya | Kichijirou |
| 金屋吉次郎 | Kanaya Kichijiro | - | Full merchant name | Kanaya Kichijirou |
| 助五郎 | Sukegoro | - | Traitorous Kasumi thief | Sukegorou |
| セイラ | Seira | - | Dewa Sanzan mystic under Sayaka | Sheila, Sarah |
| 海尊 | Kaison | - | Old ally turned into Overlord of Conquest | Kaison-sama |
| 牙怒 | Gedo | - | Sorcerer guarding Yoshitsune Mound | Kiba-do, Gado |
| ラファエル | Raphael | - | Immortal wizard of Ezo | Rafael |
| ダンテ | Dante | - | Immortal wizard, Raphael's friend | Danté |
| 帝 | Emperor | - | Sovereign in Kyoto | Mikado |
| 剛弁 | Goben | - | Keeper of the Gold Blade | Gouben |
| 天輪上人 | Abbot Tenrin | - | Purifies the Gold Blade | Tenrin-shonin |
| 夢仙人 | Dream Sage | - | Hermit who teaches of demonic blood | Yume Sennin |
| 角ベエ | Kakube | - | Thief who steals the Yasakani | Kakubee |
| ぬえ | Nue | - | Fiend guarding the Star Blade | Chimera |
| 修羅王 | Shura King | - | Lieutenant of the Overlord of Conquest | Asura King |
| 覇者の王 | Overlord of Conquest | - | Commander of the Dark Demon Gate; Kaison [ENEMY:Overlord] | Conqueror King |
| 墓守り | Gravekeeper | - | Keeper of Shizuka's grave | Sexton |
| ハム | Ham | - | Village elder in Riumo, Ezo | Hamu |
| テンゼン | Tenzen | - | Elder recounting the Gold Dragon's fall | Tenzen-san |
| せいれいラア | Spirit Ra | - | Earth spirit freed by slaying Earth Dragon | Fairy Ra |
| 九十九村 | Tsukumo Village | - | Starting village near Rinsho-ji | Tsukumo-mura |
| 林省寺 | Rinsho-ji | 12 | Home temple (location box `12` or prose `Rinsho-ji Temple`) | Rinsyouji |
| 鎌倉 | Kamakura | 12 | Seat of Yoritomo's government | Kamakura-shi |
| 裏鎌倉 | Shadow Kamakura | - | Dark reflection of Kamakura; final realm | Back Kamakura |
| 陸前 | Rikuzen | 12 | Northeastern region/city (`陸前の都`) | Mutsu |
| ツガル村 | Tsugaru | 12 | Northern port village to Ezo (`Tsugaru Village` ok in dialogue) | Tsugaru Vlg |
| 尾張 | Owari | 12 | Central province | Owari-koku |
| 京都 | Kyoto | 12 | Imperial capital | Miyako |
| 京の都 | Kyoto | - | Imperial capital | Kyoto City |
| 紀伊 | Kii | 12 | Southern province | Kishu |
| 神戸 | Kobe | 12 | Harbor town | Hyogo |
| 伊予 | Iyo | 12 | Province in Shikoku | Ehime |
| 四国寺 | Shikoku-ji | 12 | Temple in Shikoku | Shikokudera |
| 長崎 | Nagasaki | 12 | Western port | Nagasaki-ura |
| 九州寺 | Kyushu-ji | 12 | Temple in Kyushu | Kyushudera |
| リウモ村 | Riumo | 12 | Fishing village in Ezo (`Riumo Village` ok in dialogue) | Riumo Vlg |
| 出羽 | Dewa | - | Mountain region of northern mystics | Dewa-koku |
| 出羽三山 | Dewa Sanzan | - | Sacred three peaks of Dewa | Mount Dewa |
| 岬の塔 | Cape Tower | - | First dungeon near Tsukumo Village | Misaki Tower |
| 壇ノ浦 | Dannoura | - | Strait of the Genpei naval battle | Dan-no-ura |
| 蛇塚 | Hebizuka | - | Shrine/mound where Dragon Orb is hidden | Serpent Mound |
| アソ山 | Mt. Aso | - | Volcanic mountain where Earth Dragon lurks | Mount Aso |
| かすみ一味 | Kasumi Band | - | Saburo's outlaw band | Kasumi Gang |
| かすみのとりで | Kasumi Keep | - | Saburo's stronghold | Kasumi Fort |
| 隠れ重塔 | Hidden Pagoda | - | Sealed pagoda revealing Kijaku's past | Secret Pagoda |
| 呪殺界 | Cursed Realm | - | Sealed domain trapping Benkei / Yoshitsune | Jusatsu Realm |
| 闇鬼門 | Dark Demon Gate | - | Gate guarded by the Overlord of Conquest | Dark Oni Gate |
| 禁断の洞窟 | Forbidden Cave | - | Cavern sealing an ancient tyrant | Forbidden Cavern |
| 七星の島 | Seven-Star Isle | - | Island housing the Star Blade | Seven Star Island |
| 義経塚 | Yoshitsune Mound | - | Sealed barrow holding Yoshitsune's soul | Yoshitsune's Grave |
| エゾ | Ezo | - | Northern island beyond Tsugaru | Hokkaido |
| 魔界 | Demon Realm | - | Realm of demons; Kijaku's rumored bloodline [ENEMY:Demon] | Makai |
| 魔界の血 | demonic blood | - | Kijaku's rumored lineage (`b11_dialogue_024`, `192`, `509`) | - |
| 魔界の蛇 | Demon Serpent | 14 | Battle enemy (`b0d_enemy_kanji_071`) | - |
| 地獄界 | Hell | - | Underworld Yoritomo tries to link to Kamakura | Jigoku Realm |
| 金龍 | Gold Dragon | - | Sacred guardian dragon of the land | Golden Dragon |
| 地龍 | Earth Dragon | - | Undead earth dragon beneath Mt. Aso | Land Dragon |
| 火龍 | Fire Dragon | - | Undead fire dragon holding Mermaid Princess | Flame Dragon |
| 水龍 | Water Dragon | - | Raging sea guardian at Dannoura | Sea Dragon |
| 三種の神器 | Imperial Regalia | - | The three sacred treasures (or `Three Regalia`) | Three Sacred Treasures |
| 書き付け | Birth Note | 11 | Foundling note naming Kijaku | Hogen's Note |
| 金屋の紋章 | Kanaya Seal | 11 | Crest token from Kanaya Kichijiro | Kanaya Crest |
| 霊光石 | Spirit Gem | 11 | Sacred gem sought by demons at Cape Tower | Reiko Stone |
| 黄金の刀 | Gold Blade | 11 | Unseals the Cursed Realm | Golden Sword |
| 静寂の笛 | Calm Flute | 11 | Shizuka's keepsake; escapes dungeons | Silence Flute |
| 龍水晶 | Dragon Orb | 11 | Restores sleep to the Water Dragon | Dragon Crystal |
| 虹色日記 | Prism Diary | 11 | Key item (`虹色日記`) | Rainbow Diary |
| 人魚の涙 | Siren Tear | 11 | Revives withered land (`人魚の涙`) | Mermaid's Tear |
| リッツの杖 | Ritz Staff | 11 | Key staff found in Ezo | Litz Staff |
| 覚醒の炎 | Waking Fire | 11 | Dante's flame restoring Raphael's memory | Awakening Flame |
| 舞空印 | Sky Seal | 11 | Yoshitsune's seal of strength (`舞空印`) | Sky-Dance Seal |
| 導魔の鍵 | Demon Key | 11 | Key item (`導魔の鍵`) | Doma Key |
| 封解の針 | Unseal Pin | 11 | Unseals cursed locks (`封解の針`) | Seal Needle |
| やたの鏡 | Yata Mirror | 11 | Sacred mirror (`八咫鏡`) | Yata no Kagami |
| むらくもの剣 | Murakumo | 11 | Sacred sword recovered from Dannoura | Kusanagi, Ame no Murakumo |
| やさかにの勾玉 | Yasakani | 11 | Sacred curved jewel (`八尺瓊勾玉`) | Magatama |
| 七星の宝刀 | Star Blade | 11 | Sword awakening the Regalia (`七星の宝刀`) | Seven-Star Sword |
| 夢操の回鏡 | Dream Lens | 11 | Mirror bestowed by Dream Sage | Dream Mirror |
| 邪極無転 | Jakoku-Muten | - | Hogen's ultimate sacrificial jutsu | Jagoku Muten |
| 会話  法術 | Talk  Jutsu | 11 | [UI] Field menu col row 1 (space at byte idx 5) | Speak |
| 力   道具 | Stats Items | 11 | [UI] Field menu col row 2 (space at byte idx 5) | Power, Status |
| 装備  調査 | Equip Check | 11 | [UI] Field menu col row 3 (space at byte idx 5) | Gear, Search |
| 攻撃 遁走 | Fight Flee | 10 | [UI] Battle command row 1 (space at byte idx 5; cols 1..13 box fits 5+1+4) | Attack, Run |
| 法術 道具 | Jutsu Item | 10 | [UI] Battle command row 2 (space at byte idx 5; cols 1..13 box fits 5+1+4) | Magic, Spells |
| 会話 | Talk | 5 | [UI] Field menu col 1 (`Talk  Jutsu`, space at idx 5) | Speak |
| 法術 | Jutsu | 5 | Battle/Field menu (`Jutsu`, `Items`) and dialogue | Magic, Spells |
| 力 | Stats / STR | 5 | [NOTE] Field menu uses `Stats`, Status col uses `STR:`/`Power:` | - |
| 道具 | Items | 5 | [UI] Field/Battle menu col 2 | Item |
| 装備 | Equip | 5 | [UI] Field menu col 1 (`Equip Check`, space at idx 5) | Gear |
| 調査 | Check | 5 | [UI] Field menu col 2 | Search, Inspect |
| 攻撃 | Fight | 5 | [UI] Battle menu col 1 (`Fight Flee`, space at idx 5) | Attack |
| 遁走 | Flee | 5 | [UI] Battle menu col 2 | Run, Escape |
| 銭 | Sen | 3 | Currency unit; lower `sen` in prose, `Sen` HUD | Gold, Yen, Mon |
| レベル | Lv / Level | 4 | [NOTE] `Lv` prefix before digits (`b02_sys[24]`), `Next Level` (`b02_sys[32]`) | Lvl |
| 体力 | HP | 4 | [UI] Hit points label | Life, Vitality |
| 法力 | MP | 4 | [UI] Jutsu/spirit points (`b02_sys_026_mid`) | SP, Spirit |
| 経験値 | EXP / Experience | 14 | [NOTE] `Experience` (`b02_sys[31]`), `Gained       EXP!` (`b02_sys[53]`) | XP |
| 旅の記録 | Password | 10 | [UI] Password entry mode on Continue screen | Travel Log |
| バックアップ | Save RAM | 10 | [UI] Battery-backed RAM save menu | Backup |
| 弁慶 1 | Benkei 1 | 10 | [UI] BRAM slot 1 | Slot 1 |
| 弁慶 2 | Benkei 2 | 10 | [UI] BRAM slot 2 | Slot 2 |
| 弁慶 3 | Benkei 3 | 10 | [UI] BRAM slot 3 | Slot 3 |
| とりけし | Cancel | 10 | [UI] BRAM menu cancel option | Back |
| はい | Yes | 4 | [UI] Yes/No prompt | Yeah |
| いいえ | No | 4 | [UI] Yes/No prompt | Nope |
| 死 | KO | 3 | [UI] Status indicator replacing Lv digits (`$20B4`) | Dead |
| 毒 | PSN | 3 | [UI] Status indicator replacing Lv digits (`$20B4`) | Poi |
| 極 | MAX | 3 | [UI] Max level indicator replacing Lv digits | Ult |
| 風神 | Fujin | 14 | Wind god boss (`b11_dialogue_223`, `612`) | Fuujin |
| 雷神 | Raijin | 14 | Thunder god boss (`b11_dialogue_223`, `612`) | - |
| 土豪 | Earth Tyrant | 14 | Earth-draining fiend (`b11_dialogue_309/312/317/319/595`; keep singular form in compound phrases) | Dogo |
| 魔人 | Golem | 14 | [NOTE] Battle: `Earth/Stone/Bronze Golem`; dialogue `74`/`277`: `Golem`/`Golems` | Majin |
| 本宮ひろ志 | H. Motomiya | 14 | Credits creator name (`b11_bg34_credits_019`, 14-col slide limit) | - |
| 本宮企画 | Motomiya Kikaku | 20 | Credits studio name (`b11_bg34_credits_020`) | - |
| 寺田白雲 | Hakuun Terada | 14 | Credits calligrapher (`b11_bg34_credits`) | - |
| 籏野 篤 | Atsushi Hatano | 14 | [NOTE] Credits programmer (extracted JP displays `篠野 篤`) | - |
| 合鍵 | Passkey | 11 | Key item (`b11_dialogue_071`, `259`) | Master Key |
| 牢の鍵 | Prison Key | 11 | Key item (`b0e_items`) | Cell Key |
| 木の霊薬 | Wood Tonic | 11 | Elemental elixir (`b11_dialogue_345`) | Wood Elixir |
| 土の霊薬 | Earth Tonic | 11 | Elemental elixir | Earth Elixir |
| 火の霊薬 | Fire Tonic | 12 | Elemental elixir | Fire Elixir |
| 水の霊薬 | Water Tonic | 12 | Elemental elixir | Water Elixir |
| 風の霊薬 | Wind Tonic | 12 | Elemental elixir | Wind Elixir |
| 薬 | Salve | 12 | Healing medicine (`b0e_items`) | Medicine, Herb |
| 大薬 | Great Salve | 12 | Strong healing medicine (`b0e_items`) | Hi-Salve |
| 解毒剤 | Antidote | 12 | Poison cure (`b11_dialogue_341`) | - |
| 封魔香 | Ward Incense | 12 | Repels weak encounters (`b11_dialogue_472`) | - |
| 六道の秘薬 | Realm Elixir | 12 | Secret elixir (`b11_dialogue_270`) | - |
| 身返しの手鏡 | Echo Mirror | 12 | Reflective mirror item (`b0e_items`) | - |
| 聖踏 | Holy Step | 11 | Safe-tile field jutsu (`b11_dialogue_070`, `589`) | - |
| 極無転 | Goku-Muten | 11 | Ultimate jutsu (`b0e_jutsu`) | - |
| 転生 | Revive | 11 | [UI] Shrine revival / Jutsu menu (`b02_sys_041`, `b0e_jutsu_025`) | Reincarnate |
| イズモ | Izumo | - | Desertified village (`Izumo Village` / `village of Izumo`) | - |
| 九州 | Kyushu | - | Southern region (`b11_dialogue_299`, `302`, `354`) | Kyuushuu |
| 能登 | Noto | - | Bandit-plagued northern peninsula (`b11_dialogue_102`, `283`) | - |
| 三日月いけ | Crescent Pond | - | Landmark south of Kasumi Keep (`b11_dialogue_056`, `611`) | - |
| 恐山 | Mt. Osore | - | Northern mountain hiding the Hidden Pagoda (`b11_dialogue_061`, `142`, `157`) | Mount Osore |
| 水牢 | water prison | - | Mermaid Princess's submerged prison (`b11_dialogue_242`, `372`) | - |
| 北斗七星 | Big Dipper | - | Star of Death awakening the Imperial Regalia (`b11_dialogue_296`, `322`) | - |
| 月影 | Tsukikage | - | [NOTE] Legendary ascetic (`Legend of Tsukikage`, `b11_dialogue_307..320`) | - |
