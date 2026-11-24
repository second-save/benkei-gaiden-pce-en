#!/usr/bin/env python3
"""Generate README showcase screenshots and animated preview GIF for benkei-gaiden-pce."""
from __future__ import annotations

import os
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
QA = ROOT / "work" / "qa"
OUT = ROOT / "screenshots"
SAMPLES = QA / "gif_samples"
SCALE = 2


def upscale(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGB")
    return im.resize((im.width * SCALE, im.height * SCALE), Image.Resampling.NEAREST)


def save_png(src: Path, dst: Path) -> None:
    im = upscale(src).convert("P", palette=Image.Palette.ADAPTIVE, colors=256)
    im.save(dst, optimize=True)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    SAMPLES.mkdir(parents=True, exist_ok=True)

    stills = [
        ("01-title.png", QA / "p7_en" / "title_menu" / "final.png"),
        ("02-prologue.png", QA / "p8_prologue" / "f002610.png"),
        ("03-dialogue.png", QA / "p7_intro" / "f003870.png"),
        ("04-town-shops.png", QA / "p8_kyoto_mkt" / "f000630.png"),
        ("05-status-menu.png", QA / "p7_en" / "status_full" / "final.png"),
        ("06-battle-menu.png", QA / "p7_en" / "battle_party" / "final.png"),
    ]
    for name, src in stills:
        assert src.exists(), f"missing source screenshot: {src}"
        save_png(src, OUT / name)

    seq: list[tuple[Path, int]] = []
    # 1. Temple torii title logo reveal
    seq.append((QA / "gif_intro" / "f001248.png", 1200))

    # 2. Title menu (New Game / Continue)
    seq.append((QA / "p7_en" / "title_menu" / "final.png", 1000))

    # 3. Scrolling opening English prologue over dimmed BENKEI GAIDEN logo
    for f in range(2500, 2650, 10):
        dur = 900 if f == 2610 else 80
        seq.append((QA / "gif_prologue" / f"f{f:06d}.png", dur))

    # 4. Rinsho-ji opening dialogue typing out + Yes/No prompt
    for f in (3696, 3704, 3712, 3720, 3728, 3736, 3744, 3752, 3760):
        seq.append((QA / "gif_intro" / f"f{f:06d}.png", 70))
    for f in (3808, 3816, 3824, 3832, 3840):
        seq.append((QA / "gif_intro" / f"f{f:06d}.png", 70))
    seq.append((QA / "gif_intro" / "f003848.png", 1200))

    # 5. Kyoto town & translated KANAYA shop sign, Status screen, and 4-hero Battle
    seq.append((QA / "p8_kyoto_mkt" / "f000630.png", 1100))
    seq.append((QA / "p7_en" / "status_full" / "final.png", 1100))
    seq.append((QA / "p7_en" / "battle_party" / "final.png", 1400))

    frames = []
    durations = []
    for p, dur in seq:
        assert p.exists(), f"missing GIF frame: {p}"
        im = upscale(p).convert("P", palette=Image.Palette.ADAPTIVE, colors=256, dither=Image.Dither.NONE)
        frames.append(im)
        durations.append(dur)

    gif_path = OUT / "preview.gif"
    frames[0].save(
        gif_path,
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )

    # Extract 6 evenly spaced sample frames from the encoded GIF for visual inspection
    gif = Image.open(gif_path)
    n = gif.n_frames
    picks = [int(round(i * (n - 1) / 5)) for i in range(6)]
    for idx, frame_no in enumerate(picks, 1):
        gif.seek(frame_no)
        gif.convert("RGB").save(SAMPLES / f"sample_{idx:02d}_f{frame_no:02d}.png")

    print(f"Generated {len(stills)} PNGs + preview.gif ({n} frames, {os.path.getsize(gif_path)} B)")
    for name, _ in stills:
        p = OUT / name
        im = Image.open(p)
        print(f"  {name}: {im.size} {im.mode} {os.path.getsize(p)} B")


if __name__ == "__main__":
    main()
