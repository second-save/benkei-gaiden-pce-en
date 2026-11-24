"""Batch splitter, checker, pair renderer, and script merger for PCE Benkei Gaiden."""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "script"
MANIFEST_PATH = SCRIPT_DIR / "manifest.json"
GLOSSARY_PATH = ROOT / "glossary.md"
TL_DIR = ROOT / "work" / "tl"
PAIRS_DIR = TL_DIR / "pairs"

if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import fit  # noqa: E402

TABLE_GROUPS = [
    "b02_sys",
    "b0a_menus",
    "b0a_locations",
    "b0e_battle",
    "b0e_jutsu",
    "b0e_items",
    "b0d_enemy_kanji",
    "b11_bg34_credits",
    "b11_ending_nar",
    "b1b_staff",
]
DIALOGUE_GROUPS = ["b11_dialogue"]
EXCLUDED_GROUPS = {"b0d_enemy_kana", "b09_password"}

TAG_STRIP_RE = re.compile(r"\{nl\}|\{page\}|\{end\}|\[EC\]|\[\w+\]")
SPACE_BREAK_RE = re.compile(r"\{nl\}|\{page\}")
END_ONLY_RE = re.compile(r"\{end\}")
CJK_RE = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff\uff00-\uffef]")
HONORIFIC_RE = re.compile(
    r"(?:-(?:san|sama|dono|chan|kun|sensei)\b|\b(?:oji-?san|ojii-?(?:chan|san)|jii-?san)\b)",
    re.IGNORECASE,
)


ENEMY_ALIAS_RE = re.compile(r"\[ENEMY:([^\]]+)\]")


@dataclass(frozen=True)
class Term:
    """One row from the canonical glossary table."""

    jp: str
    en: str
    max_cols: int | None
    notes: str
    avoid: tuple[str, ...]
    ui_only: bool
    note_only: bool
    enemy_en: str | None = None


def _char_kind(ch: str) -> str:
    if "\u4e00" <= ch <= "\u9fff" or ch == "々":
        return "kanji"
    if "\u3040" <= ch <= "\u309f":
        return "hira"
    if "\u30a0" <= ch <= "\u30ff" or ch == "ー":
        return "kata"
    if ch.isascii() and (ch.isalnum() or ch == "_"):
        return "ascii"
    return "other"


def _term_spans(plain: str, term: str) -> list[tuple[int, int]]:
    """Return all `(start, end)` spans of `term` at whole-script-run boundaries in `plain`."""
    if not term:
        return []
    spans: list[tuple[int, int]] = []
    start = 0
    k_first = _char_kind(term[0])
    k_last = _char_kind(term[-1])
    while True:
        idx = plain.find(term, start)
        if idx < 0:
            return spans
        left_ok = idx == 0 or k_first == "other" or _char_kind(plain[idx - 1]) != k_first
        end = idx + len(term)
        right_ok = end == len(plain) or k_last == "other" or _char_kind(plain[end]) != k_last
        if left_ok and right_ok:
            spans.append((idx, end))
        start = idx + 1


def has_term(jp: str, term: str) -> bool:
    """Return True if term occurs inside jp at whole-script-run boundaries."""
    return bool(_term_spans(TAG_STRIP_RE.sub("", jp), term))


def load_glossary(path: Path = GLOSSARY_PATH) -> list[Term]:
    """Parse 5-column markdown glossary rows (`| JP | EN | max | notes | Avoid |`)."""
    if not path.exists():
        return []
    terms: list[Term] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 5:
            continue
        jp, en, max_str, notes, avoid_str = cells[:5]
        if not jp or jp == "JP" or jp.startswith("---"):
            continue
        max_cols = int(max_str) if max_str.isdigit() else None
        avoid = tuple(
            a.strip().strip("`")
            for a in re.split(r"[,;]", avoid_str)
            if a.strip() and a.strip() != "-"
        )
        alias_m = ENEMY_ALIAS_RE.search(notes)
        terms.append(
            Term(
                jp=jp,
                en=en.strip("`"),
                max_cols=max_cols,
                notes=notes,
                avoid=avoid,
                ui_only="[UI]" in notes,
                note_only="[NOTE]" in notes,
                enemy_en=alias_m.group(1).strip() if alias_m else None,
            )
        )
    return terms


