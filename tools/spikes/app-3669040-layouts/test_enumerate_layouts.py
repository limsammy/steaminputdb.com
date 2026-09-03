import json
import unittest
from datetime import datetime, timezone

import enumerate_layouts as subject


def response(body, status=200):
    return subject.HTTPResult(
        status=status,
        headers={"content-type": "application/json", "date": "Thu, 03 Sep 2026 00:00:00 GMT"},
        body=json.dumps(body, separators=(",", ":")).encode(),
        retrieved_at=datetime.now(timezone.utc).isoformat(),
    )


class ParseSearchBodyTests(unittest.TestCase):
    def test_empty_object_is_a_valid_zero_result(self):
        shape, total, items, keys = subject.parse_search_body({})

        self.assertEqual(shape, "empty_object")
        self.assertEqual(total, 0)
        self.assertEqual(items, [])
        self.assertEqual(keys, [])

    def test_rejects_invalid_items_shape(self):
        with self.assertRaisesRegex(ValueError, "items"):
            subject.parse_search_body({"total": 1, "items": {}})


class EnumerationTests(unittest.TestCase):
    def test_pages_until_reported_total_is_exhausted(self):
        pages = iter(
            [
                response({"total": 3, "items": [{"file_id": 11}, {"file_id": 12}]}),
                response({"total": 3, "items": [{"file_id": 13}]}),
            ]
        )

        items, observations = subject.enumerate_one_filter(
            lambda _payload: next(pages),
            app_id="3669040",
            controller_type=None,
            limit=2,
        )

        self.assertEqual([item["file_id"] for item in items], [11, 12, 13])
        self.assertEqual([item["page"] for item in observations], [1, 2])

    def test_stops_if_api_claims_more_results_but_returns_no_items(self):
        with self.assertRaisesRegex(RuntimeError, "returned no items"):
            subject.enumerate_one_filter(
                lambda _payload: response({"total": 1, "items": []}),
                app_id="3669040",
                controller_type="controller_steamcontroller_gordon",
                limit=100,
            )

    def test_inventory_preserves_requested_fields(self):
        item = subject.inventory_item(
            {
                "file_id": 99,
                "title": "Layout",
                "description": "Description",
                "controller_type": "controller_steamcontroller_gordon",
                "controller_type_nice": "Steam Controller (2015)",
                "creator_id": "public-creator-id",
                "time_created": "2026-01-01T00:00:00Z",
                "time_updated": "2026-02-01T00:00:00Z",
                "subscriptions": 4,
                "votes": {"up": 3, "down": 1, "score": 0.75},
                "file_url": "https://cdn.example/config.vdf",
            },
            retrieved_at="2026-09-03T00:00:00Z",
        )

        self.assertEqual(item["file_id"], "99")
        self.assertEqual(item["subscriptions"], 4)
        self.assertEqual(item["votes"]["up"], 3)
        self.assertEqual(
            item["workshop_url"],
            "https://steamcommunity.com/sharedfiles/filedetails/?id=99",
        )


if __name__ == "__main__":
    unittest.main()
