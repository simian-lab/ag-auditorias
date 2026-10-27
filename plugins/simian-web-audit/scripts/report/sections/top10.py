"""Top N: expandable rows with sharp headline, impact, effort, real screenshot crop, today vs proposal."""
from report.render import Section, esc

AREA = {"ux": "Experiencia de usuario", "a11y": "Accesibilidad", "vis": "Visual", "tec": "Técnico"}
FILTER = {"ux": "Uso", "a11y": "Accesibilidad", "vis": "Visual", "tec": "Técnico"}

CSS = """
.sa-top-head{display:flex;justify-content:space-between;align-items:end;gap:24px;margin-bottom:32px;flex-wrap:wrap}
.sa-top-filters{display:flex;gap:4px;background:var(--mist);padding:4px;border-radius:9999px;flex-wrap:wrap}
.sa-top-filters button{border:0;background:transparent;border-radius:9999px;padding:8px 14px;font:500 14px Inter,sans-serif;color:var(--graphite);cursor:pointer}
.sa-top-filters button.sa-top-on{background:#fff;color:var(--carbon);box-shadow:var(--shadow-1)}
.sa-top-item{margin-bottom:12px;overflow:hidden}
.sa-top-row{display:grid;grid-template-columns:56px 1fr 160px 90px 24px;gap:20px;align-items:center;padding:20px 24px;cursor:pointer}
.sa-top-rank{font-size:32px;font-weight:600;color:var(--ash);letter-spacing:-1px}
.sa-top-t{font-weight:600;font-size:18px}.sa-top-s{font-size:14px;color:var(--graphite)}
.sa-top-tag{display:inline-block;border-radius:9999px;padding:2px 10px;font-size:12px;font-weight:500}
.sa-top-ux{background:var(--amber-wash);color:var(--amber-ink)}.sa-top-a11y{background:#e8f0ff;color:var(--sky)}
.sa-top-vis{background:#fbe6f3;color:#a8307c}.sa-top-tec{background:#efeeff;color:#5f59d6}
.sa-top-imp{display:flex;gap:3px}.sa-top-imp i{width:14px;height:22px;border-radius:3px;background:var(--fog)}.sa-top-imp i.sa-top-full{background:var(--carbon)}
.sa-top-mini{font-size:11px;color:var(--ash);margin-top:4px}
.sa-top-chev{color:var(--ash);transition:transform .2s}.sa-top-open .sa-top-chev{transform:rotate(180deg)}
.sa-top-detail{display:none;border-top:1px solid var(--fog);padding:32px 24px;gap:32px;grid-template-columns:1.2fr 1fr}
.sa-top-open .sa-top-detail{display:grid}
.sa-top-shot{position:relative;border-radius:8px;overflow:hidden;border:1px solid var(--fog);aspect-ratio:16/10;background:#fff no-repeat}
.sa-top-pin{position:absolute;width:28px;height:28px;border-radius:50%;background:var(--ember);color:#fff;font-size:13px;font-weight:600;display:grid;place-items:center;box-shadow:0 0 0 6px rgba(255,62,0,.18)}
.sa-top-checks{display:grid;gap:8px}
.sa-top-checks div{display:flex;justify-content:space-between;padding:12px 16px;border:1px solid var(--fog);border-radius:12px;font-size:14px}
.sa-top-ok{color:var(--mint-ink);font-weight:600}.sa-top-no{color:var(--ember-ink);font-weight:600}
.sa-top-ba{display:grid;gap:12px}
.sa-top-box{padding:16px;border-radius:12px}.sa-top-now{background:var(--ember-wash)}.sa-top-fix{background:var(--mint-wash)}
.sa-top-k{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;margin-bottom:4px}
.sa-top-now .sa-top-k{color:var(--ember-ink)}.sa-top-fix .sa-top-k{color:var(--mint-ink)}
@media(max-width:860px){.sa-top-row{grid-template-columns:40px 1fr 24px}.sa-top-hm{display:none}.sa-top-detail{grid-template-columns:1fr}}
"""