def _matched_terms(jp: str, box: str, terms: list[Term], entry_id: str = "") -> list[Term]:
    plain = TAG_STRIP_RE.sub("", jp)
    candidates: list[tuple[int, Term]] = []
    for idx, t in enumerate(terms):
        if t.note_only:
            continue
        if t.ui_only and box not in ("menu_sys", "title_menu"):
            continue
        if entry_id == "b02_sys_026_05ED3" and t.jp == "法力":
            continue
        candidates.append((idx, t))

    claimed: list[tuple[int, int]] = []
    chosen: list[tuple[int, Term]] = []
    for idx, t in sorted(candidates, key=lambda item: (-len(item[1].jp), item[0])):
        spans = _term_spans(plain, t.jp)
        if not spans:
            continue
        uncovered = [sp for sp in spans if not any(cs <= sp[0] and sp[1] <= ce for cs, ce in claimed)]
        if uncovered:
            chosen.append((idx, t))
            claimed.extend(uncovered)

    chosen.sort(key=lambda item: item[0])
    return [t for _, t in chosen]


def _effective_en(term: Term, box: str) -> str:
    return term.enemy_en if (box == "enemy_kanji" and term.enemy_en) else term.en


def _format_terms(matched: list[Term], box: str = "") -> str:
    return "; ".join(f"{t.jp} -> {_effective_en(t, box)}" for t in matched)


def _is_excluded(group: str, entry: dict) -> bool:
    if group in EXCLUDED_GROUPS:
        return True
    if entry.get("status") not in ("todo", "done"):
        return True
    if group == "b0a_menus":
        idx = entry["index"]
        if idx < 4 or 21 <= idx <= 29:
            return True
    return False


def _combine_notes(*parts: str) -> str:
    seen: list[str] = []
    for part in parts:
        p = part.strip()
        if p and p not in seen:
            seen.append(p)
    return " | ".join(seen)


def _iter_group_records(group: str, entries: list[dict]) -> list[dict]:
    records: list[dict] = []
    for e in entries:
        if _is_excluded(group, e):
            continue
        eid = e["id"]
        box = e["box"]
        budget = fit.entry_budget(eid, box)
        records.append(
            {
                "group": group,
                "index": e["index"],
                "id": eid,
                "box": box,
                "jp": e["jp"],
                "en": e.get("en", ""),
                "status": e["status"],
                "notes": _combine_notes(e.get("notes", ""), budget.get("notes", "")),
                "is_mid": False,
            }
        )
        if group == "b02_sys" and e["index"] == 26:
            mid_budget = fit.entry_budget("b02_sys_026_mid", "menu_sys")
            records.append(
                {
                    "group": "b02_sys",
                    "index": 26,
                    "id": "b02_sys_026_mid",
                    "box": "menu_sys",
                    "jp": "法力{end}",
                    "en": e.get("en_mid", ""),
                    "status": "done" if (e.get("status") == "done" and e.get("en_mid")) else "todo",
                    "notes": _combine_notes(mid_budget.get("notes", "")),
                    "is_mid": True,
                }
            )
    return records


def _load_manifest(script_dir: Path = SCRIPT_DIR) -> dict:
    return json.loads((script_dir / "manifest.json").read_text(encoding="utf-8"))


def _iter_all_records(script_dir: Path = SCRIPT_DIR) -> list[tuple[str, list[dict]]]:
    manifest = _load_manifest(script_dir)
    groups = manifest["groups"]
    ordered = [g for g in TABLE_GROUPS + DIALOGUE_GROUPS if g in groups and g not in EXCLUDED_GROUPS]
    out: list[tuple[str, list[dict]]] = []
    for g in ordered:
        data = json.loads((script_dir / groups[g]["file"]).read_text(encoding="utf-8"))
        out.append((g, _iter_group_records(g, data["entries"])))
    return out


def _jp_weight(jp: str) -> int:
    return max(1, len(TAG_STRIP_RE.sub("", jp)))


def _escape_cell(val: str) -> str:
    return val.replace("\t", " ").replace("\r", "").replace("\n", " ")


