#!/usr/bin/env python3
"""Behavioral tests for the fail-closed Gumroad publication gate."""

from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "gumroad_publish.py"
SPEC = importlib.util.spec_from_file_location("gumroad_publish", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class FakeAPI:
    def __init__(self, files: list[dict] | None, *, lose_files=False):
        self.files = files
        self.lose_files = lose_files
        self.published = False
        self.enable_calls = 0
        self.disable_calls = 0
        self.metadata_updates = 0

    def __call__(self, _token, method, path, **fields):
        if method == "GET":
            files = [] if self.lose_files and self.metadata_updates else self.files
            return 200, {"product": {
                "files": files,
                "published": self.published,
                "short_url": "https://example.gumroad.com/l/test",
                "price": 38000,
                "formatted_price": "¥38,000",
            }}
        if path.endswith("/enable"):
            self.enable_calls += 1
            self.published = True
            return 200, {"success": True}
        if path.endswith("/disable"):
            self.disable_calls += 1
            self.published = False
            return 200, {"success": True}
        assert method == "PUT"
        assert "url" not in fields and "delivery_url" not in fields
        self.metadata_updates += 1
        return 200, {"success": True}


def run() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "--existing-product-id" in source
    assert "--test-purchase-confirmed" in source
    assert "--delivery-url" not in source
    assert "POST\", \"/products" not in source

    original_call = MODULE.call
    original_verify = MODULE.verify_public
    try:
        unconfirmed = FakeAPI([{"id": "file-1"}])
        MODULE.call = unconfirmed
        result = MODULE.publish_existing(
            "token", "product", MODULE.PRODUCTS["extended"], test_purchase_confirmed=False
        )
        assert result["status"] == "aborted_test_purchase_not_confirmed"
        assert unconfirmed.metadata_updates == 0 and unconfirmed.enable_calls == 0

        missing = FakeAPI([])
        MODULE.call = missing
        result = MODULE.publish_existing(
            "token", "product", MODULE.PRODUCTS["extended"], test_purchase_confirmed=True
        )
        assert result["status"] == "aborted_not_ready"
        assert missing.metadata_updates == 0 and missing.enable_calls == 0

        lost = FakeAPI([{"id": "file-1"}], lose_files=True)
        MODULE.call = lost
        result = MODULE.publish_existing(
            "token", "product", MODULE.PRODUCTS["extended"], test_purchase_confirmed=True
        )
        assert result["status"] == "aborted_content_missing_before_enable"
        assert lost.enable_calls == 0

        live = FakeAPI([{"id": "file-1"}])
        MODULE.call = live
        MODULE.verify_public = lambda _url: (200, True)
        result = MODULE.publish_existing(
            "token", "product", MODULE.PRODUCTS["extended"], test_purchase_confirmed=True
        )
        assert result["status"] == "published_verified"
        assert result["attached_file_count"] == 1
        assert live.enable_calls == 1 and live.disable_calls == 0

        public_fail = FakeAPI([{"id": "file-1"}])
        MODULE.call = public_fail
        MODULE.verify_public = lambda _url: (503, False)
        result = MODULE.publish_existing(
            "token", "product", MODULE.PRODUCTS["extended"], test_purchase_confirmed=True
        )
        assert result["status"] == "verification_failed_disabled"
        assert public_fail.enable_calls == 1 and public_fail.disable_calls == 1
    finally:
        MODULE.call = original_call
        MODULE.verify_public = original_verify

    print("gumroad publish safety tests passed (5 scenarios)")


if __name__ == "__main__":
    run()
