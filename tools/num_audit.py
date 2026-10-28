#!/usr/bin/env python3
"""
Audit every number in src/pages/*.html (including visible <text> inside <svg>,
excluding SVG coordinates/attributes and HTML tags/attributes) and in the
metrics / interpretation / summary / positive / steps fields of atlas/data/tests.yaml
against C:/Users/ahmed/OneDrive/Desktop/lumbar_evidence_verified.md and
C:/Users/ahmed/OneDrive/Desktop/upgrade_evidence_verified.md and the
Rule 2.10 whitelist.
"""
import html
import pathlib
import re
import sys
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parent.parent
EVIDENCE_PATHS = [
    pathlib.Path(r"C:\Users\ahmed\OneDrive\Desktop\lumbar_evidence_verified.md"),
    pathlib.Path(r"C:\Users\ahmed\OneDrive\Desktop\upgrade_evidence_verified.md"),
]
PAGES_DIR = ROOT / "src" / "pages"
YAML_PATH = ROOT / "atlas" / "data" / "tests.yaml"

WHITELIST_RULES = [
    (
        "Spinal level / nerve root names (T10-S4, L1-S1, S2-S4)",
        re.compile(
            r"\b(?:T(?:1[0-2]|[1-9])|L[1-5]|S[1-5])"
            r"(?:\s*[\-\u2013\u2014/]\s*(?:T(?:1[0-2]|[1-9])|L[1-5]|S[1-5]|[1-5]))*\b"
        ),
    ),
    (
        "Calculator scoring rules & item wording (ODI, RMDQ, STarT Back, OMPSQ-10, TSK-11, NPRS, PSFS, HHD)",
        re.compile(
            r"(?<![\d.])(?:0[\-\u2013]100%?|0[\-\u2013]50|0[\-\u2013]24|0[\-\u2013]10|0[\-\u2013]5|1[\-\u2013]4|11[\-\u2013]44|"
            r"10\s+items|24\s+items|9\s+items|11\s+items|5\s+items|6\s+tests|"
            r"\u00f7\s*50|\u00f7\s*100|\u00d7\s*100)(?![\d.])"
        ),
    ),
    (
        "Visit / week numbers in log tables (1-12)",
        re.compile(
            r"(?<![\d.])(?:\bVisit\s*(?:[1-9]|1[0-2])\b|\bWk\s*(?:[1-9]|1[0-2])\b|"
            r"\b12[\-\u2013][Ww]eek\b|\b12[\-\u2013][Vv]isit\b|"
            r"(?<![A-Za-z\d.])(?:[0-9]|1[0-2])(?![A-Za-z\d.]))"
        ),
    ),
    (
        "Page numbers (1-9, p1-p9)",
        re.compile(r"(?<![\d.])(?:\b[pP][1-9](?:/[pP][1-9])*\b|\b[pP]age\s*[1-9]\b)"),
    ),
]


def normalize_numeric_text(s: str) -> str:
    s = re.sub(r"(\d),(\d{3})\b", r"\1\2", s)
    s = re.sub(r"(\d)\u00b7(\d)", r"\1.\2", s)
    return s


def load_verified_numbers(md_paths: list[pathlib.Path]) -> set[str]:
    nums: set[str] = set()
    for md_path in md_paths:
        text = md_path.read_text(encoding="utf-8")
        for marker in ("## ⚠️ Corrections", "## ❌ Rejected"):
            if marker in text:
                text = text.split(marker, 1)[0]
        lines = [ln for ln in text.splitlines() if not ln.strip().startswith(">")]
        norm = normalize_numeric_text("\n".join(lines))
        nums.update(re.findall(r"(?<![\d.])\d+(?:\.\d+)?(?![\d.])", norm))
        for m in re.findall(r"(?<!\d)\.(\d+)\b", norm):
            nums.add(m)
            nums.add(f"0.{m}")
    return nums


def extract_svg_visible_text(svg_block: str) -> str:
    texts = re.findall(r"<text\b[^>]*>(.*?)</text>", svg_block, flags=re.DOTALL | re.IGNORECASE)
    cleaned = [re.sub(r"<[^>]+>", " ", t) for t in texts]
    return " ".join(cleaned)


