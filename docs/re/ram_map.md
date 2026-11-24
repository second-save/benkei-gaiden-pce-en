# WRAM, BRAM, and Save-State Memory Map (`$2000–$3FFF`)

*Benkei Gaiden* (PC Engine HuCard, 1989). All addresses below reflect HuC6280 CPU logical RAM (`MPR1 = $F8`, `8 KiB` Work RAM `$2000–$3FFF`; Mesen `pceWorkRam` offsets `$0000–$1FFF`). Every live dump value and ROM routine address listed here was verified against `rom/Benkei Gaiden (Japan).pce` (`B$00`, `B$01`, `B$08`, `B$09`, `B$1F`) and headless MesenCE snapshots (`world_run`, `ow_run3`, `town_run2`, `shop_run2`, `shop_run3`, `bat_cmd_dump`).

---

## 1. High-Level WRAM Layout (`$2000–$3FFF`)

| CPU Range | Size | Purpose |
|---|---|---|
| `$2000–$20FF` | 256 B | Zero-Page (HuC6280 ZP maps to `$2000+$xx`): RNG/frame counters, text state (`$74`), joypad, map/warp/gold/BGM globals (`$A2..$FA`) |
| `$2100–$21FF` | 256 B | Stack (`$0100` hardware page at `$2100–$21FF`) & IRQ/VDC transfer tail |
| `$2200–$223F` | 64 B | **Party Member Persistent Structs** (4 slots × 16 bytes; `$FF` = empty) |
| `$2240–$22BF` | 128 B | **Mode-shared / Battle Enemy Structs** (16-byte stride; holds loaded enemy template/stats in battle, e.g. `大ぐも` ID `$1D` at `$2240`, or UI/actor scratch in town/overworld) |
| `$22C0–$22FF` | 64 B | **Party Computed Combat Stats** (4 slots × 16 bytes: MaxHP, MaxMP, ATK, DEF, AGI) |
| `$2300–$230F` | 16 B | **Consumable Item Bag (`道具`)** (`16` slots shared by party, `$FF` = empty; `B$01:$CD39`) |
| `$2310–$231F` | 16 B | **Equipment Bag (`装備`)** (`16` slots shared by party, `$FF` = empty; `B$01:$CD69`, `B$09:$CE61`) |
| `$2320–$2329` | 10 B | **Event / Story Progress Flags** (serialized in both Password and BRAM saves; bitflags including `$2324` field/event bits) |
| `$232A–$23FF` | 214 B | Extra progression/engine state (`$232A..$232E` referenced by `B$01`/`B$08`; `$2330..$233F` observed static/engine data across Town & Battle) |
| `$2400–$25FF` | 512 B | Field/window attribute & tile staging buffers (`$2401..$247F`, `$2514..$257F` updated when opening Field/Shop/Battle windows) |
| `$2600–$27FF` | 512 B | **SATB (Hardware Sprite OAM) Staging Buffer** (64 sprites × 8 bytes `[Y, X, pattern, attr]`; DMA/transferred to VDC SATB) |
| `$2800–$2BFF` | 1 KiB | Palette / BG scroll / screen update staging (`$2803..$28DE`, `$2902..$2926`, `$2B04..$2B0E` observed changing on battle transition) |
| `$2C00–$2CFF` | 256 B | **Window / Menu Tile & Saved-Backdrop Buffer** (populated during Field Menu, Shop Menu, Battle, and Password menus) |
| `$2D00–$2D3F` | 64 B | **Shared List / Jutsu / Shop Scratch** (learned Jutsu IDs in `B$00:$F33B` 8-byte blocks; `[ItemID, 24-bit Price LE]` 4-byte records terminated by `$FF` in Shop Menu; cleared during Battle init) |
| `$2E00–$2FFF` | 512 B | **Text Engine String Assembly Buffer** (`$FF`-terminated encoded message buffer; observed `大ぐもがあらわれた` at `$2E00` in Battle and shop greeting in `shop_run3`) |
| `$3000–$30FF` | 256 B | **Battle Combatant Action / Status Table & Frame Counters** (`$3000–$303F` party, `$3040–$30BF` enemy runtime slots, 16-byte stride; `$30C0–$30DF` frame/PRNG/timing state) |
| `$3400–$34FF` | 256 B | **Field Actor / NPC Coordinate Table** (up to 32 actors × 8-byte stride; Slot 0 `$3400–$3407` = Lead Player) |
| `$3520–$352F` | 16 B | **Camera / Viewport Tracking** (`$3529` & `$352B` mirror Player X/Y in tiles; `$3528`/`$352A` sub-tile/fine offset) |
| `$3800–$38FF` | — | Engine display/BRAM UI flags (`$3801–$3804` observed in Overworld/Battle/BRAM) |
| `$3C00–$3E9D` | — | **Sound Engine & Temp Buffers** (`$3C04–$3C0E` anim/SFX temp, `$3C13–$3C14` BRAM slot byte size/scratch, `$3C18–$3E00` active BGM/SFX channels) |
| `$3E9D–$3F9F` | — | **Save / Password / BRAM Scratch** (`$3E9D..$3EAB` cursor/UI state, `$3EB9+` password nibble buffer, `$3F1A..$3F9F` BRAM 94-byte (`$5E`) slot buffer & slot header) |

