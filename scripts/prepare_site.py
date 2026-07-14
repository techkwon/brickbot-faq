#!/usr/bin/env python3
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"
FILES = ["index.html", "privacy.html", "404.html", "robots.txt", ".nojekyll"]
DIRS = ["assets", "data"]


def main() -> int:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for name in FILES:
        source = ROOT / name
        if source.exists():
            shutil.copy2(source, OUT / name)
    for name in DIRS:
        shutil.copytree(ROOT / name, OUT / name)
    print(f"prepared={OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
