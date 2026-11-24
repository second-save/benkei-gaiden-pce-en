"""Phase 3 identity build, lossless/exact GFX codec, and 1 MiB WLA-DX expansion tests."""
from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build  # noqa: E402
import pce_gfx  # noqa: E402
import romdiff  # noqa: E402

ORIG_ROM = ROOT / "rom" / "Benkei Gaiden (Japan).pce"


class IdentityBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.orig = ORIG_ROM.read_bytes()

    def test_identity_rom_byte_identical(self) -> None:
        rebuilt = build.build_identity(self.orig)
        self.assertEqual(len(rebuilt), len(self.orig))
        self.assertEqual(rebuilt, self.orig)
        self.assertEqual(hashlib.sha1(rebuilt).hexdigest(), "4bc46592f3707a7c3e514abc23e640e3194879ad")

    def test_all_gfx_lossless_and_target_exact(self) -> None:
        exact_targets = {"bg": {1, 15, 16, 17, 23, 33, 34}, "spr": {21, 24}}
        for idx in range(pce_gfx.BG_COUNT):
            m = pce_gfx.bg_meta(self.orig, idx)
            tiles, orig_len = pce_gfx.decompress_stream(self.orig, m.offset, m.count, 32, m.x_end)
            comp = pce_gfx.compress_bg(tiles, m.bpp)
            redec, _ = pce_gfx.decompress_stream(comp, 0, m.count, 32, m.x_end)
            self.assertEqual(redec, tiles, f"BG[{idx}] roundtrip failed")
            self.assertLessEqual(len(comp), orig_len, f"BG[{idx}] grew")
            if idx not in pce_gfx.NON_EXACT_BG or idx in exact_targets["bg"]:
                self.assertEqual(comp, self.orig[m.offset : m.offset + orig_len], f"BG[{idx}] not bit-exact")

        for idx in range(pce_gfx.SPR_COUNT):
            m = pce_gfx.spr_meta(self.orig, idx)
            pats, orig_len = pce_gfx.decompress_stream(self.orig, m.offset, m.count, 128, m.x_end)
            comp = pce_gfx.compress_spr(pats, m.bpp)
            redec, _ = pce_gfx.decompress_stream(comp, 0, m.count, 128, m.x_end)
            self.assertEqual(redec, pats, f"SPR[{idx}] roundtrip failed")
            self.assertEqual(comp, self.orig[m.offset : m.offset + orig_len], f"SPR[{idx}] not bit-exact")

    def test_expanded_1m_identity_and_romdiff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            work_dir = Path(tmp) / "asm"
            expanded, writes = build.build_expanded_identity(self.orig, work_dir)
            self.assertEqual(len(expanded), 0x100000)
            self.assertEqual(expanded[: len(self.orig)], self.orig)

            upper = self.orig[0x40000:0x60000]
            self.assertEqual(expanded[0x80000:0xA0000], upper)
            self.assertEqual(expanded[0xA0000:0xC0000], upper)

            sig = b"BENKEI-GAIDEN-EN\x00\xea\x60"
            self.assertTrue(expanded[0x60000:].startswith(sig))
            self.assertTrue(all(b == 0xFF for b in expanded[0x60000 + len(sig) : 0x80000]))
            self.assertTrue(all(b == 0xFF for b in expanded[0xC0000:0x100000]))

            writes_log = Path(tmp) / "writes.txt"
            rb = build.RomBuilder(self.orig, 0x100000)
            rb.writes = writes
            rb.write_log(writes_log)
            parsed = romdiff.load_writes(str(writes_log))
            errs, _ = romdiff.check(self.orig, expanded, set(), parsed)
            self.assertEqual(errs, [])

    def test_romdiff_selftest(self) -> None:
        romdiff.selftest()


if __name__ == "__main__":
    unittest.main()
