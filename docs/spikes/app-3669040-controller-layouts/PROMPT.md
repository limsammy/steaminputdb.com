# Spike prompt: app 3669040 controller layouts

Target: Codex CLI in a workmux-managed worktree, with the installed OMX plugin
and native subagents available.

```text
Objective
Produce a reproducible, evidence-backed inventory of every Steam Input
controller layout discoverable for Steam app 3669040 (Our Red String), then
design a generalized Steam Controller (2015) profile suitable for Ren'Py visual
novels. The result must distinguish actual layouts from controller filter
options and must explain any disagreement between SteamInputDB, the running
Buddy app, and Steam itself.

Context
- Repository: the current workmux checkout of the SteamInputDB fork.
- Working fork: origin = limsammy/steaminputdb.com.
- Source repository: upstream = Alia5/steaminputdb.com.
- App page: https://www.steaminputdb.com/app/3669040
- The Buddy app is installed and running on Windows. Its docs are at
  http://localhost:5119/docs and its checked-in contract is openapi-buddy.yaml.
- From WSL, localhost:5119 may not be reachable directly. Use powershell.exe
  with Invoke-WebRequest/Invoke-RestMethod for the Windows-local API.
- Live evidence captured on 2026-09-03:
  - GET /v1/ping through Windows returned SteamInputDB-Buddy v0.2.2.
  - POST https://api.steaminputdb.com/v1/search/configs with app_id 3669040
    returned an empty object for an unfiltered request.
  - The same request returned zero items for every controller type shown by the
    page, including controller_steamcontroller_gordon.
  - Server-rendered page HTML said "No results found" while still rendering the
    global controller filter list.
  Treat these as observations to re-check, not a final conclusion.

Scope
- Inspect the repository source, OpenAPI contracts, and relevant history.
- Use read-only calls to the public SteamInputDB API, the website, the running
  Buddy API, and documented Steam endpoints.
- Browser automation may use the installed Playwright CLI for observation and
  network capture. Do not bypass authentication, CAPTCHA, rate limits, or Steam
  access controls.
- Write spike-only tooling under tools/spikes/app-3669040-layouts/ and results
  under docs/spikes/app-3669040-controller-layouts/.
- Do not change production backend/frontend/Buddy behavior during this spike.
- Do not apply, publish, upload, or delete a Steam configuration. Do not open
  Steam UI through Buddy unless needed for a read-only observation. Ask before
  any call that changes Steam or Buddy state.

Requirements
1. Establish the interfaces.
   - Read README.md, BUILDING.md, openapi.yaml, openapi-buddy.yaml, the public
     config-search handler, and Buddy controller/apply-config implementations.
   - Record the exact running Buddy version, Steam connection status, connected
     controller records (including raw form), and whether app 3669040 is known
     to the running Steam client. Redact account-specific data from committed
     artifacts.
2. Enumerate layouts without relying on the website's controller UI.
   - Reproduce the public POST /v1/search/configs request with limit 100 and
     page through all results until the reported total is exhausted.
   - Query once without controller tags and once for each controller type the
     live page exposes. Deduplicate by Workshop file_id.
   - Capture status, response body shape, total, page size, and timestamp.
   - If all results remain empty, inspect the live page's network traffic and
     compare it with the checked-in request construction.
3. Cross-check Steam directly only through behavior already evidenced in this
   repository or official Valve documentation.
   - Determine the exact IPublishedFileService QueryFiles request the backend
     builds for app 3669040, Steam configs app 241100, file type, KV tags, and
     controller tags.
   - If a Steam Web API key is already available through a named environment
     variable, use it without printing it. Do not request, persist, or expose a
     credential. If no key is available, record the blocked verification path.
   - Do not claim a public bulk Steam endpoint exists unless official evidence
     or a successful observed request proves it.
4. Produce the inventory.
   - Save a machine-readable JSON or CSV inventory and a Markdown summary.
   - Include Workshop file ID, title, description, controller type, creator,
     timestamps, subscriptions/votes when returned, file URL, source, and
     retrieval time.
   - If the verified answer is zero layouts, say "zero actual layouts found"
     and list the controller names separately as filter choices—not layouts.
   - State the completeness boundary and any inaccessible evidence.
5. Design the generalized Steam Controller profile.
   - Assume a legacy keyboard/mouse Ren'Py game with no native Steam Input API.
   - Prefer robust bindings that work across Ren'Py titles: right trackpad as
     mouse; click/confirm; advance; menu/back; rollback/roll-forward; hold-to-
     skip; toggle skip; hide UI; screenshot; directional choice navigation.
   - Keep gyro disabled by default and avoid relying on simultaneous gamepad and
     mouse input unless verified.
   - Provide a controller-to-action table, rationale, alternatives, and a short
     on-device test checklist for Our Red String.
   - If an existing downloaded VDF provides a safe base, create an importable
     Steam Controller VDF as a spike artifact. Otherwise provide exact Steam UI
     creation/export steps and document why hand-authoring the VDF was unsafe.
6. Add the smallest repeatable tests for any spike parser/enumerator. Run them
   and record the commands and results.

Mode: implementation.
Follow applicable repository instructions and inspect relevant files before
editing. Make the in-scope local spike artifacts and run non-destructive checks
without asking first. Use native subagents only for independent bounded research
or verification lanes. Ask before destructive actions, external writes,
publishing, applying a controller configuration, opening a pull request, or a
material expansion beyond this spike. Do not overwrite unrelated user changes.

Done when
- A fresh, reproducible query establishes how many actual layouts exist for app
  3669040 across all controller types, with no UI clicking required.
- The inventory and its completeness/limitations are saved in the spike docs.
- A practical Steam Controller mapping and validation checklist exist; an
  importable VDF exists only if it can be grounded and safely validated.
- Tests/checks for new spike tooling pass, or exact blockers are recorded.
- The branch contains no credentials or private account data.

Final response
Lead with the layout count and the Steam Controller profile result. Summarize
files changed, evidence sources, checks run, remaining uncertainty, and the next
decision. Do not claim success from controller filter names alone.
```

Optimized for: continuing the existing investigation in an isolated Codex
worktree while preventing controller filters, live hardware, and community
layouts from being conflated.
