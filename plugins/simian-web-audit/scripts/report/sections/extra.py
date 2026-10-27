"""Optional Extra: search tests, Google/WhatsApp previews, NAP consistency, real AI answers, AEO fixes."""
import re

from report.render import Section, esc

CSS = """
.sa-extra-grid{display:grid;grid-template-columns:320px 1fr;gap:24px;margin-top:40px;text-align:left}
.sa-extra-score{padding:32px}
.sa-extra-num{font-size:110px;font-weight:600;letter-spacing:-6px;line-height:1}
.sa-extra-num small{font-size:30px;color:var(--ash);letter-spacing:-1px}
.sa-extra-pill{display:inline-block;border-radius:9999px;padding:4px 12px;font-size:13px;font-weight:500;background:var(--ember-wash);color:var(--ember-ink);margin-top:12px}
.sa-extra-q{width:100%;border-collapse:collapse;font-size:14px}
.sa-extra-q td{padding:12px 8px;border-top:1px solid var(--fog);vertical-align:top}
.sa-extra-who{color:var(--ash);font-size:12px}
.sa-extra-no{color:var(--ember-ink);font-weight:600;white-space:nowrap}.sa-extra-yes{color:var(--mint-ink);font-weight:600;white-space:nowrap}
.sa-extra-pair{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:48px;text-align:left}
.sa-extra-card{padding:28px}
.sa-extra-lbl{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;margin:16px 0 8px}
.sa-extra-lnow{color:var(--ember-ink)}.sa-extra-lnew{color:var(--mint-ink)}
.sa-extra-serp{border:1px solid var(--fog);border-radius:12px;padding:16px;font-family:Arial,sans-serif;letter-spacing:0}
.sa-extra-serp p{font-size:12px;color:#4d5156}.sa-extra-serp b{display:block;font-size:19px;font-weight:400;color:#1a0dab;margin:4px 0}
.sa-extra-serp span{font-size:13px;color:#4d5156}.sa-extra-serp .sa-extra-miss{color:var(--ember-ink);font-style:italic}
.sa-extra-wa{background:#e5ddd5;border-radius:12px;padding:16px}
.sa-extra-bubble{background:#dcf8c6;border-radius:10px;padding:6px;max-width:320px;margin-left:auto;font-family:Arial,sans-serif;letter-spacing:0;font-size:12px;color:#555}
.sa-extra-og{background:#f0f0f0;border-radius:6px;overflow:hidden}
.sa-extra-og img{width:100%;aspect-ratio:1.91/1;object-fit:cover;display:block}
.sa-extra-og div{padding:8px 10px}.sa-extra-og b{display:block;color:#111;font-size:13px}
.sa-extra-link{display:block;font-size:13px;color:#027eb5;padding:6px 4px 2px}
.sa-extra-nap{padding:28px;margin-top:16px;text-align:left}
.sa-extra-nap li{list-style:none;padding:10px 0;border-top:1px solid var(--fog);font-size:14px;color:var(--graphite)}
.sa-extra-ai{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:24px;text-align:left}
.sa-extra-aic{padding:24px}
.sa-extra-eng{display:flex;justify-content:space-between;align-items:center;font-size:13px;color:var(--ash);margin-bottom:8px}
.sa-extra-prompt{font-weight:600;font-size:16px;margin-bottom:12px}
.sa-extra-names{display:flex;flex-wrap:wrap;gap:6px;margin:12px 0}
.sa-extra-names span{border-radius:9999px;padding:3px 10px;font-size:12px;background:var(--mist);color:var(--graphite)}
.sa-extra-names span.sa-extra-me{background:var(--amber-wash);color:var(--amber-ink);font-weight:600}
.sa-extra-res{border-radius:9999px;padding:3px 10px;font-size:12px;font-weight:600;background:var(--ember-wash);color:var(--ember-ink)}
.sa-extra-half{background:var(--amber-wash);color:var(--amber-ink)}
.sa-extra-aeo{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px;text-align:left}
.sa-extra-aeo li{list-style:none;padding:20px;font-size:14px;color:var(--graphite)}
.sa-extra-aeo b{display:block;color:var(--carbon);font-size:15px;margin-bottom:6px}
@media(max-width:860px){.sa-extra-grid,.sa-extra-pair,.sa-extra-ai,.sa-extra-aeo{grid-template-columns:1fr}}
"""


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def is_brand(name: str, brand: str) -> bool:
    b = _norm(brand)
    return bool(b) and b in _norm(name)


def _search(seo, score) -> tuple[str, str]:
    tests = seo.get("search_tests", [])
    hits = sum(1 for t in tests if t["appears"])
    rows = "".join(
        f'<tr><td>«{esc(t["query"])}»<div class="sa-extra-who">Aparecen: {esc(", ".join(t.get("who_appears", [])[:3]))}</div></td>'
        f'<td class="{"sa-extra-yes" if t["appears"] else "sa-extra-no"}">{"Apareces" if t["appears"] else "No apareces"}</td></tr>'
        for t in tests)
    headline = ("Buscamos lo que buscan tus compradores. No apareciste ni una vez." if hits == 0
                else f"Buscamos lo que buscan tus compradores. Apareciste en {hits} de {len(tests)}.")
    score_html = f'<div class="sa-extra-num">{score}<small>/100</small></div>' if score is not None else ""
    grid = (f'<div class="sa-extra-grid"><div class="card sa-extra-score"><div class="eyebrow">Visibilidad en buscadores</div>{score_html}'
            f'<span class="sa-extra-pill">{hits} de {len(tests)} búsquedas</span></div>'
            f'<div class="card" style="padding:12px 20px"><table class="sa-extra-q">{rows}</table></div></div>')
    return headline, grid


