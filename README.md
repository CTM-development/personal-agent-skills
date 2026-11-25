# Personal agent skills

Personal collection of agent skills in the open [Agent Skills](https://agentskills.io/specification) format. This repo is the single source of truth; every harness (claude.ai, Claude Code, ChatGPT, Codex, Copilot, Cursor, Gemini CLI, the Claude API, your own agents) gets a copy from here. Edit skills only here.

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
tools/package_plugin.py           [OpenAI]   dist/<name>-chatgpt-plugin.zip for the plugin uploader
tools/link.sh + targets.conf      [general] symlinks; [third-party] per-agent folder paths
tools/new_skill.py                [general]  scaffold a skill from the template
tools/api_push.py                 [anthropic-api] create / version skills via /v1/skills
api-skill-ids.json                [anthropic-api] skill name -> API skill id
.claude-plugin/marketplace.json   [claude]   lets Claude Code install the repo as a plugin
.github/workflows/skills.yml      [github]   CI: check, package, optional API push
```

## First-time setup [github]

```bash
cd ~/Projects/personal-agent-skills-repo
git init -b main
git add . && git commit -m "Scaffold personal skills repo"
gh repo create agent-skills-repo --private --source . --push
```

## Everyday commands

```bash
python3 tools/new_skill.py my-skill      # new skill from the template
python3 tools/check_skills.py            # all checks (--profile spec: open standard only)
python3 tools/package.py                 # build standalone skill ZIPs
python3 tools/package_plugin.py          # build ChatGPT plugin ZIPs
bash tools/link.sh --dry-run             # preview symlinks into other agents, then run without --dry-run
python3 tools/api_push.py --dry-run      # preview Claude API uploads
```

## How each harness gets the skills

| Harness | Route | Flag |
|---|---|---|
| claude.ai, Claude desktop and mobile | Upload `dist/<name>.zip` under Customize > Skills (manual; replace the old copy on changes) | [claude] |
| Claude Code, any machine | Automatic one-way sync from your claude.ai account (Claude Code v2.1.273+, same account, not with an API key or Bedrock) | [claude] |
| Claude Code, alternative | `claude plugin marketplace add <you>/agent-skills-repo`, then `claude plugin install personal@personal-skills`. Skills appear as `personal:<name>`. Use this **or** the account sync on a machine, not both. | [claude] |
| Codex | Run `bash tools/link.sh` to install a user-scoped symlink, or link the skill into a specific project’s `.agents/skills/`. | [OpenAI documentation](https://learn.chatgpt.com/docs/build-skills) |
| ChatGPT | Upload `dist/<name>-chatgpt-plugin.zip` through the plugin uploader. Standalone Skills and ChatGPT Projects are also available on supported surfaces. See below. | [OpenAI] |
| Copilot, Cursor, Gemini CLI, … | `git pull && bash tools/link.sh` on each machine | [general] mechanism, [third-party] paths |
| Claude API agents | `python3 tools/api_push.py` once per new skill; CI pushes new versions afterwards (needs repo secret `ANTHROPIC_API_KEY`) | [anthropic-api] |
| Your own agent harness | Read each `SKILL.md` frontmatter at startup, load the body when a skill is chosen, read `references/` on demand | [general] |

One-way flows to remember: the claude.ai → Claude Code sync never writes back, and skills edited through a Claude chat ("save as skill") change only claude.ai. Copy such edits back into this repo.

## Codex and ChatGPT setup

**Codex.** Preview the linker with `bash tools/link.sh --dry-run`. The supported user location is `~/.agents/skills/`. For project scope, place the full skill folder or a symlink under the target project’s `.agents/skills/`. Invoke `$evidence-based-learning` in the CLI. If upgrading from this repo’s former `~/.codex/skills/` links, remove only the old links that point to this checkout, or keep using one location to avoid duplicate entries. [Codex skill discovery](https://learn.chatgpt.com/docs/build-skills)

**ChatGPT plugin uploader.** Run `python3 tools/package_plugin.py evidence-based-learning` from the repo. Upload `dist/evidence-based-learning-chatgpt-plugin.zip` in the plugin uploader. With no skill names, the script builds one ZIP per skill. Each archive puts a Codex manifest and the bundled skill at the plugin root. The plugin version comes from the skill’s `metadata.version`. Update that value for a new release. [OpenAI plugin packaging](https://developers.openai.com/plugins/deploy/submission)

**ChatGPT with native Skills.** In an eligible workspace, open **Plugins → Skills → Create → Upload from your computer**. Run `python3 tools/package.py evidence-based-learning` to build a bundle containing the skill and its references. Try the resulting ZIP in the uploader. If the uploader requires a different format, use the Skills editor and include the referenced files. Check that the skill appears, can be selected with `@` and can open its references after installation. This repo’s ZIP layout was verified locally and needs a live ChatGPT upload check. [Skills in ChatGPT](https://help.openai.com/en/articles/20001066-skills-in-chatgpt)

**ChatGPT Project.** Put a concise version of the `SKILL.md` workflow in Project instructions. Upload the skill and both files under `references/` as source material. For example, use these instructions:

> For deep study sessions, follow evidence-based-learning in SKILL.md. Build an interactive visual representation the learner can manipulate using study-artefact.md. Diagnose task-specific prior knowledge and adapt guidance. Check independent performance on a fresh case, give feedback and plan spaced review. Consult learning-evidence.md when interpreting research or citing a technique. For quick explanations, answer directly.

Open an interactive preview where supported, or provide the learner a runnable artefact. Refresh the uploaded files when the repo changes. [ChatGPT Projects](https://help.openai.com/en/articles/10169521-projects-in-chatgpt)

## Portability map

| Piece | General | Claude / Anthropic-specific |
|---|---|---|
| `SKILL.md` format, `name` / `description` / `compatibility` / `metadata`, `references/` | Spec | |
| Description length | Spec allows 1024 characters | claude.ai allows 200; the checker enforces 200 |
| Which skill gets triggered | Every harness decides from the description, but each model decides differently: test in each tool | |
| Skill body | Pedagogy, workflows, evidence and interactive visual artefacts | Lines marked `[claude]` (artifacts, scheduled tasks, built-in `learn` skill, connected apps), each with a general fallback |
| Scripts inside skills | Run wherever the harness can run code | claude.ai runs them in its code-execution sandbox (its packages, its network allowlist) |
| ZIP packaging | Fine for sharing by hand | Required format for claude.ai uploads |
| Plugin / marketplace | | Claude Code only; other tools have their own plugin formats |
| API uploads | | Claude API workspace only; separate from claude.ai account skills |
| Agent folder paths | Codex documents symlinks and `.agents/skills/`. Verify paths for other agents separately. | |
| CI | Checks are plain Python | GitHub Actions; the marketplace validation step needs Claude Code |

## Not verified when scaffolded

- `tools/api_push.py` against the live API (written from the API reference; try `--dry-run` first).
- The `skills-ref` install path and `claude plugin validate` steps in CI (both marked `continue-on-error`).
- The non-Codex paths in `tools/targets.conf` against the respective agents.
