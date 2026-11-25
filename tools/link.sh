#!/usr/bin/env bash
# Symlink every skill in skills/ into each agent's skills folder listed in tools/targets.conf.
# [general] mechanism; target paths are per-tool conventions (see targets.conf).
#
# Usage: bash tools/link.sh [--dry-run] [--unlink]
#   --dry-run  show what would change
#   --unlink   remove links that point into this repo
# Existing files or folders that are not our symlinks are never touched.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONF="$ROOT/tools/targets.conf"
DRY=0; UNLINK=0
for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY=1 ;;
    --unlink)  UNLINK=1 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

run() { if [ "$DRY" = 1 ]; then echo "  would: $*"; else "$@"; fi; }

while IFS= read -r line; do
  line="${line%%#*}"; line="$(echo "$line" | xargs)"
  [ -z "$line" ] && continue
  target="${line/#\~/$HOME}"
  parent="$(dirname "$target")"
  if [ ! -d "$parent" ]; then
    echo "skip   $target (agent folder $parent not found)"
    continue
  fi
  echo "target $target"
  [ "$UNLINK" = 0 ] && run mkdir -p "$target"
  for skill in "$ROOT"/skills/*/; do
    [ -f "$skill/SKILL.md" ] || continue
    name="$(basename "$skill")"
    dest="$target/$name"
    src="${skill%/}"
    if [ "$UNLINK" = 1 ]; then
      if [ -L "$dest" ] && [ "$(readlink "$dest")" = "$src" ]; then run rm "$dest"; [ "$DRY" = 1 ] || echo "  unlinked $name"; fi
      continue
    fi
    if [ -L "$dest" ]; then
      if [ "$(readlink "$dest")" = "$src" ]; then echo "  ok      $name"; continue; fi
      echo "  skip    $name (symlink points elsewhere: $(readlink "$dest"))"; continue
    fi
    if [ -e "$dest" ]; then echo "  skip    $name (a real file or folder already exists)"; continue; fi
    run ln -s "$src" "$dest"; [ "$DRY" = 1 ] || echo "  linked  $name"
  done
done < "$CONF"
