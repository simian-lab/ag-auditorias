"""Path helpers. Plugin files resolve from this file's location; audits from the run directory."""
import json
import shutil
from pathlib import Path


def plugin_root() -> Path:
    return Path(__file__).resolve().parents[2]


def asset(*parts: str) -> Path:
    return plugin_root().joinpath("assets", *parts)


# Brand fonts (Simian visual identity manual) copied next to every generated page.
FONTS = ("SourceSans3-latin-wght.woff2", "Vollkorn-latin-wght.woff2")


def copy_fonts(assets_dir: Path) -> None:
    (assets_dir / "fonts").mkdir(parents=True, exist_ok=True)
    for name in FONTS:
        shutil.copy2(asset("fonts", name), assets_dir / "fonts" / name)


def config(name: str) -> dict:
    return json.loads(plugin_root().joinpath("config", f"{name}.json").read_text(encoding="utf-8"))


def plugin_version() -> str:
    return json.loads((plugin_root() / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]


def audits_root(base: Path | None = None) -> Path:
    return (base or Path.cwd()) / "audits"
