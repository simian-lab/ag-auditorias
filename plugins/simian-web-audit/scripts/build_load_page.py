"""Optional page: watch the client site load frame by frame next to competitors, plus a vision simulator."""
import base64
import json
import math
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import media, paths  # noqa: E402
from report.render import esc  # noqa: E402

TEMPLATE = paths.plugin_root() / "templates" / "load-page.html"
EXT = {"image/jpeg": "jpg", "image/webp": "webp", "image/png": "png"}
VISION_TXT = {
    "normal": "Tu página de inicio tal como se ve hoy.",
    "low": "Simulación de <b>baja visión</b> (vista borrosa y menos contraste). Los textos y botones con poco contraste son los primeros en perderse.",
    "cvd": "Simulación de <b>deuteranopía</b>, un tipo de daltonismo que confunde verdes y rojos. Solo un contraste alto mantiene los botones legibles.",
}


def _s(ms: float) -> str:
    return f"{ms / 1000:.1f}".replace(".", ",")


def extract_frames(lh: dict) -> list[tuple[int, bytes, str]]:
    items = lh.get("audits", {}).get("screenshot-thumbnails", {}).get("details", {}).get("items", [])
    frames = []
    for it in items:
        head, b64 = it["data"].split(",", 1)
        mime = head.split(":", 1)[1].split(";", 1)[0]
        frames.append((int(round(it["timing"])), base64.b64decode(b64), EXT.get(mime, "jpg")))
    return sorted(frames, key=lambda f: f[0])


def site_data(lh: dict, slug: str, name: str, url: str, me: bool) -> dict:
    a = lh.get("audits", {})
    m = (a.get("metrics", {}).get("details", {}).get("items") or [{}])[0]
    fcp = int(round(m.get("observedFirstContentfulPaint", 0)))
    lcp = int(round(m.get("observedLargestContentfulPaint", fcp)))
    frames = [[t, 1] if t < fcp else [t] for t, _, _ in extract_frames(lh)]
    return {"slug": slug, "name": name, "url": url, "me": me, "fcp": fcp, "lcp": lcp, "frames": frames,
            "lab": {k: int(round(a.get(key, {}).get("numericValue", 0))) for k, key in
                    [("fcp", "first-contentful-paint"), ("lcp", "largest-contentful-paint"), ("si", "speed-index")]}}


def _write_frames(lh: dict, slug: str, film: Path) -> None:
    for t, data, ext in extract_frames(lh):
        dst = film / f"{slug}-{t}.jpg"
        if ext == "jpg":
            dst.write_bytes(data)
        else:
            src = film / f"{slug}-{t}.{ext}"
            src.write_bytes(data)
            media.to_jpeg(src, dst)
            src.unlink()


def _vision_big(areas: dict) -> str:
    for f in areas.get("a11y", {}).get("findings", []):
        m = re.match(r"\s*(\d+,\d+):1", f.get("headline_metric") or "")
        if m:
            return f'<div class="big"><span>{esc(m.group(1))}</span>:1</div><p class="cap">{esc(f["summary"])} El mínimo recomendado es 4,5:1 (WCAG).</p>'
    return ""


def _copy(meta_domain: str, sites: list[dict]) -> tuple[str, str]:
    me = next(s for s in sites if s["me"])
    others = [s for s in sites if not s["me"]]
    if others and all(o["lcp"] < me["lcp"] for o in others):
        headline = "Mientras tu sitio sigue cargando, tu competencia ya mostró su oferta."
    else:
        headline = "Así carga tu sitio frente a tu competencia."
    if others:
        fastest = min(o["lcp"] for o in others)
        slowest = max(o["lcp"] for o in others)
        rng = f"{_s(fastest)} s" if fastest == slowest else f"entre {_s(fastest)} y {_s(slowest)} s"
        meaning = (f"<p>Tu competencia muestra su contenido principal {rng}. En {esc(meta_domain)}, el contenido principal "
                   f"tarda <b>{_s(me['lcp'])} s</b> en aparecer.</p>")
    else:
        meaning = f"<p>En {esc(meta_domain)}, el contenido principal tarda <b>{_s(me['lcp'])} s</b> en aparecer.</p>"
    return headline, meaning


def timeline_end(lcps: list[int]) -> int:
    # multiple of 6 s so the six axis ticks fall on whole seconds
    return max(6000, int(math.ceil(max(lcps) * 1.1 / 6000.0)) * 6000)


def _js(value) -> str:
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def build_load_page(audit_dir: Path) -> Path | None:
    f = audit_dir / "findings"
    meta = json.loads((f / "meta.json").read_text(encoding="utf-8"))
    client_lh = audit_dir / "raw" / "lighthouse-mobile.json"
    if not meta.get("options", {}).get("load_page") or not client_lh.exists():
        return None
    report = audit_dir / "report"
    film = report / "assets" / "film"
    film.mkdir(parents=True, exist_ok=True)
    domain = meta.get("domain", "")
    lh = json.loads(client_lh.read_text(encoding="utf-8"))
    if not extract_frames(lh):
        return None
    sites = [site_data(lh, "client", "Tu sitio", domain, True)]
    _write_frames(lh, "client", film)
    bench_path = f / "benchmark.json"
    if bench_path.exists():
        for c in json.loads(bench_path.read_text(encoding="utf-8")).get("competitors", []):
            p = audit_dir / "raw" / f"bench-{c.get('slug', '')}-lh.json"
            if c.get("slug") and p.exists():
                clh = json.loads(p.read_text(encoding="utf-8"))
                sites.append(site_data(clh, c["slug"], c["name"], c["url"].split("://")[-1].rstrip("/"), False))
                _write_frames(clh, c["slug"], film)
    end = timeline_end([s["lcp"] for s in sites])
    areas = {a: json.loads((f / f"{a}.json").read_text(encoding="utf-8")) for a in ["a11y"] if (f / f"{a}.json").exists()}
    headline, meaning = _copy(domain, sites)
    date = meta.get("created_at", "")[:10]
    html = (TEMPLATE.read_text(encoding="utf-8")
            .replace("{{DOMAIN}}", esc(domain)).replace("{{HEADLINE}}", esc(headline)).replace("{{END}}", str(end))
            .replace("{{FRAMES_CAPTION}}", esc(f"Fotogramas reales capturados por Google Lighthouse en móvil, {date}."))
            .replace("{{MEANING_HTML}}", meaning).replace("{{RINGS}}", "").replace("{{VISION_BIG}}", _vision_big(areas))
            .replace("{{SITES_JSON}}", _js(sites)).replace("{{VISION_TXT_JSON}}", _js(VISION_TXT)))
    assets = report / "assets"
    (assets / "fonts").mkdir(parents=True, exist_ok=True)
    shutil.copy2(paths.asset("fonts", "InterVariable.woff2"), assets / "fonts" / "InterVariable.woff2")
    shot = audit_dir / "screenshots" / "desktop-viewport.png"
    if shot.exists():
        shutil.copy2(shot, assets / "desktop-viewport.png")
    out = report / "feature-carga.html"
    out.write_text(html, encoding="utf-8")
    print(f"written {out}")
    return out


if __name__ == "__main__":
    build_load_page(Path(sys.argv[1]))
