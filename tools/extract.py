"""Extract all Japanese text tables and code-inline string references into `script/*.json`."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import check_rom  # noqa: E402
import pce_text  # noqa: E402

ORIG_ROM = ROOT / "rom" / "Benkei Gaiden (Japan).pce"

BOX_BY_GROUP: dict[str, str] = {
    "b00_timestamp": "timestamp",
    "b02_sys": "menu_sys",
    "b09_password": "password",
    "b0a_menus": "title_menu",
    "b0a_locations": "location",
    "b0d_enemy_kanji": "enemy_kanji",
    "b0d_enemy_kana": "enemy_kana",
    "b0e_jutsu": "jutsu",
    "b0e_items": "item",
    "b0e_battle": "battle_tpl",
    "b11_dialogue": "dialogue",
    "b11_bg34_credits": "credits_bg34",
    "b11_ending_nar": "ending_nar",
    "b1b_staff": "staff_roll",
}

KEEP_IDS: set[tuple[str, int]] = {
    ("b00_timestamp", 0),
    ("b02_sys", 10),
    ("b0e_battle", 3),
    ("b0e_battle", 4),
    ("b0e_battle", 5),
    ("b0e_battle", 7),
}


def scan_direct_code_calls(rom: bytes) -> list[tuple[int, int, str, int]]:
    """Return every `(slot_off, bank, kind, ptr)` for inline `$FDEF`/`$FE2A`/`$FE08` calls across 48 banks."""
    calls: list[tuple[int, int, str, int]] = []
    for bank in range(0x30):
        base = bank * 0x2000
        blk = rom[base : base + 0x2000]
        for i in range(len(blk) - 7):
            b0, b1, b2 = blk[i], blk[i + 1], blk[i + 2]
            if b0 != 0x20:
                continue
            if b1 == 0xEF and b2 == 0xFD:
                slot = base + i + 5
                calls.append((slot, bank, "FDEF", blk[i + 5] | (blk[i + 6] << 8)))
            elif b1 == 0x2A and b2 == 0xFE:
                slot = base + i + 3
                calls.append((slot, bank, "FE2A", blk[i + 3] | (blk[i + 4] << 8)))
            elif b1 == 0x08 and b2 == 0xFE:
                slot = base + i + 5
                calls.append((slot, bank, "FE08", blk[i + 5] | (blk[i + 6] << 8)))
    return calls


def resolve_code_target(bank: int, ptr: int, known_offsets: set[int]) -> tuple[int, int, int] | None:
    """Resolve CPU `ptr` (in `bank`) to `(rom_offset, rom_base, cpu_base)` if it points to ROM text."""
    if ptr < 0x4000:
        return None
    if ptr >= 0xE000:
        cands = ((ptr - 0xE000, 0x00000, 0xE000),)
    elif ptr >= 0xC000:
        cands = (
            (0x04000 + (ptr - 0xC000), 0x04000, 0xC000),
            (bank * 0x2000 + (ptr - 0xC000), bank * 0x2000, 0xC000),
        )
    else:
        cands = ((0x1C000 + (ptr - 0x4000), 0x1C000, 0x4000),)

    for off, rbase, cbase in cands:
        if off in known_offsets:
            return off, rbase, cbase
    return None


def scan_direct_code_slots(rom: bytes, known_offsets: set[int]) -> dict[int, list[dict[str, str]]]:
    """Map target ROM string offset -> inline `$FDEF`/`$FE2A`/`$FE08` slot records."""
    by_target: dict[int, list[dict[str, str]]] = defaultdict(list)
    for slot_off, bank, kind, ptr in scan_direct_code_calls(rom):
        resolved = resolve_code_target(bank, ptr, known_offsets)
        if resolved is None:
            continue
        off, rbase, cbase = resolved
        by_target[off].append(
            {
                "slot": f"0x{slot_off:05X}",
                "kind": kind,
                "rom_base": f"0x{rbase:05X}",
                "cpu_base": f"0x{cbase:04X}",
            }
        )
    return by_target


def extract_all(rom: bytes) -> dict[str, dict[str, object]]:
    """Decode all 1,217 strings and assemble per-group JSON payloads."""
    codec = pce_text.PceCodec()
    entries = pce_text.iter_all_rom_strings(rom)
    known_offsets = {e.offset for e in entries} | set(pce_text.MID_STRING_REFS.keys())
    direct_slots = scan_direct_code_slots(rom, known_offsets)

    ptr_table_by_group = {pt.group: pt for pt in pce_text.PTR_TABLES}
    char_tbl_off, char_indices, char_rbase, char_cbase = pce_text.CHAR_NAME_PTR_TABLE
    char_slot_by_idx = {
        sys_idx: {
            "slot": f"0x{char_tbl_off + pos * 2:05X}",
            "kind": "char_table",
            "rom_base": f"0x{char_rbase:05X}",
            "cpu_base": f"0x{char_cbase:04X}",
        }
        for pos, sys_idx in enumerate(char_indices)
    }

    groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for e in entries:
        jp_raw, raw_len = codec.decode(rom, e.offset, length=e.length, bg34=e.bg34, preserve_toggles=True)
        jp, _ = codec.decode(rom, e.offset, length=e.length, bg34=e.bg34, preserve_toggles=False)

        slots: list[dict[str, str]] = []
        pt = ptr_table_by_group.get(e.group)
        if pt is not None:
            slots.append(
                {
                    "slot": f"0x{pt.ptr_offset + e.index * 2:05X}",
                    "kind": "ptr_table",
                    "rom_base": f"0x{pt.rom_base:05X}",
                    "cpu_base": f"0x{pt.cpu_base:04X}",
                }
            )
        if e.group in ("b11_bg34_credits", "b11_ending_nar"):
            c_idx = e.index if e.group == "b11_bg34_credits" else 23 + e.index
            ct = pce_text.CREDITS_PTR_TABLE
            slots.append(
                {
                    "slot": f"0x{ct.ptr_offset + c_idx * 2:05X}",
                    "kind": "credits_table",
                    "rom_base": f"0x{ct.rom_base:05X}",
                    "cpu_base": f"0x{ct.cpu_base:04X}",
                }
            )
        if e.group == "b02_sys" and e.index in char_slot_by_idx:
            slots.append(char_slot_by_idx[e.index])
        for ds in direct_slots.get(e.offset, ()):
            slots.append(ds)

        notes = ""
        status = "todo"
        en = ""
        if e.group == "b0e_items" and e.offset == 0x1C23A:
            status = "data"
            notes = "unused item slot alias -> 0x1C23A"
        elif e.length == 0:
            status = "data"
            notes = "empty 0-byte enemy slot"
        elif (e.group, e.index) == ("b1b_staff", 40):
            status = "data"
            notes = "shared $FF end-of-staff sentinel"
        elif (e.group, e.index) == ("b0a_menus", 26):
            status = "data"
            notes = "empty menu spacer"
        elif (e.group, e.index) in KEEP_IDS:
            status = "keep"
            en = jp

        if (e.group, e.index) == ("b02_sys", 26):
            notes = "Mid-string ref B$08:$C8E7 (FDEF $DEE1 -> 0x05EE1 '{ef}法{ef}{ed}力{end}')"

        groups[e.group].append(
            {
                "id": f"{e.group}_{e.index:03d}_{e.offset:05X}",
                "index": e.index,
                "offset": f"0x{e.offset:05X}",
                "length": e.length,
                "raw_len": raw_len,
                "bg34": e.bg34,
                "ptr": slots[0]["slot"] if slots else None,
                "slots": slots,
                "jp_raw": jp_raw,
                "jp": jp,
                "en": en,
                "max": None,
                "box": BOX_BY_GROUP[e.group],
                "status": status,
                "notes": notes,
            }
        )

    return {
        g: {"group": g, "count": len(rows), "entries": rows}
        for g, rows in groups.items()
    }


def _write_json(path: Path, obj: object) -> None:
    text = json.dumps(obj, indent=1, ensure_ascii=False) + "\n"
    with path.open("w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def dump_script(rom: bytes, out_dir: Path, *, force: bool = False) -> list[Path]:
    """Write `<group>.json` and `manifest.json` under `out_dir`; refuse overwrite without `force=True`."""
    payloads = extract_all(rom)
    targets = [out_dir / f"{g}.json" for g in payloads] + [out_dir / "manifest.json"]
    if not force:
        existing = [p for p in targets if p.exists()]
        if existing:
            raise FileExistsError(f"Refusing to overwrite existing script files without --force: {existing[0]}")

    out_dir.mkdir(parents=True, exist_ok=True)
    summary_groups: dict[str, dict[str, int | str]] = {}
    totals = {"count": 0, "todo": 0, "keep": 0, "data": 0}
    for g, obj in payloads.items():
        rows = obj["entries"]
        counts = {st: sum(1 for r in rows if r["status"] == st) for st in ("todo", "keep", "data")}
        min_off = min(int(r["offset"], 16) for r in rows)
        max_end = max(int(r["offset"], 16) + int(r["raw_len"]) for r in rows)
        summary_groups[g] = {
            "file": f"{g}.json",
            "count": len(rows),
            "range": f"0x{min_off:05X}..0x{max_end:05X}",
            **counts,
        }
        totals["count"] += len(rows)
        for st in ("todo", "keep", "data"):
            totals[st] += counts[st]
        _write_json(out_dir / f"{g}.json", obj)

    manifest = {
        "total": totals,
        "groups": summary_groups,
    }
    _write_json(out_dir / "manifest.json", manifest)
    return targets


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=ROOT / "script", help="Output script directory")
    ap.add_argument("--force", action="store_true", help="Allow overwriting existing script JSON files")
    args = ap.parse_args()

    check_rom.check()
    rom = ORIG_ROM.read_bytes()
    dump_script(rom, args.out, force=args.force)

    manifest = json.loads((args.out / "manifest.json").read_text(encoding="utf-8"))
    for g, info in manifest["groups"].items():
        print(f"{g:18s} count={info['count']:3d} todo={info['todo']:3d} keep={info['keep']:2d} data={info['data']:2d} {info['range']}")
    t = manifest["total"]
    print(f"TOTAL: {t['count']} strings (todo={t['todo']}, keep={t['keep']}, data={t['data']}) -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
