"""Create (or reuse) the per-client audit folder: subfolders, BRIEF.md and findings/meta.json."""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import paths  # noqa: E402

SUBDIRS = ["raw", "screenshots", "findings", "report/assets"]

EVIDENCE_INDEX = """- raw/home.html — homepage HTML
- raw/lighthouse-mobile.json, raw/lighthouse-desktop.json — Lighthouse reports
- screenshots/desktop-viewport.png (1440x900)
- screenshots/desktop-fullpage.jpg, screenshots/mobile-fullpage.jpg (from Lighthouse)"""


def domain_of(url: str) -> str:
    if "://" not in url:
        url = "https://" + url
    host = (urlparse(url).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def slugify(url: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", domain_of(url)).strip("-")


def _context_text(context: dict) -> str:
    if not context:
        return "not provided — infer from the site and say it is inferred"
    return "; ".join(f"{k}: {v}" for k, v in context.items())


def init_audit(url: str, context: dict, base: Path | None = None, options: dict | None = None) -> Path:
    audit_dir = paths.audits_root(base) / slugify(url)
    for sub in SUBDIRS:
        (audit_dir / sub).mkdir(parents=True, exist_ok=True)

    meta_path = audit_dir / "findings" / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    meta.update({
        "url": url,
        "domain": domain_of(url),
        "slug": slugify(url),
        "plugin_version": paths.plugin_version(),
        "scoring_version": paths.config("scoring")["version"],
        "options": options if options is not None else meta.get("options", {}),
    })
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    template = (paths.plugin_root() / "skills" / "simian-web-audit" / "references" / "brief-template.md").read_text(encoding="utf-8")
    brief = (template.replace("{{domain}}", domain_of(url)).replace("{{url}}", url)
             .replace("{{context}}", _context_text(context)).replace("{{evidence_index}}", EVIDENCE_INDEX))
    (audit_dir / "BRIEF.md").write_text(brief, encoding="utf-8")
    return audit_dir


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("url")
    ap.add_argument("--context-json", type=Path)
    ap.add_argument("--options-json", type=Path)
    args = ap.parse_args()
    context = json.loads(args.context_json.read_text(encoding="utf-8")) if args.context_json else {}
    options = json.loads(args.options_json.read_text(encoding="utf-8")) if args.options_json else None
    print(init_audit(args.url, context, options=options))


if __name__ == "__main__":
    main()