def _write_tsv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    lines = ["\t".join(header)]
    for row in rows:
        lines.append("\t".join(_escape_cell(c) for c in row))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_tsv(path: Path) -> list[dict[str, str]]:
    """Read a UTF-8 TSV file with a header row (supports 2-col `id\\ten` or full .in.tsv)."""
    raw_lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not raw_lines:
        raise ValueError(f"{path}: empty TSV")
    header = raw_lines[0].split("\t")
    if "id" not in header or "en" not in header:
        raise ValueError(f"{path}: TSV header must include 'id' and 'en' columns, got {header}")
    rows: list[dict[str, str]] = []
    for ln_no, line in enumerate(raw_lines[1:], 2):
        cells = line.split("\t")
        if len(cells) < len(header):
            cells.extend([""] * (len(header) - len(cells)))
        elif len(cells) > len(header):
            raise ValueError(f"{path}:{ln_no}: expected {len(header)} tab-separated columns, got {len(cells)}")
        rows.append(dict(zip(header, cells)))
    return rows


def split_batches(
    size: int = 3200,
    script_dir: Path = SCRIPT_DIR,
    tl_dir: Path = TL_DIR,
    glossary_path: Path = GLOSSARY_PATH,
    skip_done: bool = False,
    max_rows: int = 220,
) -> list[tuple[str, str, int, int]]:
    """Split table and dialogue groups into `work/tl/bNNN.in.tsv` batches."""
    terms = load_glossary(glossary_path)
    grouped = _iter_all_records(script_dir)

    table_batches: list[list[dict]] = []
    cur_batch: list[dict] = []
    cur_chars = 0

    for g, recs in grouped:
        if skip_done:
            recs = [r for r in recs if r["status"] != "done"]
        if not recs:
            continue
        if g in TABLE_GROUPS:
            grp_chars = sum(_jp_weight(r["jp"]) for r in recs)
            if cur_batch and (cur_chars + grp_chars > size or len(cur_batch) + len(recs) > max_rows):
                table_batches.append(cur_batch)
                cur_batch = []
                cur_chars = 0
            if (grp_chars > size or len(recs) > max_rows) and not cur_batch:
                for r in recs:
                    w = _jp_weight(r["jp"])
                    if cur_batch and (cur_chars + w > size or len(cur_batch) >= max_rows):
                        table_batches.append(cur_batch)
                        cur_batch = []
                        cur_chars = 0
                    cur_batch.append(r)
                    cur_chars += w
            else:
                cur_batch.extend(recs)
                cur_chars += grp_chars
        else:
            if cur_batch:
                table_batches.append(cur_batch)
                cur_batch = []
                cur_chars = 0
            for r in recs:
                w = _jp_weight(r["jp"])
                if cur_batch and cur_chars + w > size:
                    table_batches.append(cur_batch)
                    cur_batch = []
                    cur_chars = 0
                cur_batch.append(r)
                cur_chars += w

    if cur_batch:
        table_batches.append(cur_batch)

    tl_dir.mkdir(parents=True, exist_ok=True)
    for stale in tl_dir.glob("b[0-9][0-9][0-9].in.tsv"):
        stale.unlink()

    summary: list[tuple[str, str, int, int]] = []
    header = ["id", "box", "max", "terms", "jp", "en", "notes"]
    for idx, recs in enumerate(table_batches, 1):
        name = f"b{idx:03d}"
        rows: list[list[str]] = []
        chars = 0
        groups_seen: list[str] = []
        for r in recs:
            if r["group"] not in groups_seen:
                groups_seen.append(r["group"])
            matched = _matched_terms(r["jp"], r["box"], terms, r["id"])
            rows.append(
                [
                    r["id"],
                    r["box"],
                    fit.format_budget(r["id"], r["box"]),
                    _format_terms(matched, r["box"]),
                    r["jp"],
                    r["en"],
                    r["notes"],
                ]
            )
            chars += _jp_weight(r["jp"])
        _write_tsv(tl_dir / f"{name}.in.tsv", header, rows)
        summary.append((name, "+".join(groups_seen), len(recs), chars))
    return summary


def _word_regex(phrase: str, hyphen_word: bool = False) -> re.Pattern[str]:
    bd_left = r"(?<![\w-])" if hyphen_word else r"(?<!\w)"
    bd_right = r"(?![\w-])" if hyphen_word else r"(?!\w)"
    left = bd_left if phrase[0].isalnum() else ""
    right = bd_right if phrase[-1].isalnum() else ""
    return re.compile(left + re.escape(phrase) + right, re.IGNORECASE)


