#!/usr/bin/env python3
"""Enumerate SteamInputDB layouts for one app without using the controller UI."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError
from urllib.request import Request, urlopen


DEFAULT_API_URL = "https://api.steaminputdb.com/v1/search/configs"
DEFAULT_PAGE_URL = "https://www.steaminputdb.com/app/{app_id}"
DEFAULT_FILTER_FILE = Path(__file__).with_name("controller-filters.json")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class ControllerInputParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.controller_types: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "input":
            return
        values = dict(attrs)
        if values.get("name") != "controller_type":
            return
        controller_type = values.get("value")
        if controller_type and controller_type not in self.controller_types:
            self.controller_types.append(controller_type)


@dataclass(frozen=True)
class HTTPResult:
    status: int
    headers: dict[str, str]
    body: bytes
    retrieved_at: str


def http_request(url: str, *, payload: dict[str, Any] | None, timeout: float) -> HTTPResult:
    data = None
    headers = {"Accept": "application/json"}
    method = "GET"
    if payload is not None:
        data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"
        method = "POST"
    request = Request(url, data=data, headers=headers, method=method)
    retrieved_at = utc_now()
    try:
        with urlopen(request, timeout=timeout) as response:
            return HTTPResult(
                status=response.status,
                headers={key.lower(): value for key, value in response.headers.items()},
                body=response.read(),
                retrieved_at=retrieved_at,
            )
    except HTTPError as error:
        return HTTPResult(
            status=error.code,
            headers={key.lower(): value for key, value in error.headers.items()},
            body=error.read(),
            retrieved_at=retrieved_at,
        )


def request_body(app_id: str, page: int, limit: int, controller_type: str | None) -> dict[str, Any]:
    tags = [controller_type] if controller_type else []
    return {
        "limit": limit,
        "page": page,
        "query_text": "",
        "raw": False,
        "rank": {"by": "vote", "trending_period": 30},
        "filter": {"app_id": app_id, "tags": tags, "excluded_tags": []},
        "include": {"votes": True, "tags": True},
    }


def parse_search_body(body: Any) -> tuple[str, int, list[dict[str, Any]], list[str]]:
    if not isinstance(body, dict):
        raise ValueError("search response must be a JSON object")
    shape = "empty_object" if not body else "mapped_response"
    total = body.get("total", 0)
    items = body.get("items", [])
    if not isinstance(total, int) or total < 0:
        raise ValueError("search response total must be a non-negative integer")
    if not isinstance(items, list) or not all(isinstance(item, dict) for item in items):
        raise ValueError("search response items must be an array of objects")
    return shape, total, items, sorted(body.keys())


def observation(
    result: HTTPResult,
    *,
    controller_type: str | None,
    page: int,
    limit: int,
    shape: str,
    total: int,
    item_count: int,
    response_keys: list[str],
) -> dict[str, Any]:
    return {
        "controller_type": controller_type,
        "page": page,
        "requested_page_size": limit,
        "http_status": result.status,
        "content_type": result.headers.get("content-type"),
        "server_date": result.headers.get("date"),
        "retrieved_at": result.retrieved_at,
        "response_body_shape": shape,
        "response_keys": response_keys,
        "reported_total": total,
        "items_returned": item_count,
        "response_bytes": len(result.body),
        "response_sha256": hashlib.sha256(result.body).hexdigest(),
        "empty_response_body": result.body.decode("utf-8") if shape == "empty_object" else None,
    }


FetchPage = Callable[[dict[str, Any]], HTTPResult]


def enumerate_one_filter(
    fetch_page: FetchPage,
    *,
    app_id: str,
    controller_type: str | None,
    limit: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    page = 1
    all_items: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    while True:
        payload = request_body(app_id, page, limit, controller_type)
        result = fetch_page(payload)
        if result.status != 200:
            raise RuntimeError(
                f"search failed for controller={controller_type!r} page={page}: HTTP {result.status}"
            )
        try:
            decoded = json.loads(result.body)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"search returned invalid JSON for controller={controller_type!r} page={page}"
            ) from error
        shape, total, items, response_keys = parse_search_body(decoded)
        observations.append(
            observation(
                result,
                controller_type=controller_type,
                page=page,
                limit=limit,
                shape=shape,
                total=total,
                item_count=len(items),
                response_keys=response_keys,
            )
        )
        all_items.extend(items)
        if len(all_items) >= total:
            return all_items, observations
        if not items:
            raise RuntimeError(
                f"search reported total={total} but returned no items for "
                f"controller={controller_type!r} page={page}"
            )
        page += 1


def inventory_item(item: dict[str, Any], *, retrieved_at: str) -> dict[str, Any]:
    file_id = item.get("file_id")
    if file_id is None:
        raise ValueError("a returned layout is missing file_id and cannot be deduplicated")
    return {
        "file_id": str(file_id),
        "title": item.get("title"),
        "description": item.get("description"),
        "controller_type": item.get("controller_type"),
        "controller_type_name": item.get("controller_type_nice"),
        "creator": item.get("creator_id"),
        "time_created": item.get("time_created"),
        "time_updated": item.get("time_updated"),
        "subscriptions": item.get("subscriptions"),
        "votes": item.get("votes"),
        "file_url": item.get("file_url"),
        "workshop_url": f"https://steamcommunity.com/sharedfiles/filedetails/?id={file_id}",
        "source": "SteamInputDB public /v1/search/configs",
        "retrieved_at": retrieved_at,
        "discovered_by": [],
    }


def load_filters(path: Path) -> list[dict[str, str]]:
    filters = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(filters, list):
        raise ValueError("controller filter file must contain an array")
    seen: set[str] = set()
    result: list[dict[str, str]] = []
    for entry in filters:
        if not isinstance(entry, dict) or not isinstance(entry.get("type"), str):
            raise ValueError("each controller filter needs a string type")
        if entry["type"] in seen:
            raise ValueError(f"duplicate controller filter: {entry['type']}")
        seen.add(entry["type"])
        result.append({"type": entry["type"], "name": str(entry.get("name", ""))})
    return result


def page_observation(url: str, timeout: float) -> dict[str, Any]:
    result = http_request(url, payload=None, timeout=timeout)
    parser = ControllerInputParser()
    text = result.body.decode("utf-8", errors="replace")
    parser.feed(text)
    return {
        "url": url,
        "http_status": result.status,
        "content_type": result.headers.get("content-type"),
        "server_date": result.headers.get("date"),
        "retrieved_at": result.retrieved_at,
        "response_bytes": len(result.body),
        "response_sha256": hashlib.sha256(result.body).hexdigest(),
        "server_rendered_no_results": "No results found" in text,
        "server_rendered_controller_filters": parser.controller_types,
        "note": "The server render contains the default-visible filters; Show More is client-rendered.",
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(path)


def portable_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return path.name


def run(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    filters = load_filters(args.controller_filters)
    started_at = utc_now()
    page_url = args.page_url.format(app_id=args.app_id)
    live_page = None if args.skip_page_check else page_observation(page_url, args.timeout)
    if live_page and live_page["http_status"] != 200:
        raise RuntimeError(f"app page check failed: HTTP {live_page['http_status']}")

    def fetch(payload: dict[str, Any]) -> HTTPResult:
        controller = payload["filter"]["tags"]
        label = controller[0] if controller else "unfiltered"
        print(f"querying {label} page {payload['page']}", file=sys.stderr)
        return http_request(args.api_url, payload=payload, timeout=args.timeout)

    queries: list[dict[str, Any]] = []
    deduplicated: dict[str, dict[str, Any]] = {}
    for controller_type in [None, *(entry["type"] for entry in filters)]:
        items, current_observations = enumerate_one_filter(
            fetch,
            app_id=args.app_id,
            controller_type=controller_type,
            limit=args.limit,
        )
        queries.extend(current_observations)
        discovery_label = controller_type or "unfiltered"
        for raw_item in items:
            item = inventory_item(raw_item, retrieved_at=started_at)
            existing = deduplicated.setdefault(item["file_id"], item)
            if discovery_label not in existing["discovered_by"]:
                existing["discovered_by"].append(discovery_label)

    completed_at = utc_now()
    inventory = {
        "schema_version": 1,
        "app_id": args.app_id,
        "layout_count": len(deduplicated),
        "retrieved_at": started_at,
        "source": args.api_url,
        "deduplicated_by": "file_id",
        "layouts": sorted(deduplicated.values(), key=lambda item: int(item["file_id"])),
    }
    evidence = {
        "schema_version": 1,
        "app_id": args.app_id,
        "started_at": started_at,
        "completed_at": completed_at,
        "api_url": args.api_url,
        "request_page_size": args.limit,
        "request_template": request_body(args.app_id, 1, args.limit, None),
        "controller_filter_options": filters,
        "controller_filter_source": {
            "path": portable_path(args.controller_filters),
            "basis": "checked-in frontend CONTROLLER_LIST; live default-visible subset checked separately",
        },
        "app_page": live_page,
        "queries": queries,
        "summary": {
            "query_count": len(queries),
            "all_http_200": all(query["http_status"] == 200 for query in queries),
            "all_zero": all(query["reported_total"] == 0 for query in queries),
            "deduplicated_layout_count": len(deduplicated),
        },
    }
    return inventory, evidence


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app-id", default="3669040")
    parser.add_argument("--api-url", default=DEFAULT_API_URL)
    parser.add_argument("--page-url", default=DEFAULT_PAGE_URL)
    parser.add_argument("--controller-filters", type=Path, default=DEFAULT_FILTER_FILE)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--skip-page-check", action="store_true")
    parser.add_argument("--inventory-output", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    args = parser.parse_args(argv)
    if not 1 <= args.limit <= 100:
        parser.error("--limit must be between 1 and 100")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    inventory, evidence = run(args)
    write_json(args.inventory_output, inventory)
    write_json(args.evidence_output, evidence)
    print(
        f"wrote {inventory['layout_count']} layouts from {evidence['summary']['query_count']} queries",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
