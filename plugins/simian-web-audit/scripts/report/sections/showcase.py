"""Painted band with notch tabs and a browser frame: current site, detected errors (pins), mobile."""
from report.render import Section, esc

CSS = """
.sa-show{position:relative;padding:0 0 96px;overflow:hidden;
  background:radial-gradient(60% 50% at 15% 30%,rgba(88,178,155,.7),transparent 70%),radial-gradient(50% 60% at 85% 25%,rgba(244,223,151,.5),transparent 70%),
  radial-gradient(70% 40% at 50% 95%,rgba(70,43,13,.45),transparent 70%),radial-gradient(40% 40% at 70% 70%,rgba(11,120,93,.8),transparent 70%),linear-gradient(180deg,#0b785d,#0a6a53 60%,#08503f)}
.sa-show-notch{position:relative;z-index:2;margin:0 auto;width:max-content;max-width:100%;background:#fff;padding:14px 24px 18px;border-radius:0 0 32px 32px;display:flex;gap:4px}
.sa-show-notch::before,.sa-show-notch::after{content:"";position:absolute;top:0;width:32px;height:32px}
.sa-show-notch::before{left:-32px;background:radial-gradient(circle at 0 100%,transparent 31.5px,#fff 32px)}
.sa-show-notch::after{right:-32px;background:radial-gradient(circle at 100% 100%,transparent 31.5px,#fff 32px)}
.sa-show-notch button{border:0;background:transparent;border-radius:9999px;padding:8px 16px;font:600 16px var(--font-body);color:var(--ash);cursor:pointer}
.sa-show-notch button.sa-show-on{background:var(--mist);color:var(--carbon)}
.sa-show-browser{position:relative;z-index:2;max-width:980px;margin:56px auto 0;background:#fff;border-radius:16px;box-shadow:0 30px 80px rgba(27,25,24,.3);overflow:hidden}
.sa-show-bar{display:flex;align-items:center;gap:12px;padding:12px 16px;border-bottom:1px solid var(--fog);background:var(--linen)}
.sa-show-lights{display:flex;gap:6px}.sa-show-lights i{width:11px;height:11px;border-radius:50%;background:var(--fog)}
.sa-show-url{flex:1;max-width:420px;margin:0 auto;background:#fff;border:1px solid var(--fog);border-radius:9999px;padding:5px 14px;font-size:13px;color:var(--graphite)}
.sa-show-vp{position:relative;aspect-ratio:16/10;background:#fff}
.sa-show-view{position:absolute;inset:0;transition:opacity .4s}
.sa-show-view img{width:100%;height:100%;object-fit:cover;object-position:top;display:block}
.sa-show-hidden{opacity:0;pointer-events:none}
.sa-show-phone{display:grid;place-items:center;background:var(--linen)}
.sa-show-phone div{height:92%;aspect-ratio:9/19;border-radius:28px;border:8px solid var(--carbon);overflow:hidden;background:#fff}
.sa-show-phone img{width:100%;height:auto}
.sa-show-shade{position:absolute;inset:0;background:rgba(27,25,24,.28);opacity:0;transition:opacity .3s;pointer-events:none;z-index:2}
.sa-show-pins .sa-show-shade{opacity:1}
.sa-show-hot{position:absolute;z-index:3;opacity:0;transform:scale(.6);transition:opacity .3s,transform .3s;pointer-events:none}
.sa-show-pins .sa-show-hot{opacity:1;transform:scale(1);pointer-events:auto}
.sa-show-dot{width:30px;height:30px;border-radius:50%;background:var(--ember);color:#fff;font-weight:600;font-size:13px;display:grid;place-items:center;box-shadow:0 0 0 7px rgba(255,62,0,.2);cursor:pointer}
.sa-show-tip{position:absolute;left:40px;top:-4px;width:220px;background:var(--carbon);color:#fff;font-size:12.5px;line-height:1.4;padding:10px 12px;border-radius:10px;opacity:0;pointer-events:none;transition:opacity .2s}
.sa-show-hot:hover .sa-show-tip{opacity:1}
.sa-show-tip b{display:block;font-size:13px;margin-bottom:2px}
.sa-show-cap{position:relative;z-index:2;text-align:center;color:#fff;margin-top:20px;font-size:14px}
@media(max-width:860px){.sa-show-browser{margin:32px 16px 0}.sa-show-notch button{padding:6px 10px;font-size:13px}}
"""

JS = """<script>(()=>{const caps={now:'Así ve tu sitio un visitante que llega hoy desde Google.',pins:'Pasa el cursor sobre cada punto rojo para ver el problema.',mobile:'Así se ve hoy en un celular.'};
const n=document.getElementById('sa-show-notch');if(!n)return;n.addEventListener('click',e=>{const v=e.target.dataset.v;if(!v)return;
n.querySelectorAll('button').forEach(b=>b.classList.toggle('sa-show-on',b===e.target));
const vp=document.getElementById('sa-show-vp');vp.classList.toggle('sa-show-pins',v==='pins');
const d=document.getElementById('sa-show-desk'),m=document.getElementById('sa-show-mob');d.classList.toggle('sa-show-hidden',v==='mobile');if(m)m.classList.toggle('sa-show-hidden',v!=='mobile');
document.getElementById('sa-show-cap').textContent=caps[v];});})();</script>"""


def _pins(ctx) -> str:
    by_id = {f["id"]: f for area in ctx["areas"].values() for f in area.get("findings", [])}
    out = []
    for it in ctx["top10"]["items"]:
        pin = next((by_id[s]["pin"] for s in it.get("src", []) if s in by_id and by_id[s].get("pin")
                    and by_id[s]["pin"]["screenshot"] == "desktop-viewport.png"), None)
        if not pin:
            continue
        x, y = min(max(pin["x_pct"], 2), 92), min(max(pin["y_pct"], 2), 92)
        out.append(f'<div class="sa-show-hot" style="left:{x}%;top:{y}%"><div class="sa-show-dot">{it["n"]}</div>'
                   f'<div class="sa-show-tip"><b>{esc(it["t_plain"])}</b>{esc(it["s"])}</div></div>')
    return "".join(out)


def build(ctx) -> Section | None:
    desk = ctx["asset"]("desktop-viewport.png")
    if not desk:
        return None
    mob = ctx["asset"]("mobile-fullpage.jpg")
    mobile_tab = '<button data-v="mobile">En celular</button>' if mob else ""
    mobile_view = (f'<div class="sa-show-view sa-show-phone sa-show-hidden" id="sa-show-mob"><div><img src="{mob}" alt="Captura actual en celular"></div></div>'
                   if mob else "")
    html = f"""<section class="sa-show" id="tu-sitio">
  <div class="sa-show-notch" id="sa-show-notch">
    <button class="sa-show-on" data-v="now">Tu sitio hoy</button>
    <button data-v="pins">Errores detectados</button>
    {mobile_tab}
  </div>
  <div class="sa-show-browser">
    <div class="sa-show-bar"><div class="sa-show-lights"><i></i><i></i><i></i></div><div class="sa-show-url">{esc(ctx['top10']['domain'])}</div><div style="width:45px"></div></div>
    <div class="sa-show-vp" id="sa-show-vp">
      <div class="sa-show-view" id="sa-show-desk"><img src="{desk}" alt="Captura actual de la página de inicio"></div>
      {mobile_view}
      <div class="sa-show-shade"></div>
      {_pins(ctx)}
    </div>
  </div>
  <p class="sa-show-cap" id="sa-show-cap">Así ve tu sitio un visitante que llega hoy desde Google.</p>
</section>{JS}"""
    return Section("tu-sitio", "Tu sitio", html, CSS)
