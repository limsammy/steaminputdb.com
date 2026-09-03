# App 3669040 controller-layout inventory

Date: 2026-09-03

## Direct answer

**Zero actual layouts found.** A fresh public enumeration returned no Workshop
file IDs for Our Red String (`app_id=3669040`): the unfiltered request and all
19 controller-filter requests returned HTTP 200 with a zero result. The raw
SteamInputDB proxy response was `{"total":0}`; the mapped response was `{}`
because the Go response omits a zero `total` and an empty `items` field.

The result is complete for public layouts discoverable through the deployed
SteamInputDB search backend at `2026-09-03T08:51:49Z`–`08:52:12Z`. It is not a
claim about private, unshared, deleted, or local-only Steam configurations.
Independent direct-Steam verification is blocked because no `STEAM_API_KEY`
environment variable was present.

The practical profile result is a generalized legacy keyboard/mouse Steam
Controller (2015) mapping. No VDF was created because no downloaded or
Steam-generated base was available to validate. See
[STEAM-CONTROLLER-PROFILE.md](STEAM-CONTROLLER-PROFILE.md).

## Inventory artifacts

- [inventory.json](inventory.json) is the machine-readable, `file_id`-deduplicated
  inventory. Its `layouts` array is empty and `layout_count` is 0.
- [query-evidence.json](query-evidence.json) records the request template, all
  20 page-1 observations, timestamps, HTTP status, body shape, returned count,
  response size, and response hash.
- [live-observations.json](live-observations.json) records the raw proxy probe,
  browser network observation, Buddy state, Steam app lookup, credential
  boundary, and redactions.

An inventory row would include Workshop file ID, title, description, controller
type, creator, creation/update times, subscriptions, votes, returned file URL,
Workshop URL, source, retrieval time, and the queries that found it. There are
no rows to populate for this app.

## Reproduction

From the repository root:

```sh
python3 tools/spikes/app-3669040-layouts/enumerate_layouts.py \
  --inventory-output docs/spikes/app-3669040-controller-layouts/inventory.json \
  --evidence-output docs/spikes/app-3669040-controller-layouts/query-evidence.json
```

The enumerator uses `limit=100`, begins at page 1, and keeps requesting pages
until the reported total is consumed. It queries once with no controller tag,
then once for each option in
[controller-filters.json](../../../tools/spikes/app-3669040-layouts/controller-filters.json).
It fails rather than silently truncating if the server reports more results but
returns an empty intermediate page.

## Controller filter choices (not layouts)

These 19 names are filter metadata from the frontend's `CONTROLLER_LIST`. The
first 11 were also present as radio controls in the live server-rendered HTML;
the remaining eight are the client-rendered **Show More** choices. None is a
layout unless a search result supplies a Workshop `file_id`.

| Filter name | Required Steam tag |
| --- | --- |
| Steam Controller | `controller_triton` |
| Steam Controller (2015) | `controller_steamcontroller_gordon` |
| Steam Deck | `controller_neptune` |
| DualSense | `controller_ps5` |
| DualShock 4 | `controller_ps4` |
| Xbox 360 | `controller_xbox360` |
| Xbox One | `controller_xboxone` |
| Xbox Elite | `controller_xboxelite` |
| Switch Pro | `controller_switch_pro` |
| Switch 2 Pro | `controller_switch2_pro` |
| 8BitDo | `controller_8bitdo` |
| Generic | `controller_generic` |
| Steam Controller (Headcrab) | `controller_steamcontroller_headcrab` |
| DualSense Edge | `controller_ps5_edge` |
| DualShock 3 | `controller_ps3` |
| HoriPad Steam | `controller_hori_steam` |
| Mobile Touch | `controller_mobile_touch` |
| ASUS ROG Ally | `controller_rog_ally` |
| Lenovo Legion Go S | `controller_legion_go_s` |

## Interfaces and exact request construction

The inspected contracts and implementations were `README.md`, `BUILDING.md`,
`openapi.yaml`, `openapi-buddy.yaml`, the public config-search handler and
types, Steam API client/protobuf definitions, Buddy status/controllers/apps,
and Buddy apply-config code. No production behavior was changed.

The public endpoint accepts this spike's JSON request at
`POST https://api.steaminputdb.com/v1/search/configs`. The handler constructs:

```text
GET https://api.steampowered.com/IPublishedFileService/QueryFiles/v1/
    ?input_protobuf_encoded=<base64 protobuf>
    &key=<configured STEAM_API_KEY>
```

Decoded protobuf fields for the unfiltered page-1 spike request are:

<!-- markdownlint-disable MD013 -->

| QueryFiles field | Value / source |
| --- | --- |
| `query_type` | `0`, ranked by vote |
| `page` | `1` |
| `numperpage` | `100` |
| `appid` | `241100`, Steam's controller-config Workshop app in this implementation |
| `filetype` | `15` |
| `required_kv_tags` | `visibility=public`, `deleted=0`, `app=3669040` |
| `requiredtags` | empty unfiltered; one controller tag for each filtered query |
| `excludedtags` | empty |
| `search_text` | empty string |
| `days` | `30` |
| `return_vote_data` | `true` |
| `return_tags` | `true` |
| `return_kv_tags` | `true` |
| `return_metadata` | `true` |
| `return_details` | `true` |

<!-- markdownlint-enable MD013 -->

The important distinction is that `appid=241100` selects the Workshop whose
items are controller configs; target game 3669040 is sent as the required KV
tag `app=3669040`. A controller choice is sent as `requiredtags`, not as proof
that an item exists.

Relevant implementation evidence:

- [`backend/api/search/configs/search.go`](../../../backend/api/search/configs/search.go)
  builds the request, maps app/controller filters, and maps returned fields.
