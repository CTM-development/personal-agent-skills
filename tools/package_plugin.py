#!/usr/bin/env python3
"""Build dist/<skill>-chatgpt-plugin.zip for the ChatGPT plugin uploader."""

import argparse
import json
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

from check_skills import NAME_RE, parse_frontmatter
from package import DIST, ROOT, SKILLS, write_skill

RELEASE_VERSION = re.compile(r"(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){0,2}")


def plugin_manifest(directory):
    frontmatter, _ = parse_frontmatter((directory / "SKILL.md").read_text(encoding="utf-8"))
    name = frontmatter.get("name", "")
    if not isinstance(name, str) or name != directory.name or len(name) > 64 or not NAME_RE.fullmatch(name):
        raise ValueError("skill name must match its lowercase, hyphenated folder name")
    description = frontmatter.get("description", "")
    if not isinstance(description, str) or not description.strip():
        raise ValueError("skill description is required")
    metadata = frontmatter.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a map")
    version = metadata.get("version", "0.1.0")
    if not isinstance(version, str) or not RELEASE_VERSION.fullmatch(version):
        raise ValueError("metadata.version must use one to three numeric release components")
    components = version.split(".")
    version = ".".join(components + ["0"] * (3 - len(components)))
    display_name = name.replace("-", " ").title()
    return {
        "name": name,
        "version": version,
        "description": description,
        "skills": "./skills/",
        "interface": {
            "displayName": display_name,
            "shortDescription": f"Use the {display_name} skill.",
        },
    }


def package_plugin(directory, manifest):
    DIST.mkdir(exist_ok=True)
    output = DIST / f"{directory.name}-chatgpt-plugin.zip"
    with TemporaryDirectory(dir=DIST) as staging:
        temporary = Path(staging) / output.name
        with ZipFile(temporary, "w", ZIP_DEFLATED) as archive:
            archive.writestr(".codex-plugin/plugin.json", json.dumps(manifest, indent=2) + "\n")
            write_skill(archive, directory, Path("skills") / directory.name)
        temporary.replace(output)
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skills", nargs="*", metavar="SKILL", help="skill folder names (default: all)")
    args = parser.parse_args()
    directories = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    if args.skills:
        for name in args.skills:
            if not NAME_RE.fullmatch(name):
                parser.error(f"invalid skill name: {name!r}")
        directories = [SKILLS / name for name in dict.fromkeys(args.skills)]
    if not directories:
        parser.error("no skill folders found")

    packages = []
    for directory in directories:
        try:
            packages.append((directory, plugin_manifest(directory)))
        except (OSError, ValueError) as exc:
            parser.error(f"{directory.name}: {exc}")
    for directory, manifest in packages:
        print("built", package_plugin(directory, manifest).relative_to(ROOT))


if __name__ == "__main__":
    main()
