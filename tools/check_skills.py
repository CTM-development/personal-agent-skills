#!/usr/bin/env python3
"""Check every skill in skills/ against the Agent Skills spec, plus Claude-specific limits.

[general] Spec rules (agentskills.io/specification): name, description, compatibility,
          metadata, name == folder, SKILL.md length, relative file references.
[claude]  claude.ai upload limit: description <= 200 characters (spec allows 1024).
          Use --profile spec to skip the Claude-specific checks.

Standard library only. If the official validator `skills-ref` is on PATH, it runs too.

Usage: python3 tools/check_skills.py [--profile all|spec] [skill-name ...]
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SPEC_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def parse_frontmatter(text):
    """Parse the small YAML subset SKILL.md frontmatter uses: scalars and one-level maps."""
    if not text.startswith("---\n"):
        raise ValueError("SKILL.md must start with '---' frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError("frontmatter is not closed with '---'")
    block, body = text[4:end], text[end + 4:].lstrip("\n")
    data, current = {}, None
    for raw in block.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith((" ", "\t")):
            if current is None or not isinstance(data.get(current), dict):
                raise ValueError(f"unexpected indented line: {raw.strip()}")
            key, _, val = raw.strip().partition(":")
            data[current][key.strip()] = unquote(val.strip())
            continue
        key, sep, val = raw.partition(":")
        if not sep:
            raise ValueError(f"cannot parse line: {raw}")
        key, val = key.strip(), val.strip()
        if val in ("", "|", ">"):
            data[key], current = ({} if val == "" else ""), key
        else:
            data[key], current = unquote(val), key
    return data, body


def unquote(v):
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def check_skill(d, profile):
    errors, warnings = [], []
    md = d / "SKILL.md"
    if not md.is_file():
        return [f"{d.name}: missing SKILL.md"], []
    try:
        fm, body = parse_frontmatter(md.read_text(encoding="utf-8"))
    except ValueError as e:
        return [f"{d.name}: {e}"], []

    name, desc = fm.get("name", ""), fm.get("description", "")
    # [general] spec rules
    if not (1 <= len(name) <= 64 and NAME_RE.match(name)):
        errors.append("name must be 1-64 chars: lowercase letters, digits, single hyphens [spec]")
    if name != d.name:
        errors.append(f"name '{name}' must match folder '{d.name}' [spec]")
    if not (1 <= len(desc) <= 1024):
        errors.append(f"description must be 1-1024 chars, has {len(desc)} [spec]")
    comp = fm.get("compatibility")
    if comp is not None and not (1 <= len(comp) <= 500):
        errors.append(f"compatibility must be 1-500 chars, has {len(comp)} [spec]")
    meta = fm.get("metadata")
    if meta is not None and not isinstance(meta, dict):
        errors.append("metadata must be a map of string keys to string values [spec]")
    for key in fm:
        if key not in SPEC_KEYS:
            warnings.append(f"frontmatter key '{key}' is not in the spec; other harnesses may ignore it")
    lines = body.count("\n") + 1
    if lines > 500:
        warnings.append(f"SKILL.md body has {lines} lines; spec recommends under 500")
    visible = re.sub(r"<!--.*?-->", "", body, flags=re.S)
    for ref in sorted(set(re.findall(r"\]\(((?:references|scripts|assets)/[^)\s#]+)", visible))):
        if not (d / ref).exists():
            errors.append(f"referenced file does not exist: {ref}")

    # [claude] claude.ai upload limit
    if profile == "all" and len(desc) > 200:
        errors.append(f"description has {len(desc)} chars; claude.ai uploads allow 200 [claude]")
    return [f"{d.name}: {m}" for m in errors], [f"{d.name}: {m}" for m in warnings]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--profile", choices=["all", "spec"], default="all",
                    help="all = spec + Claude limits (default); spec = open standard only")
    ap.add_argument("skills", nargs="*", help="skill folder names (default: all)")
    args = ap.parse_args()

    dirs = [SKILLS / s for s in args.skills] if args.skills else sorted(p for p in SKILLS.iterdir() if p.is_dir())
    errors, warnings = [], []
    for d in dirs:
        e, w = check_skill(d, args.profile)
        errors += e
        warnings += w
        print(f"{'FAIL' if e else 'ok  '} {d.name}")

    if shutil.which("skills-ref"):
        for d in dirs:
            r = subprocess.run(["skills-ref", "validate", str(d)], capture_output=True, text=True)
            if r.returncode != 0:
                errors.append(f"{d.name}: skills-ref: {(r.stdout + r.stderr).strip()}")
    else:
        print("note: skills-ref not on PATH; ran the built-in spec checks only")

    for w in warnings:
        print("warning:", w)
    for e in errors:
        print("error:  ", e)
    print(f"{len(dirs)} skill(s), {len(errors)} error(s), {len(warnings)} warning(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
