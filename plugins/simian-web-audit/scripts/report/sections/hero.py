"""Hero: Simian logo, audit title and one-line intro."""
import re

from report.render import Section, esc

INTRO = ("Revisamos tu sitio como lo vive un visitante real: qué tan fácil es de usar, si todas las personas "
         "pueden usarlo, cómo se ve y qué tan bien está construido. Estas son las {n} mejoras con más impacto para el negocio.")

CSS = """
.sa-hero{text-align:center;padding:72px 0 48px}
.sa-hero-logo{display:flex;justify-content:center;margin-bottom:32px}
.sa-hero-logo svg{height:36px;width:auto}
.sa-hero-dom{color:var(--graphite)}
"""


def _logo_svg(ctx) -> str:
    path = ctx["logo"]
    if not path or not path.exists():
        return ""
    svg = path.read_text(encoding="utf-8")
    svg = re.sub(r'\s(width|height|preserveAspectRatio|overflow|style)="[^"]*"', "", svg, count=5)
    return svg.replace("<svg", '<svg aria-label="Simian" role="img"', 1)


def build(ctx) -> Section:
    t = ctx["top10"]
    html = f"""<section class="sa-hero" id="inicio">
  <div class="wrap">
    <div class="sa-hero-logo">{_logo_svg(ctx)}</div>
    <span class="chip"><b>AUDITORÍA WEB</b> {esc(t['date'])}</span>
    <h1>Auditoría del sitio<br><span class="sa-hero-dom">{esc(t['domain'])}</span></h1>
    <p class="lead" style="margin:0 auto">{esc(INTRO.format(n=len(t['items'])))}</p>
  </div>
</section>"""
    return Section("inicio", None, html, CSS)
