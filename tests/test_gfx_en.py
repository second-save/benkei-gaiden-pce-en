"""Phase 7 translated graphics, password/name-entry ASCII grids, and full translate-ROM tests."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build  # noqa: E402
import gfx_en  # noqa: E402
import pce_gfx  # noqa: E402
import pce_text  # noqa: E402
import romdiff  # noqa: E402

ORIG_ROM = ROOT / "rom" / "Benkei Gaiden (Japan).pce"


class GfxAndTranslateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.orig = ORIG_ROM.read_bytes()

    def test_bg23_splash_patch_budget_and_preserve(self) -> None:
        m = pce_gfx.bg_meta(self.orig, 23)
        orig_tiles, orig_len = pce_gfx.decompress_stream(self.orig, m.offset, m.count, 32, m.x_end)
        comp, reported_len, map_90b = gfx_en.patch_bg23(self.orig)
        self.assertEqual(reported_len, orig_len)
        self.assertLessEqual(len(comp), orig_len)
        self.assertEqual(len(map_90b), 90)

        new_tiles, used = pce_gfx.decompress_stream(comp, 0, m.count, 32, m.x_end)
        self.assertEqual(used, len(comp))
        self.assertEqual(len(new_tiles), len(orig_tiles))

        preserved = list(range(0x00, 0x0C)) + list(range(0x11, 0x1B)) + list(range(0x20, 0x2E))
        for tid in preserved:
            self.assertEqual(new_tiles[tid], orig_tiles[tid], f"BG[23] SUNSOFT tile {tid:#x} modified")
        self.assertTrue(any(new_tiles[tid] != orig_tiles[tid] for tid in gfx_en.BG23_TAGLINE_TILES))

    def test_bg15_and_bg16_shop_signs_budget_and_preserve(self) -> None:
        m15 = pce_gfx.bg_meta(self.orig, 15)
        orig15, orig15_len = pce_gfx.decompress_stream(self.orig, m15.offset, m15.count, 32, m15.x_end)
        comp15, len15 = gfx_en.patch_bg15(self.orig)
        self.assertEqual(len15, orig15_len)
        self.assertLessEqual(len(comp15), orig15_len)
        new15, used15 = pce_gfx.decompress_stream(comp15, 0, m15.count, 32, m15.x_end)
        self.assertEqual(used15, len(comp15))

        bg15_targets = {46, 47, 62, 63}
        for tid in range(len(orig15)):
            if tid in bg15_targets:
                self.assertNotEqual(new15[tid], orig15[tid], f"BG[15] target tile {tid} unchanged")
            else:
                self.assertEqual(new15[tid], orig15[tid], f"BG[15] untouched tile {tid} modified")

        m16 = pce_gfx.bg_meta(self.orig, 16)
        orig16, orig16_len = pce_gfx.decompress_stream(self.orig, m16.offset, m16.count, 32, m16.x_end)
        comp16, len16 = gfx_en.patch_bg16(self.orig)
        self.assertEqual(len16, orig16_len)
        self.assertLessEqual(len(comp16), orig16_len)
        new16, used16 = pce_gfx.decompress_stream(comp16, 0, m16.count, 32, m16.x_end)
        self.assertEqual(used16, len(comp16))

        bg16_targets = {64, 65, 80, 81, 66, 67, 82, 83, 162, 163, 178, 179, *range(207, 215)}
        for tid in range(len(orig16)):
            if tid not in bg16_targets:
                self.assertEqual(new16[tid], orig16[tid], f"BG[16] untouched tile {tid} modified")
        self.assertTrue(all(new16[tid] != orig16[tid] for tid in (64, 66, 162, 207)))

    def test_spr21_spr24_and_title_oam(self) -> None:
        m21 = pce_gfx.spr_meta(self.orig, 21)
        m24 = pce_gfx.spr_meta(self.orig, 24)
        _, orig21 = pce_gfx.decompress_stream(self.orig, m21.offset, m21.count, 128, m21.x_end)
        _, orig24 = pce_gfx.decompress_stream(self.orig, m24.offset, m24.count, 128, m24.x_end)

        comp21, rep21, comp24, rep24 = gfx_en.patch_spr21_and_24(self.orig)
        self.assertEqual((rep21, rep24), (orig21, orig24))
        self.assertLessEqual(len(comp21), orig21)
        self.assertLessEqual(len(comp24), orig24)

        pats21, used21 = pce_gfx.decompress_stream(comp21, 0, m21.count, 128, m21.x_end)
        pats24, used24 = pce_gfx.decompress_stream(comp24, 0, m24.count, 128, m24.x_end)
        self.assertEqual((used21, used24), (len(comp21), len(comp24)))
        self.assertEqual((len(pats21), len(pats24)), (m21.count, m24.count))
        self.assertTrue(any(p != bytes(128) for p in pats21))
        self.assertTrue(any(p != bytes(128) for p in pats24[:6]))

        patches = gfx_en.title_oam_patches()
        self.assertEqual(
            {off: len(payload) for off, (payload, _) in patches.items()},
            {0x17D73: 9, 0x17412: 24, 0x1742B: 52, 0x1747D: 24},
        )
        # Terminators (0x90) right after 0x68, 0x69, 0x6A, and 0x6B must remain untouched.
        for term_off in (0x1742A, 0x1745F, 0x1747C, 0x17495):
            self.assertEqual(self.orig[term_off], 0x90)
            for off, (payload, _) in patches.items():
                self.assertFalse(off <= term_off < off + len(payload))

    def test_ascii_password_and_name_entry_grids(self) -> None:
        codec = pce_text.EnCodec("en")
        m_entries = json.loads((ROOT / "script" / "b0a_menus.json").read_text(encoding="utf-8"))["entries"]
        pw_entries = json.loads((ROOT / "script" / "b09_password.json").read_text(encoding="utf-8"))["entries"]

        m03_raw = b"".join(codec.encode(e["en"]) for e in m_entries[:4])
        self.assertEqual(len(m03_raw), 77)
        name_glyphs = [b for b in m03_raw if b not in (0x0F, 0xFF)]
        self.assertEqual(len(name_glyphs), 64)
        self.assertEqual(len(set(name_glyphs)), 64)
        self.assertNotIn(0x00, name_glyphs)

        pw_raw = b"".join(codec.encode(e["en"]) for e in pw_entries)
        self.assertEqual(len(pw_raw), 112)
        want_spaces = [
            [5, 11, 17],
            [5, 11, 17],
            [5, 11, 17, 19, 21],
            [5, 7, 9, 11, 17],
            [5, 11, 17],
        ]
        for entry, exp_sp in zip(pw_entries, want_spaces):
            enc = codec.encode(entry["en"])
            spaces = [i for i, b in enumerate(enc) if b == 0x0F]
            self.assertEqual(spaces, exp_sp, entry["id"])
        self.assertLessEqual(set(name_glyphs), set(pw_raw))

        name_01_chars = set("".join(e["en"].replace("{end}", "") for e in m_entries[:2]))
        for secret in ("SOUNDTEST", "DEBUGMODE"):
            self.assertTrue(set(secret) <= name_01_chars)
            self.assertNotIn(0x00, codec.encode(secret))

    def test_translate_build_romdiff_and_mirrors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work_dir = Path(tmp) / "asm"
            built, writes = build.build_patched(self.orig, ROOT / "script", work_dir, mode="translate")
            self.assertEqual(len(built), 0x100000)

            errs, _ = romdiff.check(self.orig, built, set(), writes)
            self.assertEqual(errs, [])
            self.assertEqual(built[0x80000:0xA0000], built[0x40000:0x60000])
            self.assertEqual(built[0xA0000:0xC0000], built[0x40000:0x60000])


if __name__ == "__main__":
    unittest.main()