def extract_html_visible_text(html_text: str) -> str:
    s = re.sub(r"<!--.*?-->", " ", html_text, flags=re.DOTALL)
    s = re.sub(
        r"<svg\b[^>]*>.*?</svg>",
        lambda m: " " + extract_svg_visible_text(m.group(0)) + " ",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return s


def apply_whitelist(text: str, counts: dict[str, int]) -> str:
    s = text
    for label, pattern in WHITELIST_RULES:
        matches = pattern.findall(s)
        if matches:
            counts[label] = counts.get(label, 0) + len(matches)
            s = pattern.sub(" ", s)
    return s


def collect_yaml_strings(obj) -> list[str]:
    out = []
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, list):
        for item in obj:
            out.extend(collect_yaml_strings(item))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("url", "id", "free_full_text", "video", "video_url", "video_title"):
                continue
            out.extend(collect_yaml_strings(v))
    return out


def main() -> int:
    verified_nums = load_verified_numbers(EVIDENCE_PATHS)
    whitelist_counts: dict[str, int] = {label: 0 for label, _ in WHITELIST_RULES}
    unverified: list[tuple[str, str, str]] = []

    # 1. Audit src/pages/*.html
    page_files = sorted(PAGES_DIR.glob("p*.html"))
    total_html_nums = 0
    for pf in page_files:
        raw = pf.read_text(encoding="utf-8")
        vis = normalize_numeric_text(extract_html_visible_text(raw))
        all_nums_in_page = re.findall(r"(?<![\d.])\d+(?:\.\d+)?(?![\d.])", vis)
        total_html_nums += len(all_nums_in_page)

        scrubbed = apply_whitelist(vis, whitelist_counts)
        for m in re.finditer(r"(?<![\d.])\d+(?:\.\d+)?(?![\d.])", scrubbed):
            num = m.group(0)
            if num not in verified_nums:
                start = max(0, m.start() - 35)
                end = min(len(scrubbed), m.end() + 35)
                ctx = " ".join(scrubbed[start:end].split())
                unverified.append((pf.name, num, ctx))

    # 2. Audit atlas/data/tests.yaml (metrics, interpretation, summary, positive, steps)
    data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    cards = data if isinstance(data, list) else data.get("tests", [])
    target_fields = ("metrics", "interpretation", "summary", "positive", "steps")
    total_yaml_nums = 0
    for card in cards:
        cid = card.get("id", "<unknown>")
        for field in target_fields:
            if field not in card:
                continue
            strs = collect_yaml_strings(card[field])
            joined = normalize_numeric_text(" | ".join(strs))
            all_nums_in_field = re.findall(r"(?<![\d.])\d+(?:\.\d+)?(?![\d.])", joined)
            total_yaml_nums += len(all_nums_in_field)

            scrubbed = apply_whitelist(joined, whitelist_counts)
            for m in re.finditer(r"(?<![\d.])\d+(?:\.\d+)?(?![\d.])", scrubbed):
                num = m.group(0)
                if num not in verified_nums:
                    start = max(0, m.start() - 35)
                    end = min(len(scrubbed), m.end() + 35)
                    ctx = " ".join(scrubbed[start:end].split())
                    unverified.append((f"tests.yaml:{cid}.{field}", num, ctx))

    print("=" * 72)
    print("LUMBAR DOSSIER + ATLAS NUMBER AUDIT (Rule 2.10 & Section 6.3)")
    print("=" * 72)
    print("Evidence sources:")
    for ep in EVIDENCE_PATHS:
        print(f"  - {ep}")
    print(f"Verified tokens : {len(verified_nums)} distinct numeric values across {len(EVIDENCE_PATHS)} evidence files")
    print(f"Pages audited   : {len(page_files)} files ({total_html_nums} numeric tokens extracted incl. SVG <text>)")
    print(f"YAML audited    : {len(cards)} cards across {list(target_fields)} ({total_yaml_nums} numeric tokens)")
    print("-" * 72)
    print("Rule 2.10 Whitelist Applied:")
    for label, count in whitelist_counts.items():
        print(f"  - {label}: {count} matches")
    print("-" * 72)
    if unverified:
        print(f"UNVERIFIED NUMBERS FOUND: {len(unverified)}")
        for loc, num, ctx in unverified:
            print(f"  [!] {loc}: '{num}' in ...{ctx}...")
        return 1
    else:
        print("Unverified numbers count: 0")
        print("STATUS: PASS (0 unverified numbers)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
