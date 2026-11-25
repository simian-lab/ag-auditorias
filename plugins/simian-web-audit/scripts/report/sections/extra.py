"""Optional Extra: search tests, Google/WhatsApp previews, NAP consistency, real AI answers, AEO fixes."""
import re

from report.render import Section, esc
from report.sections.score import MARK, VERDICT, _tone

CSS = """
.sa-extra-block{padding:32px;margin-top:40px;text-align:left}
.sa-extra-block h4{font-size:16px;margin-top:36px}
.sa-extra-q{width:100%;border-collapse:collapse;font-size:14px;margin-top:12px;table-layout:fixed}.sa-extra-q th:first-child{width:46%}.sa-extra-q th:nth-child(2){width:28%}
.sa-extra-q th{text-align:left;font-size:12px;font-weight:600;color:var(--ash);text-transform:uppercase;letter-spacing:.04em;padding:8px}
.sa-extra-q td{padding:12px 8px;border-top:1px solid var(--fog);vertical-align:top}
.sa-extra-q .sa-extra-first{color:var(--graphite)}
.sa-extra-pill{display:inline-block;border-radius:9999px;padding:4px 12px;font-size:13px;font-weight:500;background:var(--ember-wash);color:var(--ember-ink);margin-top:12px}.sa-extra-pill.sa-extra-ok{background:var(--mint-wash);color:var(--mint-ink)}
.sa-extra-sum{margin-top:12px;font-weight:600}
.sa-extra-scorebox{display:grid;grid-template-columns:240px 1fr;gap:32px;align-items:start;margin-top:8px}
.sa-extra-num{font-size:110px;font-weight:600;letter-spacing:-6px;line-height:1}
.sa-extra-num.sa-score-bad,.sa-extra-num.sa-score-mid,.sa-extra-num.sa-score-good{background:none}.sa-extra-num.sa-score-bad{color:var(--ember-ink)}.sa-extra-num.sa-score-mid{color:var(--amber-ink)}.sa-extra-num.sa-score-good{color:var(--mint-ink)}
.sa-extra-light{display:inline-flex;align-items:center;gap:8px;border-radius:9999px;padding:4px 12px;font-size:13px;font-weight:500;margin-top:12px}
.sa-extra-light i{width:10px;height:10px;border-radius:50%;background:currentColor}
.sa-extra-light.sa-score-bad{background:var(--ember-wash);color:var(--ember-ink)}.sa-extra-light.sa-score-mid{background:var(--amber-wash);color:var(--amber-ink)}.sa-extra-light.sa-score-good{background:var(--mint-wash);color:var(--mint-ink)}
.sa-extra-num small{font-size:30px;color:var(--ash);letter-spacing:-1px}
.sa-extra-no{color:var(--ember-ink);font-weight:600;white-space:nowrap}.sa-extra-yes{color:var(--mint-ink);font-weight:600;white-space:nowrap}
.sa-extra-pair{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:48px;text-align:left}
.sa-extra-card{padding:28px}
.sa-extra-lbl{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;margin:16px 0 8px}
.sa-extra-lnow{color:var(--ember-ink)}.sa-extra-lnew{color:var(--mint-ink)}
.sa-extra-serp{border:1px solid var(--fog);border-radius:12px;padding:16px;font-family:Arial,sans-serif;letter-spacing:0}
.sa-extra-serp p{font-size:12px;color:#4d5156}
.sa-extra-serp .sa-extra-site{display:flex;align-items:center;gap:8px;font-size:14px;color:#202124;margin-bottom:2px}.sa-extra-site i{width:22px;height:22px;border-radius:50%;background:#f1f3f4;border:1px solid #dadce0;display:grid;place-items:center;font-size:11px;font-style:normal;font-weight:700;color:#202124}.sa-extra-serp b{display:block;font-size:19px;font-weight:400;color:#1a0dab;margin:4px 0}
.sa-extra-serp span{font-size:13px;color:#4d5156}.sa-extra-serp .sa-extra-miss{color:var(--ember-ink);font-style:italic}
.sa-extra-wa{background:#e5ddd5;border-radius:12px;padding:16px}
.sa-extra-bubble{background:#dcf8c6;border-radius:10px;padding:6px;max-width:320px;margin-left:auto;font-family:Arial,sans-serif;letter-spacing:0;font-size:12px;color:#555}
.sa-extra-og{background:#f0f0f0;border-radius:6px;overflow:hidden}
.sa-extra-og img{width:100%;aspect-ratio:1.91/1;object-fit:cover;display:block}
.sa-extra-og div{padding:8px 10px}.sa-extra-og b{display:block;color:#111;font-size:13px}
.sa-extra-link{display:block;font-size:13px;color:#027eb5;padding:6px 4px 2px}
.sa-extra-mini{display:flex;align-items:stretch;background:#f0f0f0;border-radius:6px;overflow:hidden}
.sa-extra-mini img{width:72px;height:72px;object-fit:contain;background:#fff;flex:none}
.sa-extra-mini div{padding:8px 10px;align-self:center}.sa-extra-mini b{display:block;color:#111;font-size:13px}
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
.sa-extra-crit{list-style:none;margin-top:16px;display:grid;grid-template-columns:1fr 1fr;column-gap:24px;font-size:13px;color:var(--graphite)}
.sa-extra-crit li{display:flex;gap:8px;padding:6px 0;border-top:1px solid var(--fog)}
.sa-extra-crit li>div{color:var(--carbon);font-weight:600;font-size:14px}.sa-extra-crit small{display:block;font-size:14px;font-weight:400;color:var(--graphite);margin-top:4px}.sa-extra-crit li span{font-weight:700;width:14px;flex-shrink:0}
.sa-extra-crit .sa-score-pa span{color:var(--amber-ink)}.sa-extra-crit .sa-score-ko span{color:var(--ember-ink)}
@media(max-width:860px){.sa-extra-scorebox,.sa-extra-crit{grid-template-columns:1fr}.sa-extra-q thead{display:none}.sa-extra-q tr{display:block;border-top:1px solid var(--fog);padding:10px 0}.sa-extra-q td{display:block;border:0;padding:2px 0}}
@media(max-width:860px){.sa-extra-pair,.sa-extra-ai,.sa-extra-aeo{grid-template-columns:1fr}}
"""


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", s.lower())


