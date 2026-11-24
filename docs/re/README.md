# Reverse Engineering Notes Index

- `rom_map.md`: 48-bank (`$00..$2F`) HuCard layout, IRQ/reset vectors, `TAM` bank switching, free space, and expansion verification.
- `text_engine.md`: Text encoding, control codes, font tile locations/layout, HuC6280 text renderer, and full pointer/text table inventory.
- `ram_map.md`: `$2000–$3FFF` Work RAM & `$F7` BRAM layout (mode, map ID, coordinates, party stats, inventory, battles, flags).
- `graphics_text.md`: Tile-drawn Japanese graphics inventory (title screen, subtitle/copyright, shop signs, HUD/battle cards, ending/credits).
- `windows.md`: Measured 8×16 UI window budgets, dialogue auto-wrap rules, `$2E00` digit-poke offsets, and horizontal Title/BRAM coordinates.
