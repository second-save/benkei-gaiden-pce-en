"""Phase 4 extraction roundtrip, slot integrity, and full-ROM text coverage tests."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "script"
sys.path.insert(0, str(ROOT / "tools"))

import extract  # noqa: E402
import pce_text  # noqa: E402

ORIG_ROM = ROOT / "rom" / "Benkei Gaiden (Japan).pce"

CONTIGUOUS_REGIONS: tuple[tuple[str, int, int], ...] = (
    ("b00_timestamp", 0x01B75, 0x01B8A),
    ("b02_sys", 0x05E36, 0x05FBC),
    ("b09_password", 0x12609, 0x12683),
    ("b0a_menus", 0x1505E, 0x151AF),
    ("b0a_locations", 0x15268, 0x152C9),
    ("b0d_enemy_kanji", 0x1BA06, 0x1BD11),
    ("b0d_enemy_kana", 0x1BD12, 0x1BFE8),
    ("b0e_b11_all", 0x1C032, 0x23F93),
    ("b1b_staff", 0x37A3D, 0x37C2D),
)


class ExtractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rom = ORIG_ROM.read_bytes()
        cls.codec = pce_text.PceCodec()
        cls.manifest = json.loads((SCRIPT_DIR / "manifest.json").read_text(encoding="utf-8"))
        cls.groups: dict[str, dict[str, object]] = {}
        cls.rows: list[dict[str, object]] = []
        for g in cls.manifest["groups"]:
            data = json.loads((SCRIPT_DIR / f"{g}.json").read_text(encoding="utf-8"))
            cls.groups[g] = data
            cls.rows.extend(data["entries"])

    def test_committed_script_roundtrip(self) -> None:
        self.assertEqual(self.manifest["total"]["count"], 1217)
        self.assertEqual(len(self.rows), 1217)
        self.assertEqual(len({r["id"] for r in self.rows}), 1217)

        for r in self.rows:
            off = int(str(r["offset"]), 16)
            raw_len = int(r["raw_len"])  # type: ignore[arg-type]
            bg34 = bool(r["bg34"])
            enc = self.codec.encode(str(r["jp_raw"]), bg34=bg34)
            self.assertEqual(enc, self.rom[off : off + raw_len], r["id"])
            plain, _ = self.codec.decode(self.rom, off, length=r["length"], bg34=bg34, preserve_toggles=False)  # type: ignore[arg-type]
            self.assertEqual(plain, r["jp"], r["id"])

    def test_every_slot_resolves_to_entry_offset_in_orig(self) -> None:
        for r in self.rows:
            off = int(str(r["offset"]), 16)
            for s in r["slots"]:  # type: ignore[attr-defined]
                slot_off = int(s["slot"], 16)
                rbase = int(s["rom_base"], 16)
                cbase = int(s["cpu_base"], 16)
                ptr_val = self.rom[slot_off] | (self.rom[slot_off + 1] << 8)
                expected = cbase + (off - rbase)
                self.assertEqual(ptr_val, expected, f"{r['id']} slot {s}")

    def test_full_rom_text_range_coverage_zero_gaps(self) -> None:
        cov = bytearray(len(self.rom))
        for r in self.rows:
            off = int(str(r["offset"]), 16)
            raw_len = int(r["raw_len"])  # type: ignore[arg-type]
            for k in range(off, off + raw_len):
                cov[k] |= 1
        for pt in (*pce_text.PTR_TABLES, pce_text.CREDITS_PTR_TABLE):
            n = pt.count + (1 if pt.has_sentinel else 0)
            for k in range(pt.ptr_offset, pt.ptr_offset + n * 2):
                cov[k] |= 2

        for name, start, end in CONTIGUOUS_REGIONS:
            gaps = [hex(i) for i in range(start, end) if cov[i] == 0]
            self.assertEqual(gaps, [], f"uncovered bytes in {name}: {gaps[:10]}")

        self.assertEqual(self.rom[0x23F93:0x24000], b"\xff" * 109)

    def test_all_direct_fdef_fe2a_fe08_calls_covered(self) -> None:
        known = {int(str(r["offset"]), 16) for r in self.rows} | set(pce_text.MID_STRING_REFS.keys())
        unmatched = []
        for slot_off, bank, kind, ptr in extract.scan_direct_code_calls(self.rom):
            if ptr < 0x4000:
                continue
            if extract.resolve_code_target(bank, ptr, known) is None:
                unmatched.append((hex(slot_off), bank, kind, hex(ptr)))
        self.assertEqual(unmatched, [])

    def test_dump_refuses_overwrite_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "script"
            extract.dump_script(self.rom, out, force=False)
            sample = out / "b02_sys.json"
            data = json.loads(sample.read_text(encoding="utf-8"))
            data["entries"][0]["en"] = "Talk"
            sample.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

            with self.assertRaises(FileExistsError):
                extract.dump_script(self.rom, out, force=False)
            recheck = json.loads(sample.read_text(encoding="utf-8"))
            self.assertEqual(recheck["entries"][0]["en"], "Talk")

            extract.dump_script(self.rom, out, force=True)
            overwritten = json.loads(sample.read_text(encoding="utf-8"))
            self.assertEqual(overwritten["entries"][0]["en"], "")


if __name__ == "__main__":
    unittest.main()
