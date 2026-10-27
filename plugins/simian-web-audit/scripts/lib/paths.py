"""Path helpers. Plugin files resolve from this file's location; audits from the run directory."""
import json
from pathlib import Path


def plugin_root() -> Path:
    return Path(__file__).resolve().parents[2]


def asset(*parts: str) -> Path:
    return plugin_root().joinpath("assets", *parts)


def config(name: str) -> dict:
    return json.loads(plugin_root().joinpath("config", f"{name}.json").read_text(encoding="utf-8"))


def plugin_version() -> str:
    return json.loads((plugin_root() / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]


def audits_root(base: Path | None = None) -> Path:
    return (base or Path.cwd()) / "audits"