JS = """<script>(()=>{const root=document.getElementById('top');if(!root)return;
root.querySelectorAll('.sa-top-row').forEach(r=>r.addEventListener('click',()=>{r.parentElement.classList.toggle('sa-top-open');place();}));
const f=root.querySelector('.sa-top-filters');if(f)f.addEventListener('click',e=>{const v=e.target.dataset.f;if(!v)return;
f.querySelectorAll('button').forEach(b=>b.classList.toggle('sa-top-on',b===e.target));
root.querySelectorAll('.sa-top-item').forEach(it=>it.style.display=(v==='all'||it.dataset.c===v)?'':'none');});
const sizes={};function place(){root.querySelectorAll('.sa-top-shot').forEach(el=>{const src=el.dataset.src,W=el.clientWidth,H=el.clientHeight;if(!W)return;
const go=r=>{const phone=el.dataset.phone==='1',scale=phone?2.2:1,w=W*scale,h=W*r*scale,px=el.dataset.x/100*w,py=el.dataset.y/100*h;
const ox=Math.max(0,Math.min(w-W,px-W/2)),oy=Math.max(0,Math.min(h-H,py-H/2));el.style.backgroundImage=`url(${src})`;
el.style.backgroundSize=`${w}px auto`;el.style.backgroundPosition=`${-ox}px ${-oy}px`;const p=el.querySelector('.sa-top-pin');p.style.left=(px-ox-14)+'px';p.style.top=(py-oy-14)+'px';};
if(sizes[src])return go(sizes[src]);const im=new Image();im.onload=()=>{sizes[src]=im.naturalHeight/im.naturalWidth;go(sizes[src]);};im.src=src;});}
window.addEventListener('resize',place);place();})();</script>"""


def _visual(ctx, it) -> str:
    if it.get("checks"):
        rows = "".join(f'<div><span>{esc(c[0])}</span><span class="{"sa-top-ok" if c[1] == "ok" else "sa-top-no"}">'
                       f'{"✓ Sí" if c[1] == "ok" else "✕ No"}</span></div>' for c in it["checks"])
        return f'<div class="sa-top-checks">{rows}</div><div class="cap">Revisión técnica del sitio</div>'
    shot = it.get("shot")
    src = ctx["asset"](shot["img"]) if shot else None
    if not src:
        return ""
    phone = "1" if shot["img"].startswith("mobile") else "0"
    return (f'<div class="sa-top-shot" data-src="{src}" data-x="{shot["x"]}" data-y="{shot["y"]}" data-phone="{phone}">'
            f'<div class="sa-top-pin">{it["n"]}</div></div><div class="cap">Captura real del sitio · el número marca dónde está el problema</div>')


def _item(ctx, it, first: bool) -> str:
    imp = "".join(f'<i class="{"sa-top-full" if k < it["imp"] else ""}"></i>' for k in range(5))
    return f"""<div class="card sa-top-item{' sa-top-open' if first else ''}" data-c="{esc(it['c'])}">
  <div class="sa-top-row"><div class="sa-top-rank">{it['n']:02d}</div>
    <div><span class="sa-top-tag sa-top-{esc(it['c'])}">{esc(AREA[it['c']])}</span><div class="sa-top-t">{esc(it['t'])}</div><div class="sa-top-s">{esc(it['s'])}</div></div>
    <div class="sa-top-hm"><div class="sa-top-imp">{imp}</div><div class="sa-top-mini">Impacto en el negocio</div></div>
    <div class="sa-top-hm"><div style="font-weight:600">{esc(it['eff'])}</div><div class="sa-top-mini">Esfuerzo</div></div>
    <svg class="sa-top-chev" width="20" height="20" viewBox="0 0 20 20"><path d="M5 8l5 5 5-5" fill="none" stroke="currentColor" stroke-width="1.8"/></svg></div>
  <div class="sa-top-detail"><div>{_visual(ctx, it)}</div>
    <div class="sa-top-ba"><div class="sa-top-box sa-top-now"><div class="sa-top-k">Hoy</div>{esc(it['now'])}</div>
      <div class="sa-top-box sa-top-fix"><div class="sa-top-k">Propuesta</div>{esc(it['fix'])}</div>
      <p class="why"><b style="color:var(--carbon)">Por qué importa:</b> {esc(it['why'])}</p></div></div>
</div>"""


def build(ctx) -> Section | None:
    items = ctx["top10"]["items"]
    if not items:
        return None
    n = len(items)
    cats = [c for c in FILTER if any(i["c"] == c for i in items)]
    filters = '<button class="sa-top-on" data-f="all">Todos</button>' + "".join(
        f'<button data-f="{c}">{FILTER[c]}</button>' for c in cats)
    rows = "".join(_item(ctx, it, i == 0) for i, it in enumerate(items))
    html = f"""<section id="top">
  <div class="wrap">
    <div class="sa-top-head"><div><div class="eyebrow">Top {n}</div><h2>Lo que arreglaríamos primero</h2>
      <p class="lead" style="margin-top:8px">Ordenado por impacto en el negocio. Toca cada punto para ver el detalle.</p></div>
      <div class="sa-top-filters">{filters}</div></div>
    {rows}
  </div>
</section>{JS}"""
    return Section("top", f"Top {n}", html, CSS)