def is_brand(name: str, brand: str) -> bool:
    b = _norm(brand)
    return bool(b) and b in _norm(name)


def _result(t, brand: str) -> tuple[str, str]:
    """(css class, label) for «Dónde sales tú». who_appears is in Google order, so the client's best spot is
    the first entry that is theirs, site or profile."""
    own = next(((i + 1, w) for i, w in enumerate(t.get("who_appears", [])) if is_brand(w, brand)), None)
    if not t["appears"]:
        return "sa-extra-no", "No sales"  # only the site counts; a profile alone is not "showing up"
    m = re.search(r"[Pp]uesto (\d+)", t.get("position_or_note") or "")
    site = int(m.group(1)) if m else None
    pos = min(p for p in (site, own and own[0]) if p) if (site or own) else None
    return "sa-extra-yes", f"Puesto {pos}" if pos else "Sí sales"


def _table(tests, brand: str, first_col: str) -> str:
    rows = "".join(
        f'<tr><td>«{esc(t["query"])}»</td><td class="sa-extra-first">{esc((t.get("who_appears") or ["—"])[0])}</td>'
        f'<td class="{_result(t, brand)[0]}">{esc(_result(t, brand)[1])}</td></tr>' for t in tests)
    return (f'<table class="sa-extra-q"><thead><tr><th>{first_col}</th><th>Quién sale primero</th><th>Dónde sales tú</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>')


def _score_block(seo, rubric, target: int = 80) -> str:
    """Criteria count, not the weighted score: what the client reads is exactly what is counted."""
    results = {c["id"]: c["result"] for c in seo.get("checks", [])}
    notes = {c["id"]: c.get("note_es") for c in seo.get("checks", [])}
    note = lambda cid: f"<small>{esc(notes[cid])}</small>" if notes.get(cid) else ""
    crit = [c for c in (rubric or {}).get("areas", {}).get("seo", []) if results.get(c["id"], "na") != "na"]
    if not crit:
        return ""
    ok = sum(results[c["id"]] == "pass" for c in crit)
    half = sum(results[c["id"]] == "partial" for c in crit)
    # traffic light on the same thresholds as the base score (partial = half), target from the score config
    tone = _tone(round(100 * (ok + half / 2) / len(crit)), target)
    items = "".join(
        f'<li class="{MARK[results[c["id"]]][0]}"><span>{MARK[results[c["id"]]][1]}</span><div>{esc(c["label"])}'
        f'{" (la prueba de arriba)" if c["id"] == "seo-appears" else ""}{note(c["id"])}</div></li>'
        for c in crit if results[c["id"]] in ("fail", "partial"))
    ul = f'<p class="why">Lo que te falta:</p><ul class="sa-extra-crit">{items}</ul>' if items else ""
    return (f'<div class="card sa-extra-block"><div class="eyebrow">Tu puntaje en buscadores</div><div class="sa-extra-scorebox">'
            f'<div><div class="sa-extra-num {tone}">{ok}<small> de {len(crit)}</small></div>'
            f'<p class="sa-extra-sum">criterios cumplidos{f" · {half} a medias" if half else ""}</p>'
            f'<span class="sa-extra-light {tone}"><i></i>{VERDICT[tone]}</span></div>'
            f'<div><p class="why">Revisamos {len(crit)} criterios que Google y la IA tienen en cuenta para mostrarte.</p>{ul}</div></div></div>')


