"""Plan: three base stages with every Top item, an optional fourth stage, and a table of all points."""
from report.render import Section, esc
from report.sections import extra, redesign

STAGES = {1: ("Semanas 1–2", "Victorias rápidas"), 2: ("Semanas 3–5", "Que entiendan qué vendes"), 3: ("Semanas 6–8", "Que te elijan")}
AREA = {"ux": "Experiencia", "a11y": "Accesibilidad", "vis": "Visual", "tec": "Técnico"}

CSS = """
.sa-plan-stages{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-top:40px}
.sa-plan-card{padding:32px}
.sa-plan-when{font-size:13px;color:var(--ash);font-weight:500}
.sa-plan-card h3{margin:8px 0 16px}
.sa-plan-card ul{list-style:none;font-size:15px;color:var(--graphite)}
.sa-plan-card li{padding:8px 0;border-top:1px solid var(--fog)}
.sa-plan-card li b{color:var(--carbon);font-weight:500;margin-right:6px}
.sa-plan-opt{border:1.5px dashed var(--brand);background:var(--brand-wash)}
.sa-plan-chip{display:inline-block;background:var(--brand);color:#fff;border-radius:9999px;padding:2px 10px;font-size:11px;font-weight:600;margin-left:6px}
.sa-plan-table{width:100%;border-collapse:collapse;margin-top:40px;font-size:14px}
.sa-plan-table th{text-align:left;font-size:12px;font-weight:500;color:var(--ash);text-transform:uppercase;letter-spacing:.04em;padding:10px 12px;border-bottom:1px solid var(--fog)}
.sa-plan-table td{padding:12px;border-bottom:1px solid var(--fog);vertical-align:middle}
.sa-plan-n{font-weight:600;color:var(--ash);width:48px}
.sa-plan-optrow td{color:var(--graphite)}.sa-plan-optrow .sa-plan-n{color:var(--brand)}
.sa-plan-st{display:inline-block;border-radius:9999px;padding:2px 10px;font-size:12px;font-weight:500;background:var(--mist);white-space:nowrap}
.sa-plan-st4{background:var(--brand-wash);color:var(--brand)}
.sa-plan-dt{display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--fog);margin-right:4px}
.sa-plan-dton{background:var(--carbon)}
.sa-plan-sep td{background:var(--linen);font-size:12px;font-weight:600;color:var(--graphite);text-transform:uppercase;letter-spacing:.04em}
@media(max-width:860px){.sa-plan-hm{display:none}}
"""


def extra_rows(ctx) -> list[tuple[str, str, str, str]]:
    rows = []
    pres, seo = (ctx["presence"], ctx["seo"]) if extra.enabled(ctx) else (None, None)
    if pres:
        rows.append(("E1", "Título, descripción y vista previa para Google y WhatsApp", "SEO / IA", "Bajo"))
        if pres.get("nap", {}).get("inconsistencies"):
            rows.append(("E2", "Un solo nombre, teléfono y dirección en todas partes", "SEO / IA", "Bajo"))
        if pres.get("ai_answer", {}).get("aeo_fixes"):
            rows.append(("E3", "Preguntas frecuentes, ficha de empresa y cifras para la IA", "SEO / IA", "Medio"))
    if seo and seo.get("findings"):
        rows.append(("E4", "Contenido y estructura para aparecer en Google", "SEO / IA", "Medio"))
    if redesign.redesign_image(ctx):
        rows.append(("R", "Rediseño de la portada (concepto Simian)", "Diseño", "Alto"))
    return rows


def build(ctx) -> Section | None:
    items = ctx["top10"]["items"]
    if not items:
        return None
    by_stage = {k: [i for i in items if i.get("stage", 1) == k] for k in STAGES}
    cards = "".join(
        f'<div class="card sa-plan-card"><div class="sa-plan-when">{STAGES[k][0]}</div><h3>{STAGES[k][1]}</h3><ul>'
        + "".join(f'<li data-n="{i["n"]}"><b>#{i["n"]}</b>{esc(i["t_plain"])}</li>' for i in by_stage[k]) + "</ul></div>"
        for k in STAGES if by_stage[k])
    extras = extra_rows(ctx)
    if extras:
        cards += ('<div class="card sa-plan-card sa-plan-opt"><div class="sa-plan-when">Semanas 9–12 <span class="sa-plan-chip">OPCIONAL</span></div>'
                  '<h3>Que te encuentren</h3><ul>' + "".join(f"<li><b>{c}</b>{esc(t)}</li>" for c, t, _, _ in extras) + "</ul></div>")

    def dots(n):
        return "".join(f'<span class="sa-plan-dt{" sa-plan-dton" if k < n else ""}"></span>' for k in range(5))
    rows = "".join(
        f'<tr data-n="{i["n"]}"><td class="sa-plan-n">{i["n"]:02d}</td><td>{esc(i["t_plain"])}</td><td class="sa-plan-hm">{AREA[i["c"]]}</td>'
        f'<td class="sa-plan-hm">{dots(i["imp"])}</td><td class="sa-plan-hm">{esc(i["eff"])}</td>'
        f'<td><span class="sa-plan-st">{STAGES[i.get("stage", 1)][0]}</span></td></tr>' for i in items)
    if extras:
        rows += '<tr class="sa-plan-sep"><td colspan="6">Opcional · Que te encuentren</td></tr>' + "".join(
            f'<tr class="sa-plan-optrow"><td class="sa-plan-n">{c}</td><td>{esc(t)}</td><td class="sa-plan-hm">{a}</td>'
            f'<td class="sa-plan-hm">—</td><td class="sa-plan-hm">{e}</td><td><span class="sa-plan-st sa-plan-st4">Semanas 9–12</span></td></tr>'
            for c, t, a, e in extras)
    title = "Tres etapas para la base, y una cuarta si quieres ir por más." if extras else "Tres etapas, con resultados desde las primeras semanas."
    html = f"""<section id="plan">
  <div class="wrap">
    <div class="eyebrow">Plan sugerido</div>
    <h2>{title}</h2>
    <div class="sa-plan-stages">{cards}</div>
    <table class="sa-plan-table"><thead><tr><th>#</th><th>Mejora</th><th class="sa-plan-hm">Área</th><th class="sa-plan-hm">Impacto</th><th class="sa-plan-hm">Esfuerzo</th><th>Etapa</th></tr></thead>
    <tbody>{rows}</tbody></table>
  </div>
</section>"""
    return Section("plan", "Plan", html, CSS)
