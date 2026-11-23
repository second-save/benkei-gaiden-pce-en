# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in `glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-19 | Project order | SNES (*Suna no Shou*) first vs PCE/PSP (*Benkei Gaiden*) first | **SNES (*Suna no Shou*) first** (completed & published), then **PCE HuCard (*Benkei Gaiden*) first** before PSP PSN (`NPJJ30035`) (`D9`). |
| D2 | 2026-11-19 | Honorifics and name order | keep (`-san`, `-sama`, `-dono`), drop; JP or Western order | **Drop honorifics**, adapt naturally into English feudal titles (*Lord*, *Lady*, *Master*); use standard historical/Western rendering where natural. |
| D3 | 2026-11-19 | Romanization source for names | official art, earlier patch, Hepburn | **Standard Hepburn** / established English historical spellings for real figures (e.g., *Benkei*, *Yoshitsune*, *Yoritomo*). |
| D4 | 2026-11-19 | Credits | stay Japanese, translate | **Translate into English**. |
| D5 | 2026-11-19 | Abbreviations | engine work first (default), abbreviate | **Full names and terms, engine work first** (ROM bank expansion/layout extension/text relocation); never glue ordinal suffixes onto variables; keep wordplay punchy. |
| D6 | 2026-11-19 | Graphics text left in Japanese | none (default), list | **None — translate all tile-drawn Japanese** (title screen, copyright/subtitle, banners, graphics text). |
| D7 | 2026-11-19 | Specs and plans | need approval, pre-approved | **Pre-approved** — run straight through phases, reporting at major milestones/completion. |
| D8 | 2026-11-19 | Git identity, emulator, saves | user input | Git `user.name` / `user.email`: `second-save` (`second-save@users.noreply.github.com` repo-local); playtest emulator: **MesenCE**; **no existing saves/savestates**; release zip = patch + README only. |
| D9 | 2026-11-24 | Next target order | PCE HuCard first vs PSP `NPJJ30035` first | **PC Engine HuCard (*Benkei Gaiden*, 1989) first**, then PSP PSN (`NPJJ30035`). |
