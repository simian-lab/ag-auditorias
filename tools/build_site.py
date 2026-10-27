"""Build the publishable site: every audits/<slug>/report plus a generated index.html.

Usage: python3 tools/build_site.py [OUT_DIR]   (default: _site)
"""
import html
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDITS = ROOT / "audits"

PAGE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Auditorías de prospectos</title>
<style>
  :root {{ --bg: #f7f7f5; --fg: #1a1a1a; --muted: #666; --card: #fff; --line: #e3e3df; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg: #141414; --fg: #eee; --muted: #999; --card: #1d1d1d; --line: #2c2c2c; }}
  }}
  body {{ margin: 0; background: var(--bg); color: var(--fg); font: 16px/1.5 system-ui, sans-serif; }}
  main {{ max-width: 720px; margin: 0 auto; padding: 48px 16px; }}
  h1 {{ margin: 0 0 4px; font-size: 1.6rem; }}
  p {{ color: var(--muted); margin: 0 0 32px; }}
  ul {{ list-style: none; padding: 0; margin: 0; display: grid; gap: 12px; }}
  a {{ display: flex; justify-content: space-between; align-items: center; padding: 16px 20px;
      background: var(--card); border: 1px solid var(--line); border-radius: 10px;
      color: inherit; text-decoration: none; }}
  a:hover {{ border-color: var(--muted); }}
  .score {{ font-variant-numeric: tabular-nums; color: var(--muted); }}
</style>
</head>
<body>
<main>
  <h1>Auditorías de prospectos</h1>
  <p>Informes generados con el plugin <code>simian-web-audit</code>.</p>
  <ul>
{items}
  </ul>
</main>
</body>
</html>
"""


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def collect() -> list[dict]:
    audits = []
    for audit in sorted(AUDITS.iterdir()):
        if not (audit / "report" / "index.html").is_file():
            continue
        meta = read_json(audit / "findings" / "meta.json")
        scores = read_json(audit / "findings" / "scores.json")
        audits.append({
            "slug": audit.name,
            "domain": meta.get("domain") or audit.name,
            "score": scores.get("overall"),
        })
    return audits


def render_index(audits: list[dict]) -> str:
    items = []
    for a in audits:
        score = f"{a['score']}/100" if a["score"] is not None else ""
        items.append(
            f'    <li><a href="audits/{html.escape(a["slug"])}/report/index.html">'
            f'<span>{html.escape(a["domain"])}</span><span class="score">{score}</span></a></li>'
        )
    return PAGE.format(items="\n".join(items))


def build(out: Path) -> list[dict]:
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    audits = collect()
    for a in audits:
        shutil.copytree(
            AUDITS / a["slug"] / "report",
            out / "audits" / a["slug"] / "report",
            ignore=shutil.ignore_patterns(".DS_Store"),
        )
    (out / "index.html").write_text(render_index(audits), encoding="utf-8")
    (out / ".nojekyll").touch()
    return audits


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "_site"
    built = build(target.resolve())
    print(f"built {len(built)} audits into {target}")
