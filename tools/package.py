#!/usr/bin/env python3
"""Build dist/<skill>.zip for every skill, with the skill folder as the ZIP's top level.

[claude]  This is the format claude.ai expects for Customize > Skills > Upload a skill.
[general] The same ZIP works for sharing a skill by hand with any Agent Skills harness.

Usage: python3 tools/package.py [skill-name ...]
"""
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS, DIST = ROOT / "skills", ROOT / "dist"
SKIP = {".DS_Store", "__pycache__", ".pytest_cache"}


def package(d):
    DIST.mkdir(exist_ok=True)
    out = DIST / f"{d.name}.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(d.rglob("*")):
            if f.is_file() and not SKIP.intersection(f.relative_to(d).parts):
                z.write(f, Path(d.name) / f.relative_to(d))
    return out


def main():
    names = sys.argv[1:]
    dirs = [SKILLS / n for n in names] if names else sorted(p for p in SKILLS.iterdir() if p.is_dir())
    for d in dirs:
        if not (d / "SKILL.md").is_file():
            sys.exit(f"{d.name}: no SKILL.md, not packaging")
        print("built", package(d).relative_to(ROOT))


if __name__ == "__main__":
    main()