---

## 2. Key Zero-Page & Global Variables (`$2000–$20FF`)

| ZP | CPU Addr | Size | Confirmed Purpose & Observed Live Values |
|---|---|---|---|
| `$16` | `$2016` | 1 B | Preemptive strike threshold compared against agility delta in `B$08:$D9F0` |
| `$17` | `$2017` | 1 B | Directional / step state bitmask checked with `AND #$1E` in `B$00:$E9DC` |
| `$74` | `$2074` | 1 B | Active text plane (`$00` base, `$20` EF, `$FD` ED, `$1D` FD; see `docs/re/text_engine.md`) |
| `$A2` | `$20A2` | 1 B | **Map Layer / Mode**: `$00` = Overworld (`ow_run3`, `mpr5=$15`), `$01` = Interior/Town/Temple (`Rinsho-ji`, `Kujukuri/Tsukumo`, `mpr5=$18`), `$04` = Title / Battle (`mpr5=$15`, `mpr6=$08` in battle) |
| `$A4` | `$20A4` | 1 B | **Current Map ID** (`$FF` on Overworld, `$00` in Rinsho-ji & Tsukumo Village) |
| `$A5–$A6` | `$20A5–$20A6` | 2 B | Warp / sub-map zone state (`$FF` on Overworld; `$A6=$00` in towns/temples, `$FF` after settle in Overworld) |
| `$A7–$A8` | `$20A7–$20A8` | 2 B | **Saved Entry / Return Coordinates (X, Y)**: `(E4, D1)` outside Rinsho-ji on Overworld/Battle; `(12, 24)` upon entering Tsukumo Village |
| `$B7–$B8` | `$20B7–$20B8` | 2 B | **Gold (`銭`)**: 16-bit little-endian (`$32 $00` = `50 sen`, verified on `力` Status UI and `道` Item Shop UI; printed by `B$08:$C944`, serialized by `B$09:$C357/$C3C9`) |
| `$BA` | `$20BA` | 1 B | Menu cursor / selection result returned by UI helpers (`B$00:$F357`, `B$09:$CFD0`) |
| `$BE–$C0` | `$20BE–$20C0` | 3 B | Enemy group slots during battle (`$1D $FF $FF` vs lone `大ぐも` in `bat_cmd_dump`) |
| `$C1` | `$20C1` | 1 B | Active battle actor offset into `$3000` (`$00..$30` party, `$40..$B0` enemy, `16`-byte stride; `B$08:$D9C9`, `B$09:$C000`) |
| `$DE` | `$20DE` | 1 B | Current BGM track (`B$1F:$DEBE`; bit 7 = suppress BGM) |
| `$E0` | `$20E0` | 1 B | **Field Control / Scene State**: `$00` = Title/Fade/Dialog (`e0=00`), `$01` = Active control inside Interiors (`$A2=01`), `$02/$82` = Fade transition (`Overworld`), `$03` = Active Overworld control (`$A2=00`), `$82` = Battle (`$A2=04`, `b08=$FF`) |
| `$FA` | `$20FA` | 1 B | Battle mode flag (`$00` field -> `$80` battle in `ow_run3` & `bat_cmd_dump`) |

---

## 3. Party, Computed Stats, Enemies, and Inventory

### 3.1 Party Persistent Structs (`$2200–$223F`, 4 × 16 bytes)
Verified from live `snap_01_town_enter`, `snap_06_battle`, `snap_bat_cmd_f1000`, `B$08:$D9B4..$D9EB`, and `B$09:$C3D5..$C3F2`:

