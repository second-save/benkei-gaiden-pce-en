"""Phase 5 English codec, 8x16 BG[01] font, far-string engine ASM, marker build, and window budget tests."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build  # noqa: E402
import font_en  # noqa: E402
import pce_gfx  # noqa: E402
import pce_text  # noqa: E402
import romdiff  # noqa: E402

ORIG_ROM = ROOT / "rom" / "Benkei Gaiden (Japan).pce"


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.orig = ORIG_ROM.read_bytes()

    def test_en_codec_roundtrip(self) -> None:
        codec = pce_text.EnCodec("en")
        self.assertEqual(len(codec.tbl.dec), 84)
        all_chars = (
            '0123456789?"!:- _/.,;+*\'()'
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz[]&%#~"
        )
        self.assertEqual(len(all_chars), 84)
        sample = f"{all_chars[:23]}{{nl}}{all_chars[23:46]}{{page}}{all_chars[46:]}[EC]{{end}}"
        enc = codec.encode(sample)
        dec, used = codec.decode(enc)
        self.assertEqual(used, len(enc))
        self.assertEqual(dec, sample)

    def test_font_bg01_patch(self) -> None:
        m = pce_gfx.bg_meta(self.orig, 1)
        orig_tiles, orig_len = pce_gfx.decompress_stream(self.orig, m.offset, m.count, 32, m.x_end)
        comp, reported_len = font_en.patch_bg01(self.orig)
        self.assertEqual(reported_len, orig_len)
        self.assertLessEqual(len(comp), orig_len)

        new_tiles, _ = pce_gfx.decompress_stream(comp, 0, m.count, 32, m.x_end)
        self.assertEqual(len(new_tiles), len(orig_tiles))

        # Tiles >= $60 (borders, cursors, remaining glyphs) must remain identical to original.
        for idx in range(0x60, len(orig_tiles)):
            self.assertEqual(new_tiles[idx], orig_tiles[idx], f"BG[01] tile {idx:#x} modified")

        # Planes 2 and 3 (bytes 16..31) across all 253 tiles must remain identical ($EF kanji preserved).
        for idx in range(len(orig_tiles)):
            self.assertEqual(new_tiles[idx][16:], orig_tiles[idx][16:], f"BG[01] tile {idx:#x} p2/p3 modified")

    def test_engine_asm_assemble(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work_dir = Path(tmp)
            b00, b00_sym = build.assemble_section(ROOT / "asm" / "engine_b00.asm", work_dir, 0x1F90, 80)
            b02, b02_sym = build.assemble_section(ROOT / "asm" / "engine_b02.asm", work_dir, 0x1FBC, 68)
            b09_raw, b09_sym = build._run_wla(ROOT / "asm" / "engine_b09.asm", work_dir)

            self.assertLessEqual(len(b00), 80)
            self.assertLessEqual(len(b02), 68)
            self.assertTrue({"SafeWait_E2C0", "SafeWait_EF33", "Hook_F915", "Inc11By3"} <= b00_sym.keys())
            self.assertTrue({"Hook_CE45", "Hook_CF27", "Hook_EnemyBank"} <= b02_sym.keys())
            self.assertEqual(b09_sym["Menu2_Run"], 0xD28E)
            self.assertEqual(b09_sym["Menu4_Run"], 0xD2BD)
            self.assertEqual(b09_sym["ClearCursor4"], 0xD35D)
            self.assertEqual(len(b09_raw[0x128E:0x139B]), 269)

    def test_marker_build_and_romdiff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work_dir = Path(tmp) / "asm"
            built, writes = build.build_patched(self.orig, ROOT / "script", work_dir, mode="marker")
            self.assertEqual(len(built), 0x100000)

            errs, _ = romdiff.check(self.orig, built, set(), writes)
            self.assertEqual(errs, [])

            # Validate Bank $60 enemy pointer table ($A000..$BFFF, 112 entries + sentinel).
            ptrs = [int.from_bytes(built[0xC0000 + i * 2 : 0xC0000 + i * 2 + 2], "little") for i in range(113)]
            self.assertEqual(ptrs[0], 0xA000 + 113 * 2)
            self.assertTrue(all(ptrs[i] <= ptrs[i + 1] for i in range(112)))
            self.assertLessEqual(ptrs[-1], 0xC000)
            codec = pce_text.EnCodec("en")
            e000_off = 0xC0000 + (ptrs[0] - 0xA000)
            txt0, _ = codec.decode(built, e000_off, length=ptrs[1] - ptrs[0])
            self.assertEqual(txt0, "E000")

    def test_windows_json_covers_all_boxes(self) -> None:
        win = json.loads((ROOT / "tools" / "windows.json").read_text(encoding="utf-8"))
        manifest = json.loads((ROOT / "script" / "manifest.json").read_text(encoding="utf-8"))
        seen_boxes: set[str] = set()
        seen_ids: set[str] = set()
        for info in manifest["groups"].values():
            entries = json.loads((ROOT / "script" / info["file"]).read_text(encoding="utf-8"))["entries"]
            for e in entries:
                seen_boxes.add(e["box"])
                seen_ids.add(e["id"])

        missing_boxes = seen_boxes - win["boxes"].keys()
        self.assertEqual(missing_boxes, set(), f"Missing boxes in windows.json: {missing_boxes}")
        for oid in win["overrides"]:
            if oid != "b02_sys_026_mid":
                self.assertIn(oid, seen_ids, f"Unknown override id in windows.json: {oid}")


if __name__ == "__main__":
    unittest.main()
