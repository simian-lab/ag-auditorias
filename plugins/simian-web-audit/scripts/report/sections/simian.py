"""Why Simian: portfolio cases chosen by matching their tags to the Top problems."""
from report.render import Section, esc

AREA_TAGS = {"ux": {"ux"}, "a11y": {"accessibility"}, "tec": {"performance", "security", "wordpress"}, "vis": {"design-system"}}
KEYWORD_TAGS = [(("whatsapp", "cotiz", "venta"), {"whatsapp", "quote-cta"}), (("formulario",), {"forms"}),
                (("celular", "móvil"), {"mobile"}), (("seguridad", "cerradura"), {"security"})]

CSS = """
.sa-sim-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:40px}
.sa-sim-card{overflow:hidden;text-decoration:none;color:inherit}
.sa-sim-card img{width:100%;aspect-ratio:16/10;object-fit:cover;display:block}
.sa-sim-bd{padding:24px}
.sa-sim-rel{font-size:12px;color:var(--brand);font-weight:600;margin-bottom:8px}
.sa-sim-card ul{list-style:none;margin-top:12px;font-size:14px;color:var(--graphite)}
.sa-sim-card li{padding:6px 0;border-top:1px solid var(--fog)}
@media(max-width:860px){.sa-sim-grid{grid-template-columns:1fr}}
"""


def _keyword_tags(item: dict) -> set[str]:
    text = f'{item.get("t", "")} {item.get("t_plain", "")}'.lower()
    tags: set[str] = set()
    for words, kw_tags in KEYWORD_TAGS:
        if any(w in text for w in words):
            tags |= kw_tags
    return tags


def _item_tags(item: dict) -> set[str]:
    return set(AREA_TAGS.get(item["c"], set())) | _keyword_tags(item)


def _weight(item: dict, matches: set[str]) -> int:
    # rank-weighted; a specific keyword match counts double over a generic area match
    if not _item_tags(item) & matches:
        return 0
    return (11 - item["n"]) * (2 if _keyword_tags(item) & matches else 1)


def pick_cases(cases: list[dict], top10_items: list[dict], k: int = 3) -> list[tuple[dict, list[int]]]:
    scored = []
    for order, case in enumerate(cases):
        matches = set(case.get("matches", []))
        related = [i["n"] for i in top10_items if _item_tags(i) & matches]
        weight = sum(_weight(i, matches) for i in top10_items)
        if related:
            scored.append((-weight, order, case, related))
    scored.sort(key=lambda s: (s[0], s[1]))
    return [(case, related) for _, _, case, related in scored[:k]]


def build(ctx) -> Section | None:
    picked = pick_cases(ctx["cases"], ctx["top10"]["items"])
    if not picked:
        return None
    cards = []
    for case, related in picked:
        img = ctx["plugin_asset"]("simian", "img", case["image"]) if case.get("image") else None
        rel = "Relacionado con " + ", ".join(f"#{n}" for n in related)
        results = "".join(f"<li>{esc(r)}</li>" for r in case.get("results", []))
        cards.append(f'<a class="card sa-sim-card" href="{esc(case["url"])}" target="_blank">'
                     f'{f"<img src={chr(34)}{img}{chr(34)} alt={chr(34)}{chr(34)}>" if img else ""}'
                     f'<div class="sa-sim-bd"><div class="sa-sim-rel">{rel}</div><div class="eyebrow">{esc(case["client"])}</div>'
                     f'<h3 style="margin-top:6px">{esc(case["headline"])}</h3><ul>{results}</ul></div></a>')
    html = f"""<section class="band" id="simian">
  <div class="wrap">
    <div class="eyebrow">Por qué Simian</div>
    <h2>Ya resolvimos estos mismos problemas para otras empresas.</h2>
    <div class="sa-sim-grid">{''.join(cards)}</div>
  </div>
</section>"""
    return Section("simian", "Simian", html, CSS)
