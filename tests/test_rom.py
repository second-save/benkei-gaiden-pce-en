"""Base ROM integrity and header/vector sanity tests."""
import hashlib
import sys
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_rom  # noqa: E402

ROM_PATH = ROOT / "rom" / "Benkei Gaiden (Japan).pce"


class RomTests(unittest.TestCase):
    def test_rom_sha1_and_crc32(self) -> None:
        check_rom.check()
        data = ROM_PATH.read_bytes()
        self.assertEqual(len(data), 393216)
        self.assertEqual(zlib.crc32(data) & 0xFFFFFFFF, 0xE1A73797)
        self.assertEqual(hashlib.sha1(data).hexdigest(), "4bc46592f3707a7c3e514abc23e640e3194879ad")

    def test_reset_vector(self) -> None:
        data = ROM_PATH.read_bytes()
        reset_vec = data[0x1FFE] | (data[0x1FFF] << 8)
        self.assertEqual(reset_vec, 0xE000)


if __name__ == "__main__":
    unittest.main()
