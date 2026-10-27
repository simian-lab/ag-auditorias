"""Collect shared evidence once per audit: homepage HTML, Lighthouse (mobile + desktop), screenshots."""
import base64
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import media, units  # noqa: E402
from preflight import CHROME  # noqa: E402

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
EXT = {"image/webp": "webp", "image/jpeg": "jpg", "image/png": "png"}


def fetch_html(url: str, run=subprocess.run) -> str:
    # system curl uses the macOS keychain; python.org builds often lack CA certificates
    res = run(["curl", "-sL", "--max-time", "30", "-A", UA, url], check=True, capture_output=True)
    out = res.stdout
    return out.decode("utf-8", errors="replace") if isinstance(out, bytes) else out


def _decode(data_uri: str) -> tuple[bytes, str]:
    head, b64 = data_uri.split(",", 1)
    mime = head.split(":", 1)[1].split(";", 1)[0]
    return base64.b64decode(b64), EXT.get(mime, "bin")


def extract_lighthouse_screenshots(lh_json: Path, out_dir: Path, prefix: str, run=subprocess.run) -> list[Path]:
    lh = json.loads(lh_json.read_text(encoding="utf-8"))
    data = (lh.get("fullPageScreenshot") or {}).get("screenshot", {}).get("data")
    if not data:
        return []
    raw, ext = _decode(data)
    src = out_dir / f"{prefix}-fullpage.{ext}"
    src.write_bytes(raw)
    return [media.to_jpeg(src, out_dir / f"{prefix}-fullpage.jpg", run=run)]


def _summary(lh: dict) -> dict:
    audits = lh.get("audits", {})
    return {
        "scores": {k: round((v.get("score") or 0) * 100) for k, v in lh.get("categories", {}).items()},
        "lcp": units.seconds(audits.get("largest-contentful-paint", {}).get("numericValue", 0)),
        "total": units.mb_from_kib(audits.get("total-byte-weight", {}).get("numericValue", 0) / 1024),
    }


def collect(audit_dir: Path, url: str, run=subprocess.run, fetch=fetch_html) -> dict:
    raw, shots = audit_dir / "raw", audit_dir / "screenshots"
    (raw / "home.html").write_text(fetch(url), encoding="utf-8")
    summary = {}
    for ff, extra in [("mobile", ["--form-factor=mobile"]), ("desktop", ["--preset=desktop"])]:
        out = raw / f"lighthouse-{ff}.json"
        run(["lighthouse", url, "--quiet", "--chrome-flags=--headless=new", "--output=json",
             f"--output-path={out}", *extra], check=False, capture_output=True)
        if out.exists():
            extract_lighthouse_screenshots(out, shots, ff, run=run)
            summary[ff] = _summary(json.loads(out.read_text(encoding="utf-8")))
    run([CHROME, "--headless=new", "--hide-scrollbars", "--window-size=1440,900", "--virtual-time-budget=8000",
         f"--screenshot={shots / 'desktop-viewport.png'}", url], check=False, capture_output=True)
    return summary


def resolve_url(audit_dir: Path, url: str | None) -> str:
    if url:
        return url
    return json.loads((audit_dir / "findings" / "meta.json").read_text(encoding="utf-8"))["url"]


if __name__ == "__main__":
    target = Path(sys.argv[1])
    summary = collect(target, resolve_url(target, sys.argv[2] if len(sys.argv) > 2 else None))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
