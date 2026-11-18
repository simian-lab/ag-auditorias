"""Measure the client and its competitors in the same step, round by round, so the load comparison is fair.

Each round runs Lighthouse mobile once per site (order rotates every round). For each site the run with the
median recorded LCP is kept as raw/load-<slug>.json (client slug: "client"); every LCP goes to raw/load-runs.json.
"""
import json
import statistics
import subprocess
import sys
from pathlib import Path

ROUNDS = 3


def _lcp(lh: dict) -> float:
    items = lh.get("audits", {}).get("metrics", {}).get("details", {}).get("items") or [{}]
    return items[0].get("observedLargestContentfulPaint", 0)


def sites(audit_dir: Path) -> list[tuple[str, str]]:
    meta = json.loads((audit_dir / "findings" / "meta.json").read_text(encoding="utf-8"))
    bench = audit_dir / "findings" / "benchmark.json"
    comps = json.loads(bench.read_text(encoding="utf-8")).get("competitors", []) if bench.exists() else []
    return [("client", meta["url"])] + [(c["slug"], c["url"]) for c in comps if c.get("slug") and c.get("url")]


def measure(audit_dir: Path, rounds: int = ROUNDS, run=subprocess.run) -> dict:
    raw = audit_dir / "raw"
    tmp = raw / "load-tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    targets = sites(audit_dir)
    runs: dict[str, list[tuple[float, Path]]] = {s: [] for s, _ in targets}
    for r in range(rounds):
        for slug, url in targets[r % len(targets):] + targets[:r % len(targets)]:
            out = tmp / f"{slug}-{r + 1}.json"
            run(["lighthouse", url, "--quiet", "--chrome-flags=--headless=new", "--form-factor=mobile",
                 "--output=json", f"--output-path={out}"], check=False, capture_output=True)
            if out.exists():
                lh = json.loads(out.read_text(encoding="utf-8"))
                if not lh.get("runtimeError") and _lcp(lh):
                    runs[slug].append((_lcp(lh), out))
    summary = {}
    for slug, got in runs.items():
        if not got:
            continue
        got.sort(key=lambda g: g[0])
        median = got[(len(got) - 1) // 2]  # lower median: always a real run
        median[1].replace(raw / f"load-{slug}.json")
        summary[slug] = {"lcp_ms": [round(g[0]) for g in got], "median_ms": round(median[0]),
                         "spread_ms": round(statistics.pstdev([g[0] for g in got]))}
    for f in tmp.glob("*.json"):
        f.unlink()
    tmp.rmdir()
    (raw / "load-runs.json").write_text(json.dumps({"rounds": rounds, "sites": summary}, indent=2), encoding="utf-8")
    print(f"measured {len(summary)} sites x {rounds} rounds -> raw/load-<slug>.json")
    return summary


if __name__ == "__main__":
    measure(Path(sys.argv[1]), int(sys.argv[2]) if len(sys.argv) > 2 else ROUNDS)
