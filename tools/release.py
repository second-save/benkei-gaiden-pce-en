"""Release packager for Benkei Gaiden (PC Engine) English fan translation."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = ROOT / "tools"
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

import batches  # noqa: E402
import bps  # noqa: E402
import build  # noqa: E402
import check_rom  # noqa: E402
import romdiff  # noqa: E402

OPEN_CHECKBOX_RE = re.compile(r"^\s*-\s*\[\s\]", re.MULTILINE)
CJK_RE = re.compile(r"[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\uFF00-\uFFEF]")
PLACEHOLDER_TOKENS = ("Work in progress", "<Game title>", "minhnhattonthat", "ko-fi", "<CRC32>", "<SHA-1>", "TBD")
BYPASSED_B0A_TODO = {21, 22, 23, 24, 25, 27, 28, 29}

BPS_NAME = "benkei-gaiden-pce-en.bps"
ZIP_NAME = "benkei-gaiden-pce-en.zip"


def _hashes(data: bytes) -> tuple[int, str, str]:
    return len(data), f"{zlib.crc32(data) & 0xFFFFFFFF:08x}", hashlib.sha1(data).hexdigest()


def _check_script_coverage() -> int:
    """Validate script batches, active translations, and expected bypassed entries."""
    if batches.main(["check"]) != 0:
        raise RuntimeError("tools/batches.py check failed")
    errs = batches.check_script()
    if errs:
        raise RuntimeError("tools/batches.py check --script failed:\n" + "\n".join(errs[:20]))

    manifest = json.loads((ROOT / "script" / "manifest.json").read_text(encoding="utf-8"))
    done_count = 0
    for grp, info in manifest["groups"].items():
        entries = json.loads((ROOT / "script" / info["file"]).read_text(encoding="utf-8"))["entries"]
        for e in entries:
            st = e["status"]
            idx = e["index"]
            if st == "done":
                en = e.get("en", "")
                if not en or CJK_RE.search(en):
                    raise ValueError(f"{e['id']}: invalid or untranslated done entry {en!r}")
                done_count += 1
            elif st == "todo":
                if grp == "b0d_enemy_kana" or (grp == "b0a_menus" and idx in BYPASSED_B0A_TODO):
                    continue
                raise ValueError(f"{e['id']}: unexpected todo entry in release build")
            elif st not in ("keep", "data"):
                raise ValueError(f"{e['id']}: unknown status {st!r}")
    return done_count


def _check_docs() -> str:
    """Ensure docs/polish.md has no open items and README.md has no placeholders."""
    polish_path = ROOT / "docs" / "polish.md"
    if not polish_path.is_file():
        raise FileNotFoundError(f"Missing {polish_path}")
    if OPEN_CHECKBOX_RE.search(polish_path.read_text(encoding="utf-8")):
        raise ValueError("docs/polish.md still contains open '- [ ]' items")

    readme_path = ROOT / "README.md"
    if not readme_path.is_file():
        raise FileNotFoundError(f"Missing {readme_path}")
    readme_text = readme_path.read_text(encoding="utf-8")
    for bad in PLACEHOLDER_TOKENS:
        if bad.lower() in readme_text.lower():
            raise ValueError(f"README.md still contains forbidden placeholder/link {bad!r}")
    return readme_text


def _run_unit_suite() -> None:
    r = subprocess.run(
        [sys.executable, "-X", "utf8", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
        cwd=ROOT,
    )
    if r.returncode != 0:
        raise RuntimeError(f"Unit test suite failed with exit code {r.returncode}")


def package_release(
    *,
    out_dir: Path | None = None,
    force: bool = False,
    run_suite: bool = True,
) -> dict[str, tuple[int, str, str]]:
    """Run all release gates, build & verify ROM + BPS + zip, and return asset hashes."""
    check_rom.check()
    done_count = _check_script_coverage()
    _check_docs()
    if run_suite:
        _run_unit_suite()

    release_dir = out_dir or (ROOT / "release")
    release_dir.mkdir(parents=True, exist_ok=True)
    bps_path = release_dir / BPS_NAME
    zip_path = release_dir / ZIP_NAME
    if not force:
        for dest in (bps_path, zip_path):
            if dest.exists():
                raise FileExistsError(f"Refusing to overwrite existing release artifact {dest} without --force")

    orig_rom = build.ORIG_ROM.read_bytes()
    work_dir = ROOT / "work" / "asm"
    release_rom, writes = build.build_patched(orig_rom, ROOT / "script", work_dir, mode="translate")
    errs, _ = romdiff.check(orig_rom, release_rom, set(), writes)
    if errs:
        raise RuntimeError("romdiff check failed on release ROM:\n" + "\n".join(errs[:20]))

    built_pce_path = ROOT / "build" / "benkei_en.pce"
    built_pce_path.parent.mkdir(parents=True, exist_ok=True)
    built_pce_path.write_bytes(release_rom)
    build.write_writes_log(ROOT / "build" / "writes.txt", writes)

    patch_bytes = bps.make(orig_rom, release_rom)
    bps_path.write_bytes(patch_bytes)

    applied = bps.apply(orig_rom, patch_bytes)
    if applied != release_rom or hashlib.sha1(applied).hexdigest() != hashlib.sha1(release_rom).hexdigest():
        raise ValueError("BPS roundtrip mismatch against clean Japanese ROM")

    readme_path = ROOT / "README.md"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        zf.write(bps_path, arcname=BPS_NAME)
        zf.write(readme_path, arcname="README.md")

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = sorted(zf.namelist())
        if names != ["README.md", BPS_NAME]:
            raise ValueError(f"Unexpected zip contents {names}; expected ['README.md', '{BPS_NAME}']")

    zip_bytes = zip_path.read_bytes()
    results = {
        "orig": _hashes(orig_rom),
        "pce": _hashes(release_rom),
        "bps": _hashes(patch_bytes),
        "zip": _hashes(zip_bytes),
    }

    print(f"Release build OK ({done_count} done JSON entries + en_mid, {len(writes)} writes):")
    for label, key, path in (
        ("Clean JP ROM", "orig", build.ORIG_ROM),
        ("Release PCE ", "pce", built_pce_path),
        ("BPS Patch   ", "bps", bps_path),
        ("Release Zip ", "zip", zip_path),
    ):
        sz, crc, sha = results[key]
        rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path
        print(f"  {label}: {sz:>10,d} B  CRC32={crc}  SHA1={sha}  ({rel})")
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true", help="Overwrite existing release artifacts")
    ap.add_argument("--out-dir", type=Path, default=None, help="Override release output directory")
    args = ap.parse_args(argv)
    package_release(out_dir=args.out_dir, force=args.force, run_suite=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
