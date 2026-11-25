#!/usr/bin/env python3
"""Create skills/<name>/ from templates/skill-template.  [general]

Usage: python3 tools/new_skill.py <name>   (lowercase letters, digits, single hyphens)
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

if len(sys.argv) != 2 or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", sys.argv[1]) or len(sys.argv[1]) > 64:
    sys.exit(__doc__)
name = sys.argv[1]
dest = ROOT / "skills" / name
if dest.exists():
    sys.exit(f"skills/{name} already exists")
shutil.copytree(ROOT / "templates" / "skill-template", dest)
md = dest / "SKILL.md"
md.write_text(md.read_text().replace("TEMPLATE-NAME", name))
print(f"created skills/{name}/SKILL.md; edit it, then run python3 tools/check_skills.py {name}")
