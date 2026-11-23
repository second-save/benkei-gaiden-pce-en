"""One-command repository check: verifies base ROM hash, batch lint (when present), and unit tests."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_rom  # noqa: E402


def main() -> int:
    check_rom.check()
    print("rom ok")

    batches = ROOT / "tools" / "batches.py"
    if batches.is_file() and any((ROOT / "work" / "tl").glob("*.tsv")) if (ROOT / "work" / "tl").is_dir() else False:
        r_lint = subprocess.run([sys.executable, "-X", "utf8", str(batches), "check"], cwd=ROOT)
        if r_lint.returncode != 0:
            return r_lint.returncode

    tests_dir = ROOT / "tests"
    if tests_dir.is_dir() and any(tests_dir.glob("test_*.py")):
        r = subprocess.run(
            [sys.executable, "-X", "utf8", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
            cwd=ROOT,
        )
        if r.returncode != 0:
            return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
