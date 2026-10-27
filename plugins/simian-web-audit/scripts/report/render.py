"""Page assembly: escaping, the Section contract, and the final HTML document."""
import html
from collections import namedtuple
from pathlib import Path

# Shared classes defined in base.css; every other class must be prefixed `sa-<section>-`.
BASE_CLASSES = {
    "wrap", "band", "eyebrow", "lead", "chip", "card", "btn", "btn-primary", "btn-ghost",
    "src", "why", "cap", "explain", "center",
}

# id: anchor id; nav_label: dock label or None; html/css: section markup and its prefixed styles
Section = namedtuple("Section", "id nav_label html css")

BASE_CSS = Path(__file__).with_name("base.css")


def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def _dock(sections: list[Section]) -> str:
    links = "".join(f'<a href="#{esc(s.id)}">{esc(s.nav_label)}</a>' for s in sections if s.nav_label)
    return f'<nav class="sa-dock">{links}</nav>' if links else ""


DOCK_CSS = """
.sa-dock{position:fixed;left:50%;bottom:20px;transform:translateX(-50%);z-index:40;background:var(--carbon);border-radius:9999px;padding:6px;display:flex;gap:2px;box-shadow:0 10px 30px rgba(0,0,0,.25)}
.sa-dock a{color:#bbb;text-decoration:none;font-size:13px;font-weight:500;padding:8px 14px;border-radius:9999px;white-space:nowrap}
.sa-dock a:hover{color:#fff;background:rgba(255,255,255,.08)}
@media(max-width:860px){.sa-dock{display:none}}
"""


def page(sections: list[Section], title: str) -> str:
    css = BASE_CSS.read_text(encoding="utf-8") + DOCK_CSS + "".join(s.css for s in sections)
    body = "\n".join(s.html for s in sections)
    return (
        "<!DOCTYPE html>\n<html lang=\"es\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{esc(title)}</title>\n<style>{css}</style>\n</head>\n<body>\n{body}\n{_dock(sections)}\n</body>\n</html>\n"
    )
