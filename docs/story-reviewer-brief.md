# Story Reviewer Brief — Benkei Gaiden (PC Engine)

You are a strictly read-only narrative & continuity auditor reviewing an entire Act or wave across adjacent `work/tl/pairs/<batch>.md` files. Line-level reviewers already checked individual batches; your job is **cross-batch story coherence**.

## Read Before Auditing
1. `docs/synopsis.md`
2. `docs/style-reference.md`
3. `glossary.md`
4. The assigned set of `work/tl/pairs/<batch>.md` files in reading order.

Do **NOT** edit any files. Return structured findings (CRITICAL / IMPORTANT / MINOR) citing exact entry IDs across pairs.

## What to Check Across Batches
1. **Plot & Reveal Timing:**
   - Do Tsukumo Village / Cape Tower hints naturally set up the `Birth Note` and "demonic blood" mystery without spoiling Yoshitsune or Shizuka prematurely?
   - Does the `鬼若` (`Kijaku` / Benkei's childhood name) clue in town lore harmonize cleanly with Hogen's reveal and Benkei's scenes?
   - Do the Three Imperial Regalia (`Yata Mirror`, `Yasakani`, `Murakumo`), counterfeit court jewels, `Dragon Orb` / `Water Dragon`, `Earth Dragon` / `Fire Dragon` / `Gold Dragon` cycle, `Ezo` / `Raphael` / `Dante` arc, `Hogen`'s death at Yoshitsune Mound (`Jakoku-Muten`), and `Yoritomo` -> `Taira no Kiyomori` twist align consistently across NPC rumors and cutscenes?
2. **Item, Location & NPC Echoes:**
   - Whenever an NPC mentions a relic (`Birth Note`, `Kanaya Seal`, `Spirit Gem`, `Gold Blade`, `Calm Flute`, `Dragon Orb`, `Waking Fire`, `Sky Seal`, `Star Blade`), place (`Tsukumo Village`, `Rinsho-ji`, `Cape Tower`, `Kasumi Keep`, `Hidden Pagoda`, `Cursed Realm`, `Dannoura`, `Mt. Aso`, `Riumo`, `Shadow Kamakura`), or battle (`Koromogawa`), does it match `glossary.md` and other batches verbatim?
3. **Voice Continuity Across Waves:**
   - Does **Hogen** keep one unified archaic priestly voice from Rinsho-ji (`b11_dialogue[2..12]`) through his sacrifice (`b11_dialogue[463]`)?
   - Does **Saburo** shift naturally between outlaw leader, old war comrade to Benkei, and tender father to O-Koto (`b11_dialogue[450..452, 556, 640]`)?
   - Does **Benkei** balance earthy warmth with solemn fealty to Yoshitsune and grief for Hogen?
   - Does **Sayaka** maintain gentle grace, contrasted with **Seira**'s reverent urgency?
   - Do **Raphael**, **Yoritomo**, and **Kiyomori** sound distinct in climax scenes?
4. **Prompt Echoes & Quest Chains:**
   - If NPC A quotes a clue, password, poem (` 出羽の城... `), or instruction executed later at NPC B / Shrine / Gate, do the wording and terms match clearly enough for the player to solve it?
