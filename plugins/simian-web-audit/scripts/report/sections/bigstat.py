"""The most painful measured number, a 100-cell grid, and the optional load-page teaser."""
from report.render import Section, esc

CSS = """
.sa-big-split{display:grid;grid-template-columns:1fr 1fr;gap:64px;align-items:center}
.sa-big-num{font-size:clamp(72px,10vw,140px);font-weight:600;letter-spacing:-6px;line-height:.9;white-space:nowrap;color:var(--ember)}
.sa-big-grid{display:grid;grid-template-columns:repeat(10,1fr);gap:6px}
.sa-big-grid i{aspect-ratio:1;border-radius:4px;background:var(--mint)}
.sa-big-grid i.sa-big-on{background:var(--ember)}
.sa-big-teaser{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-top:24px;padding:20px 24px;text-decoration:none;color:inherit}
.sa-big-teaser b{display:block;font-size:17px}
.sa-big-teaser .btn{flex-shrink:0;white-space:nowrap;padding:12px 20px}
@media(max-width:860px){.sa-big-split{grid-template-columns:1fr}}
"""


def build(ctx) -> Section | None:
    b = ctx["top10"].get("big_stat")
    if not b:
        return None
    grid = ""
    if b.get("grid_pct") is not None:
        on = int(b["grid_pct"])
        legend = b.get("grid_legend") or ["", ""]
        cells = "".join(f'<i class="{"sa-big-on" if i < on else ""}"></i>' for i in range(100))
        grid = (f'<div><div class="sa-big-grid">{cells}</div><p class="cap">Cada cuadro es 1%. '
                f'<span style="color:var(--ember)">■</span> {esc(legend[0])} &nbsp; '
                f'<span style="color:var(--mint)">■</span> {esc(legend[1] if len(legend) > 1 else "")}</p></div>')
    teaser = ""
    if ctx["has_load_page"]:
        teaser = ('<a class="card sa-big-teaser" href="feature-carga.html"><span><b>Mira cómo carga tu sitio frente a tu competencia</b>'
                  '<span class="why">Cuadro a cuadro, con el reloj corriendo · y cómo lo ve alguien con baja visión</span></span>'
                  '<span class="btn btn-primary">Ver comparación ▶</span></a>')
    html = f"""<section class="band" id="dato">
  <div class="wrap sa-big-split">
    <div>
      <div class="eyebrow">Lo que más pesa</div>
      <div class="sa-big-num">{esc(b['value'])}</div>
      <h3 style="margin-top:16px">{esc(b['headline'])}</h3>
      <div class="explain"><b>¿Qué significa?</b> {esc(b['explain'])}</div>
      <p class="src">{esc(b['source'])}</p>
      {teaser}
    </div>
    {grid}
  </div>
</section>"""
    return Section("dato", None, html, CSS)