def _search(seo, brand: str = "", rubric=None, target: int = 80) -> tuple[str, str]:
    tests = seo.get("search_tests", [])
    named = [t for t in tests if is_brand(t["query"], brand)]
    buyer = [t for t in tests if t not in named] or tests
    named = [t for t in named if t not in buyer]
    hits = sum(1 for t in buyer if t["appears"])
    headline = ("Buscamos lo que buscan tus compradores. No apareciste ni una vez." if hits == 0
                else f"Buscamos lo que buscan tus compradores. Apareciste en {hits} de {len(buyer)}.")
    html = ('<div class="card sa-extra-block"><h3>¿Te encuentra un comprador en Google?</h3>'
            '<p class="why">Buscamos en Google lo que escribiría un comprador que todavía no te conoce, sin sesión iniciada.</p>'
            f'<span class="sa-extra-pill{" sa-extra-ok" if hits * 2 >= len(buyer) else ""}">{hits} de {len(buyer)} búsquedas</span>'
            f'{_table(buyer, brand, "Lo que buscan los compradores")}'
            f'<p class="sa-extra-sum">Te encuentran en {hits} de {len(buyer)} búsquedas de compradores.</p>')
    if named:
        if not all(t["appears"] for t in named):
            note = "Ni buscándote por tu nombre apareces siempre."
        elif hits * 2 < len(buyer):
            note = "Quien ya te conoce te encuentra; un comprador nuevo, casi nunca."
        else:
            note = "Quien ya te conoce te encuentra."
        html += (f'<h4>Cuando te buscan por tu nombre</h4>{_table(named, brand, "Tu nombre")}'
                 f'<p class="sa-extra-sum">{note}</p>')
    html += "</div>" + _score_block(seo, rubric, target)
    return headline, html


def _previews(ctx, pres) -> str:
    today, prop = pres["serp"]["today"][0], pres["serp"]["proposed"][0]
    sp = pres["share_preview"]["proposed"]
    preview_title = pres["share_preview"].get("today_title") or today["title"]
    if today.get("meta_description"):
        desc = f'<span>{esc(today["meta_description"])}</span>'
    elif today.get("google_snippet"):
        desc = (f'<span>{esc(today["google_snippet"])}</span>'
                '<span class="sa-extra-miss">No definiste una descripción: Google toma este texto de tu página.</span>')
    else:
        desc = '<span class="sa-extra-miss">Sin descripción: Google improvisa el texto que ve el comprador.</span>'
    domain = ctx["meta"].get("domain", "")
    # Google shows the site name (with its icon) above the breadcrumb
    sn = today.get("site_name")
    site = f'<p class="sa-extra-site"><i>{esc(sn[:1].upper())}</i>{esc(sn)}</p>' if sn else ""
    serp = (f'<div class="card sa-extra-card"><h3>Así apareces en Google</h3><p class="why">Lo primero que ve un comprador nuevo.</p>'
            f'<div class="sa-extra-lbl sa-extra-lnow">Hoy</div><div class="sa-extra-serp">{site}<p>{esc(today["url"])}</p><b>{esc(today["title"])}</b>{desc}</div>'
            f'<div class="sa-extra-lbl sa-extra-lnew">Propuesta</div><div class="sa-extra-serp">{site}<p>{esc(today["url"])}</p><b>{esc(prop["title"])}</b>'
            f'<span>{esc(prop["description"])}</span></div></div>')

    def bubble(img_local, title, desc):
        img = ctx["asset"](img_local) if img_local else None
        og_img = f'<img src="{img}" alt="">' if img else ""
        return (f'<div class="sa-extra-wa"><div class="sa-extra-bubble"><div class="sa-extra-og">{og_img}'
                f'<div><b>{esc(title)}</b>{esc(desc or "")}</div></div><span class="sa-extra-link">{esc(domain or today["url"])}</span></div></div>')
    # today's real link preview (og tags read without JavaScript); plain title only when the site has no og image/description
    # collect_evidence.py saves og-today.jpg / og-today-icon.png; presence.json may name them explicitly
    th = (pres["share_preview"].get("today") or {}).get("home") or {}
    icon_name = pres["share_preview"].get("today_icon_local") or "og-today-icon.png"
    t_img = pres["share_preview"].get("today_og_image_local") or ("og-today.jpg" if ctx["asset"]("og-today.jpg") else None)
    if t_img == icon_name:  # the icon is not an og:image: WhatsApp shows it small, never as the large picture
        t_img = None
    icon = ctx["asset"](icon_name)
    t_title, t_desc = th.get("og:title") or preview_title, (th.get("og:description") or "").strip()
    if t_img:
        wa_today = bubble(t_img, t_title, t_desc)
    elif icon:
        # no og:image: WhatsApp falls back to the site icon as a small square beside the title (and description)
        wa_today = (f'<div class="sa-extra-wa"><div class="sa-extra-bubble"><div class="sa-extra-mini">'
                    f'<img src="{icon}" alt=""><div><b>{esc(t_title)}</b>{esc(t_desc)}</div></div>'
                    f'<span class="sa-extra-link">{esc(domain or today["url"])}</span></div></div>')
    elif t_desc:
        wa_today = bubble(None, t_title, t_desc)
    else:
        wa_today = (f'<div class="sa-extra-wa"><div class="sa-extra-bubble"><span class="sa-extra-link">{esc(domain or today["url"])}</span>'
                    f'{esc(preview_title)}</div></div>')
    share = (f'<div class="card sa-extra-card"><h3>Así se ve tu enlace en WhatsApp</h3><p class="why">Cada vez que compartes el sitio con un cliente.</p>'
             f'<div class="sa-extra-lbl sa-extra-lnow">Hoy</div>{wa_today}'
             f'<div class="sa-extra-lbl sa-extra-lnew">Propuesta</div>{bubble(sp.get("og_image_local"), sp["og:title"], sp["og:description"])}</div>')
    return f'<div class="sa-extra-pair">{serp}{share}</div>'


