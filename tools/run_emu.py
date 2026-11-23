"""Headless MesenCE runner for PC Engine (.pce) QA and Lua reverse engineering."""
from __future__ import annotations

import argparse
import glob
import json
import os
import shutil
import struct
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402

sys.path.insert(0, os.path.join(SKILL, "scripts"))
import sheet as sheetmod  # noqa: E402


def find_mesen() -> str:
    patterns = [
        str(ROOT / "tools" / "mesen" / "**" / "Mesen"),
        str(ROOT / "tools" / "mesen" / "**" / "Mesen.exe"),
    ]
    for pat in patterns:
        hits = sorted(p for p in glob.glob(pat, recursive=True) if os.path.isfile(p) and os.access(p, os.X_OK))
        if hits:
            return os.path.abspath(hits[0])
    sys.exit("Mesen executable not found under tools/mesen/: run fetch_emu.py mesen")


def lua_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, (list, tuple)):
        return "{" + ",".join(lua_value(x) for x in v) + "}"
    return json.dumps(str(v).replace("\\", "/"))


def ensure_mesen_portable(exe: str) -> None:
    path = os.path.join(os.path.dirname(exe), "settings.json")
    cfg = json.load(open(path, encoding="utf-8-sig")) if os.path.exists(path) else {}
    script = cfg.setdefault("Debug", {}).setdefault("ScriptWindow", {})
    port = cfg.setdefault("PcEngine", {}).setdefault("Port1", {})
    if script.get("AllowIoOsAccess") is True and "ConfigUpgrade" in cfg and port.get("Type") == "PceController":
        return
    port["Type"] = "PceController"
    script["AllowIoOsAccess"] = True
    cfg.setdefault("ConfigUpgrade", 1)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)


def stamp_state(exe: str, state: str, out: str) -> str:
    d = open(state, "rb").read()
    exe_bytes = open(exe, "rb").read()
    i = exe_bytes.rfind(struct.pack("<I", 0xFEEF04BD))
    if d[:3] != b"MSS" or i < 0:
        return state
    ms, ls = struct.unpack("<II", exe_bytes[i + 8:i + 16])
    ver = struct.pack("<I", (ms >> 16) << 16 | (ms & 0xFFFF) << 8 | ls >> 16)
    if d[3:7] == ver:
        return state
    fixed = os.path.join(out, "_state_in.mss")
    open(fixed, "wb").write(d[:3] + ver + d[7:])
    return fixed


def read_route(path: str) -> list[tuple[int, str]]:
    steps = []
    for line in open(path, encoding="utf-8"):
        line = line.split("#")[0].strip()
        if line:
            n, spec = line.split()
            steps.append((int(n), spec))
    return steps


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("rom")
    ap.add_argument("--out", required=True)
    ap.add_argument("--route")
    ap.add_argument("--frames", type=int)
    ap.add_argument("--shot-every", type=int, default=0)
    ap.add_argument("--shots")
    ap.add_argument("--state-in")
    ap.add_argument("--state-out")
    ap.add_argument("--state-every", type=int, default=0)
    ap.add_argument("--sav")
    ap.add_argument("--mash", type=int, default=0)
    ap.add_argument("--mash-key", default="i")
    ap.add_argument("--script", action="append")
    ap.add_argument("--var", action="append")
    ap.add_argument("--emu")
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--sheet", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()

    if not (a.route or a.frames):
        sys.exit("give --route FILE or --frames N")

    exe = a.emu or find_mesen()
    ensure_mesen_portable(exe)
    out = os.path.abspath(a.out)
    rom = os.path.abspath(a.rom)
    stem = os.path.splitext(os.path.basename(rom))[0]
    os.makedirs(out, exist_ok=True)
    if a.state_out:
        os.makedirs(os.path.dirname(os.path.abspath(a.state_out)), exist_ok=True)
    for old in glob.glob(os.path.join(out, "f[0-9]*.*")) + [os.path.join(out, n) for n in ("final.png", "lua_error.txt")]:
        if os.path.exists(old):
            os.remove(old)

    route = a.route and os.path.abspath(a.route)
    shots = [int(x) for x in a.shots.split(",")] if a.shots else None
    err = os.path.join(out, "lua_error.txt")
    g = {
        "OUT": out + "/",
        "ERRFILE": err,
        "FRAMES": a.frames,
        "SHOT_EVERY": a.shot_every,
        "SHOTS": shots,
        "MASH": a.mash,
        "MASH_KEY": a.mash_key,
        "STATE_EVERY": a.state_every,
        "SYSTEM": "pce",
        "ROUTE": route,
        "STATE_IN": stamp_state(exe, os.path.abspath(a.state_in), out) if a.state_in else None,
        "STATE_OUT": os.path.abspath(a.state_out) if a.state_out else None,
    }
    head = "\n".join(f"{k} = {lua_value(v)}" for k, v in g.items() if v is not None)
    head += "".join(f"\n{kv.split('=', 1)[0].strip()} = {kv.split('=', 1)[1]}" for kv in a.var or [])
    pce_lib = (ROOT / "tools" / "lua" / "pce_lib.lua").read_text(encoding="utf-8")
    parts = [head, pce_lib]
    for s in a.script or []:
        src = open(s, encoding="utf-8").read()
        eq = "="
        while f"]{eq}]" in src:
            eq += "="
        parts.append(
            f"L.safe(function() local f, e = (loadstring or load)([{eq}[\n{src}]{eq}], "
            f"{lua_value('@' + os.path.basename(s))}); if not f then error(e, 0) end; f() end)()"
        )
    lua = os.path.join(out, "_run.lua")
    with open(lua, "w", encoding="utf-8") as f:
        f.write("\n".join(parts) + "\n")

    restore = []
    if a.sav:
        dest = os.path.join(os.path.dirname(exe), "Saves", stem + ".sav")
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        restore.append((dest, open(dest, "rb").read() if os.path.exists(dest) else None))
        shutil.copy(a.sav, dest)

    t0 = time.time()
    cmd = [exe, "--testRunner", f"--timeout={a.timeout}", rom, lua]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    print(f"emulator pid {p.pid} (to stop only this run: taskkill /T /F /PID {p.pid})", flush=True)
    try:
        stdout, rc = p.communicate(timeout=a.timeout + 30)[0], p.returncode
    except subprocess.TimeoutExpired:
        p.kill()
        p.communicate()
        rc = 124
    finally:
        if restore:
            time.sleep(0.5)
        for path, old in restore:
            if old is None and os.path.exists(path):
                os.remove(path)
            elif old is not None:
                open(path, "wb").write(old)

    if rc not in (0, 2) and time.time() - t0 >= a.timeout:
        rc = 124
    if os.path.exists(err):
        print("Lua error:", open(err, encoding="utf-8").read().strip())
        rc = 2
    elif rc not in (0, 124) and stdout.strip():
        print("\n".join(stdout.strip().splitlines()[-10:]))

    shot_files = sorted(glob.glob(os.path.join(out, "f[0-9]*.png")))
    final = os.path.join(out, "final.png")
    print(f"exit {rc}  shots {len(shot_files)}  final {'yes' if os.path.exists(final) else 'NO'}  dir {out}")
    if rc == 0 and a.smoke:
        if not os.path.exists(final) or sheetmod.is_blank(sheetmod.read_png(final)):
            print("SMOKE FAIL: final frame is one flat colour (black screen / hang)")
            rc = 3
        else:
            print("smoke ok: final frame has content")
    if a.sheet and shot_files:
        sheetmod.make(out, changed=0.02)
    return rc


if __name__ == "__main__":
    sys.exit(main())