def _normalize_en(text: str) -> str:
    plain = END_ONLY_RE.sub("", text)
    plain = SPACE_BREAK_RE.sub(" ", plain)
    plain = plain.replace("[EC]", " ")
    return re.sub(r"\s+", " ", plain).strip()


def validate_row(
    entry_id: str,
    box: str,
    jp: str,
    en: str,
    terms: list[Term],
) -> list[str]:
    """Validate one translated entry against fit, tokens, honorifics, and glossary."""
    errs: list[str] = []
    if not en or not en.strip():
        return [f"{entry_id}: empty translation"]
    if re.search(r"\bTODO\b", en, re.IGNORECASE):
        errs.append(f"{entry_id}: contains TODO marker")
    if CJK_RE.search(en):
        errs.append(f"{entry_id}: contains untranslated CJK/kana characters ({en!r})")

    errs.extend(fit.check_entry(entry_id, box, en, jp=jp))

    jp_ec = jp.count("[EC]")
    en_ec = en.count("[EC]")
    if jp_ec != en_ec:
        errs.append(f"{entry_id}: [EC] count mismatch (jp={jp_ec}, en={en_ec})")

    if HONORIFIC_RE.search(en):
        errs.append(f"{entry_id}: forbidden Japanese honorific suffix in {en!r}")

    norm = _normalize_en(en)
    for t in _matched_terms(jp, box, terms, entry_id):
        target_en = re.sub(r"\s+", " ", _effective_en(t, box)).strip()
        if not _word_regex(target_en).search(norm):
            errs.append(f"{entry_id}: missing glossary term {t.jp} -> {target_en!r} in {en!r}")
        for bad in t.avoid:
            if _word_regex(bad, hyphen_word=True).search(norm):
                errs.append(f"{entry_id}: uses avoided term {bad!r} for {t.jp} in {en!r}")
    return errs


def check_batch(
    batch: str,
    tl_dir: Path = TL_DIR,
    glossary_path: Path = GLOSSARY_PATH,
) -> list[str]:
    """Validate `work/tl/<batch>.out.tsv` against `<batch>.in.tsv`."""
    in_path = tl_dir / f"{batch}.in.tsv"
    out_path = tl_dir / f"{batch}.out.tsv"
    if not in_path.exists():
        return [f"{batch}: missing input file {in_path}"]
    if not out_path.exists():
        return [f"{batch}: missing output file {out_path}"]

    try:
        in_rows = read_tsv(in_path)
        out_rows = read_tsv(out_path)
    except ValueError as exc:
        return [str(exc)]

    in_ids = [r["id"] for r in in_rows]
    out_ids = [r["id"] for r in out_rows]
    if in_ids != out_ids:
        return [f"{batch}: ID mismatch between {in_path.name} ({len(in_ids)}) and {out_path.name} ({len(out_ids)})"]

    terms = load_glossary(glossary_path)
    errs: list[str] = []
    for ir, orow in zip(in_rows, out_rows):
        errs.extend(validate_row(ir["id"], ir["box"], ir["jp"], orow["en"], terms))
    return errs


def check_script(
    script_dir: Path = SCRIPT_DIR,
    glossary_path: Path = GLOSSARY_PATH,
) -> list[str]:
    """Validate all non-excluded translated strings directly inside `script/*.json`."""
    terms = load_glossary(glossary_path)
    errs: list[str] = []
    for _, recs in _iter_all_records(script_dir):
        for r in recs:
            errs.extend(validate_row(r["id"], r["box"], r["jp"], r["en"], terms))
    return errs


def write_pairs(
    batch: str,
    tl_dir: Path = TL_DIR,
    pairs_dir: Path = PAIRS_DIR,
) -> Path:
    """Render side-by-side JP/EN review markdown for `batch`."""
    in_rows = read_tsv(tl_dir / f"{batch}.in.tsv")
    out_rows = read_tsv(tl_dir / f"{batch}.out.tsv")
    out_map = {r["id"]: r["en"] for r in out_rows}
    pairs_dir.mkdir(parents=True, exist_ok=True)
    dest = pairs_dir / f"{batch}.md"
    lines = [f"# Review Pairs — {batch}", ""]
    for ir in in_rows:
        eid = ir["id"]
        en = out_map.get(eid, "")
        widths = " / ".join(fit.measure_lines(eid, ir["box"], en)) if en else "(empty)"
        lines.append(f"## `{eid}` (`{ir['box']}`, max `{ir['max']}`)")
        if ir["terms"]:
            lines.append(f"- **Terms:** {ir['terms']}")
        if ir["notes"]:
            lines.append(f"- **Notes:** {ir['notes']}")
        lines.append(f"- **Widths:** {widths}")
        lines.append(f"- **JP:** `{ir['jp']}`")
        lines.append(f"- **EN:** `{en}`")
        lines.append("")
    dest.write_text("\n".join(lines), encoding="utf-8")
    return dest


