"""Release packaging tests for tools/release.py."""
from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import bps  # noqa: E402
import build  # noqa: E402
import release  # noqa: E402


class ReleaseTests(unittest.TestCase):
    def test_release_help_is_non_destructive(self) -> None:
        r = subprocess.run(
            [sys.executable, "-X", "utf8", str(ROOT / "tools" / "release.py"), "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--force", r.stdout)

    def test_package_release_roundtrip_and_force_guard(self) -> None:
        orig = build.ORIG_ROM.read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "rel"
            res = release.package_release(out_dir=out_dir, force=False, run_suite=False)

            bps_path = out_dir / release.BPS_NAME
            zip_path = out_dir / release.ZIP_NAME
            self.assertTrue(bps_path.is_file())
            self.assertTrue(zip_path.is_file())

            rebuilt = bps.apply(orig, bps_path.read_bytes())
            self.assertEqual(len(rebuilt), 0x100000)
            self.assertEqual(hashlib.sha1(rebuilt).hexdigest(), res["pce"][2])

            with zipfile.ZipFile(zip_path, "r") as zf:
                self.assertEqual(sorted(zf.namelist()), ["README.md", release.BPS_NAME])

            with self.assertRaises(FileExistsError):
                release.package_release(out_dir=out_dir, force=False, run_suite=False)

            res2 = release.package_release(out_dir=out_dir, force=True, run_suite=False)
            self.assertEqual(res2["bps"], res["bps"])


if __name__ == "__main__":
    unittest.main()
