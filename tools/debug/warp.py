"""Cold-boot scene warp & verification harness for Benkei Gaiden (PCE)."""
from __future__ import annotations

import argparse
import concurrent.futures
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

DEBUG_DIR = Path(__file__).resolve().parent
SCENES_LUA = DEBUG_DIR / "scenes.lua"
WARP_LUA = DEBUG_DIR / "warp.lua"
DEFAULT_ROM = ROOT / "rom" / "Benkei Gaiden (Japan).pce"


def load_scenes() -> dict[str, dict[str, object]]:
    """Parse M.NAMES and top-level scene frames/descriptions from scenes.lua."""
    text = SCENES_LUA.read_text(encoding="utf-8")
    names_m = re.search(r"M\.NAMES\s*=\s*\{(.*?)\}", text, re.S)
    order = re.findall(r'"([^"]+)"', names_m.group(1)) if names_m else []
    scenes: dict[str, dict[str, object]] = {}
    for name in order:
        pat = re.compile(rf"\b{re.escape(name)}\s*=\s*\{{(.*?)\n  \}},", re.S)
        m = pat.search(text)
        if not m:
            continue
        blk = m.group(1)
        desc_m = re.search(r'desc\s*=\s*"([^"]*)"', blk)
        frm_m = re.search(r"frames\s*=\s*(\d+)", blk)
        scenes[name] = {
            "desc": desc_m.group(1) if desc_m else "",
            "frames": int(frm_m.group(1)) if frm_m else 360,
        }
    return scenes


def run_scene(
    name: str,
    meta: dict[str, object],
    rom: Path,
    out_dir: Path,
    *,
    save_state: bool = False,
    god: bool = False,
    noenc: bool = False,
    noclip: bool = False,
    fast: bool = False,
    shot_every: int = 0,
    sheet: bool = False,
) -> tuple[str, int, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-X",
        "utf8",
        str(ROOT / "tools" / "run_emu.py"),
        str(rom),
        "--out",
        str(out_dir),
        "--frames",
        str(meta["frames"]),
        "--script",
        str(WARP_LUA),
        "--var",
        f"DEBUG_DIR={repr(str(DEBUG_DIR))}",
        "--var",
        f"SCENE={repr(name)}",
        "--smoke",
    ]
    if god:
        cmd.extend(["--var", "GOD=1"])
    if noenc:
        cmd.extend(["--var", "NOENC=1"])
    if noclip:
        cmd.extend(["--var", "NOCLIP=1"])
    if fast:
        cmd.extend(["--var", "FAST=1"])
    if shot_every > 0:
        cmd.extend(["--shot-every", str(shot_every)])
    if sheet:
        cmd.append("--sheet")
    if save_state:
        st_path = ROOT / "work" / "states" / f"{name}.mss"
        st_path.parent.mkdir(parents=True, exist_ok=True)
        cmd.extend(["--state-out", str(st_path)])

    res = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    msg = (res.stdout + res.stderr).strip()
    return name, res.returncode, msg


def make_all_sheet(scene_names: list[str], out_root: Path) -> Path | None:
    shots = [str(out_root / name / "final.png") for name in scene_names if (out_root / name / "final.png").exists()]
    if not shots:
        return None
    sheet_path = out_root / "all_scenes_sheet.png"
    res = subprocess.run(
        [sys.executable, "-X", "utf8", os.path.join(SKILL, "scripts", "sheet.py"), *shots, "--out", str(sheet_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if res.returncode != 0:
        print(res.stdout + res.stderr, file=sys.stderr)
        return None
    return sheet_path


def main() -> int:
    scenes = load_scenes()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("scene", nargs="?", help="Scene name from tools/debug/scenes.lua")
    ap.add_argument("--list", action="store_true", help="List all available cold-boot scenes")
    ap.add_argument("--all", action="store_true", help="Run every scene from a cold boot and build a contact sheet")
    ap.add_argument("--rom", type=Path, default=DEFAULT_ROM)
    ap.add_argument("--out", type=Path, default=ROOT / "work" / "qa" / "warp")
    ap.add_argument("--states", action="store_true", help="Also export work/states/<scene>.mss for each scene")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--god", action="store_true")
    ap.add_argument("--noenc", action="store_true")
    ap.add_argument("--noclip", action="store_true")
    ap.add_argument("--fast", action="store_true")
    ap.add_argument("--shot-every", type=int, default=0)
    ap.add_argument("--sheet", action="store_true")
    args = ap.parse_args()

    if args.list:
        for name, meta in scenes.items():
            print(f"{name:18s} ({meta['frames']:4d}f)  {meta['desc']}")
        return 0

    if not args.rom.exists():
        print(f"ROM not found: {args.rom}", file=sys.stderr)
        return 2

    if args.all:
        failed = []
        names = list(scenes.keys())
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
            futs = [
                pool.submit(
                    run_scene,
                    name,
                    scenes[name],
                    args.rom,
                    args.out / name,
                    save_state=args.states,
                    god=args.god,
                    noenc=args.noenc,
                    noclip=args.noclip,
                    fast=args.fast,
                )
                for name in names
            ]
            for fut in concurrent.futures.as_completed(futs):
                name, code, msg = fut.result()
                status = "OK" if code == 0 else f"FAIL({code})"
                print(f"[{status}] {name}")
                if code != 0:
                    print(msg)
                    failed.append(name)
        sheet_path = make_all_sheet(names, args.out)
        if sheet_path:
            print(f"Contact sheet: {sheet_path}")
        if failed:
            print(f"FAILED scenes ({len(failed)}): {', '.join(failed)}", file=sys.stderr)
            return 1
        print(f"All {len(names)} cold-boot scenes passed.")
        return 0

    if not args.scene:
        ap.error("specify a scene name, --list, or --all")
    if args.scene not in scenes:
        ap.error(f"unknown scene '{args.scene}' (run --list)")

    name, code, msg = run_scene(
        args.scene,
        scenes[args.scene],
        args.rom,
        args.out,
        save_state=args.states,
        god=args.god,
        noenc=args.noenc,
        noclip=args.noclip,
        fast=args.fast,
        shot_every=args.shot_every,
        sheet=args.sheet,
    )
    print(msg)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