def merge_batches(
    batches: list[str],
    tl_dir: Path = TL_DIR,
    script_dir: Path = SCRIPT_DIR,
    glossary_path: Path = GLOSSARY_PATH,
    overwrite: bool = False,
) -> tuple[int, list[str]]:
    """Verify and merge `<batch>.out.tsv` files back into `script/*.json`."""
    all_errs: list[str] = []
    for b in batches:
        all_errs.extend(check_batch(b, tl_dir=tl_dir, glossary_path=glossary_path))
    if all_errs:
        return 0, all_errs

    manifest = _load_manifest(script_dir)
    group_files: dict[str, Path] = {
        g: script_dir / info["file"] for g, info in manifest["groups"].items()
    }
    loaded: dict[str, dict] = {}
    id_lookup: dict[str, tuple[str, dict]] = {}
    for g, path in group_files.items():
        if g in EXCLUDED_GROUPS:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        loaded[g] = data
        for e in data["entries"]:
            id_lookup[e["id"]] = (g, e)

    merged = 0
    touched: set[str] = set()
    for b in batches:
        for row in read_tsv(tl_dir / f"{b}.out.tsv"):
            eid = row["id"]
            new_en = row["en"]
            if eid == "b02_sys_026_mid":
                grp, entry = id_lookup["b02_sys_026_05ED3"]
                prev = entry.get("en_mid", "")
                if prev and prev != new_en and not overwrite:
                    all_errs.append(f"{eid}: refusing to overwrite existing en_mid {prev!r} with {new_en!r} without --overwrite")
                    continue
                entry["en_mid"] = new_en
                if entry.get("en"):
                    entry["status"] = "done"
                touched.add(grp)
                merged += 1
                continue

            if eid not in id_lookup:
                all_errs.append(f"{eid}: unknown entry id in manifest groups")
                continue
            grp, entry = id_lookup[eid]
            prev = entry.get("en", "")
            if prev and prev != new_en and not overwrite:
                all_errs.append(f"{eid}: refusing to overwrite existing en {prev!r} with {new_en!r} without --overwrite")
                continue
            entry["en"] = new_en
            if eid == "b02_sys_026_05ED3":
                if entry.get("en_mid"):
                    entry["status"] = "done"
            else:
                entry["status"] = "done"
            touched.add(grp)
            merged += 1

    if all_errs:
        return 0, all_errs

    for g in sorted(touched):
        group_files[g].write_text(json.dumps(loaded[g], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return merged, []


def refresh_terms(tl_dir: Path = TL_DIR, glossary_path: Path = GLOSSARY_PATH) -> int:
    """Re-evaluate the `terms` column on all `work/tl/bNNN.in.tsv` files from `glossary.md`."""
    terms = load_glossary(glossary_path)
    updated = 0
    for in_path in sorted(tl_dir.glob("b[0-9][0-9][0-9].in.tsv")):
        rows = read_tsv(in_path)
        header = ["id", "box", "max", "terms", "jp", "en", "notes"]
        out_rows: list[list[str]] = []
        for r in rows:
            matched = _matched_terms(r["jp"], r["box"], terms, r["id"])
            out_rows.append(
                [r["id"], r["box"], r["max"], _format_terms(matched, r["box"]), r["jp"], r["en"], r["notes"]]
            )
        _write_tsv(in_path, header, out_rows)
        updated += 1
    return updated


def _selftest() -> None:
    assert has_term("鬼若だ!", "鬼若")
    assert not has_term("平清盛", "清盛")
    assert has_term("セイラも", "セイラ")
    assert has_term("おコトちゃん", "おコト")
    assert fit.check_entry("b11_dialogue_000_1C571", "dialogue", "A" * 23 + "{nl}" + "B" * 24 + "{end}") == []
    assert fit.check_entry("b11_dialogue_000_1C571", "dialogue", "A" * 24 + "{nl}" + "B" + "{end}") != []
    assert fit.check_entry("b02_sys_000_05E36", "menu_sys", "Talk  Jutsu{end}") == []
    assert fit.check_entry("b02_sys_000_05E36", "menu_sys", "Spells Jutsu{end}") != []
    assert fit.check_entry("b0d_enemy_kanji_000_19B1D", "enemy_kanji", "Giant Spider") == []
    assert fit.check_entry("b0d_enemy_kanji_000_19B1D", "enemy_kanji", "Giant Spider{end}") != []
    print("batches selftest ok")


def _all_batch_names(suffix: str, tl_dir: Path = TL_DIR) -> list[str]:
    return sorted(p.name[: -len(suffix)] for p in tl_dir.glob(f"b[0-9][0-9][0-9]{suffix}"))


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description="PCE Benkei Gaiden translation batch pipeline")
    parser.add_argument("--selftest", action="store_true", help="Run built-in pipeline assertions")
    sub = parser.add_subparsers(dest="cmd")

    p_split = sub.add_parser("split", help="Split untranslated entries into work/tl/bNNN.in.tsv")
    p_split.add_argument("--size", type=int, default=3200, help="Target JP chars per batch (default 3200)")
    p_split.add_argument("--skip-done", action="store_true", help="Omit entries already marked status=done")

    p_chk = sub.add_parser("check", help="Validate work/tl/bNNN.out.tsv or merged script/*.json")
    p_chk.add_argument("batches", nargs="*", help="Batch names such as b001 (default: all .out.tsv)")
    p_chk.add_argument("--script", action="store_true", help="Validate merged script/*.json directly")

    p_pairs = sub.add_parser("pairs", help="Generate side-by-side work/tl/pairs/bNNN.md review files")
    p_pairs.add_argument("batches", nargs="*", help="Batch names (default: all .out.tsv)")

    p_merge = sub.add_parser("merge", help="Merge validated .out.tsv batches into script/*.json")
    p_merge.add_argument("batches", nargs="*", help="Batch names (default: all .out.tsv)")
    p_merge.add_argument("--overwrite", action="store_true", help="Overwrite differing existing translations")

    sub.add_parser("refresh-terms", help="Refresh glossary terms column in work/tl/bNNN.in.tsv")

    args = parser.parse_args(argv)
    if args.selftest:
        _selftest()
        return 0

    if args.cmd == "split":
        summary = split_batches(size=args.size, skip_done=args.skip_done)
        total_rows = sum(s[2] for s in summary)
        total_chars = sum(s[3] for s in summary)
        for name, grps, count, chars in summary:
            print(f"{name}: {count:3d} rows, {chars:5d} chars  [{grps}]")
        print(f"Total: {len(summary)} batches, {total_rows} rows, {total_chars} JP chars")
        return 0

    if args.cmd == "check":
        if args.script:
            errs = check_script()
        else:
            targets = args.batches or _all_batch_names(".out.tsv")
            if not targets:
                print("No .out.tsv batches yet (OK)")
                return 0
            errs = []
            for b in targets:
                errs.extend(check_batch(b))
        if errs:
            for e in errs:
                print(f"ERR: {e}", file=sys.stderr)
            print(f"FAILED: {len(errs)} error(s)", file=sys.stderr)
            return 1
        print("OK")
        return 0

    if args.cmd == "pairs":
        targets = args.batches or _all_batch_names(".out.tsv")
        if not targets:
            print("No .out.tsv batches found", file=sys.stderr)
            return 1
        for b in targets:
            dest = write_pairs(b)
            print(f"wrote {dest.relative_to(ROOT)}")
        return 0

    if args.cmd == "merge":
        targets = args.batches or _all_batch_names(".out.tsv")
        if not targets:
            print("No .out.tsv batches found", file=sys.stderr)
            return 1
        merged, errs = merge_batches(targets, overwrite=args.overwrite)
        if errs:
            for e in errs:
                print(f"ERR: {e}", file=sys.stderr)
            return 1
        print(f"Merged {merged} entries from {len(targets)} batch(es)")
        return 0

    if args.cmd == "refresh-terms":
        count = refresh_terms()
        print(f"Refreshed terms in {count} batch input file(s)")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
