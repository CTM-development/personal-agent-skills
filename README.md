# agent-skills-repo

Personal collection of agent skills in the open [Agent Skills](https://agentskills.io/specification) format. This repo is the single source of truth; every harness (claude.ai, Claude Code, Codex, Copilot, Cursor, Gemini CLI, the Claude API, your own agents) gets a copy from here. Edit skills only here.

## Flags used throughout

| Flag | Meaning |
|---|---|
| **[general]** | Open standard or plain files/scripts. Works with any harness that reads `SKILL.md` folders. |
| **[claude]** | Depends on a Claude product (claude.ai, Claude apps, Claude Code). |
| **[anthropic-api]** | Depends on the Claude API (`/v1/skills`). |
| **[github]** | Depends on GitHub (hosting, Actions). |
| **[third-party]** | A convention taken from community sources, not vendor docs. Verify before relying on it. |

## Layout

```
skills/<name>/SKILL.md            [general]  one folder per skill (spec format)
skills/<name>/references/         [general]  detail loaded on demand
templates/skill-template/         [general]  starting point for new skills
tools/check_skills.py             [general] spec checks + [claude] 200-char description limit
tools/package.py                  [claude]   dist/<name>.zip in the claude.ai upload format
tools/link.sh + targets.conf      [general] symlinks; [third-party] per-agent folder paths
tools/new_skill.py                [general]  scaffold a skill from the template
tools/api_push.py                 [anthropic-api] create / version skills via /v1/skills
api-skill-ids.json                [anthropic-api] skill name -> API skill id
.claude-plugin/marketplace.json   [claude]   lets Claude Code install the repo as a plugin
.github/workflows/skills.yml      [github]   CI: check, package, optional API push
```

## First-time setup [github]

```bash
cd ~/Projects/agent-skills-repo
git init -b main
git add . && git commit -m "Scaffold personal skills repo"
gh repo create agent-skills-repo --private --source . --push
```

## Everyday commands

```bash
python3 tools/new_skill.py my-skill      # new skill from the template
python3 tools/check_skills.py            # all checks (--profile spec: open standard only)
python3 tools/package.py                 # build dist/*.zip
bash tools/link.sh --dry-run             # preview symlinks into other agents, then run without --dry-run
python3 tools/api_push.py --dry-run      # preview Claude API uploads
```

## How each harness gets the skills

| Harness | Route | Flag |
|---|---|---|
| claude.ai, Claude desktop and mobile | Upload `dist/<name>.zip` under Customize > Skills (manual; replace the old copy on changes) | [claude] |
| Claude Code, any machine | Automatic one-way sync from your claude.ai account (Claude Code v2.1.273+, same account, not with an API key or Bedrock) | [claude] |
| Claude Code, alternative | `claude plugin marketplace add <you>/agent-skills-repo`, then `claude plugin install personal@personal-skills`. Skills appear as `personal:<name>`. Use this **or** the account sync on a machine, not both. | [claude] |
| Codex, Copilot, Cursor, Gemini CLI, … | `git pull && bash tools/link.sh` on each machine | [general] mechanism, [third-party] paths |
| Claude API agents | `python3 tools/api_push.py` once per new skill; CI pushes new versions afterwards (needs repo secret `ANTHROPIC_API_KEY`) | [anthropic-api] |
| Your own agent harness | Read each `SKILL.md` frontmatter at startup, load the body when a skill is chosen, read `references/` on demand | [general] |

One-way flows to remember: the claude.ai → Claude Code sync never writes back, and skills edited through a Claude chat ("save as skill") change only claude.ai. Copy such edits back into this repo.

## Portability map

| Piece | General | Claude / Anthropic-specific |
|---|---|---|
| `SKILL.md` format, `name` / `description` / `compatibility` / `metadata`, `references/` | Spec | |
| Description length | Spec allows 1024 characters | claude.ai allows 200; the checker enforces 200 |
| Which skill gets triggered | Every harness decides from the description, but each model decides differently: test in each tool | |
| Skill body | Pedagogy, workflows, evidence, HTML artefacts | Lines marked `[claude]` (artifacts, scheduled tasks, built-in `learn` skill, connected apps), each with a general fallback |
| Scripts inside skills | Run wherever the harness can run code | claude.ai runs them in its code-execution sandbox (its packages, its network allowlist) |
| ZIP packaging | Fine for sharing by hand | Required format for claude.ai uploads |
| Plugin / marketplace | | Claude Code only; other tools have their own plugin formats |
| API uploads | | Claude API workspace only; separate from claude.ai account skills |
| Agent folder paths | Symlinking works everywhere | Paths are per-tool conventions ([third-party]) |
| CI | Checks are plain Python | GitHub Actions; the marketplace validation step needs Claude Code |

## Not verified when scaffolded

- `tools/api_push.py` against the live API (written from the API reference; try `--dry-run` first).
- The `skills-ref` install path and `claude plugin validate` steps in CI (both marked `continue-on-error`).
- The per-agent folders in `tools/targets.conf`.