```
Kijaku Lv1 live ($2200..$220F): 00 16 00  00 00 00  01  FF FF FF  05 01 02  FF FF FF
```

| Offset | Size | Field | Observed / Code Evidence |
|---|---|---|---|
| `+$00` | 1 B | **Character ID & Absent/Status Flag** | Bits 2..0 = Char ID (`0`=Kijaku; `& #$07` in `B$08:$D9B7`, `B$09:$C048`); `$FF` = empty slot (`B$09:$CD35`) |
| `+$01` | 1 B | **Current HP (`体力`)** | `$16` = `22` (matches `22/22` in Status UI & `22/0` in Battle HUD; zeroed in `B$08:$DC61`) |
| `+$02` | 1 B | **Current MP (`法力`)** | `$00` = `0` (matches `0/0`; decremented by spell cost in `B$08:$DA37`) |
| `+$03..$05` | 3 B | **Experience (`経験値`)** | **24-bit big-endian** (`+$03`=hi, `+$04`=mid, `+$05`=lo; verified byte-by-byte compare loop `INX/INY` `CPY #$03` in `B$09:$CD6D..$CD7C`) |
| `+$06` | 1 B | **Level (`レベル`)** | `$01` = Lv 1 (`B$09:$CD86`, `$CF8A`) |
| `+$07..$09` | 3 B | **Equipped Gear (Weapon / Armor / Accessory)** | `$FF` = none (`+$07` checked in `B$08:$D9E0` & `B$09:$C052`) |
| `+$0A` | 1 B | **Base Strength (`力`)** | `$05` = `5` (matches Status screen `力: 5`) |
| `+$0B` | 1 B | **Base Endurance / Defense (`守備力` factor)** | `$01` = `1` (matches Status screen `守備力: 1`) |
| `+$0C` | 1 B | **Base Agility (`素早さ`)** | `$02` = `2` (matches Status screen `素早さ: 2`; compared in `B$08:$D9E7`) |
| `+$0D..$0F` | 3 B | Unused / padding (`$FF`) | Filled `$FF` |

### 3.2 Computed Combat Stats (`$22C0–$22FF`, 4 × 16 bytes)
Verified live (`$22C0: 00 00 0A 16 00 05 01 02 00 ...`) and via `B$01`/`B$08` references:
- `+$02` (`$22C2`): Next-level countdown / base speed factor (`$0A` = `10` = `つぎのレベルまで あと 10`? Note `$2203=0`, Status UI showed `あと 10`)
- `+$03` (`$22C3`): **Max HP** (`$16` = `22`)
- `+$04` (`$22C4`): **Max MP** (`$00` = `0`)
- `+$05` (`$22C5`): **Attack Power (`攻撃力`)** (`$05` = `5`)
- `+$06` (`$22C6`): **Defense (`守備力`)** (`$01` = `1`)
- `+$07` (`$22C7`): **Agility (`素早さ`)** (`$02` = `2`)

### 3.3 Battle Enemy Template Buffer (`$2240–$22BF`)
In Town/Overworld `$2240..$226F` is used as field/UI scratch (`68 32 ...`), whereas in Battle it holds loaded enemy template data:
- Observed in `snap_bat_cmd_f1000` (`大ぐも`):
  `$2240: 1D 07 00 05 18 00 03 04 82 7C 0B 05 02 FF 00 00`
  (`$1D` = Enemy ID, `$07` = HP, `$2248/$2249` = graphic/sprite refs copied to `$3C07/$3C08` by `B$09:$C020`).

### 3.4 Inventory Bags (`$2300–$231F`) & Event Flags (`$2320–$2329`)
- **`$2300–$230F`**: `16`-slot shared **Consumable Item Bag** (`道具`, indexed in `B$01:$CD39` / `B$08:$DA8B`, shifted by `B$00:$F361`; `$FF` = empty slot).
- **`$2310–$231F`**: `16`-slot shared **Equipment Bag** (`装備`, indexed in `B$01:$CD69`, shifted/unequipped by `B$09:$CDEC..$CE96`; bit 7 `$80` marks active transition flags during BRAM/equip handling; `$FF` = empty slot).
- **`$2320–$2329`**: `10` bytes of persistent game/story flags (`$2320..$2329` serialized verbatim by Password & BRAM routines; live start value `80 00 00 80 00 00 00 00 00 00`; `$2324` bit 2 = intro/event state checked at `B$00:$E99A`).

