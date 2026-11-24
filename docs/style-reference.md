# Benkei Gaiden (PC Engine) — Style Reference & Approved Pilot

## Tone & Prose Rules
- **Mythic Heian-Kamakura adventure:** Grounded, brisk, earnest dark-fantasy prose matching 1989 Sunsoft console RPG pacing. Avoid modern slang, memes, fourth-wall jokes, or stiff dictionary English.
- **UI & Control Tags:** Keep `{nl}`, `{page}`, `{end}`, and `[EC]` exact. Never place `{nl}` after a `24`-character line (`$CF27` auto-wraps at column `24`, causing a blank line; `{nl}` lines must stay `<= 23` columns, and each `{page}` box allows at most `3` lines).
- **Dialogue Quotes:** When a speaker tag prefixes multi-page speech (`Hogen: "...{page}...{page}..."`), open `"` after `Speaker: `, keep intermediate pages unclosed if the same speaker continues, and close `"` on their final spoken line.
- **Honorifics & Names:** Never retain `-san`, `-sama`, `-dono`, `-chan`, `-kun`, or `ojisan`/`jii-san` suffixes (`docs/decisions.md` D2). Follow `glossary.md` spellings strictly (`Kijaku`, `Hogen`, `O-Koto`, `Rinsho-ji`, `Tsukumo Village`, `Birth Note`, `Spirit Gem`, `sen`).

## Speaker Voice Table

| Speaker / Type | JP Markers | EN Voice Devices |
| --- | --- | --- |
| **Kijaku** (`鬼若`) | Earnest, impulsive youth (`なんだって!?`, `まかせてくれじっちゃん!!`, terse `...`) | Direct, warm, determined; respects elders without servility |
| **Hogen** (`法眼`) | Archaic priest (`じゃ`, `おるぞ`, `ならぬ`, measured pauses) | Formal, fatherly cadence (`Aye`, `I would have you...`, `Hold fast`); weighty without purple prose |
| **Ise Saburo** (`三郎`) | Rough ex-samurai bandit chief (`おれ`, `わかった`, blunt camaraderie) | Contractions, crisp soldier/outlaw warmth, plain loyalty |
| **Musashibo Benkei** (`弁慶`) | Boisterous warrior-monk (`だれがハゲだ`, `よくねた`, fierce loyalty to Yoshitsune & Hogen) | Big-hearted, booming humor in camp (`Who are you calling bald?!`), solemn reverence in tragedy |
| **Sayaka** (`沙夜香`) | Polite young shrine maiden (`わたくし`, `ましょう`, serene yet resolute) | Graceful, composed phrasing (`Let us hurry`, `I shall gladly lend my strength`) |
| **Seira** (`セイラ`) | Devoted attendant (`沙夜香さま`, `〜でございます`, urgent foresight) | Deferential but urgent (`Lady Sayaka`, `Wait—I hear a voice from the Demon Realm!`) |
| **Minamoto no Yoshitsune** (`義経`) | Noble lord (`わたし`, `そなた`, `れいをいう`, calm restraint) | Measured aristocratic dignity (`My thanks`, `Forgive me`, `For the peace of all`) |
| **Minamoto no Yoritomo / Kiyomori** | Cold mockery (`クククッ`, `死ね`), archaic wrath (`われなり`, `おもいしるがよい`) | Chilling scorn from Yoritomo; hollow, wrathful grandeur from Kiyomori |
| **Kanaya Kichijiro** (`吉次郎`) | Courteous master merchant (`わたし`, `〜なされ`, `〜ましょう`) | Polished, hospitable merchant register |
| **Villagers / Rural NPCs** | Dialect (`てつだいてぇ`, `そうもなんね`, `物さもってけ`, `死ぬでねえぞ`, `ですだ`) | Earthy contractions, dropped g's sparingly (`dyin'`, `what's`), homey rhythm |
| **Sukegoro / Thieves / Demons** | Cowardly whines (`ひえー`, `かんべんしてくだせえ`), snarls (`コわっぱ`, `グフッ`, `いかしてかえさぬ`) | Wheedling slang (`Spare me!`, `Have mercy!`) vs. sharp, cruel boasts (`whelp`, `Urgh!`) |

## Before / After Voice Example (`b11_dialogue_015_1C933`)

- **JP:** `はなしはきいただよ、鬼若。てつだいてぇだが、そうもなんね。さ、この中の物さもってけ。{nl}死ぬでねえぞ{end}`
- **Before (flat/generic, plus line overflow risk):** `I heard the story, Kijaku. I want to help, but I cannot. Come, take the items inside here.{nl}Do not die.{end}`
- **After (approved rural voice + tight box fit):**
  `Heard all about it,{nl}Kijaku. Wish I could{nl}go, but I'm stuck here.{page}Take what's stashed in{nl}here. Just don't go{nl}gettin' killed.{end}`

## Approved Pilot Slice (`script/b11_dialogue.json`)

Every pilot translation below has been verified for `23`-col `{nl}` limit, `24`-col final line limit, and `3`-line-per-page cap:

- **`2` (`b11_dialogue_002_1C582`)**
  - JP: `ほっ、法眼さま!!{page}法眼「与市ではないか。どうしたのだ!」{page}与市「む、村に魔物たちがせめてきて、 おコトが魔物に!」{page}法眼「なんだと!」{end}`
  - EN: `"P-Priest Hogen!!"{page}Hogen: "Yoichi! What is{nl}the matter?"{page}Yoichi: "Demons stormed{nl}the village! They've{nl}taken O-Koto!"{page}Hogen: "What?!"{end}`
