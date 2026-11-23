# Glossary — *Benkei Gaiden* (PC Engine, 1989)

Binding names, historical spellings, and UI terms. Confirmed spellings below apply across all batches and graphics.

## Core Rulings (from `docs/decisions.md`)
- Drop honorifics (`-san`, `-sama`, `-dono`, `-kun`, `-chan`); render titles naturally (*Lord*, *Lady*, *Master*).
- Standard Hepburn romanization & established historical spellings.
- Full names and terms; no abbreviations by default.

## Key Characters & Historical Figures
| Japanese | English | Notes |
|---|---|---|
| 弁慶 / 武蔵坊弁慶 | Benkei / Musashibo Benkei | Titular warrior-monk (`0x05E7C`, `0x1E0E7`) |
| 鬼若 (きじゃく) | Kijaku | Protagonist; canonical reading confirmed in-game at `0x1C700` & `0x1CAC3` |
| 沙夜香 | Sayaka | Party heroine (`0x05E71`, `0x1D5A2`) |
| 三郎 | Saburo | Okoto's father / former Kasumi leader (`0x05E77`, `0x1D04A`, `0x1D2D0`) |
| 法眼 | Hogen | Rinsho-ji Temple master (`0x05EBD`, `0x1C582`) |
| 与市 | Yoichi | Temple attendant / former Kasumi member (`0x1C582`, `0x1D30D`) |
| おコト | Okoto | Ward at Rinsho-ji Temple (`0x1C5D7`, `0x1D2D0`) |
| 義経 / 源義経 | Yoshitsune / Minamoto no Yoshitsune | Historical Minamoto lord (`0x05EC2`, `0x1D957`, `0x1D9A0`) |
| 頼朝 / 源頼朝 | Yoritomo / Minamoto no Yoritomo | Historical Minamoto shogun (`0x1BCEB`, `0x1D9A0`) |
| 金屋吉次郎 | Kanaya Kichijiro | Capital gold merchant (`0x1C7E7`) |

## Key Places & Factions
| Japanese | English | Notes |
|---|---|---|
| 林省寺 | Rinsho-ji Temple | Starting temple (`0x15282`, `0x1C620`) |
| 九十九村 (つくもむら) | Tsukumo Village | Starting village; reading confirmed at `0x1CAE3` (*not* Kujukuri) |
| 岬の塔 | Cape Tower | Early dungeon south of Tsukumo Village (`0x1C620`, `0x1CAE3`) |
| 京都 / 都 | Kyoto / The Capital | (`0x05E91`, `0x1C7E7`) |
| 鎌倉 | Kamakura | (`0x05E60`) |
| 陸前 | Rikuzen | (`0x05E66`) |
| 金屋 | Kanaya | Gold shop / merchant house (`BG[16]` sign, `0x1C3FE` `金屋の紋章`) |

## Currency & Standard UI Terms (Verified from `b02_sys` / `b0a_menus`)
| Japanese | English | Context |
|---|---|---|
| 銭 | sen | Currency (`0x05EC7`, `0x05F99`) |
| 冒頭 / 継続 | New Game / Continue | Title menu (`0x15159..0x15166`, rendered via `BG[34]`) |
| 旅の記録 / バックアップ | Travel Log / Backup | Save/Load menus (`0x1510A..0x15118`); slots `弁慶 1`–`弁慶 3` (`Benkei 1`–`3`), `とりけし` (`Cancel`) |
| 会話 / 法術 / 力 / 道具 / 装備 / 調査 | Talk / Jutsu / Status / Item / Equip / Search | Field command menu (`0x05E36..0x05E57`) |
| 攻撃 / 遁走 / 法術 / 道具 | Attack / Flee / Jutsu / Item | Battle command menu (`0x05E9E..0x05EB4`) |
| レベル / 体力 / 法力 / 経験値 | Level / HP / MP / Experience | Status & battle HUD (`0x05ECA..0x05F13`) |
| 力 / 素早さ / 攻撃力 / 守備力 | Strength / Agility / Attack / Defense | Status screen stats (`0x05EE7..0x05F0B`) |
| かう / うる | Buy / Sell | Shop menu (`0x05F30..0x05F35`) |
| 宿 / 武 / 防 / 道 | Inn / Weapons / Armor / Items | Town shop signs (`BG[15]`, `BG[16]`) |

*(Extended during Phase 6 batch translation.)*
