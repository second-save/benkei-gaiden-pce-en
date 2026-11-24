"""Text table and full-ROM decode/encode roundtrip tests."""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pce_text  # noqa: E402

ROM_PATH = ROOT / "rom" / "Benkei Gaiden (Japan).pce"
UNKNOWN_RE = re.compile(r"\[([0-9A-Fa-f]{2}|[A-Za-z0-9]+:[0-9A-Fa-f]{2})\]")


class TextCodecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.codec = pce_text.PceCodec()
        cls.rom = ROM_PATH.read_bytes()
        cls.entries = pce_text.iter_all_rom_strings(cls.rom)

    def test_entry_count(self) -> None:
        # 1 + 56 + 5 + 31 + 13 + 112 + 112 + 32 + 128 + 13 + 648 + 23 + 2 + 41 = 1217
        self.assertEqual(len(self.entries), 1217)

    def test_byte_exact_roundtrip_all_strings(self) -> None:
        for entry in self.entries:
            txt, used = self.codec.decode(
                self.rom,
                entry.offset,
                length=entry.length,
                bg34=entry.bg34,
                preserve_toggles=True,
            )
            unknowns = UNKNOWN_RE.findall(txt)
            # Only known unmapped byte is the 4 spacer slots ($EC) in B$0A $50E9
            if entry.offset == 0x150E9:
                self.assertEqual(unknowns, ["EC", "EC", "EC", "EC"])
            else:
                self.assertEqual(unknowns, [], f"unknowns in {entry}: {txt!r}")

            reencoded = self.codec.encode(txt, bg34=entry.bg34)
            expected = self.rom[entry.offset : entry.offset + used]
            self.assertEqual(reencoded, expected, f"byte mismatch at {entry}: {txt!r}")

    def test_plain_unicode_roundtrip_all_strings(self) -> None:
        for entry in self.entries:
            plain, _ = self.codec.decode(
                self.rom,
                entry.offset,
                length=entry.length,
                bg34=entry.bg34,
                preserve_toggles=False,
            )
            reencoded = self.codec.encode(plain, bg34=entry.bg34)
            redecoded, _ = self.codec.decode(
                reencoded,
                0,
                length=len(reencoded) if entry.length is not None else None,
                bg34=entry.bg34,
                preserve_toggles=False,
            )
            self.assertEqual(redecoded, plain, f"plain roundtrip mismatch at {entry}")


if __name__ == "__main__":
    unittest.main()
