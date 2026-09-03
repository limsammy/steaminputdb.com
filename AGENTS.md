# SteamInputDB fork project instructions

This repository is the working fork of `Alia5/steaminputdb.com`. Keep `origin`
pointed at `limsammy/steaminputdb.com` and `upstream` pointed at the source
repository.

## Working model

- Use one workmux worktree and one writing agent per branch.
- Keep upstream-facing product changes separate from local experiments and
  research artifacts.
- Put time-boxed investigations under `docs/spikes/<topic>/` and record the
  question, evidence, result, and next decision.
- Use `docs/project/BACKLOG.md` for local task state until a task is promoted to
  a GitHub issue. Link the issue from the backlog when promoted.
- Do not commit credentials, Steam API keys, cookies, local API responses that
  contain private account data, or machine-specific absolute paths.

## Commits

Use Conventional Commits:

```text
<type>(optional-scope): <imperative summary>
```

Allowed common types are `feat`, `fix`, `docs`, `test`, `refactor`, `chore`,
`build`, `ci`, `perf`, and `revert`. Mark breaking changes with `!` and explain
them in the body. Keep commits atomic; do not mix generated files, research,
and product behavior unless they are inseparable.

Examples:

```text
docs(spike): record app 3669040 layout inventory
feat(buddy): expose controller layout discovery
test(search): cover controller-type pagination
```

## Local Windows boundary

The Buddy app runs on Windows at `http://localhost:5119`. From WSL, call it
through `powershell.exe` when WSL localhost forwarding is unavailable. Read-only
health, status, app, and controller requests are safe. Applying a configuration,
opening Steam UI, installing, updating, or uninstalling the Buddy app changes
external state and must be explicitly in scope.

## Validation

Run the smallest relevant checks first, then broader checks when the changed
area supports them. Follow `BUILDING.md`. The current upstream requirements are
Go 1.26+, Node.js 26+, protobuf, and optional `just`; do not silently use a
different toolchain to regenerate committed output.
