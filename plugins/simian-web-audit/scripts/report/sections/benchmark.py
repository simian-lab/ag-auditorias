"""Five-second test: client first-screen next to competitors, same checks for everyone."""
from report.render import Section, esc

CHECKS = [("¿Se entiende qué vende?", "what"), ("¿Dice para quién?", "for_whom"), ("¿Titular en texto?", "text_headline"),
          ("¿Pruebas de confianza?", "trust_proof"), ("¿Botón para cotizar?", "quote_cta")]

CSS = """
.sa-bench-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-top:40px}
.sa-bench-card{overflow:hidden}
.sa-bench-card img{width:100%;aspect-ratio:16/10;object-fit:cover;object-position:top;display:block;border-bottom:1px solid var(--fog)}
.sa-bench-me{outline:2px solid var(--ember);outline-offset:-1px}
.sa-bench-bd{padding:16px}.sa-bench-bd h4{font-size:15px;font-weight:600;margin-bottom:10px}
.sa-bench-ck{display:flex;justify-content:space-between;font-size:13px;padding:5px 0;border-top:1px solid var(--fog);color:var(--graphite)}
.sa-bench-y{color:var(--mint-ink);font-weight:600}.sa-bench-n{color:var(--ember-ink);font-weight:600}
@media(max-width:860px){.sa-bench-grid{grid-template-columns:1fr 1fr}}
"""


def _mb(v: float) -> str:
    return f"{v:.1f}".replace(".", ",") + " MB"


def _card(ctx, site, me: bool) -> str:
    src = ctx["asset"](site["screenshot"].split("/")[-1])
    img = f'<img src="{src}" alt="Primera pantalla de {esc(site.get("name", ""))}">' if src else ""
    rows = "".join(f'<div class="sa-bench-ck"><span>{q}</span>'
                   f'{"<span class=sa-bench-y>Sí</span>" if site["five_second"][k] else "<span class=sa-bench-n>No</span>"}</div>'
                   for q, k in CHECKS)
    mb = site["lighthouse"]["total_mb"]
    rows += f'<div class="sa-bench-ck"><span>Peso de la página</span><span class="{"sa-bench-n" if mb > 5 else "sa-bench-y"}">{_mb(mb)}</span></div>'
    name = "Tu sitio" if me else site["name"]
    return f'<div class="card sa-bench-card{" sa-bench-me" if me else ""}">{img}<div class="sa-bench-bd"><h4>{esc(name)}</h4>{rows}</div></div>'


def build(ctx) -> Section | None:
    b = ctx["benchmark"]
    if not b:
        return None
    cards = _card(ctx, b["client"], True) + "".join(_card(ctx, c, False) for c in b["competitors"])
    html = f"""<section id="competencia">
  <div class="wrap">
    <div class="eyebrow">La prueba de los 5 segundos</div>
    <h2>Lo que ve un comprador en tu sitio… y en el de tu competencia.</h2>
    <p class="lead" style="margin-top:12px">{esc(b['takeaway_es'])}</p>
    <div class="sa-bench-grid">{cards}</div>
    <p class="src">Capturas y mediciones propias (Google Lighthouse, celular). Todos los sitios se evalúan con los mismos criterios; un botón de WhatsApp no cuenta como botón de cotización.</p>
  </div>
</section>"""
    return Section("competencia", "Competencia", html, CSS)
