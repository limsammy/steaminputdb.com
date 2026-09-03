# Cursor integration guide

This project can use Cursor as an implementation/review surface without making
Cursor the owner of repository state. Git, workmux, `AGENTS.md`, tests, and
small handoff artifacts remain the portable control plane.

## Current machine state (2026-09-03)

- Windows Cursor is installed at version 3.18.9.
- WSL `cursor-agent` is installed at version `2026.08.11-e8db854`, but the WSL
  CLI is not authenticated. Run `cursor-agent login` interactively before using
  it; do not copy browser tokens into repository files.
- Workmux 0.1.238 is installed and this repo's default agent is Codex.
- Warp/Oz is installed on Windows at version
  `0.2026.08.12.21.54.stable_00`. Its live model list includes Claude, Gemini,
  GPT, Grok, and other provider models, but it does not expose a Cursor Composer
  model ID.

Model catalogs, quotas, and CLI flags are volatile. Re-run
`cursor-agent --list-models`, `cursor-agent --help`, and `oz model list` before
pinning a model in automation.

## Recommended architecture

Use one writing agent per worktree and pass work through Git:

```text
Claude or Codex plans/researches
            |
            v
Cursor Agent/Composer implements in a workmux branch
            |
            v
Codex reviews the diff and runs independent checks
            |
            v
Human merges or workmux merges after approval
```

This is an orchestration convention, not a direct model API. Cursor documents
model selection inside Cursor and through `cursor-agent --model`, but there is
no verified first-party interface that lets Claude Code call Composer as a
provider or lets Codex directly spawn Composer. Worktrees, commits, prompt
files, and review artifacts are the reliable interoperability layer.

## Migrate the editor safely

1. Open the repository from WSL in Cursor:

   ```bash
   cd ~/projects/deck/steaminputdb.com
   cursor .
   ```