ENGINE_NAMES = {"chatgpt": "ChatGPT", "gemini": "Gemini", "perplexity": "Perplexity",
                "claude": "Claude", "copilot": "Copilot", "google": "Google",
                "google_ai_overview": "Google (visión general con IA)", "google_ai_mode": "Google (modo IA)"}


def _ai(ai, brand: str) -> str:
    def card(a):
        a = {**a, "engine": ENGINE_NAMES.get(a["engine"].strip().lower(), a["engine"])}
        res = ('<span class="sa-extra-res sa-extra-half">Te menciona</span>' if a["mentioned"]
               else '<span class="sa-extra-res">No apareces</span>')
        names = "".join(f'<span class="{"sa-extra-me" if is_brand(n, brand) else ""}">{esc(n)}</span>' for n in a["named"])
        return (f'<div class="card sa-extra-aic"><div class="sa-extra-eng"><span>{esc(a["engine"])}</span>{res}</div>'
                f'<div class="sa-extra-prompt">«{esc(a["prompt"])}»</div><div class="sa-extra-names">{names}</div><p class="why">{esc(a["note_es"])}</p></div>')
    return ('<h3 style="margin-top:56px">Le preguntamos a la IA lo que preguntaría un comprador</h3>'
            '<p class="lead" style="margin-top:8px">Respuestas reales, consultadas desde el país del cliente.</p>'
            f'<div class="sa-extra-ai">{"".join(card(a) for a in ai["answers"])}</div>'
            f'<p class="src">Fecha de la consulta: {esc(ai["date"])}. Fuente: {esc(ai["source"])}. Las respuestas de la IA cambian con el tiempo.</p>')


def enabled(ctx) -> bool:
    """Single predicate shared with the plan: the Extra exists when selected and some Extra data was produced."""
    return bool(ctx["meta"].get("options", {}).get("extra") and (ctx["seo"] or ctx["presence"]))


def build(ctx) -> Section | None:
    if not enabled(ctx):
        return None
    seo, pres, ai = ctx["seo"] or {}, ctx["presence"], ctx["ai"]
    parts = []
    if seo.get("search_tests"):
        headline, grid = _search(seo, (ctx["ai"] or {}).get("brand") or ctx["top10"]["client"], ctx.get("rubric"), (ctx["scores"] or {}).get("target", 80))
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
                     '<p class="lead" style="margin-top:8px">Los asistentes de IA recomiendan empresas que pueden entender y citar.</p>'
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
