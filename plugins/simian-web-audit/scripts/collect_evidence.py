"""Collect shared evidence once per audit: homepage HTML, Lighthouse (mobile + desktop), screenshots."""
import base64
import json
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

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


class _ShareTags(HTMLParser):
    """og:image and icon links, as link-preview crawlers (WhatsApp, LinkedIn) read them without JavaScript."""
    def __init__(self):
        super().__init__()
        self.og_image, self.icons = None, []

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        if tag == "meta" and a.get("property", a.get("name", "")).lower() == "og:image" and a.get("content") and not self.og_image:
            self.og_image = a["content"].strip()
        rel = a.get("rel", "").lower().split()
        if tag == "link" and a.get("href") and ("icon" in rel or "apple-touch-icon" in rel):
            size = max((int(x.split("x")[0]) for x in a.get("sizes", "").lower().split() if x.split("x")[0].isdigit()), default=0)
            self.icons.append((size, a["href"].strip()))


def share_image(html: str, base_url: str, shots: Path, run=subprocess.run) -> dict:
    """Save what WhatsApp shows today: og:image -> og-today.jpg; without one, the largest site icon -> og-today-icon.png."""
    tags = _ShareTags()
    tags.feed(html)
    if tags.og_image:
        url, tmp, name = urljoin(base_url, tags.og_image), shots / "og-today-src", "og-today.jpg"
    elif tags.icons:
        url, tmp, name = urljoin(base_url, max(tags.icons)[1]), shots / "og-today-icon-src", "og-today-icon.png"
    else:
        return {}
    if run(["curl", "-sfL", "--max-time", "30", "-A", UA, "-o", str(tmp), url], check=False, capture_output=True).returncode:
        return {}
    if name.endswith(".jpg"):
        media.to_jpeg(tmp, shots / name, max_px=1200, run=run)
    else:
        run(["sips", "-s", "format", "png", str(tmp), "--out", str(shots / name)], check=False, capture_output=True)
    tmp.unlink(missing_ok=True)
    if not (shots / name).exists():
        return {}
    key = "today_og_image_local" if name.endswith(".jpg") else "today_icon_local"
    return {"source": url, key: name}


def _summary(lh: dict) -> dict:
    audits = lh.get("audits", {})
    return {
        "scores": {k: round((v.get("score") or 0) * 100) for k, v in lh.get("categories", {}).items()},
        "lcp": units.seconds(audits.get("largest-contentful-paint", {}).get("numericValue", 0)),
        "total": units.mb_from_kib(audits.get("total-byte-weight", {}).get("numericValue", 0) / 1024),
    }


def collect(audit_dir: Path, url: str, run=subprocess.run, fetch=fetch_html) -> dict:
    raw, shots = audit_dir / "raw", audit_dir / "screenshots"
    html = fetch(url)
    (raw / "home.html").write_text(html, encoding="utf-8")
    summary = {"share_preview": share_image(html, url, shots, run=run)}
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
