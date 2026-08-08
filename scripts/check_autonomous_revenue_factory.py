#!/usr/bin/env python3
"""Validate the autonomous revenue-factory policy, config, and current state."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "autonomous_revenue_factory.json"
STATE_PATH = ROOT / "state" / "autonomous_revenue_factory.json"
POLICY_PATH = ROOT / "OPERATIONS" / "AUTONOMOUS_REVENUE_FACTORY.md"
REPORT_PATH = ROOT / "reports" / "autonomous_revenue_factory.json"


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def walk(value: Any, path: str = "$"):
    if isinstance(value, dict):
        for key, item in value.items():
            yield f"{path}.{key}", key, item
            yield from walk(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk(item, f"{path}[{index}]")


def main() -> int:
    errors: list[str] = []
    for path in (CONFIG_PATH, STATE_PATH, POLICY_PATH):
        if not path.is_file():
            errors.append(f"missing required file: {path.relative_to(ROOT)}")

    config = load_json(CONFIG_PATH) if CONFIG_PATH.is_file() else {}
    state = load_json(STATE_PATH) if STATE_PATH.is_file() else {}

    if config.get("enabled") is not True:
        errors.append("factory config must remain enabled")
    if state.get("enabled") is not True or state.get("status") != "active":
        errors.append("factory state must be active and enabled")
    if config.get("max_concurrent_builds") != 1:
        errors.append("max_concurrent_builds must equal 1")
    if config.get("state_path") != "state/autonomous_revenue_factory.json":
        errors.append("config state_path mismatch")
    if config.get("policy_path") != "OPERATIONS/AUTONOMOUS_REVENUE_FACTORY.md":
        errors.append("config policy_path mismatch")
    if state.get("cost_yen") != 0:
        errors.append("factory external cost must be zero")

    gate = config.get("autonomous_build_gate", {})
    expected_gate = {
        "additional_cost_yen_must_equal": 0,
        "requires_new_contract": False,
        "requires_identity_verification": False,
        "requires_payment_or_bank_details": False,
        "requires_tax_information": False,
        "uses_only_verified_source_facts": True,
        "contains_personal_or_secret_data": False,
        "build_and_link_qa_required": True,
        "rollback_or_disable_required": True,
        "other_existing_repository_write_allowed": False,
    }
    for key, expected in expected_gate.items():
        if gate.get(key) != expected:
            errors.append(f"autonomous_build_gate.{key} must equal {expected!r}")

    publication = config.get("publication_gate", {})
    if publication.get("provider_and_runtime_approval_required") is not True:
        errors.append("provider/runtime approval must be required for publication")
    if publication.get("retry_after_explicit_denial_without_new_authority") is not False:
        errors.append("publication denial must not be bypassed or retried without new authority")

    asset = state.get("first_asset", {})
    qa = asset.get("qa", {})
    if asset.get("deployment_status") != "succeeded":
        errors.append("first asset deployment must be recorded as succeeded")
    if not str(asset.get("url", "")).startswith("https://"):
        errors.append("first asset must have an HTTPS deployment URL")
    if asset.get("access_mode") not in {"custom", "public"}:
        errors.append("first asset access_mode must be custom or public")
    if asset.get("access_mode") == "public" and asset.get("publicly_accessible") is not True:
        errors.append("public access mode requires publicly_accessible=true")
    if asset.get("access_mode") != "public" and asset.get("publicly_accessible") is not False:
        errors.append("non-public access mode requires publicly_accessible=false")
    if asset.get("source_product", {}).get("item_id") != "8691522":
        errors.append("canonical BOOTH item ID mismatch")
    if asset.get("source_product", {}).get("price_yen") != 1480:
        errors.append("canonical BOOTH price mismatch")
    required_qa = (
        "build_passed",
        "deployment_succeeded",
        "html_lang_ja",
        "title_verified",
        "primary_cta_verified",
        "all_links_verified",
        "utm_verified",
        "mobile_overflow_absent",
    )
    for key in required_qa:
        if qa.get(key) is not True:
            errors.append(f"first_asset.qa.{key} must be true")
    if qa.get("site_content_contains_secrets_or_personal_data") is not False:
        errors.append("site content secret/PII scan must be false")

    optimization_version = asset.get("optimization_version")
    if not isinstance(optimization_version, int) or optimization_version < 1:
        errors.append("first_asset optimization_version must be a positive integer")
    else:
        latest_key = f"latest_v{optimization_version}_deployment"
        latest = asset.get(latest_key)
        if not isinstance(latest, dict):
            errors.append(f"first_asset.{latest_key} must exist")
        else:
            if asset.get("site_source_commit") != latest.get("source_commit"):
                errors.append("first_asset site_source_commit must match latest deployment")
            if asset.get("optimization_record") != latest.get("validation_record"):
                errors.append("first_asset optimization_record must match latest deployment")
            if qa.get("test_count") != latest.get("test_count"):
                errors.append("first_asset qa.test_count must match latest deployment")
            record = latest.get("validation_record")
            if not record or not (ROOT / str(record)).is_file():
                errors.append("latest deployment validation record must exist")

    forbidden_key_parts = ("password", "token", "cookie", "secret", "credential", "bearer")
    for path, key, value in walk(state):
        lowered = key.lower()
        if any(part in lowered for part in forbidden_key_parts) and value not in (False, None, ""):
            errors.append(f"forbidden secret-like state key at {path}")

    report = {
        "schema_version": "1.0",
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "checked_files": [
            str(POLICY_PATH.relative_to(ROOT)),
            str(CONFIG_PATH.relative_to(ROOT)),
            str(STATE_PATH.relative_to(ROOT)),
        ],
        "deployment_status": asset.get("deployment_status"),
        "access_mode": asset.get("access_mode"),
        "publicly_accessible": asset.get("publicly_accessible"),
        "cost_yen": state.get("cost_yen"),
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("autonomous revenue factory validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
