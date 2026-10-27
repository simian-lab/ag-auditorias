"""Overall score, four area bars against the recommended level, and how the score is computed."""
from report.render import Section, esc

ROWS = [("ux", "Facilidad de uso", "Experiencia de usuario"), ("a11y", "Para todas las personas", "Accesibilidad"),
        ("visual", "Primera impresión", "Diseño visual"), ("tech", "Cómo está hecho", "Calidad técnica")]

CSS = """
.sa-score-box{margin:40px auto 0;display:grid;grid-template-columns:320px 1fr;gap:24px;text-align:left}
.sa-score-main{padding:32px;display:flex;flex-direction:column;justify-content:space-between}
.sa-score-num{font-size:120px;font-weight:600;letter-spacing:-6px;line-height:1}
.sa-score-num small{font-size:32px;color:var(--ash);letter-spacing:-1px}
.sa-score-verdict{display:inline-block;border-radius:9999px;padding:4px 12px;font-size:13px;font-weight:500;margin-top:12px}
.sa-score-bad{background:var(--ember-wash);color:var(--ember-ink)}.sa-score-mid{background:var(--amber-wash);color:var(--amber-ink)}.sa-score-good{background:var(--mint-wash);color:var(--mint-ink)}
.sa-score-areas{padding:32px}
.sa-score-row{display:grid;grid-template-columns:170px 1fr 60px;gap:16px;align-items:center;padding:14px 0;border-bottom:1px solid var(--fog)}
.sa-score-lbl{font-weight:500}.sa-score-lbl span{display:block;font-size:12px;color:var(--ash);font-weight:400}
.sa-score-track{height:10px;background:var(--mist);border-radius:9999px;position:relative}
.sa-score-fill{height:100%;border-radius:9999px}
.sa-score-ref{position:absolute;top:-4px;bottom:-4px;width:2px;background:var(--carbon);opacity:.35}
.sa-score-val{text-align:right;font-weight:600;font-size:20px}
.sa-score-how{font-size:12px;color:var(--ash);margin-top:16px}
.sa-score-lbl .sa-score-count{font-size:12px;color:var(--graphite);font-weight:500;margin-top:2px}
.sa-score-crit{margin-top:16px;padding:20px 24px}
.sa-score-crit summary{cursor:pointer;font-weight:600}
.sa-score-cols{display:grid;grid-template-columns:repeat(4,1fr);gap:24px;margin-top:20px}
.sa-score-cols h4{font-size:14px;margin-bottom:8px}
.sa-score-cols ul{list-style:none;font-size:13px;color:var(--graphite)}
.sa-score-cols li{display:flex;gap:8px;padding:6px 0;border-top:1px solid var(--fog)}
.sa-score-cols li span{font-weight:700;width:14px;flex-shrink:0}
.sa-score-ok span{color:var(--mint-ink)}.sa-score-pa span{color:var(--amber-ink)}.sa-score-ko span{color:var(--ember-ink)}.sa-score-na{color:var(--ash)}
@media(max-width:860px){.sa-score-cols{grid-template-columns:1fr}}
@media(max-width:860px){.sa-score-box{grid-template-columns:1fr}.sa-score-row{grid-template-columns:110px 1fr 44px}}
"""


def _tone(v: int, target: int) -> str:
    return "sa-score-bad" if v < 50 else ("sa-score-mid" if v < target else "sa-score-good")


def _color(v: int, target: int) -> str:
    return "var(--ember)" if v < 50 else ("var(--amber)" if v < target else "var(--mint)")


MARK = {"pass": ("sa-score-ok", "✓"), "partial": ("sa-score-pa", "◐"), "fail": ("sa-score-ko", "✕"), "na": ("sa-score-na", "—")}


def _criteria_list(ctx) -> str:
    cols = []
    for k, a, _ in ROWS:
        results = {c["id"]: c["result"] for c in (ctx["areas"].get(k) or {}).get("checks", [])}
        items = "".join(
            f'<li class="{MARK[results.get(c["id"], "na")][0]}"><span>{MARK[results.get(c["id"], "na")][1]}</span>{esc(c["label"])}</li>'
            for c in ctx["rubric"]["areas"][k])
        cols.append(f'<div><h4>{esc(a)}</h4><ul>{items}</ul></div>')
    return (f'<details class="card sa-score-crit"><summary>Ver los criterios evaluados</summary>'
            f'<div class="sa-score-cols">{"".join(cols)}</div></details>')


def build(ctx) -> Section | None:
    s = ctx["scores"]
    if not s:
        return None
    target, overall = s["target"], s["overall"]
    verdict = {"sa-score-bad": "Necesita mejoras importantes", "sa-score-mid": "Por debajo del nivel recomendado",
               "sa-score-good": "En buen nivel"}[_tone(overall, target)]
    detail = s.get("detail", {})

    def count(k):
        d = detail.get(k)
        if not d:
            return ""
        part = d.get("partial", 0)
        extra = f' · {part} parcial{"es" if part > 1 else ""}' if part else ""
        return f'<span class="sa-score-count">{d["passed"]} de {d["total"]} criterios{extra}</span>'
    rows = "".join(
        f'<div class="sa-score-row"><div class="sa-score-lbl">{esc(a)}<span>{esc(b)}</span>{count(k)}</div>'
        f'<div class="sa-score-track"><div class="sa-score-fill" style="width:{s[k]}%;background:{_color(s[k], target)}"></div>'
        f'<div class="sa-score-ref" style="left:{target}%"></div></div><div class="sa-score-val">{s[k]}</div></div>'
        for k, a, b in ROWS)
    cfg = ctx["scoring"]
    how = ("¿Cómo calculamos este puntaje? Cada área se evalúa con la misma lista fija de criterios, con peso según su importancia; "
           "el puntaje es el porcentaje que el sitio cumple (un criterio cumplido a medias vale la mitad). En accesibilidad y calidad técnica se promedia con la medición de "
           f"Google Lighthouse. El total es el promedio de las cuatro áreas. Fórmula v{cfg['version']}.")
    criteria = _criteria_list(ctx) if detail else ""
    html = f"""<section id="resultado">
  <div class="wrap">
    <div class="eyebrow center">Resultado general</div>
    <h2 class="center" style="margin-top:8px">Así está el sitio hoy</h2>
    <div class="sa-score-box">
      <div class="card sa-score-main"><div><div class="eyebrow">Salud general del sitio</div>
        <div class="sa-score-num">{overall}<small>/100</small></div>
        <span class="sa-score-verdict {_tone(overall, target)}">{verdict}</span></div>
        <p class="why" style="margin-top:24px">Un sitio que vende bien debería estar por encima de <b>{target}</b>.</p></div>
      <div class="card sa-score-areas">{rows}<p class="sa-score-how">{esc(how)}</p></div>
    </div>
    {criteria}
  </div>
</section>"""
    return Section("resultado", "Resultado", html, CSS)
