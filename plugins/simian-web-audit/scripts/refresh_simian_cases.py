"""Refresh assets/simian/cases.json and case images from https://simian.co/portafolio/.

Curated fields (`matches`, `results`, `headline`, `sector`) of existing cases are preserved; new cases get
empty `matches` and must be tagged by hand before the report can pick them.
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import paths  # noqa: E402

BASE = "https://simian.co"
CARD = re.compile(
    r'<div class="item-destacado">.*?<a href="/(?P<slug>[a-z0-9-]+)/">\s*<img src="(?P<img>[^"]+)".*?'
    r"<h4>(?P<client>.*?)</h4>.*?<h2>(?P<title>.*?)</h2>.*?(?:<p>(?P<desc>.*?)</p>)?",
    re.S,
)
CURATED = ("matches", "results", "headline", "sector")


def _text(s: str | None) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s or ""))).strip()


def parse_portfolio(page: str, existing: list[dict]) -> list[dict]:
    known = {c["slug"]: c for c in existing}
    cases = []
    for m in CARD.finditer(page):
        slug = m["slug"]
        img_url = BASE + m["img"] if m["img"].startswith("/") else m["img"]
        case = {
            "slug": slug,
            "client": _text(m["client"]),
            "url": f"{BASE}/{slug}/",
            "image": img_url.rsplit("/", 1)[-1],
            "image_url": img_url,
            "headline": _text(m["desc"]) or _text(m["title"]),
            "results": [],
            "matches": [],
        }
        for key in CURATED:
            if key in known.get(slug, {}):
                case[key] = known[slug][key]
        cases.append(case)
    return cases


def ensure_cases(cases: list[dict]) -> list[dict]:
    if not cases:
        raise SystemExit("no cases parsed from the portfolio (markup changed?) — cases.json left untouched")
    return cases


def _curl(url: str) -> bytes:
    return subprocess.run(["curl", "-sL", "--max-time", "30", url], check=True, capture_output=True).stdout


def main() -> None:
    target = paths.asset("simian", "cases.json")
    current = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {"cases": []}
    cases = ensure_cases(parse_portfolio(_curl(f"{BASE}/portafolio/").decode("utf-8", "replace"), current.get("cases", [])))
    img_dir = paths.asset("simian", "img")
    img_dir.mkdir(parents=True, exist_ok=True)
    for c in cases:
        (img_dir / c["image"]).write_bytes(_curl(c["image_url"]))
    current["cases"] = cases
    current["source"] = f"{BASE}/portafolio/"
    target.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
    untagged = [c["slug"] for c in cases if not c["matches"]]
    print(f"{len(cases)} cases written to {target}")
    if untagged:
        print("tag these cases with `matches` before they can be picked: " + ", ".join(untagged))


if __name__ == "__main__":
    main()
