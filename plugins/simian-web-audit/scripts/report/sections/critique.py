"""Design critique: verdict, inventory cards with real crops, proposed palette."""
from report.render import Section, esc

CSS = """
.sa-crit-verdict{font-size:28px;line-height:1.3;letter-spacing:-.6px;font-weight:500;max-width:900px;margin:16px 0 48px}
.sa-crit-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.sa-crit-card{padding:28px}
.sa-crit-crops{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin:20px 0;padding:20px;background:var(--linen);border-radius:12px;min-height:110px}
.sa-crit-crops img{max-height:56px;max-width:100%;border-radius:6px;background:#fff}
.sa-crit-sw{width:44px;height:44px;border-radius:8px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.08)}
.sa-crit-font{font-size:22px;font-weight:600;padding:6px 12px;background:#fff;border-radius:8px}
.sa-crit-font small{font:12px Inter,sans-serif;color:var(--ash)}
.sa-crit-prop{display:flex;gap:10px;font-size:14px;color:var(--graphite);border-top:1px solid var(--fog);padding-top:14px}
.sa-crit-prop b{color:var(--mint-ink);white-space:nowrap}
.sa-crit-pal{display:flex;gap:8px;margin-top:24px;flex-wrap:wrap}
.sa-crit-pal div{flex:1;min-width:140px;border:1px solid var(--fog);border-radius:12px;overflow:hidden;font-size:13px}
.sa-crit-pal i{display:block;height:64px}
.sa-crit-pal p{padding:10px 12px}.sa-crit-pal b{display:block}
@media(max-width:860px){.sa-crit-grid{grid-template-columns:1fr}.sa-crit-verdict{font-size:22px}}
"""


def _crops(ctx, group) -> str:
    out = []
    for it in group.get("items", []):
        if it.get("crop"):
            src = ctx["asset"](it["crop"].split("/")[-1])
            if src:
                out.append(f'<img src="{src}" alt="{esc(it["label"])}">')
        elif it.get("hex"):
            out.append(f'<span class="sa-crit-sw" title="{esc(it["hex"])}" style="background:{esc(it["hex"])}"></span>')
        elif it.get("family"):
            out.append(f'<span class="sa-crit-font" style="font-family:{esc(it["family"])},sans-serif">Aa <small>{esc(it["label"])}</small></span>')
    return "".join(out)


def build(ctx) -> Section | None:
    ui = ctx["ui"]
    if not ui:
        return None
    cards = "".join(
        f'<div class="card sa-crit-card"><h3>{esc(g["title"])}</h3><p class="why" style="margin-top:8px">{esc(g["explanation"])}</p>'
        f'<div class="sa-crit-crops">{_crops(ctx, g)}</div>'
        f'<div class="sa-crit-prop"><b>Lo que proponemos →</b><span>{esc(g["proposal"])}</span></div></div>'
        for g in ui["inventory"][:4])
    pal = "".join(f'<div><i style="background:{esc(c["hex"])}"></i><p><b>{esc(c["name"])} · {esc(c["hex"])}</b>{esc(c["role"].split(".")[0])}</p></div>'
                  for c in ui["proposed_system"]["colors"])
    html = f"""<section class="band" id="critica">
  <div class="wrap">
    <div class="eyebrow">Mirada de diseño</div>
    <p class="sa-crit-verdict">“{esc(ui['verdict'])}”</p>
    <div class="sa-crit-grid">{cards}</div>
    <div class="card sa-crit-card" style="margin-top:16px"><h3>Un sistema simple para que todo hable igual</h3>
      <p class="why">Pocos colores, cada uno con un trabajo fijo. Así cada página se ve de la misma empresa.</p><div class="sa-crit-pal">{pal}</div></div>
  </div>
</section>"""
    return Section("critica", "Diseño", html, CSS)
