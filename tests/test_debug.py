"""Metadata and CLI sanity tests for tools/debug/ (no emulator launch)."""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEBUG_DIR = ROOT / "tools" / "debug"
sys.path.insert(0, str(DEBUG_DIR))

import warp  # noqa: E402


class DebugHarnessTests(unittest.TestCase):
    def test_debug_files_exist(self) -> None:
        self.assertTrue((DEBUG_DIR / "scenes.lua").is_file())
        self.assertTrue((DEBUG_DIR / "warp.lua").is_file())
        self.assertTrue((DEBUG_DIR / "warp.py").is_file())

    def test_scenes_metadata_complete(self) -> None:
        lua_text = warp.SCENES_LUA.read_text(encoding="utf-8")
        names_m = re.search(r"M\.NAMES\s*=\s*\{(.*?)\}", lua_text, re.S)
        self.assertIsNotNone(names_m)
        declared = re.findall(r'"([^"]+)"', names_m.group(1))
        self.assertEqual(len(declared), 25)
        self.assertEqual(len(set(declared)), 25)

        scenes = warp.load_scenes()
        self.assertEqual(list(scenes.keys()), declared)
        for name, meta in scenes.items():
            self.assertTrue(isinstance(meta["desc"], str) and len(meta["desc"]) > 0, name)
            self.assertTrue(isinstance(meta["frames"], int) and meta["frames"] > 0, name)

    def test_warp_list_cli(self) -> None:
        res = subprocess.run(
            [sys.executable, "-X", "utf8", str(DEBUG_DIR / "warp.py"), "--list"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        self.assertEqual(res.returncode, 0, res.stderr)
        for name in warp.load_scenes():
            self.assertIn(name, res.stdout)


if __name__ == "__main__":
    unittest.main()
