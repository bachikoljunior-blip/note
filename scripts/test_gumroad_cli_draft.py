#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "create_gumroad_draft.py"
CONFIG = ROOT / "config" / "gumroad_cli_draft.json"
REPORT = ROOT / "reports" / "gumroad_cli_draft.json"

EXPECTED_CLI_VERSION = "2026.08.06"
EXPECTED_CLI_SHA256 = "9808ce12419e65f4debd2dabd8edb4e221444258d04b1bebccdea7fcd8cba606"
EXPECTED_CONFIG_SHA256 = "722be093d1574075c8b94b7e33ff91454316e3a574175a3985464bfd01ee043f"
EXPECTED_SEMANTIC_PLAN_SHA256 = "2a055ecf17d9995c42eb76b6d904864833f846d5cc193e07bd4859cf4a473509"
EXPECTED_PRODUCT_BYTES = 97319
EXPECTED_PRODUCT_SHA256 = "3adb147dc55b671d99141281cc9849e3530a8865def543d341c326a54bcf0113"


def load_module():
    spec = importlib.util.spec_from_file_location("create_gumroad_draft", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot_load_create_gumroad_draft")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def expect_validation_error(module, label: str, callback) -> None:
    try:
        callback()
    except module.ValidationError:
        return
    raise AssertionError(label)


def dry_run_payload(module, expectation: dict) -> dict:
    file_id = "cli-upload-11111111-1111-4111-8111-111111111111"
    uid = "22222222-2222-4222-8222-222222222222"
    body = {
        "custom_permalink": expectation["custom_permalink"],
        "custom_summary": expectation["custom_summary"],
        "description": expectation["description_html"],
        "files": [{
            "display_name": expectation["product"]["display_name"],
            "id": file_id,
            "url": "<uploaded:file:0>",
        }],
        "name": expectation["title"],
        "native_type": expectation["type"],
        "price": str(expectation["price_minor_units"]),
        "price_currency_type": expectation["currency"],
        "refund_fine_print": expectation["refund_fine_print"],
        "refund_period": expectation["refund_period"],
        "rich_content": [{
            "description": {
                "content": [
                    {
                        "attrs": {"collapsed": False, "id": file_id, "uid": uid},
                        "type": "fileEmbed",
                    },
                    {"type": "paragraph"},
                ],
                "type": "doc",
            },
            "title": "Page 1",
        }],
        "tags": expectation["tags"],
    }
    return {
        "dry_run": True,
        "uploads": [module.expected_product_upload(expectation)]
        + [module.expected_media_upload(item) for item in expectation["media"]],
        "request": {"method": "POST", "path": "/products", "body": body},
        "follow_up_requests": module.expected_follow_ups(expectation),
    }


def view_payload(expectation: dict, product_id: str, *, published: bool = False) -> dict:
    return {
        "product": {
            "id": product_id,
            "name": expectation["title"],
            "published": published,
            "description": expectation["description_html"],
            "custom_summary": expectation["custom_summary"],
            "custom_permalink": expectation["custom_permalink"],
            "is_tiered_membership": False,
            "price": 1200,
            "currency": "usd",
            "tags": list(expectation["tags"]),
            "files": [{
                "name": expectation["product"]["display_name"],
                "size": expectation["product"]["bytes"],
            }],
            "refund_policy": {
                "refund_period": "7",
                "fine_print": expectation["refund_fine_print"],
                "inherited": False,
            },
            "covers": [{"id": "c1"}, {"id": "c2"}, {"id": "c3"}],
            "thumbnail_url": "https://example.invalid/thumb.png",
        }
    }


class QueueRunner:
    def __init__(self, module, results):
        self.module = module
        self.results = list(results)
        self.commands: list[list[str]] = []
        self.environments: list[dict[str, str]] = []

    def __call__(self, command: list[str], environment: dict[str, str], timeout: int):
        self.commands.append(command)
        self.environments.append(environment)
        assert timeout > 0
        if not self.results:
            raise AssertionError("unexpected_extra_command")
        result = self.results.pop(0)
        if isinstance(result, Exception):
            raise result
        return result


class JournalAwareRunner(QueueRunner):
    def __init__(self, module, results, journal_path: Path):
        super().__init__(module, results)
        self.journal_path = journal_path

    def __call__(self, command: list[str], environment: dict[str, str], timeout: int):
        if "create" in command:
            journal = self.module.read_attempt_journal(self.journal_path)
            assert journal is not None
            assert journal["resolved"] is False
            assert journal["status"] == "create_request_pending_reconciliation"
        return super().__call__(command, environment, timeout)


def json_result(module, value: dict, returncode: int = 0, stderr: str = ""):
    return module.ProcessResult(returncode, json.dumps(value), stderr)


def isolated_execute(module, cli, command, environment, expectation, runner):
    with tempfile.TemporaryDirectory() as temporary:
        private = Path(temporary)
        return module.execute_with_reconciliation(
            cli,
            command,
            environment,
            expectation,
            runner,
            lock_path=private / "execute.lock",
            journal_path=private / "attempt.json",
        )


def main() -> int:
    module = load_module()
    assert module.OFFICIAL_CLI_VERSION == EXPECTED_CLI_VERSION
    assert module.OFFICIAL_CLI_SHA256 == EXPECTED_CLI_SHA256
    assert module.CANONICAL_CONFIG_SHA256 == EXPECTED_CONFIG_SHA256
    config, config_sha256 = module.load_config_once(CONFIG, execute=True)
    assert config_sha256 == EXPECTED_CONFIG_SHA256
    cli = Path("/private/pinned/gumroad")
    with tempfile.TemporaryDirectory() as dry_stage, tempfile.TemporaryDirectory() as execute_stage, tempfile.TemporaryDirectory() as alternate_stage:
        dry_command, expectation = module.build_command(
            cli, config, execute=False, private_root=Path(dry_stage)
        )
        execute_command, execute_expectation = module.build_command(
            cli, config, execute=True, private_root=Path(execute_stage)
        )
        _, alternate_expectation = module.build_command(
            Path("/different/checkout/pinned/gumroad"),
            config,
            execute=False,
            private_root=Path(alternate_stage),
        )

    assert "--dry-run" in dry_command
    assert "--dry-run" not in execute_command
    assert expectation["semantic_plan_sha256"] == execute_expectation["semantic_plan_sha256"]
    assert expectation["semantic_plan_sha256"] == alternate_expectation["semantic_plan_sha256"]
    assert expectation["semantic_plan_sha256"] == EXPECTED_SEMANTIC_PLAN_SHA256
    assert expectation["product"]["bytes"] == EXPECTED_PRODUCT_BYTES
    assert expectation["product"]["sha256"] == EXPECTED_PRODUCT_SHA256
    recorded_report = json.loads(REPORT.read_text(encoding="utf-8"))
    assert recorded_report["cli_version"] == EXPECTED_CLI_VERSION
    assert recorded_report["cli_binary_sha256"] == EXPECTED_CLI_SHA256
    assert recorded_report["canonical_config_sha256"] == EXPECTED_CONFIG_SHA256
    assert recorded_report["inputs"]["semantic_plan_sha256"] == EXPECTED_SEMANTIC_PLAN_SHA256
    assert recorded_report["inputs"]["product"]["bytes"] == EXPECTED_PRODUCT_BYTES
    assert recorded_report["inputs"]["product"]["sha256"] == EXPECTED_PRODUCT_SHA256
    assert recorded_report["ok"] is True
    assert recorded_report["mode"] == "dry_run"
    assert recorded_report["status"] == "full_exact_dry_run_passed"
    assert recorded_report["dry_run_flag_present"] is True
    assert recorded_report["errors"] == []
    assert recorded_report["official_cli_auth_used"] is False
    assert recorded_report["authenticated_api_request_used"] is False
    assert recorded_report["authenticated_api_request_succeeded"] is False
    assert recorded_report["authenticated_write_attempted"] is False
    assert recorded_report["authenticated_write_performed"] is False
    assert recorded_report["publication_attempted"] is False
    assert recorded_report["authentication_flow_started"] is False
    assert "authentication_started" not in recorded_report
    report_cli_output = recorded_report["cli_output"]
    assert report_cli_output["dry_run"] is True
    assert report_cli_output["exact_request_body_validated"] is True
    assert report_cli_output["rich_content_file_id_relation_validated"] is True
    assert len(report_cli_output["follow_up_requests"]) == 8
    assert "--custom-permalink" in dry_command
    assert dry_command[dry_command.index("--custom-permalink") + 1] == "non-repetitive-ai-trivia-shorts-kit"
    for command in (dry_command, execute_command):
        products_index = command.index("products")
        assert command[products_index : products_index + 2] == ["products", "create"]
        assert command[command.index("--refund-period") + 1] == "7"
        assert command.count("--file") == 1
        assert command.count("--cover-image") == 1
        assert command.count("--preview-image") == 2
        assert command.count("--thumbnail") == 1
        assert all(token not in command for token in ("publish", "unpublish", "delete", "update"))

    # A config cannot approve an arbitrary CLI. The binary digest and version
    # are script constants, and self-approval keys invalidate the config.
    evil_config = deepcopy(config)
    evil_config["cli"]["approved_linux_amd64_sha256"] = ["0" * 64]
    expect_validation_error(
        module,
        "self_approved_cli_config_not_rejected",
        lambda: module.validate_config_shape(evil_config),
    )
    evil_report = deepcopy(config)
    evil_report["report_path"] = "reports/attacker.json"
    expect_validation_error(
        module,
        "config_controlled_report_path_not_rejected",
        lambda: module.validate_config_shape(evil_report),
    )
    bad_product = deepcopy(config)
    bad_product["product"]["sha256"] = "0" * 64
    with tempfile.TemporaryDirectory() as temporary:
        expect_validation_error(
            module,
            "product_hash_mutation_not_rejected",
            lambda: module.build_command(
                cli, bad_product, execute=False, private_root=Path(temporary)
            ),
        )
    bad_media = deepcopy(config)
    bad_media["visuals"][0]["sha256"] = "0" * 64
    with tempfile.TemporaryDirectory() as temporary:
        expect_validation_error(
            module,
            "media_hash_mutation_not_rejected",
            lambda: module.build_command(
                cli, bad_media, execute=False, private_root=Path(temporary)
            ),
        )
    with tempfile.TemporaryDirectory() as temporary:
        fake_cli = Path(temporary) / "gumroad"
        fake_cli.write_bytes(b"#!/bin/sh\necho fake\n")
        fake_cli.chmod(0o700)
        expect_validation_error(
            module,
            "fake_cli_not_rejected",
            lambda: module.pinned_cli_copy(str(fake_cli)).__enter__(),
        )
        evil_path = Path(temporary) / "config.json"
        evil_path.write_text(json.dumps(evil_config), encoding="utf-8")
        expect_validation_error(
            module,
            "noncanonical_execute_config_not_rejected",
            lambda: module.load_config_once(evil_path, execute=False),
        )
        state_target = Path(temporary) / "real-state.json"
        state_target.write_text("{}", encoding="utf-8")
        state_symlink = Path(temporary) / "state-link.json"
        state_symlink.symlink_to(state_target)
        expect_validation_error(
            module,
            "atomic_state_symlink_not_rejected",
            lambda: module.atomic_write_json(state_symlink, {"ok": True}, 0o600),
        )

    # Full dry-run shape accepts the exact plan and rejects even one omitted
    # listing field or one missing media follow-up request.
    exact_dry = dry_run_payload(module, expectation)
    exact_result = json_result(module, exact_dry)
    exact_summary = module.validate_dry_run_output(exact_result, expectation)
    assert exact_summary["exact_request_body_validated"] is True
    missing_description = deepcopy(exact_dry)
    del missing_description["request"]["body"]["description"]
    expect_validation_error(
        module,
        "dry_run_missing_description_not_rejected",
        lambda: module.validate_dry_run_output(json_result(module, missing_description), expectation),
    )
    missing_follow_up = deepcopy(exact_dry)
    missing_follow_up["follow_up_requests"].pop()
    expect_validation_error(
        module,
        "dry_run_missing_follow_up_not_rejected",
        lambda: module.validate_dry_run_output(json_result(module, missing_follow_up), expectation),
    )

    # Execute responses and the read-only view must both independently prove
    # unpublished state; refund policy omission is fail-closed.
    create_ok = {
        "product": {
            "id": "prod_new",
            "name": expectation["title"],
            "published": False,
        }
    }
    assert module.validate_create_response(create_ok, expectation) == "prod_new"
    padded_product_id = "AbCdEf_0123456789=="
    create_padded = deepcopy(create_ok)
    create_padded["product"]["id"] = padded_product_id
    assert module.validate_create_response(create_padded, expectation) == padded_product_id
    assert module.view_command(cli, padded_product_id)[-1] == padded_product_id
    assert module.view_command(cli, "A" * 128)[-1] == "A" * 128
    assert module.view_command(cli, "A" * 126 + "==")[-1] == "A" * 126 + "=="
    expect_validation_error(
        module,
        "middle_product_id_padding_not_rejected",
        lambda: module.view_command(cli, "AbCd=Ef"),
    )
    expect_validation_error(
        module,
        "overlong_product_id_not_rejected",
        lambda: module.view_command(cli, "A" * 129),
    )
    create_missing_published = deepcopy(create_ok)
    del create_missing_published["product"]["published"]
    expect_validation_error(
        module,
        "missing_create_published_not_rejected",
        lambda: module.validate_create_response(create_missing_published, expectation),
    )
    create_published = deepcopy(create_ok)
    create_published["product"]["published"] = True
    expect_validation_error(
        module,
        "published_create_response_not_rejected",
        lambda: module.validate_create_response(create_published, expectation),
    )
    missing_refund = view_payload(expectation, "prod_new")
    del missing_refund["product"]["refund_policy"]
    expect_validation_error(
        module,
        "missing_refund_policy_not_rejected",
        lambda: module.validate_product_view(missing_refund, "prod_new", expectation),
    )
    published_view = view_payload(expectation, "prod_new", published=True)
    expect_validation_error(
        module,
        "published_view_not_rejected",
        lambda: module.validate_product_view(published_view, "prod_new", expectation),
    )
    reordered_tags = view_payload(expectation, "prod_new")
    reordered_tags["product"]["tags"] = list(reversed(expectation["tags"]))
    reordered_summary = module.validate_product_view(
        reordered_tags, "prod_new", expectation
    )
    assert set(reordered_summary["tags"]) == set(expectation["tags"])
    duplicate_tags = view_payload(expectation, "prod_new")
    duplicate_tags["product"]["tags"][-1] = duplicate_tags["product"]["tags"][0]
    expect_validation_error(
        module,
        "duplicate_or_missing_remote_tag_not_rejected",
        lambda: module.validate_product_view(duplicate_tags, "prod_new", expectation),
    )

    # Failure diagnostics never persist authenticated or signed HTTP(S) URLs.
    signed_url = (
        "https://s3.example.invalid/file?X-Amz-Credential=AKIA"
        "&X-Amz-Signature=ULTRASECRET&X-Amz-Security-Token=SESSION#fragment"
    )
    generic_token_url = "https://example.invalid/download?token=ONETIMESECRET"
    redacted = module.redact_and_limit(f"first={signed_url} second={generic_token_url}")
    for secret in ("AKIA", "ULTRASECRET", "SESSION", "ONETIMESECRET", "https://"):
        assert secret not in redacted
    assert redacted.count("[REDACTED_URL]") == 2
    leaking_view = view_payload(expectation, "prod_new")
    leaking_view["product"]["files"][0]["url"] = signed_url
    del leaking_view["product"]["refund_policy"]
    leaking_runner = QueueRunner(module, [json_result(module, leaking_view)])
    _, leaking_error = module.read_product_view(
        cli, "prod_new", {"HOME": "/unused"}, expectation, leaking_runner
    )
    assert leaking_error is not None
    leaking_error_json = json.dumps(leaking_error)
    assert "ULTRASECRET" not in leaking_error_json
    assert "X-Amz" not in leaking_error_json
    signed_blob_capability = "BLOB-CAPABILITY-VERY-SECRET=="
    recovery_signed_id = "RECOVERY-CAPABILITY-VERY-SECRET=="
    capability_output = json.dumps({
        "upload": {"signed_blob_id": signed_blob_capability},
        "recovery": {"signed_id": recovery_signed_id},
    })
    capability_diagnostics = module.diagnostics(
        module.ProcessResult(1, capability_output, "signed-id=SECOND-RECOVERY-SECRET")
    )
    capability_json = json.dumps(capability_diagnostics)
    for secret in (
        signed_blob_capability,
        recovery_signed_id,
        "SECOND-RECOVERY-SECRET",
    ):
        assert secret not in capability_json
    assert capability_json.count("[REDACTED]") >= 3

    # Environment allowlists exclude API-base overrides, proxies, CA bundle
    # injection, loader injection, and environment tokens.
    with tempfile.TemporaryDirectory() as temporary:
        private_root = Path(temporary)
        isolated = module.make_isolated_environment(private_root)
        assert set(isolated) == module.EXECUTE_ENV_KEYS
        assert Path(isolated["HOME"]).parent == private_root
        assert Path(isolated["XDG_CONFIG_HOME"]).parent == private_root
        host_home = private_root / "saved-home"
        host_home.mkdir()
        poisoned = {
            "HOME": str(host_home),
            "XDG_CONFIG_HOME": str(host_home / "xdg"),
            "GUMROAD_ACCESS_TOKEN": "secret-token",
            "GUMROAD_API_BASE_URL": "https://evil.invalid",
            "HTTP_PROXY": "https://evil.invalid",
            "HTTPS_PROXY": "https://evil.invalid",
            "ALL_PROXY": "socks5://evil.invalid",
            "NO_PROXY": "*",
            "SSL_CERT_FILE": "/evil/ca",
            "SSL_CERT_DIR": "/evil/cadir",
            "REQUESTS_CA_BUNDLE": "/evil/requests-ca",
            "LD_PRELOAD": "/evil/preload.so",
            "LD_LIBRARY_PATH": "/evil/lib",
        }
        with patch.dict(os.environ, poisoned, clear=True):
            execute_env = module.make_execute_environment()
        assert set(execute_env) == module.EXECUTE_ENV_KEYS
        assert execute_env["HOME"] == str(host_home)
        assert execute_env["XDG_CONFIG_HOME"] == str(host_home / "xdg")
        assert not set(poisoned).intersection(execute_env) - {"HOME", "XDG_CONFIG_HOME"}

    safe_env = {"HOME": "/saved/home", "XDG_CONFIG_HOME": "/saved/home/.config", **module.LOCALE_ENV}

    failed_preflight_runner = QueueRunner(module, [
        module.ProcessResult(1, "", "saved authentication failed"),
    ])
    failed_preflight = isolated_execute(
        module,
        cli,
        execute_command,
        safe_env,
        expectation,
        failed_preflight_runner,
    )
    assert failed_preflight["authenticated_cli_command_attempted"] is True
    assert failed_preflight["official_cli_auth_used"] is None
    assert failed_preflight["authenticated_api_request_used"] is None
    assert failed_preflight["authenticated_api_request_succeeded"] is None
    assert failed_preflight["create_attempted"] is False

    # An existing canonical slug is viewed, duplicate creation is blocked, and
    # unverifiable remote file/image hashes force manual review.
    existing_list = {
        "products": [{
            "id": "prod_existing",
            "name": expectation["title"],
            "published": False,
            "custom_permalink": expectation["custom_permalink"],
        }]
    }
    existing_runner = QueueRunner(module, [
        json_result(module, existing_list),
        json_result(module, view_payload(expectation, "prod_existing")),
    ])
    existing_outcome = isolated_execute(
        module,
        cli, execute_command, safe_env, expectation, existing_runner
    )
    assert existing_outcome["ok"] is False
    assert existing_outcome["needs_manual_review"] is True
    assert existing_outcome["status"] == "existing_potential_duplicate_metadata_matches_but_remote_artifact_hashes_unverifiable"
    assert existing_outcome["duplicate_create_prevented"] is True
    assert existing_outcome["create_attempted"] is False
    assert len(existing_runner.commands) == 2
    assert all("create" not in command for command in existing_runner.commands)

    # A clean create is followed by a read-only view using the exact same
    # pinned CLI path and validates the complete product contract.
    clean_runner = QueueRunner(module, [
        json_result(module, {"products": []}),
        json_result(module, create_ok),
        json_result(module, view_payload(expectation, "prod_new")),
    ])
    clean_outcome = isolated_execute(
        module,
        cli, execute_command, safe_env, expectation, clean_runner
    )
    assert clean_outcome["ok"] is True
    assert clean_outcome["status"] == "created_and_verified_exact_unpublished_draft"
    assert [command[0] for command in clean_runner.commands] == [str(cli)] * 3
    assert sum("create" in command for command in clean_runner.commands) == 1
    assert "view" in clean_runner.commands[-1]
    assert clean_outcome["attempt_journal"]["resolved"] is True

    # A local spawn/resource failure after a valid create response is converted
    # into a truthful manual-review result. The product ID was already durably
    # journaled, so a later invocation cannot duplicate the product.
    with tempfile.TemporaryDirectory() as temporary:
        private = Path(temporary)
        post_create_runner = QueueRunner(module, [
            json_result(module, {"products": []}),
            json_result(module, create_ok),
            OSError("simulated post-create spawn failure"),
        ])
        post_create_failure = module.execute_with_reconciliation(
            cli,
            execute_command,
            safe_env,
            expectation,
            post_create_runner,
            lock_path=private / "execute.lock",
            journal_path=private / "attempt.json",
        )
        post_create_journal = module.read_attempt_journal(private / "attempt.json")
        assert post_create_failure["ok"] is False
        assert post_create_failure["needs_manual_review"] is True
        assert post_create_failure["authenticated_write_performed"] is True
        assert post_create_failure["product_id"] == "prod_new"
        assert post_create_journal["resolved"] is False
        assert post_create_journal["product_id"] == "prod_new"
        assert post_create_journal["status"] == "post_create_view_failed_manual_review"
        assert "simulated post-create spawn failure" in json.dumps(post_create_failure)

    # A durable-write failure while marking a verified journal resolved cannot
    # erase the known product facts or turn the result into a false success.
    with tempfile.TemporaryDirectory() as temporary:
        private = Path(temporary)
        original_update = module.update_attempt_journal

        def fail_resolution_write(path, journal, *, status_value, resolved, product_id=None):
            if status_value == "verified_unpublished_draft_created":
                raise OSError("simulated journal fsync failure")
            return original_update(
                path,
                journal,
                status_value=status_value,
                resolved=resolved,
                product_id=product_id,
            )

        journal_failure_runner = QueueRunner(module, [
            json_result(module, {"products": []}),
            json_result(module, create_ok),
            json_result(module, view_payload(expectation, "prod_new")),
        ])
        with patch.object(module, "update_attempt_journal", side_effect=fail_resolution_write):
            journal_failure = module.execute_with_reconciliation(
                cli,
                execute_command,
                safe_env,
                expectation,
                journal_failure_runner,
                lock_path=private / "execute.lock",
                journal_path=private / "attempt.json",
            )
        unresolved_after_fsync = module.read_attempt_journal(private / "attempt.json")
        assert journal_failure["ok"] is False
        assert journal_failure["needs_manual_review"] is True
        assert journal_failure["status"] == "created_and_verified_but_attempt_journal_resolution_failed"
        assert journal_failure["authenticated_write_performed"] is True
        assert journal_failure["product_id"] == "prod_new"
        assert "simulated journal fsync failure" in journal_failure["attempt_journal_update_error"]
        assert unresolved_after_fsync["resolved"] is False
        assert unresolved_after_fsync["product_id"] == "prod_new"

    # Media/command failure may have created a partial draft. Reconcile once,
    # never retry create, and fail for manual review when exact view validation
    # is impossible.
    partial_list = {
        "products": [{
            "id": "prod_partial",
            "custom_permalink": expectation["custom_permalink"],
            "published": False,
        }]
    }
    partial_view = view_payload(expectation, "prod_partial")
    partial_view["product"]["covers"] = [{"id": "only-one"}]
    partial_runner = QueueRunner(module, [
        json_result(module, {"products": []}),
        module.ProcessResult(1, "", "access_token=super-secret media failed"),
        json_result(module, partial_list),
        json_result(module, partial_view),
    ])
    partial_outcome = isolated_execute(
        module,
        cli, execute_command, safe_env, expectation, partial_runner
    )
    assert partial_outcome["ok"] is False
    assert partial_outcome["needs_manual_review"] is True
    assert partial_outcome["product_id"] == "prod_partial"
    assert partial_outcome["automatic_create_retries"] == 0
    assert sum("create" in command for command in partial_runner.commands) == 1
    assert "super-secret" not in json.dumps(partial_outcome)

    # A nonzero create whose exact metadata is observed still requires manual
    # review because a later read cannot prove remote file/image hashes.
    reconciled_runner = QueueRunner(module, [
        json_result(module, {"products": []}),
        module.ProcessResult(1, "", "media response lost"),
        json_result(module, partial_list),
        json_result(module, view_payload(expectation, "prod_partial")),
    ])
    reconciled_outcome = isolated_execute(
        module,
        cli, execute_command, safe_env, expectation, reconciled_runner
    )
    assert reconciled_outcome["ok"] is False
    assert reconciled_outcome["needs_manual_review"] is True
    assert reconciled_outcome["status"] == "create_failed_reconciliation_metadata_matches_but_remote_artifact_hashes_unverifiable"
    assert sum("create" in command for command in reconciled_runner.commands) == 1

    # Gumroad may normalize or suffix a requested slug. The exact product name
    # is an independent duplicate signal: view it and never create another.
    normalized_slug_list = {
        "products": [{
            "id": "prod_normalized",
            "name": expectation["title"],
            "custom_permalink": expectation["custom_permalink"] + "-2",
            "published": False,
        }]
    }
    normalized_slug_view = view_payload(expectation, "prod_normalized")
    normalized_slug_view["product"]["custom_permalink"] += "-2"
    normalized_runner = QueueRunner(module, [
        json_result(module, normalized_slug_list),
        json_result(module, normalized_slug_view),
    ])
    normalized_outcome = isolated_execute(
        module, cli, execute_command, safe_env, expectation, normalized_runner
    )
    assert normalized_outcome["ok"] is False
    assert normalized_outcome["needs_manual_review"] is True
    assert normalized_outcome["duplicate_create_prevented"] is True
    assert normalized_outcome["candidate_products"][0]["match_reasons"] == [
        "exact_product_name"
    ]
    assert len(normalized_runner.commands) == 2
    assert all("create" not in command for command in normalized_runner.commands)

    # A durable unresolved journal survives invocation boundaries. The second
    # invocation performs reconciliation only and cannot issue a second POST.
    with tempfile.TemporaryDirectory() as temporary:
        private = Path(temporary)
        lock_path = private / "execute.lock"
        journal_path = private / "attempt.json"
        first_runner = JournalAwareRunner(module, [
            json_result(module, {"products": []}),
            module.ProcessResult(None, "", "request timed out", timed_out=True),
            json_result(module, {"products": []}),
        ], journal_path)
        first_outcome = module.execute_with_reconciliation(
            cli,
            execute_command,
            safe_env,
            expectation,
            first_runner,
            lock_path=lock_path,
            journal_path=journal_path,
        )
        durable_journal = module.read_attempt_journal(journal_path)
        assert durable_journal is not None
        assert durable_journal["resolved"] is False
        assert first_outcome["durable_pre_create_journal_used"] is True
        assert sum("create" in command for command in first_runner.commands) == 1

        second_runner = QueueRunner(module, [json_result(module, {"products": []})])
        second_outcome = module.execute_with_reconciliation(
            cli,
            execute_command,
            safe_env,
            expectation,
            second_runner,
            lock_path=lock_path,
            journal_path=journal_path,
        )
        assert second_outcome["ok"] is False
        assert second_outcome["needs_manual_review"] is True
        assert second_outcome["create_attempted"] is False
        assert second_outcome["status"] == "prior_create_attempt_no_candidate_no_product_id_no_create"
        assert sum("create" in command for command in second_runner.commands) == 0

    # A resolved journal also permanently blocks automatic recreation. Even an
    # empty later list must reconcile the journal product ID and never POST.
    with tempfile.TemporaryDirectory() as temporary:
        private = Path(temporary)
        lock_path = private / "execute.lock"
        journal_path = private / "attempt.json"
        first_clean_runner = QueueRunner(module, [
            json_result(module, {"products": []}),
            json_result(module, create_padded),
            json_result(module, view_payload(expectation, padded_product_id)),
        ])
        first_clean = module.execute_with_reconciliation(
            cli,
            execute_command,
            safe_env,
            expectation,
            first_clean_runner,
            lock_path=lock_path,
            journal_path=journal_path,
        )
        assert first_clean["ok"] is True
        resolved_journal = module.read_attempt_journal(journal_path)
        assert resolved_journal["resolved"] is True
        assert resolved_journal["product_id"] == padded_product_id

        resolved_second_runner = QueueRunner(module, [
            json_result(module, {"products": []}),
            json_result(module, view_payload(expectation, padded_product_id)),
        ])
        resolved_second = module.execute_with_reconciliation(
            cli,
            execute_command,
            safe_env,
            expectation,
            resolved_second_runner,
            lock_path=lock_path,
            journal_path=journal_path,
        )
        assert resolved_second["ok"] is False
        assert resolved_second["needs_manual_review"] is True
        assert resolved_second["status"] == "prior_create_attempt_product_id_metadata_matches_no_create"
        assert resolved_second["create_attempted"] is False
        assert sum("create" in command for command in resolved_second_runner.commands) == 0

    # A concurrently held process lock blocks before auth reads or API calls.
    with tempfile.TemporaryDirectory() as temporary:
        private = Path(temporary)
        lock_path = private / "execute.lock"
        blocked_runner = QueueRunner(module, [])
        with module.exclusive_execution_lock(lock_path):
            blocked_outcome = module.execute_with_reconciliation(
                cli,
                execute_command,
                safe_env,
                expectation,
                blocked_runner,
                lock_path=lock_path,
                journal_path=private / "attempt.json",
            )
        assert blocked_outcome["status"] == "execute_lock_busy_no_api_request_no_create"
        assert blocked_outcome["official_cli_auth_used"] is False
        assert blocked_outcome["authenticated_cli_command_attempted"] is False
        assert blocked_outcome["authenticated_api_request_succeeded"] is False
        assert blocked_runner.commands == []

    print(json.dumps({
        "ok": True,
        "official_cli_version_pinned_in_script": module.OFFICIAL_CLI_VERSION,
        "official_cli_sha256_pinned_in_script": module.OFFICIAL_CLI_SHA256,
        "canonical_config_sha256": module.CANONICAL_CONFIG_SHA256,
        "semantic_plan_sha256": expectation["semantic_plan_sha256"],
        "exact_dry_run_mutations_rejected": True,
        "execute_product_contract_mutations_rejected": True,
        "minimal_environment_verified": True,
        "existing_slug_duplicate_create_blocked": True,
        "same_title_normalized_slug_duplicate_blocked": True,
        "cross_invocation_lock_and_journal_verified": True,
        "post_create_local_failure_preserves_truth_and_product_id": True,
        "journal_resolution_failure_preserves_truth_and_product_id": True,
        "signed_url_diagnostics_redacted": True,
        "signed_blob_and_recovery_capabilities_redacted": True,
        "partial_create_reconciled_without_retry": True,
        "publish_command_present": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