### 3.5 Shared List Scratch (`$2D00–$2D3F`) & String Buffer (`$2E00–$2FFF`)
- **`$2D00–$2D3F`**: Dual-purpose 64-byte buffer:
  - **Learned Jutsu lookup (`B$00:$F33B`)**: `LDX` indexed in `8`-byte chunks per party slot (`$FF`-terminated Jutsu IDs; empty in Lv 1 Town `00 00 ...`).
  - **Shop Buy List (`shop_run3`)**: Observed live inside Tsukumo Item Shop (`道`):
    `60 14 00 00  62 0A 00 00  66 50 00 00  FF ...` -> 4-byte entries `[ItemID, 24-bit Price LE]`, `$FF`-terminated (`$60` = `薬` 20 sen, `$62` = `解毒剤` 10 sen, `$66` = `封魔香` 80 sen).
- **`$2E00–$2FFF`**: Active string buffer holding `$FF`-terminated text codes for window rendering.

---

## 4. Battle Action Slots (`$3000–$30FF`) & Field Actors (`$3400–$34FF`)

- **`$3000–$30BF`**: `12` combatant runtime action slots × 16 bytes (`$3000..$303F` = party slots 0–3, `$3040..$30BF` = enemy slots 0–7).
  - Verified fields in `B$08:$D9B4..$DA8B` and `B$09:$C002..$C01A`:
    - `+$00`: Combatant active/owner info (`B$09:$C002`)
    - `+$01`: Target slot / param (`B$08:$DC7A`)
    - `+$02`: Action class/subcommand (`B$00:$F383`, `B$08:$DA13`)
    - `+$03`: Selected spell / item slot / action ID (`B$08:$DA33/$DA87`, `B$00:$F379`)
    - `+$05`: Status / preemptive bitflags (`ORA #$02` in `B$08:$D9F4`)
    - `+$06`: Combat flags (`AND #$40` in `B$08:$DC76`)
    - `+$08`: Source actor index (`0..3` for party, `$40+` / combatant slot; live `$00` on command menu)
    - `+$09`: Character ID & status byte copied from `$2200,X` (`B$08:$D9CB`)
    - `+$0A`: Turn/initiative state (`B$08:$D9FD`)
  - Live `bat_cmd_dump` (`f=1000`, cursor hovering `遁走` before submit): `$3000 = 00 00 FF FF FF 00 00 00 FF FF FF 01 02 FF FF FF`.
- **`$30C0–$30DF`**: Engine frame/PRNG/timers (`$30C2..$30C3` observed ticking per menu/world frame).
- **`$3400–$34FF`**: Map actor / NPC structs (8-byte stride, `$00..$FF`):
  - Slot 0 (`$3400–$3407`) = Lead Player: `+$01` Tile X, `+$03` Tile Y, `+$04/$05` Prev Tile (X, Y), `+$07` Facing direction (`$01` OW step, `$03` Town/Temple).
  - Camera `$3529` / `$352B` mirrors Player `$3401` / `$3403` (`snap_01_town_enter` = `12, 24`; `snap_02_shop_320` = `0D, 17`).

---

## 5. Password (`B$09:$C2C0`) & Backup RAM (`BRAM $F7`, `B$09:$DB01–$DF50`)

- **Password Nibble Stream (`$3EB9+`, `B$09:$C326–$C403`)**: Encodes nibble-by-nibble via `$C3F3`:
  - `$3E9D` (`$A2` map layer), `$3401` (X), `$3403` (Y)
  - `$2300–$231F` (32B inventories, `+1` biased on encode; `$00` -> `$FF` empty on decode)
  - `$2320–$2329` (10B event flags)
  - `$20B7–$20B8` (Gold, 16-bit LE)
  - `$2200–$223F` (`4` party members: `C3DA` encodes first `$0A` [10] bytes `+$00..$09`; `$C363` decodes `$07` bytes `+$00..$06` and fills `+$07..$0F` with `$FF`).
- **PC Engine BRAM (`TAM #$10` with bank `#$F7`, mapped `$8000–$9FFF`, `B$09:$DB01–$DF50`)**:
  - Formatted signature: `HUBM!BM FORMAT!` checked at `B$09:$DB89` (bank header/allocator at `$8000–$8011`, free size `$8006–$8007`).
  - Save slots (`弁慶 1`–`弁慶 3`): **`$5E` (94 bytes)** per slot (`B$09:$D117: CMP #$5E`), staged via `$3F20–$3F7F` (`B$09:$CCA2`, `$CD9F`, `$CF24..$D140`).
