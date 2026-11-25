#!/usr/bin/env python3
"""Upload skills to the Claude API Skills endpoint (/v1/skills).  [anthropic-api]

Only needed for agents you run on the Claude API (Messages API with code execution,
Claude Agent SDK on the API). These uploads live in your API workspace, separate from your
claude.ai account skills; no documented sync between the two was found when this was written.

- First upload of a skill creates it and records its id in api-skill-ids.json (commit that file).
- Later uploads create a new version of the recorded skill.
- --no-create: only push versions of skills already recorded (used in CI, which cannot commit).
- --changed-since REF: only skills whose folder changed since a git ref.

Env: ANTHROPIC_API_KEY (required), ANTHROPIC_VERSION (default 2026-10-21),
     ANTHROPIC_WORKSPACE_ID (optional), ANTHROPIC_BASE_URL (default https://api.anthropic.com).

Not tested against the live API when scaffolded: run once with --dry-run, then for real.
Usage: python3 tools/api_push.py [--dry-run] [--no-create] [--changed-since REF] [skill-name ...]
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
IDS = ROOT / "api-skill-ids.json"
SKIP = {".DS_Store", "__pycache__"}


def skill_files(d):
    for f in sorted(d.rglob("*")):
        if f.is_file() and not SKIP.intersection(f.relative_to(d).parts):
            yield f"{d.name}/{f.relative_to(d).as_posix()}", f.read_bytes()


def multipart(files, fields):
    boundary = uuid.uuid4().hex
    out = bytearray()
    for k, v in fields.items():
        out += f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    for name, data in files:
        out += (f'--{boundary}\r\nContent-Disposition: form-data; name="files[]"; filename="{name}"\r\n'
                f"Content-Type: application/octet-stream\r\n\r\n").encode() + data + b"\r\n"
    out += f"--{boundary}--\r\n".encode()
    return bytes(out), f"multipart/form-data; boundary={boundary}"


def post(path, body, ctype):
    base = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")
    headers = {
        "Authorization": f"Bearer {os.environ['ANTHROPIC_API_KEY']}",
        "anthropic-version": os.environ.get("ANTHROPIC_VERSION", "2026-10-21"),
        "Content-Type": ctype,
    }
    if os.environ.get("ANTHROPIC_WORKSPACE_ID"):
        headers["anthropic-workspace-id"] = os.environ["ANTHROPIC_WORKSPACE_ID"]
    req = urllib.request.Request(base + path, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"API error {e.code} on {path}: {e.read().decode(errors='replace')}")


def changed_since(ref):
    if not ref.strip("0"):  # first push to a new branch: GitHub sends 000…0 as "before"
        return sorted(p.name for p in SKILLS.iterdir() if p.is_dir())
    out = subprocess.run(["git", "diff", "--name-only", ref, "--", "skills"],
                         cwd=ROOT, capture_output=True, text=True, check=True).stdout
    return sorted({Path(p).parts[1] for p in out.splitlines() if len(Path(p).parts) > 2})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("skills", nargs="*")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-create", action="store_true")
    ap.add_argument("--changed-since")
    a = ap.parse_args()

    ids = json.loads(IDS.read_text()) if IDS.exists() else {}
    names = a.skills or (changed_since(a.changed_since) if a.changed_since
                         else sorted(p.name for p in SKILLS.iterdir() if p.is_dir()))
    names = [n for n in names if (SKILLS / n / "SKILL.md").is_file()]
    if not names:
        print("nothing to push")
        return
    if not a.dry_run and "ANTHROPIC_API_KEY" not in os.environ:
        sys.exit("ANTHROPIC_API_KEY is not set")

    for n in names:
        files = list(skill_files(SKILLS / n))
        if n in ids:
            action, path, fields = "new version of", f"/v1/skills/{ids[n]}/versions", {}
        elif a.no_create:
            print(f"skip {n}: not in api-skill-ids.json and --no-create is set")
            continue
        else:
            action, path, fields = "create", "/v1/skills", {"display_name": n}
        print(f"{action} {n} ({len(files)} files) -> POST {path}")
        if a.dry_run:
            continue
        body, ctype = multipart(files, fields)
        res = post(path, body, ctype)
        if n not in ids:
            ids[n] = res["id"]
            IDS.write_text(json.dumps(ids, indent=2, sort_keys=True) + "\n")
            print(f"  created {res['id']}; recorded in api-skill-ids.json (commit it)")
        else:
            print(f"  version {res.get('id')}")


if __name__ == "__main__":
    main()
