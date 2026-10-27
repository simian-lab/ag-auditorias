"""Image helpers backed by macOS `sips`."""
import subprocess
from pathlib import Path


def to_jpeg(src: Path, dst: Path, quality: int = 72, max_px: int | None = None, run=subprocess.run) -> Path:
    argv = ["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(quality)]
    if max_px:
        argv += ["-Z", str(max_px)]
    argv += [str(src), "--out", str(dst)]
    run(argv, check=True, capture_output=True)
    return dst


def crop(src: Path, dst: Path, x: int, y: int, w: int, h: int, run=subprocess.run) -> Path:
    run(["sips", "-c", str(h), str(w), "--cropOffset", str(y), str(x), str(src), "--out", str(dst)],
        check=True, capture_output=True)
    return dst
