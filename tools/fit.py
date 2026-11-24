"""PCE screen-width, control-code, cursor, and $2E00 digit-poke validation for translations."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WINDOWS_PATH = ROOT / "tools" / "windows.json"

import sys

if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))

import pce_text  # noqa: E402

BUILTIN_OVERRIDES: dict[str, dict] = {
    "b02_sys_034_05F20": {"cols": 3, "lines": 1, "notes": "HUD dead status indicator replacing Lv digits ($20B4)"},
    "b02_sys_037_05F2A": {"cols": 3, "lines": 1, "notes": "HUD poison status indicator replacing Lv digits ($20B4)"},
    "b02_sys_038_05F2D": {"cols": 3, "lines": 1, "notes": "HUD max-level indicator replacing Lv digits ($20B4)"},
}

# Fixed $2E00 battle template digit-poke spaces verified from B$08:$B828..$B890:
# - EXP (`05F87`) draws at x=4 and writes formatted digits at x=$0B (byte offset 7..11).
# - Sen (`05F99`) draws at x=6 and writes formatted digits at x=$0B (byte offset 5..9).
EXTRA_POKES: dict[str, tuple[int, int, int | None]] = {
    "b11_dialogue_566_22EA9": (3, 6, 6),  # literal '0' at byte offset 6
    "b02_sys_053_05F87": (7, 12, None),
    "b02_sys_054_05F99": (5, 10, None),
}

TWO_COL_MENU_IDS = {
    "b02_sys_000_05E36",
    "b02_sys_001_05E40",
    "b02_sys_002_05E4D",
    "b02_sys_017_05E9E",
    "b02_sys_018_05EAA",
}

TAG_RE = re.compile(r"\{nl\}|\{page\}|\{end\}|\[EC\]")


@lru_cache(maxsize=1)
def _windows() -> dict:
    return json.loads(WINDOWS_PATH.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _codec() -> pce_text.EnCodec:
    return pce_text.EnCodec("en")


def entry_budget(entry_id: str, box: str) -> dict:
    """Return merged box and per-entry override limits from windows.json."""
    win = _windows()
    if box not in win["boxes"]:
        raise KeyError(f"Unknown box {box!r} for {entry_id}")
    budget = dict(win["boxes"][box])
    if entry_id in win["overrides"]:
        budget.update(win["overrides"][entry_id])
    if entry_id in BUILTIN_OVERRIDES:
        budget.update(BUILTIN_OVERRIDES[entry_id])
    return budget


def visible_cols(line: str) -> int:
    """Count visible 8x16 columns in a single decoded line (`[EC]` renders 1 col)."""
    return len(line.replace("[EC]", "?"))


def _split_pages(text: str) -> list[list[str]]:
    body = text[:-5] if text.endswith("{end}") else text
    return [page.split("{nl}") for page in body.split("{page}")]


def measure_lines(entry_id: str, box: str, text: str) -> list[str]:
    """Return compact per-page width summaries such as `'P1: 22/23, 18/24'`."""
    budget = entry_budget(entry_id, box)
    nl_max = budget.get("nl_max_cols", budget["cols"])
    line1_max = budget.get("line1_cols")
    pages = _split_pages(text)
    out: list[str] = []
    for p_idx, lines in enumerate(pages, 1):
        parts: list[str] = []
        for l_idx, line in enumerate(lines):
            cols = visible_cols(line)
            if p_idx == 1 and l_idx == 0 and line1_max is not None:
                lim = min(line1_max, nl_max if l_idx < len(lines) - 1 else budget["cols"])
            elif l_idx < len(lines) - 1:
                lim = nl_max
            else:
                lim = budget["cols"]
            parts.append(f"{cols}/{lim}")
        prefix = f"P{p_idx}: " if len(pages) > 1 or box == "dialogue" else ""
        out.append(prefix + " | ".join(parts))
    return out


def format_budget(entry_id: str, box: str) -> str:
    """Format a compact budget label for batch TSVs."""
    b = entry_budget(entry_id, box)
    if b.get("cols", 0) == 0:
        return "0"
    parts = [f"{b['cols']}x{b['lines']}" if b["lines"] > 1 else f"{b['cols']}"]
    extras: list[str] = []
    if "line1_cols" in b:
        extras.append(f"l1<={b['line1_cols']}")
    if "nl_max_cols" in b:
        extras.append(f"nl<={b['nl_max_cols']}")
    if b.get("terminator") == "length":
        extras.append("no {end}")
    if "poke_range" in b:
        lo, hi = b["poke_range"]
        extras.append(f"spaces[{lo}:{hi}]")
    elif entry_id in EXTRA_POKES:
        lo, hi, zero = EXTRA_POKES[entry_id]
        extras.append(f"spaces[{lo}:{hi}]" + (f"+'0'@{zero}" if zero is not None else ""))
    if entry_id in TWO_COL_MENU_IDS:
        extras.append("space@5")
    return f"{parts[0]} ({', '.join(extras)})" if extras else parts[0]


def check_entry(entry_id: str, box: str, text: str, jp: str | None = None) -> list[str]:
    """Validate charset, control tags, width limits, cursor slot, and $2E00 pokes."""
    errors: list[str] = []
    if box == "enemy_kana":
        return [f"{entry_id}: box 'enemy_kana' is runtime-skipped and must not be translated"]
    if not text:
        return [f"{entry_id}: empty text"]

    budget = entry_budget(entry_id, box)
    codec = _codec()
    try:
        enc = codec.encode(text)
    except (ValueError, KeyError) as exc:
        return [f"{entry_id}: encoding error: {exc}"]

    expects_end = budget.get("terminator") != "length"
    if jp is not None:
        expects_end = jp.endswith("{end}")

    if expects_end:
        if not text.endswith("{end}"):
            errors.append(f"{entry_id}: missing trailing '{{end}}'")
        body = text[:-5] if text.endswith("{end}") else text
        if "{end}" in body:
            errors.append(f"{entry_id}: stray '{{end}}' inside text")
    else:
        if "{end}" in text:
            errors.append(f"{entry_id}: length-indexed entry must not contain '{{end}}'")
        body = text

    pages = body.split("{page}")
    if len(pages) > 1 and box != "dialogue" and budget["lines"] < 3:
        errors.append(f"{entry_id}: '{{page}}' only allowed in multi-line dialogue boxes (box={box})")

    nl_max = budget.get("nl_max_cols", budget["cols"])
    line1_max = budget.get("line1_cols")

    for p_idx, page in enumerate(pages, 1):
        lines = page.split("{nl}")
        if len(lines) > budget["lines"]:
            errors.append(f"{entry_id}: page {p_idx} has {len(lines)} lines > max {budget['lines']}")
        for l_idx, line in enumerate(lines):
            cols = visible_cols(line)
            if p_idx == 1 and l_idx == 0 and line1_max is not None and cols > line1_max:
                errors.append(f"{entry_id}: P1 L1 is {cols} cols > line1 max {line1_max} ({line!r})")
            if l_idx < len(lines) - 1:
                if cols > nl_max:
                    errors.append(
                        f"{entry_id}: P{p_idx} L{l_idx + 1} before '{{nl}}' is {cols} cols > max {nl_max} ({line!r})"
                    )
            elif cols > budget["cols"]:
                errors.append(f"{entry_id}: P{p_idx} L{l_idx + 1} is {cols} cols > max {budget['cols']} ({line!r})")

    sp_byte = codec.encode(" ")[0]
    zero_byte = codec.encode("0")[0]
    poke_spec: tuple[int, int, int | None] | None = None
    if "poke_range" in budget:
        lo, hi = budget["poke_range"]
        zero = EXTRA_POKES.get(entry_id, (lo, hi, None))[2]
        poke_spec = (lo, hi, zero)
    elif entry_id in EXTRA_POKES:
        poke_spec = EXTRA_POKES[entry_id]

    if poke_spec is not None:
        lo, hi, zero = poke_spec
        payload = enc[:-1] if text.endswith("{end}") else enc
        if len(payload) < hi or any(b != sp_byte for b in payload[lo:hi]):
            errors.append(f"{entry_id}: must keep spaces at byte offsets {lo}..{hi - 1} for $2E00 digit pokes")
        if zero is not None and (len(payload) <= zero or payload[zero] != zero_byte):
            errors.append(f"{entry_id}: must keep literal '0' at byte offset {zero}")

    if entry_id in TWO_COL_MENU_IDS and len(body) > 5:
        if body[5] != " ":
            errors.append(f"{entry_id}: two-column menu cursor requires space ' ' at byte index 5 ({body!r})")
        if len(body) > 11:
            errors.append(f"{entry_id}: two-column menu exceeds 11 cols ({len(body)})")

    return errors
