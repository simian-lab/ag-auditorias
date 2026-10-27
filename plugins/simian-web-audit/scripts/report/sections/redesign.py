"""Before/after slider: current homepage vs the Simian redesign concept."""
from report.render import Section, esc

CSS = """
.sa-ba-slider{position:relative;max-width:1100px;margin:40px auto 0;border-radius:16px;overflow:hidden;box-shadow:0 30px 80px rgba(27,25,24,.18);aspect-ratio:16/10;user-select:none;cursor:ew-resize;background:#fff}
.sa-ba-slider img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:top;pointer-events:none}
.sa-ba-after{clip-path:inset(0 0 0 50%)}
.sa-ba-handle{position:absolute;top:0;bottom:0;left:50%;width:2px;background:#fff;box-shadow:0 0 0 1px rgba(0,0,0,.1)}
.sa-ba-handle::after{content:"⇆";position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);width:44px;height:44px;border-radius:50%;background:#fff;display:grid;place-items:center;font-size:18px;box-shadow:var(--shadow-3)}
.sa-ba-lbl{position:absolute;top:16px;z-index:2;background:var(--carbon);color:#fff;border-radius:9999px;padding:6px 12px;font-size:12px;font-weight:500}
.sa-ba-l{left:16px}.sa-ba-r{right:16px;background:var(--brand)}
.sa-ba-solves{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin-top:24px}
.sa-ba-solves b{color:var(--mint-ink)}
.sa-ba-solves span{border:1px solid var(--fog);background:#fff;border-radius:9999px;padding:6px 12px;font-size:13px}
"""

JS = """<script>(()=>{const b=document.getElementById('sa-ba');if(!b)return;const a=b.querySelector('.sa-ba-after'),h=b.querySelector('.sa-ba-handle');let d=false;
const set=x=>{const r=b.getBoundingClientRect();const p=Math.max(0,Math.min(100,(x-r.left)/r.width*100));a.style.clipPath=`inset(0 0 0 ${p}%)`;h.style.left=p+'%'};
b.addEventListener('pointerdown',e=>{d=true;b.setPointerCapture(e.pointerId);set(e.clientX)});b.addEventListener('pointermove',e=>d&&set(e.clientX));b.addEventListener('pointerup',()=>d=false);})();</script>"""


def redesign_image(ctx) -> str | None:
    for name in ("redesign-desktop.jpg", "redesign-desktop.png"):
        if (ctx["assets_dir"] / name).exists():
            return f"assets/{name}"
    return None


def build(ctx) -> Section | None:
    after = redesign_image(ctx)
    before = ctx["asset"]("desktop-viewport.png")
    if not after or not before:
        return None
    by_n = {i["n"]: i for i in ctx["top10"]["items"]}
    solved = sorted(n for n in (ctx.get("redesign") or {}).get("solves", []) if n in by_n)
    solves = ('<div class="sa-ba-solves">' + "".join(f'<span><b>#{n}</b> {esc(by_n[n]["t_plain"])}</span>' for n in solved) + "</div>"
              if solved else "")
    full = ('<p style="margin-top:24px"><a class="btn btn-ghost" href="assets/redesign/index.html" target="_blank">Ver el concepto completo →</a></p>'
            if (ctx["assets_dir"] / "redesign" / "index.html").exists() else "")
    html = f"""<section class="band" id="propuesta">
  <div class="wrap center">
    <div class="eyebrow">Concepto Simian</div>
    <h2>Así podría verse tu sitio.</h2>
    <p class="lead" style="margin-top:12px">Tu marca, tus fotos reales y los problemas del Top resueltos. Desliza para comparar.</p>
    <div class="sa-ba-slider" id="sa-ba">
      <img src="{before}" alt="Sitio actual"><img class="sa-ba-after" src="{after}" alt="Concepto de rediseño">
      <span class="sa-ba-lbl sa-ba-l">Hoy</span><span class="sa-ba-lbl sa-ba-r">Propuesta</span><div class="sa-ba-handle"></div>
    </div>
    {solves}
    {full}
    <p class="src">Concepto ilustrativo. Los datos entre [corchetes] están por confirmar con ustedes.</p>
  </div>
</section>{JS}"""
    return Section("propuesta", "Propuesta", html, CSS)