def _previews(ctx, pres) -> str:
    today, prop = pres["serp"]["today"][0], pres["serp"]["proposed"][0]
    sp = pres["share_preview"]["proposed"]
    desc = (f'<span>{esc(today["meta_description"])}</span>' if today.get("meta_description")
            else '<span class="sa-extra-miss">Sin descripción: Google improvisa el texto que ve el comprador.</span>')
    serp = (f'<div class="card sa-extra-card"><h3>Así apareces en Google</h3><p class="why">Lo primero que ve un comprador nuevo.</p>'
            f'<div class="sa-extra-lbl sa-extra-lnow">Hoy</div><div class="sa-extra-serp"><p>{esc(today["url"])}</p><b>{esc(today["title"])}</b>{desc}</div>'
            f'<div class="sa-extra-lbl sa-extra-lnew">Propuesta</div><div class="sa-extra-serp"><p>{esc(today["url"])}</p><b>{esc(prop["title"])}</b>'
            f'<span>{esc(prop["description"])}</span></div></div>')
    img = ctx["asset"](sp["og_image_local"]) if sp.get("og_image_local") else None
    og_img = f'<img src="{img}" alt="">' if img else ""
    share = (f'<div class="card sa-extra-card"><h3>Así se ve tu enlace en WhatsApp</h3><p class="why">Cada vez que compartes el sitio con un cliente.</p>'
             f'<div class="sa-extra-lbl sa-extra-lnow">Hoy</div><div class="sa-extra-wa"><div class="sa-extra-bubble"><span class="sa-extra-link">{esc(today["url"])}</span>{esc(today["title"])}</div></div>'
             f'<div class="sa-extra-lbl sa-extra-lnew">Propuesta</div><div class="sa-extra-wa"><div class="sa-extra-bubble"><div class="sa-extra-og">{og_img}'
             f'<div><b>{esc(sp["og:title"])}</b>{esc(sp["og:description"])}</div></div><span class="sa-extra-link">{esc(today["url"])}</span></div></div></div>')
    return f'<div class="sa-extra-pair">{serp}{share}</div>'


def _ai(ai, brand: str) -> str:
    def card(a):
        res = ('<span class="sa-extra-res sa-extra-half">Te menciona</span>' if a["mentioned"]
               else '<span class="sa-extra-res">No apareces</span>')
        names = "".join(f'<span class="{"sa-extra-me" if is_brand(n, brand) else ""}">{esc(n)}</span>' for n in a["named"])
        return (f'<div class="card sa-extra-aic"><div class="sa-extra-eng"><span>{esc(a["engine"])}</span>{res}</div>'
                f'<div class="sa-extra-prompt">«{esc(a["prompt"])}»</div><div class="sa-extra-names">{names}</div><p class="why">{esc(a["note_es"])}</p></div>')
    return ('<h3 style="margin-top:56px">Le preguntamos a la IA lo que preguntaría un comprador</h3>'
            '<p class="lead" style="margin-top:8px">Respuestas reales, consultadas desde el país del cliente.</p>'
            f'<div class="sa-extra-ai">{"".join(card(a) for a in ai["answers"])}</div>'
            f'<p class="src">Consulta del {esc(ai["date"])} ({esc(ai["source"])}). Las respuestas de la IA cambian con el tiempo.</p>')


def enabled(ctx) -> bool:
    """Single predicate shared with the plan: the Extra exists when selected and some Extra data was produced."""
    return bool(ctx["meta"].get("options", {}).get("extra") and (ctx["seo"] or ctx["presence"]))


def build(ctx) -> Section | None:
    if not enabled(ctx):
        return None
    seo, pres, ai = ctx["seo"] or {}, ctx["presence"], ctx["ai"]
    parts = []
    if seo.get("search_tests"):
        headline, grid = _search(seo, (ctx["scores"] or {}).get("seo"))
        parts.append(grid)
    else:
        headline = "¿Te encuentran Google y la IA cuando un comprador busca lo que vendes?"
    if pres:
        if pres["serp"].get("today") and pres["serp"].get("proposed"):
            parts.append(_previews(ctx, pres))
        if pres.get("nap", {}).get("inconsistencies"):
            parts.append('<div class="card sa-extra-nap"><h3>Tu marca no dice lo mismo en todas partes</h3>'
                         '<p class="why">Google y la IA confían menos en un negocio con datos contradictorios.</p><ul style="margin-top:12px">'
                         + "".join(f"<li>{esc(x)}</li>" for x in pres["nap"]["inconsistencies"]) + "</ul></div>")
    if ai:
        parts.append(_ai(ai, ai.get("brand") or ctx["top10"]["client"]))
    fixes = (pres or {}).get("ai_answer", {}).get("aeo_fixes", [])
    if fixes:
        parts.append('<h3 style="margin-top:56px">Cómo hacemos que la IA te recomiende</h3>'
                     '<p class="lead" style="margin-top:8px">ChatGPT, Gemini y Perplexity recomiendan empresas que pueden entender y citar.</p>'
                     '<ul class="sa-extra-aeo">' + "".join(f'<li class="card"><b>{esc(x["title"])}</b>{esc(x["fix"])}</li>' for x in fixes) + "</ul>")
    note = seo.get("search_tests_note", "")
    html = f"""<section id="extra">
  <div class="wrap center">
    <span class="chip" style="margin-bottom:16px"><b>EXTRA</b> Visibilidad en Google e IA · no incluido en la auditoría base</span>
    <h2>{esc(headline)}</h2>
    <p class="lead" style="margin-top:12px">{esc(seo.get('extra_pitch_es', ''))}</p>
    {''.join(parts)}
    <p class="src">{esc(note)}</p>
  </div>
</section>"""
    return Section("extra", "Extra", html, CSS)
