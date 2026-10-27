"""Build report/index.html for an audit folder from its findings."""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import paths  # noqa: E402
from report import render  # noqa: E402
from report.sections import benchmark, bigstat, critique, extra, hero, plan, redesign, score, showcase, simian, top10  # noqa: E402

SECTIONS = [hero, showcase, score, bigstat, top10, critique, benchmark, redesign, extra, plan, simian]
AREAS = ["ux", "a11y", "visual", "tech"]


def _read(path: Path):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def load_ctx(audit_dir: Path) -> dict:
    f = audit_dir / "findings"
    report = audit_dir / "report"
    assets = report / "assets"
    used: dict[str, Path] = {}

    def asset(name: str) -> str | None:
        src = audit_dir / "screenshots" / name
        if not src.exists():
            return None
        used[name] = src
        return f"assets/{name}"

    plugin_used: dict[str, Path] = {}

    def plugin_asset(*parts: str) -> str | None:
        src = paths.asset(*parts)
        if not src.exists():
            return None
        rel = "/".join(parts)
        plugin_used[rel] = src
        return f"assets/{rel}"

    cases = _read(paths.asset("simian", "cases.json"))
    return {
        "audit_dir": audit_dir,
        "assets_dir": assets,
        "top10": _read(f / "top10.json"),
        "scores": _read(f / "scores.json"),
        "areas": {a: _read(f / f"{a}.json") or {} for a in AREAS},
        "meta": _read(f / "meta.json") or {},
        "ui": _read(f / "ui-critique.json"),
        "benchmark": _read(f / "benchmark.json"),
        "seo": _read(f / "seo.json"),
        "presence": _read(f / "presence.json"),
        "ai": _read(f / "ai-visibility.json"),
        "redesign": _read(f / "redesign.json"),
        "cases": (cases or {}).get("cases", []),
        "scoring": paths.config("scoring"),
        "rubric": paths.config("rubric"),
        "settings": paths.config("settings"),
        "logo": paths.asset("simian", "logo.svg"),
        "has_load_page": (report / "feature-carga.html").exists(),
        "asset": asset,
        "plugin_asset": plugin_asset,
        "_used": used,
        "_plugin_used": plugin_used,
    }


def build_report(audit_dir: Path) -> Path:
    ctx = load_ctx(audit_dir)
    if not ctx["top10"]:
        raise SystemExit(f"missing {audit_dir / 'findings' / 'top10.json'}")
    n, minimum = len(ctx["top10"]["items"]), ctx["settings"]["top_n_min"]
    if n < minimum:
        print(f"warning: only {n} items in the Top (target minimum {minimum}); the report shows Top {n}.")
    sections = [s for s in (mod.build(ctx) for mod in SECTIONS) if s is not None]
    assets = ctx["assets_dir"]
    (assets / "fonts").mkdir(parents=True, exist_ok=True)
    shutil.copy2(paths.asset("fonts", "InterVariable.woff2"), assets / "fonts" / "InterVariable.woff2")
    for name, src in ctx["_used"].items():
        shutil.copy2(src, assets / name)
    for rel, src in ctx["_plugin_used"].items():
        (assets / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, assets / rel)
    out = audit_dir / "report" / "index.html"
    out.write_text(render.page(sections, f"Auditoría {ctx['top10']['domain']}"), encoding="utf-8")
    print(f"written {out}")
    return out


if __name__ == "__main__":
    build_report(Path(sys.argv[1]))