2. In Cursor Settings, use the VS Code import flow for extensions, settings,
   keybindings, and themes. Treat it as editor-profile migration only; it does
   not migrate Claude/Codex conversations, auth, hooks, or agent state. See
   [Cursor's VS Code migration guide](https://cursor.com/docs/get-started/migrate-from-vs-code).
3. Keep source control in WSL. Verify Cursor's integrated terminal opens the
   same WSL checkout instead of a second Windows clone.
4. Trust only this repository root, not all of `~/projects/deck`, because the
   parent is a separate wrapper repository.
5. Keep large design assets and generated output out of agent context through
   the checked-in `.cursorignore`.

## Rules, skills, plugins, and MCP

- `AGENTS.md` is the shared source of truth. Cursor CLI reads it alongside
  `.cursor/rules`; the small checked-in Cursor rule adds only Cursor-specific
  boundaries. See [Cursor CLI rules support](https://docs.cursor.com/en/cli/using)
  and [Cursor rules](https://cursor.com/docs/rules).
- Put portable project skills in `.agents/skills/<name>/SKILL.md`. Cursor
  discovers Agent Skills and Warp also supports repository skills. Keep
  provider-only adapters in `.cursor/skills`, `.claude/skills`, or `.warp/skills`
  only when the shared format cannot express the behavior. See
  [Cursor Agent Skills](https://cursor.com/docs/skills) and
  [Warp AI objects](https://docs.warp.dev/knowledge-and-collaboration/warp-drive/ai-objects).
- Cursor plugins can bundle skills, MCP servers, rules, agents, commands, and
  hooks. Prefer an open Agent Plugin for portable skills/MCP; use a Cursor
  Plugin only for Cursor-specific hooks or rules. See
  [Cursor plugins](https://cursor.com/docs/plugins).
- The Buddy API at `localhost:5119` is HTTP/OpenAPI, not MCP. Do not add it to
  `.cursor/mcp.json` directly. A future adapter should expose read-only
  ping/status/apps/controllers first and require an explicit approval gate for
  apply/install/update/uninstall operations. Cursor supports project MCP config
  and MCP management through its CLI; see
  [Cursor CLI parameters](https://cursor.com/docs/cli/reference/parameters).
- Cloud/background agents run away from the Windows Steam client and cannot use
  its localhost Buddy service by default. Use a local WSL agent or a deliberately
  secured private worker for Buddy-related tasks.

## Workmux + Cursor

Workmux remains the default worktree owner so all agents share one lifecycle.
This repo's `.workmux.yaml` defines `cursor`, `codex`, and `claude` agents.

Create an isolated Cursor branch from the repository root:

```bash
workmux add feat/example --agent cursor --prompt-file docs/path/PROMPT.md
```

Create a prompt file without starting a second agent pane when using Cursor's
IDE chat in the worktree:

```bash
workmux add feat/example \
  --agent cursor \
  --prompt-file docs/path/PROMPT.md \
  --prompt-file-only
```

Open the path reported by `workmux path feat/example` in Cursor. Do not also
activate Cursor's `--worktree` flag for that run; nested worktree managers make
ownership and cleanup ambiguous. Cursor's native worktrees are useful when
workmux is not managing the task. See [Cursor worktrees](https://cursor.com/docs/configuration/worktrees)
and [workmux quick start](https://workmux.raine.dev/guide/quick-start/).

## Claude -> Cursor -> Codex flow

Use a small, auditable handoff:

1. Claude or Codex writes/approves a task prompt under `docs/spikes/` or links a
   GitHub issue with acceptance criteria.
2. Start Cursor in a dedicated workmux branch. Let Composer/Agent implement and
   create atomic Conventional Commits.
3. Start Codex in read-only review mode against the branch diff. Require
   findings with file references and fresh test evidence.
4. Send findings back to the same Cursor worktree for fixes, or let Codex fix
   them only after explicitly changing ownership.
5. Run the branch's checks once more, then merge with workmux or open a PR.

For noninteractive Cursor runs, remember that `--print` still has write and
shell tools. Use `--mode plan` for read-only planning, avoid `--force`/`--yolo`
as a default, and prefer an isolated worktree. The current CLI also supports
`--model`, `--resume`, structured output, plugins, MCP approval, sandboxing, and
its own worktrees; verify flags with the local help before scripting them. See
[Cursor CLI parameter reference](https://cursor.com/docs/cli/reference/parameters).

## Warp's role

Warp is a good terminal and optional Oz orchestration surface. Its Windows CLI
can run an agent with selected skills/MCP/model, for example conceptually:

```text
oz agent run --cwd <WORKTREE> --skill <SKILL> --model <MODEL_ID> <PROMPT>
```

Use the exact syntax from `oz agent run --help` on Windows. Warp's support for
Claude Code and Codex in the terminal is not proof that Warp automatically
injects every Warp/Claude skill into those third-party CLIs. The portable path
is `.agents/skills`; each host may still need its own discovery adapter. See the
[Oz CLI reference](https://docs.warp.dev/reference/cli).

## What not to migrate

- Do not move Git ownership from WSL to a duplicate Windows clone.
- Do not copy API keys or auth databases between Codex, Claude, Cursor, and Warp.
- Do not duplicate the same instruction in `AGENTS.md`, Cursor rules, Claude
  memory, and Warp rules. Keep one shared rule and only thin host adapters.
- Do not let two writing agents share a branch or generated directory.
- Do not expose the Windows Buddy service to cloud agents or the public network
  merely to make MCP convenient.

## Adoption checklist

- [ ] Authenticate WSL Cursor CLI with `cursor-agent login`.
- [ ] Import VS Code editor preferences in Windows Cursor.
- [ ] Open the WSL repo and confirm terminal/Git paths.
- [ ] Run `cursor-agent --list-models` after login; choose models per task rather
      than hard-coding a stale catalog.
- [ ] Run the first spike through workmux with Codex, then repeat a small branch
      with `--agent cursor` to validate the handoff.
- [ ] Review Cursor-authored commits with Codex before merge.
- [ ] Prototype Buddy MCP only after the read-only Windows bridge is stable.