- [`backend/api/search/configs/structs.go`](../../../backend/api/search/configs/structs.go)
  defines the public request, `limit <= 100`, and omitted empty response fields.
- [`backend/steamapi/client.go`](../../../backend/steamapi/client.go) and
  [`publishedfile.go`](../../../backend/steamapi/publishedfile.go) encode the
  protobuf and call `IPublishedFileService/QueryFiles/v1`.
- [`service_publishedfile.proto`](../../../steam_protobufs/webui/service_publishedfile.proto)
  defines the request/response fields.
- [`frontend/src/lib/api/searchConfigs.ts`](../../../frontend/src/lib/api/searchConfigs.ts)
  builds the page's equivalent request with page size 20 and pushes the selected
  controller into `filter.tags`.

## Cross-checks and disagreement analysis

### SteamInputDB API and website

All 20 mapped requests returned the identical three-byte body `{}` with HTTP
200. A separate `raw=true` unfiltered request at `2026-09-03T08:48:42Z`
returned HTTP 200 and `{"total":0}`. This proves that `{}` is the mapped shape
of a reported zero, not a malformed response.

The live page returned HTTP 200 and server-rendered **No results found**. A
fresh-profile headless Chrome load of the Steam Controller (2015) filter
captured a GET to the filtered app URL and no browser-origin request to
`api.steaminputdb.com`; hydrated page data contained `configs:{}`. This agrees
with the checked-in SvelteKit server load: the API request happens on the
server, and the browser receives its result in the page payload.

The same browser observation found the **Show More** control: the DOM contained
11 controller filters before clicking it and all 19 filters afterward. That
live list matched the checked-in filter inventory used by the enumerator.

### Running Buddy and Steam client

Read-only Windows-local calls through `powershell.exe` recorded:

- Buddy service/version: `SteamInputDB-Buddy v0.2.2`.
- Steam running: yes; CEF enable file present: yes; remote debugging reachable:
  yes. The install path was redacted.
- Mapped controllers: HTTP 200 with `null`; raw controllers: HTTP 200 with `[]`.
  Both mean zero connected controllers; there was no raw controller record to
  redact or treat as a layout.
- `/v1/steam/apps` contained no record for app 3669040, so the running client did
  not report the app as known.

This is not a disagreement with SteamInputDB. Buddy's controller endpoint
describes currently connected hardware, and its app endpoint describes the
running client's library/cache. Neither endpoint enumerates public Workshop
layouts. The mutating `/v1/steam/apply_config` implementation downloads a
241100 Workshop item and calls Steam's config selection API; it was inspected
but never called.

### Steam Web API

[Valve's IPublishedFileService reference](https://partner.steamgames.com/doc/webapi/IPublishedFileService)
documents `QueryFiles/v1` and marks a Web API key as required. No environment
variable named `STEAM_API_KEY` was present, so the direct call was not made and
no credential was requested or read from files. No official source found in
this spike documents a keyless bulk QueryFiles path.

The deployed SteamInputDB backend is therefore the live Steam-backed evidence,
but direct request equivalence could not be independently verified. The handler
also contains an unresolved comment that search uses `filetype=15` although a
returned config may report file type 12. Without the key, testing alternative
QueryFiles encodings or file types would exceed the verified path.

## Completeness boundary

High confidence: zero public layouts were returned by the deployed
SteamInputDB backend for the app KV tag, unfiltered and across every checked-in
controller filter, at the recorded time. This includes an explicit raw total of
zero.

Not accessible or not claimed:

- private, friends-only, deleted, unpublished, or local-only Steam configs;
- a direct keyed Steam QueryFiles response from this environment;
- layouts that Steam might index under undocumented tags or request semantics;
- a connected Steam Controller or Steam-known local copy of app 3669040;
- a safe Steam-generated base VDF.

Relevant git history for the search handler/filter list was also inspected. The
available history showed the broad import and a later layout-preview capsense
change, but no search fix or commit explaining the empty result.

## Checks

```text
python3 -m unittest discover \
  -s tools/spikes/app-3669040-layouts \
  -p 'test_*.py' -v
Ran 5 tests ... OK

python3 -m py_compile \
  tools/spikes/app-3669040-layouts/enumerate_layouts.py \
  tools/spikes/app-3669040-layouts/test_enumerate_layouts.py
exit 0
```

The tests cover `{}` normalization, response-shape validation, multi-page
exhaustion, non-progress failure, and inventory field preservation.

## Next decision

Create the keyboard/mouse profile as a Steam **Personal** layout, run the
on-device checklist, and only then consider preserving a sanitized exported VDF
as a follow-up artifact. Do not publish it until Our Red String's title-specific
skip, rollback, screenshot, and menu behavior has been verified.

## External primary sources

- [Valve: IPublishedFileService](https://partner.steamgames.com/doc/webapi/IPublishedFileService)
- [Valve: Web API Overview](https://partner.steamgames.com/doc/webapi_overview?language=english)
- [Valve: Browsing Configurations](https://partner.steamgames.com/doc/features/steam_controller/browse_configs?language=english)
- [Valve: General Concepts](https://partner.steamgames.com/doc/features/steam_controller/concepts?language=english)
- [Valve: Legacy Mode Bindings](https://partner.steamgames.com/doc/features/steam_controller/legacy_mode?language=english)
- [Valve: Steam Controller (2015)](https://partner.steamgames.com/doc/features/steam_controller/device/steam_controller?language=english)
- [Ren'Py: Customizing the Keymap](https://www.renpy.org/doc/html/keymap.html)
- [Ren'Py: Saving, Loading, and Rollback](https://www.renpy.org/doc/html/save_load_rollback.html)