- **`6` (`b11_dialogue_006_1C620`)**
  - JP: `法眼「鬼若よ、ここ、林省寺でくらしていた おコトが岬の塔に ひそむ魔物に さらわれてしまったのだ。{page}鬼若「なんだって!? おコトが魔物に!」{page}法眼「うむ、魔物がなぜ おコトをさらったのかは わからぬが、おコトの身がしんぱいじゃ。{page}おまえにおコトを助けにいってもらいたい。いってくれるか。」{end}`
  - EN: `Hogen: "Kijaku, demons{nl}at Cape Tower abducted{nl}O-Koto from Rinsho-ji."{page}Kijaku: "What?! Demons{nl}took O-Koto?!"{page}Hogen: "Aye. I know not{nl}why they want her, but{nl}I fear for her safety.{page}I must ask you to save{nl}O-Koto. Will you go?"{end}`
- **`7` (`b11_dialogue_007_1C6C8`)**
  - JP: `法眼「おまえには、あとで話さねばならぬことがある。だが・・・しっかりな。わたしはおまえをしんじておるぞ」{end}`
  - EN: `Hogen: "I have much to{nl}tell you when you are{nl}back.{page}Stay strong, Kijaku.{nl}I believe in you."{end}`
- **`8` (`b11_dialogue_008_1C700`)**
  - JP: `法眼「よくやった。おコトもぶじでなによりじゃ、ついにおまえも しんじつをしるときがきたようだ{page}おまえのなまえ、'鬼若(きじゃく)'は、あかごだったおまえが ゆいいつ身につけていた書き付けにしるされていた なだ。{page}おまえはみずからの 生まれのひみつをとく旅にたたねばならぬ。{page}そのためには、いずれ魔界に ふみこむこととなるだろう。{page}それでもいくか?」{end}`
  - EN: `Hogen: "Well done. With{nl}O-Koto safe, it is time{nl}you learned the truth.{page}Your name, Kijaku, came{nl}from the note kept on{nl}you as a helpless babe.{page}Its kanji mean "demon"{nl}and "young."{page}You must set forth on a{nl}journey to uncover the{nl}secret of your birth.{page}In time, that path may{nl}even lead you into the{nl}Demon Realm itself.{page}Even knowing that, will{nl}you still go?"{end}`
- **`11` (`b11_dialogue_011_1C7E7`)**
  - JP: `法眼「そうか。{nl}それだけのかくごがあるのならよい。さあ、この書き付けをもっていけ。わしのてがみをそえておく{page}それをもって都にいき、金屋吉次郎をたずねるがよい。{page}さあ、いけ。なかまをあつめ、しんじるもののために生きるがよい。{page}わたしはおまえを、いつもしんじておるぞ」{page}書き付けをうけとった{end}`
  - EN: `Hogen: "So be it. Your{nl}mind is set. Take this{nl}note and my own letter.{page}Carry them to the city{nl}and seek out Kanaya{nl}Kichijiro.{page}Go now. Gather allies,{nl}and live for what you{nl}truly believe in.{page}Know that I will always{nl}believe in you."{page}Got the Birth Note!{end}`
- **`12` (`b11_dialogue_012_1C88D`)**
  - JP: `書き付けをもって都にいき、{nl}金屋吉次郎をたずねるがよい{page}さあ、いけ。なかまをあつめ、しんじるもののためにいきるがよい。わたしはおまえを、いつもしんじておるぞ{end}`
  - EN: `Carry that note to the{nl}city and seek out{nl}Kanaya Kichijiro.{page}Go, gather allies, and{nl}live for your beliefs.{nl}I will always trust you.{end}`
- **`15` (`b11_dialogue_015_1C933`)**
  - JP: `はなしはきいただよ、鬼若。てつだいてぇだが、そうもなんね。さ、この中の物さもってけ。{nl}死ぬでねえぞ{end}`
  - EN: `Heard all about it,{nl}Kijaku. Wish I could{nl}go, but I'm stuck here.{page}Take what's stashed in{nl}here. Just don't go{nl}gettin' killed.{end}`
- **`23` (`b11_dialogue_023_1CA36`)**
  - JP: `よくここまできた、コわっぱ。 このむすめは、{nl}'霊光石'を、うばうための たいせつなひとじち。{page}だがおまえはいかしてかえさぬ!{end}`
  - EN: `You did well to make it{nl}this far, whelp. This{nl}girl is vital bait to{page}seize the Spirit Gem.{nl}And you will not leave{nl}here alive!{end}`
- **`24` (`b11_dialogue_024_1CA7C`)**
  - JP: `・・・お、おのれ。だが、おまえの苦しみはこれからはじまるのだ・・・{page}おまえのからだには、おれたちとおなじ{nl}魔界の血が・・・グフッ{end}`
  - EN: `C-Curse you... Yet your{nl}torment has only just{nl}begun...{page}Within your veins flows{nl}the same demonic blood{nl}as ours... Urgh!{end}`
- **`25` (`b11_dialogue_025_1CAC3`)**
  - JP: `おコト「わぁ きじゃく!たすけにきてくれたんだね!ありがとう」{end}`
  - EN: `O-Koto: "Kijaku! You{nl}came to rescue me!{nl}Thank you!"{end}`
