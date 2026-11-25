#!/usr/bin/env python3
"""Build dist/<skill>-chatgpt-plugin.zip for the ChatGPT plugin uploader."""

import argparse
import json
import re
import unicodedata
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

from check_skills import NAME_RE
from package import DIST, ROOT, SKILLS, skill_paths

RELEASE_VERSION = re.compile(r"(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){0,2}")
FRONTMATTER = re.compile(r"\A---[ \t]*\n(.*?)^---[ \t]*(?:\n|\Z)", re.MULTILINE | re.DOTALL)
MIB = 1024 * 1024


def read_skill_frontmatter(directory):
    try:
        import yaml
    except ImportError as exc:
        raise ValueError("PyYAML is required; install it with python3 -m pip install PyYAML") from exc

    skill = directory / "SKILL.md"
    if directory.is_symlink() or skill.is_symlink() or not skill.is_file():
        raise ValueError("expected a regular SKILL.md in the skill folder")
    source = skill.read_text(encoding="utf-8")
    match = FRONTMATTER.match(source)
    if not match:
        raise ValueError("SKILL.md must start with YAML frontmatter between '---' lines")
    if not source[match.end():].strip():
        raise ValueError("SKILL.md must contain instructions after its frontmatter")
    try:
        frontmatter = yaml.safe_load(match[1])
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid SKILL.md YAML: {exc}") from exc
    if not isinstance(frontmatter, dict):
        raise ValueError("SKILL.md frontmatter must be a map")
    return frontmatter


def required_text(value, field, limit, allowed_controls=""):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"{field} must be a non-empty string of at most {limit} characters")
    if any(unicodedata.category(char) in {"Cc", "Cs"} and char not in allowed_controls for char in value):
        raise ValueError(f"{field} contains unsupported characters")
    return value.strip()


def plugin_manifest(directory):
    frontmatter = read_skill_frontmatter(directory)
    name = frontmatter.get("name", "")
    if not isinstance(name, str) or name != directory.name or len(name) > 64 or not NAME_RE.fullmatch(name):
        raise ValueError("skill name must match its lowercase, hyphenated folder name")
    if len(f"{name}:{name}") > 64:
        raise ValueError("skill name must be at most 31 characters when also used as the plugin name")
    description = required_text(frontmatter.get("description"), "description", 1024, "\n")
    metadata = frontmatter.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a map")
    author = required_text(metadata.get("author"), "metadata.author", 120)
    version = metadata.get("version", "0.1.0")
    if not isinstance(version, str) or not RELEASE_VERSION.fullmatch(version):
        raise ValueError("metadata.version must be a quoted release with one to three numeric components")
    components = version.split(".")
    version = ".".join(components + ["0"] * (3 - len(components)))
    if len(version) > 64:
        raise ValueError("plugin version must be at most 64 characters after normalization")
    display_name = name.replace("-", " ").title()
    return {
        "name": name,
        "version": version,
        "description": description,
        "author": {"name": author},
        "skills": "./skills/",
        "interface": {
            "displayName": display_name,
            "shortDescription": f"Use the {display_name} skill.",
            "longDescription": description,
            "developerName": author,
            "category": "Other",
            "capabilities": [],
        },
    }


def write_plugin_skill(archive, directory):
    archive_root = Path("skills") / directory.name
    normalized_paths = set()
    uncompressed_size = sum(entry.file_size for entry in archive.infolist())
    for path, relative in skill_paths(directory):
        member = archive_root / relative
        entry = member.as_posix()
        if "\\" in entry or entry != entry.strip() or len(member.parts) > 20:
            raise ValueError(f"invalid ZIP path: {entry!r}")
        normalized = unicodedata.normalize("NFC", entry.casefold())
        if normalized in normalized_paths:
            raise ValueError(f"duplicate ZIP path after case and Unicode normalization: {entry!r}")
        normalized_paths.add(normalized)
        if path.is_symlink():
            raise ValueError(f"symbolic links cannot be packaged: {relative}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f"only regular files can be packaged: {relative}")
        size = path.stat().st_size
        if size > 100 * MIB:
            raise ValueError(f"ZIP entry exceeds 100 MiB: {entry}")
        uncompressed_size += size
        if uncompressed_size > 512 * MIB or len(archive.infolist()) >= 5000:
            raise ValueError("plugin ZIP exceeds 512 MiB uncompressed or 5,000 entries")
        archive.write(path, entry)


def package_plugin(directory, manifest):
    DIST.mkdir(exist_ok=True)
    output = DIST / f"{directory.name}-chatgpt-plugin.zip"
    with TemporaryDirectory(dir=DIST) as staging:
        temporary = Path(staging) / output.name
        with ZipFile(temporary, "w", ZIP_DEFLATED) as archive:
            archive.writestr(".codex-plugin/plugin.json", json.dumps(manifest, indent=2) + "\n")
            write_plugin_skill(archive, directory)
        if temporary.stat().st_size > 100_000_000:
            raise ValueError("compressed plugin ZIP exceeds 100 MB")
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
        try:
            output = package_plugin(directory, manifest)
        except (OSError, ValueError) as exc:
            parser.error(f"{directory.name}: {exc}")
        print("built", output.relative_to(ROOT))


if __name__ == "__main__":
    main()
