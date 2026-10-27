"""Validate every known findings file present in an audit folder against its schema."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import paths  # noqa: E402
from lib.validate import validate  # noqa: E402

SCHEMA_FOR = {
    "ux.json": "area", "a11y.json": "area", "visual.json": "area", "tech.json": "area",
    "top10.json": "top10", "ui-critique.json": "ui-critique", "benchmark.json": "benchmark",
    "seo.json": "seo", "presence.json": "presence", "ai-visibility.json": "ai-visibility",
}


REQUIRED = ["ux.json", "a11y.json", "visual.json", "tech.json", "top10.json"]


def _schema(name: str) -> dict:
    return json.loads((paths.plugin_root() / "schemas" / f"{name}.schema.json").read_text(encoding="utf-8"))


RUBRIC_AREA = {"ux.json": "ux", "a11y.json": "a11y", "visual.json": "visual", "tech.json": "tech", "seo.json": "seo"}


def rubric_errors(area: str, doc: dict) -> list[str]:
    expected = [c["id"] for c in paths.config("rubric")["areas"][area]]
    got = [c.get("id") for c in doc.get("checks", [])]
    errors = [f"$.checks: missing criterion {cid}" for cid in expected if cid not in got]
    errors += [f"$.checks: unknown criterion {cid}" for cid in got if cid not in expected]
    errors += [f"$.checks: duplicate criterion {cid}" for cid in set(got) if got.count(cid) > 1]
    return errors


def validate_dir(findings_dir: Path) -> dict[str, list[str]]:
    results = {}
    for filename, schema_name in SCHEMA_FOR.items():
        f = findings_dir / filename
        if not f.exists():
            if filename in REQUIRED:
                results[filename] = ["missing required file"]
            continue
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            results[filename] = [f"invalid JSON: {exc}"]
            continue
        results[filename] = validate(doc, _schema(schema_name))
        if filename in RUBRIC_AREA and not results[filename]:
            results[filename] = rubric_errors(RUBRIC_AREA[filename], doc)
    return results


def main() -> None:
    audit_dir = Path(sys.argv[1])
    results = validate_dir(audit_dir / "findings")
    bad = {k: v for k, v in results.items() if v}
    for name, errs in bad.items():
        print(f"{name}:")
        for e in errs:
            print(f"  - {e}")
    print("ok" if not bad else f"{len(bad)} file(s) with errors")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
