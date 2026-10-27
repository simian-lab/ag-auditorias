"""Deterministic area scores: weighted share of rubric criteria passed, blended with Lighthouse where configured."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import paths  # noqa: E402

AREAS = ["ux", "a11y", "visual", "tech"]


def _rubric_score(area: str, doc: dict | None, rubric: dict) -> tuple[float, dict]:
    if not doc or "checks" not in doc:
        raise ValueError(f"{area}: missing rubric checks — an unaudited area cannot be scored")
    results = {c["id"]: c["result"] for c in doc["checks"]}
    applicable = [c for c in rubric["areas"][area] if results.get(c["id"]) != "na"]
    passed = [c for c in applicable if results.get(c["id"]) == "pass"]
    partial = [c for c in applicable if results.get(c["id"]) == "partial"]
    total_w = sum(c["weight"] for c in applicable)
    earned = sum(c["weight"] for c in passed) + 0.5 * sum(c["weight"] for c in partial)  # partial = half weight
    value = 100 * earned / total_w if total_w else 100
    return value, {"passed": len(passed), "partial": len(partial), "total": len(applicable)}


def compute_scores(findings: dict[str, dict], lighthouse: dict | None, cfg: dict, rubric: dict) -> dict:
    scores, detail = {}, {}
    cats = (lighthouse or {}).get("categories", {})
    for a in AREAS:
        value, detail[a] = _rubric_score(a, findings.get(a), rubric)
        blend = [cats[c]["score"] * 100 for c in cfg["lighthouse_blend"].get(a, [])
                 if c in cats and cats[c].get("score") is not None]
        if blend:
            value = (value + sum(blend) / len(blend)) / 2
        scores[a] = round(value)
    scores["overall"] = round(sum(scores[a] for a in AREAS) / len(AREAS))
    if findings.get("seo", {}).get("checks"):  # Extra module: same rubric rule, not part of the base overall
        value, detail["seo"] = _rubric_score("seo", findings["seo"], rubric)
        scores["seo"] = round(value)
    scores.update(target=cfg["target"], version=cfg["version"], rubric_version=rubric["version"], detail=detail)
    return scores


def missing_areas(fdir: Path) -> list[str]:
    return [a for a in AREAS if not (fdir / f"{a}.json").exists()]


def main() -> None:
    audit_dir = Path(sys.argv[1])
    fdir = audit_dir / "findings"
    missing = missing_areas(fdir)
    if missing:
        sys.exit(f"missing area findings: {', '.join(missing)} — an unaudited area cannot be scored")
    findings = {a: json.loads((fdir / f"{a}.json").read_text(encoding="utf-8"))
                for a in AREAS + ["seo"] if (fdir / f"{a}.json").exists()}
    lh_path = audit_dir / "raw" / "lighthouse-mobile.json"
    lh = json.loads(lh_path.read_text(encoding="utf-8")) if lh_path.exists() else None
    try:
        result = compute_scores(findings, lh, paths.config("scoring"), paths.config("rubric"))
    except ValueError as exc:
        sys.exit(str(exc))
    (fdir / "scores.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "detail"}))


if __name__ == "__main__":
    main()
