# Release Polish Checklist

Every item below must be checked (`[x]`) before `tools/release.py` ships a release.

- [ ] Base ROM SHA-1 verified against `rom.sha1` (`Benkei Gaiden (Japan).pce`, `393,216` B, CRC32 `e1a73797`, SHA-1 `4bc46592f3707a7c3e514abc23e640e3194879ad`)
- [ ] All text tables & dialogue fully extracted and roundtrip-verified in identity build
- [ ] Full English script translated, lint-clean, and dual-reviewed (story + batch checks passing)
- [ ] All menus, shop/battle UI, password/BRAM prompts, and tile-drawn graphics translated
- [ ] Zero leftover Japanese in pointer-reachable areas (`jp_left.py` clean)
- [ ] Debug warp tool disabled in release build (`build.py` release mode)
- [ ] Headless MesenCE visual QA suites (`smoke`, towns, dungeons, battles, shops, ending) passing
- [ ] `.bps` patch generated, roundtrip-verified on clean JP ROM, and clean-ROM smoke-tested
- [ ] `README.md` complete with base/patched checksums, instructions, and screenshots
