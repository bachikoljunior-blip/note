#!/usr/bin/env python3
"""Create one verified, unpublished Gumroad draft with fail-closed reconciliation.

Default execution is a fully validated official-CLI dry-run. ``--execute`` may
only use the canonical, hash-pinned repository configuration. It blocks a
duplicate when the deterministic permalink or exact product name already
exists, and never calls a publish, update, delete, or authentication command.
"""

from __future__ import annotations

import argparse
import base64
import fcntl
import hashlib
import html
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

ROOT = Path(__file__).resolve().parents[1]
CANONICAL_CONFIG = ROOT / "config" / "gumroad_cli_draft.json"
REPORT_PATH = ROOT / "reports" / "gumroad_cli_draft.json"
ATTEMPT_JOURNAL_PATH = ROOT / "reports" / "gumroad_cli_draft_create_attempt.json"
EXECUTION_LOCK_PATH = ROOT / "reports" / ".gumroad_cli_draft_execute.lock"
CANONICAL_CONFIG_SHA256 = "722be093d1574075c8b94b7e33ff91454316e3a574175a3985464bfd01ee043f"
OFFICIAL_CLI_VERSION = "2026.08.06"
OFFICIAL_CLI_SHA256 = "9808ce12419e65f4debd2dabd8edb4e221444258d04b1bebccdea7fcd8cba606"
LOCALE_ENV = {"LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "TZ": "UTC"}
EXECUTE_ENV_KEYS = frozenset({"HOME", "XDG_CONFIG_HOME", *LOCALE_ENV})
MAX_DIAGNOSTIC_CHARS = 2_000
PROCESS_TIMEOUT_SECONDS = 120
UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)
# Gumroad external IDs are URL-safe Base64 and may have up to two trailing
# padding characters. Padding is never accepted in the middle, and the total
# identifier length remains capped at 128 characters.
PRODUCT_ID_RE = re.compile(r"^(?=.{1,128}$)[A-Za-z0-9_-]+={0,2}$")
SECRET_PATTERNS = [
    re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s\"']+"),
    re.compile(
        r'''(?ix)(["']?(?:access[_-]?token|api[_-]?token|token|secret|password|x-amz-credential|x-amz-signature|x-amz-security-token|signed[_-]?blob[_-]?id|signed[_-]?id)["']?\s*[:=]\s*["']?)([^\s,"'}]+)'''
    ),
    re.compile(r"\beyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b"),
]
HTTP_URL_PATTERN = re.compile(r"(?i)\bhttps?://\S+")


class ValidationError(RuntimeError):
    pass


class ExecutionLockBusy(ValidationError):
    pass


@dataclass(frozen=True)
class ProcessResult:
    returncode: int | None
    stdout: str
    stderr: str
    timed_out: bool = False


Runner = Callable[[list[str], dict[str, str], int], ProcessResult]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def md5_base64(data: bytes) -> str:
    # MD5 is required by the official direct-upload checksum contract; it is
    # not used here as a security integrity primitive.
    return base64.b64encode(hashlib.md5(data).digest()).decode("ascii")  # noqa: S324


def redact_and_limit(value: str) -> str:
    # Diagnostics are evidence about a failure, not a place to persist remote
    # URLs. Gumroad product JSON may contain expiring signed download URLs, so
    # redact every HTTP(S) URL including its query and fragment before applying
    # the narrower token patterns below.
    redacted = HTTP_URL_PATTERN.sub("[REDACTED_URL]", value)
    for pattern in SECRET_PATTERNS:
        if pattern.groups:
            redacted = pattern.sub(lambda match: match.group(1) + "[REDACTED]", redacted)
        else:
            redacted = pattern.sub("[REDACTED]", redacted)
    if len(redacted) > MAX_DIAGNOSTIC_CHARS:
        omitted = len(redacted) - MAX_DIAGNOSTIC_CHARS
        return redacted[:MAX_DIAGNOSTIC_CHARS] + f"\n...[truncated {omitted} chars]"
    return redacted


def diagnostics(result: ProcessResult) -> dict[str, Any]:
    return {
        "exit_code": result.returncode,
        "timed_out": result.timed_out,
        "stdout_excerpt": redact_and_limit(result.stdout.strip()),
        "stderr_excerpt": redact_and_limit(result.stderr.strip()),
    }


def _validate_state_target(path: Path) -> None:
    directory = path.parent
    if directory.is_symlink() or not directory.is_dir():
        raise ValidationError(f"state_directory_not_regular:{directory}")
    if path.is_symlink():
        raise ValidationError(f"state_target_symlink:{path.name}")
    if path.exists() and not path.is_file():
        raise ValidationError(f"state_target_not_regular:{path.name}")


def atomic_write_json(path: Path, value: dict[str, Any], mode: int) -> None:
    _validate_state_target(path)
    data = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        if temporary.is_symlink() or not temporary.is_file():
            raise ValidationError("temporary_state_not_regular")
        os.replace(temporary, path)
        directory_flags = os.O_RDONLY
        if hasattr(os, "O_DIRECTORY"):
            directory_flags |= os.O_DIRECTORY
        directory_descriptor = os.open(path.parent, directory_flags)
        try:
            os.fsync(directory_descriptor)
        finally:
            os.close(directory_descriptor)
    finally:
        if temporary.exists():
            temporary.unlink()


@contextmanager
def exclusive_execution_lock(path: Path | None = None) -> Iterator[None]:
    lock_path = EXECUTION_LOCK_PATH if path is None else path
    _validate_state_target(lock_path)
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(lock_path, flags, 0o600)
    except OSError as exc:
        raise ValidationError(f"execute_lock_open:{type(exc).__name__}:{exc}") from exc
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode):
            raise ValidationError("execute_lock_not_regular")
        os.fchmod(descriptor, 0o600)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise ExecutionLockBusy("execute_lock_busy_no_create") from exc
        try:
            yield
        finally:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
    finally:
        os.close(descriptor)


def read_attempt_journal(path: Path | None = None) -> dict[str, Any] | None:
    journal_path = ATTEMPT_JOURNAL_PATH if path is None else path
    if not journal_path.exists() and not journal_path.is_symlink():
        return None
    _validate_state_target(journal_path)
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(journal_path, flags)
        with os.fdopen(descriptor, "rb") as handle:
            info = os.fstat(handle.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise ValidationError("attempt_journal_not_regular")
            data = handle.read()
    except OSError as exc:
        raise ValidationError(f"attempt_journal_read:{type(exc).__name__}:{exc}") from exc
    try:
        journal = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"attempt_journal_invalid_json:{type(exc).__name__}") from exc
    required = {
        "schema_version",
        "classification",
        "attempt_id",
        "created_at_utc",
        "updated_at_utc",
        "resolved",
        "status",
        "semantic_plan_sha256",
        "custom_permalink",
        "title",
        "product_sha256",
    }
    allowed = required | {"product_id"}
    if not isinstance(journal, dict) or not required.issubset(journal) or not set(journal).issubset(allowed):
        raise ValidationError("attempt_journal_shape")
    if journal.get("schema_version") != "1.0":
        raise ValidationError("attempt_journal_schema_version")
    if journal.get("classification") != "assistant_operational_safety_journal_not_permanent_directive":
        raise ValidationError("attempt_journal_classification")
    if type(journal.get("resolved")) is not bool or not isinstance(journal.get("status"), str):
        raise ValidationError("attempt_journal_resolution_state")
    if not isinstance(journal.get("attempt_id"), str) or not UUID_RE.fullmatch(journal["attempt_id"]):
        raise ValidationError("attempt_journal_attempt_id")
    for key in ("created_at_utc", "updated_at_utc", "custom_permalink", "title"):
        if not isinstance(journal.get(key), str) or not journal[key]:
            raise ValidationError(f"attempt_journal_field:{key}")
    for key in ("semantic_plan_sha256", "product_sha256"):
        if not isinstance(journal.get(key), str) or not re.fullmatch(r"[0-9a-f]{64}", journal[key]):
            raise ValidationError(f"attempt_journal_digest:{key}")
    if "product_id" in journal and (
        not isinstance(journal["product_id"], str) or not PRODUCT_ID_RE.fullmatch(journal["product_id"])
    ):
        raise ValidationError("attempt_journal_product_id")
    return journal


def write_attempt_journal(path: Path, journal: dict[str, Any]) -> None:
    atomic_write_json(path, journal, 0o600)


def new_attempt_journal(expectation: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "schema_version": "1.0",
        "classification": "assistant_operational_safety_journal_not_permanent_directive",
        "attempt_id": str(uuid.uuid4()),
        "created_at_utc": now,
        "updated_at_utc": now,
        "resolved": False,
        "status": "create_request_pending_reconciliation",
        "semantic_plan_sha256": expectation["semantic_plan_sha256"],
        "custom_permalink": expectation["custom_permalink"],
        "title": expectation["title"],
        "product_sha256": expectation["product"]["sha256"],
    }


def update_attempt_journal(
    path: Path,
    journal: dict[str, Any],
    *,
    status_value: str,
    resolved: bool,
    product_id: str | None = None,
) -> dict[str, Any]:
    updated = dict(journal)
    updated["updated_at_utc"] = datetime.now(timezone.utc).isoformat()
    updated["status"] = status_value
    updated["resolved"] = resolved
    if product_id is not None:
        if not PRODUCT_ID_RE.fullmatch(product_id):
            raise ValidationError("attempt_journal_product_id")
        updated["product_id"] = product_id
    write_attempt_journal(path, updated)
    return updated


def run_process(command: list[str], environment: dict[str, str], timeout: int) -> ProcessResult:
    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=ROOT,
            env=environment,
        )
        return ProcessResult(completed.returncode, completed.stdout, completed.stderr)
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode("utf-8", errors="replace") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode("utf-8", errors="replace") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return ProcessResult(None, stdout, stderr, timed_out=True)


def invoke_runner(
    runner: Runner,
    command: list[str],
    environment: dict[str, str],
    timeout: int,
) -> ProcessResult:
    try:
        return runner(command, environment, timeout)
    except (OSError, subprocess.SubprocessError, UnicodeError) as exc:
        # Convert local spawn/resource/decoding failures into a normal failed
        # process result so execute reconciliation retains the accumulated auth,
        # create and product-ID facts instead of falling back to main's initial
        # all-false report.
        return ProcessResult(
            None,
            "",
            f"local_runner_error:{type(exc).__name__}:{exc}",
            timed_out=False,
        )


def parse_config_bytes(data: bytes) -> dict[str, Any]:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValidationError(f"config_read:{type(exc).__name__}:{exc}") from exc
    if not isinstance(value, dict):
        raise ValidationError("config_top_level_not_object")
    return value


def load_config_once(path: Path, execute: bool = False) -> tuple[dict[str, Any], str]:
    try:
        resolved = path.resolve(strict=True)
    except OSError as exc:
        raise ValidationError("config_missing") from exc
    if path.is_symlink() or resolved != CANONICAL_CONFIG.resolve(strict=True):
        raise ValidationError("canonical_config_path_required")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(resolved, flags)
        with os.fdopen(descriptor, "rb") as handle:
            info = os.fstat(handle.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise ValidationError("config_not_regular_file")
            data = handle.read()
    except OSError as exc:
        raise ValidationError(f"config_read:{type(exc).__name__}:{exc}") from exc
    digest = sha256_bytes(data)
    if digest != CANONICAL_CONFIG_SHA256:
        raise ValidationError(f"canonical_config_sha256_mismatch:{digest}")
    return parse_config_bytes(data), digest


def validate_config_shape(config: dict[str, Any]) -> None:
    expected_top = {
        "schema_version",
        "classification",
        "channel",
        "purpose",
        "cli",
        "listing",
        "product",
        "visuals",
        "report_path",
        "cost_yen",
    }
    if set(config) != expected_top:
        raise ValidationError(f"config_top_level_keys:{sorted(config)}")
    if config.get("schema_version") != "1.0":
        raise ValidationError("config_schema_version")
    if config.get("classification") != "assistant_operational_configuration_not_permanent_directive":
        raise ValidationError("config_classification")
    if config.get("channel") != "Gumroad" or config.get("cost_yen") != 0:
        raise ValidationError("config_channel_or_cost")
    if config.get("report_path") != "reports/gumroad_cli_draft.json":
        raise ValidationError("config_report_path_contract")
    cli_config = config.get("cli")
    expected_cli_keys = {"command", "draft_only", "default_dry_run", "forbidden_command_words"}
    if not isinstance(cli_config, dict) or set(cli_config) != expected_cli_keys:
        raise ValidationError("cli_config_keys_or_self_approval")
    if cli_config.get("command") != ["products", "create"]:
        raise ValidationError("command_must_be_products_create")
    if cli_config.get("draft_only") is not True or cli_config.get("default_dry_run") is not True:
        raise ValidationError("draft_safety_contract_missing")
    if cli_config.get("forbidden_command_words") != ["publish", "unpublish", "delete", "update"]:
        raise ValidationError("forbidden_command_contract")


def repo_bytes(relative: str, expected_sha256: str, expected_bytes: int | None = None) -> tuple[Path, bytes]:
    if not isinstance(relative, str) or not relative:
        raise ValidationError("invalid_relative_path")
    unresolved = ROOT / relative
    try:
        resolved = unresolved.resolve(strict=True)
    except OSError as exc:
        raise ValidationError(f"missing_file:{relative}") from exc
    if resolved != ROOT and ROOT not in resolved.parents:
        raise ValidationError(f"path_outside_repository:{relative}")
    if unresolved.is_symlink() or not resolved.is_file():
        raise ValidationError(f"not_regular_file:{relative}")
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(resolved, flags)
        with os.fdopen(descriptor, "rb") as handle:
            info = os.fstat(handle.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise ValidationError(f"not_regular_file:{relative}")
            data = handle.read()
    except OSError as exc:
        raise ValidationError(f"file_read:{relative}:{type(exc).__name__}:{exc}") from exc
    actual_sha256 = sha256_bytes(data)
    if actual_sha256 != expected_sha256:
        raise ValidationError(f"sha256_mismatch:{relative}:{actual_sha256}")
    if expected_bytes is not None and len(data) != expected_bytes:
        raise ValidationError(f"byte_count_mismatch:{relative}:{len(data)}")
    return resolved, data


def read_utf8(relative: str, expected_sha256: str) -> str:
    _, data = repo_bytes(relative, expected_sha256)
    try:
        return data.decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise ValidationError(f"not_utf8:{relative}") from exc


def stage_verified_bytes(
    private_root: Path,
    category: str,
    index: int,
    filename: str,
    data: bytes,
    expected_sha256: str,
) -> Path:
    stage_directory = private_root / "verified-inputs" / category / f"{index:02d}"
    stage_directory.mkdir(mode=0o700, parents=True, exist_ok=False)
    staged = stage_directory / filename
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(staged, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            os.close(descriptor)
        except OSError:
            pass
        raise
    os.chmod(staged, 0o600)
    if sha256_bytes(staged.read_bytes()) != expected_sha256:
        raise ValidationError(f"staged_input_sha256:{category}:{filename}")
    return staged


def description_html(source: str) -> str:
    blocks: list[str] = []
    paragraph: list[str] = []
    bullets: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append(f"<p>{' '.join(paragraph)}</p>")
            paragraph.clear()

    def flush_bullets() -> None:
        if bullets:
            blocks.append("<ul>" + "".join(f"<li>{item}</li>" for item in bullets) + "</ul>")
            bullets.clear()

    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line:
            flush_paragraph()
            flush_bullets()
        elif line.startswith("• "):
            flush_paragraph()
            bullets.append(html.escape(line[2:].strip()))
        elif line == line.upper() and any(character.isalpha() for character in line):
            flush_paragraph()
            flush_bullets()
            blocks.append(f"<h2>{html.escape(line)}</h2>")
        else:
            flush_bullets()
            paragraph.append(html.escape(line))
    flush_paragraph()
    flush_bullets()
    return "\n".join(blocks)


def resolve_binary_path(binary_arg: str) -> Path:
    candidate = Path(binary_arg).expanduser() if "/" in binary_arg else None
    if candidate is None:
        discovered = shutil.which(binary_arg)
        if discovered is None:
            raise ValidationError(f"gumroad_cli_not_found:{binary_arg}")
        candidate = Path(discovered)
    try:
        return candidate.resolve(strict=True)
    except OSError as exc:
        raise ValidationError(f"gumroad_cli_not_found:{binary_arg}") from exc


@contextmanager
def pinned_cli_copy(binary_arg: str) -> Iterator[tuple[Path, Path]]:
    source = resolve_binary_path(binary_arg)
    try:
        with source.open("rb") as handle:
            info = os.fstat(handle.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise ValidationError("gumroad_cli_not_regular_file")
            source_bytes = handle.read()
    except OSError as exc:
        raise ValidationError(f"gumroad_cli_read:{type(exc).__name__}:{exc}") from exc
    digest = sha256_bytes(source_bytes)
    if digest != OFFICIAL_CLI_SHA256:
        raise ValidationError(f"gumroad_cli_sha256_not_official:{digest}")

    with tempfile.TemporaryDirectory(prefix="gumroad-cli-pinned-", dir="/tmp") as temporary:
        private_root = Path(temporary)
        os.chmod(private_root, 0o700)
        copied = private_root / "gumroad"
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(copied, flags, 0o700)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(source_bytes)
                handle.flush()
                os.fsync(handle.fileno())
        except Exception:
            try:
                os.close(descriptor)
            except OSError:
                pass
            raise
        os.chmod(copied, 0o700)
        copied_info = copied.stat()
        if stat.S_IMODE(copied_info.st_mode) != 0o700:
            raise ValidationError("pinned_cli_copy_mode")
        if sha256_bytes(copied.read_bytes()) != OFFICIAL_CLI_SHA256:
            raise ValidationError("pinned_cli_copy_sha256")
        yield copied, private_root


def make_isolated_environment(private_root: Path) -> dict[str, str]:
    home = private_root / "isolated-home"
    xdg = private_root / "isolated-xdg"
    home.mkdir(mode=0o700)
    xdg.mkdir(mode=0o700)
    return {"HOME": str(home), "XDG_CONFIG_HOME": str(xdg), **LOCALE_ENV}


def make_execute_environment() -> dict[str, str]:
    home_value = os.environ.get("HOME")
    if not home_value:
        raise ValidationError("execute_home_missing")
    home = Path(home_value).expanduser()
    if not home.is_absolute() or not home.is_dir():
        raise ValidationError("execute_home_invalid")
    xdg_value = os.environ.get("XDG_CONFIG_HOME")
    xdg = Path(xdg_value).expanduser() if xdg_value else home / ".config"
    if not xdg.is_absolute():
        raise ValidationError("execute_xdg_config_home_invalid")
    environment = {"HOME": str(home), "XDG_CONFIG_HOME": str(xdg), **LOCALE_ENV}
    if set(environment) != EXECUTE_ENV_KEYS:
        raise ValidationError("execute_environment_not_minimal")
    return environment


def validate_version(cli: Path, environment: dict[str, str], runner: Runner = run_process) -> str:
    result = invoke_runner(runner, [str(cli), "--version"], environment, 15)
    output = (result.stdout + result.stderr).strip()
    if result.timed_out or result.returncode != 0:
        raise ValidationError(f"gumroad_cli_version_failed:{diagnostics(result)}")
    if output != f"gumroad version {OFFICIAL_CLI_VERSION}":
        raise ValidationError(f"gumroad_cli_version_mismatch:{redact_and_limit(output)}")
    return OFFICIAL_CLI_VERSION


def media_expectation(
    flag: str,
    staged_path: Path,
    relative: str,
    sha256: str,
    data: bytes,
) -> dict[str, Any]:
    kind = {"cover-image": "cover", "preview-image": "preview", "thumbnail": "thumbnail"}[flag]
    return {
        "flag": flag,
        "kind": kind,
        "relative_path": relative,
        "absolute_path": str(staged_path),
        "filename": Path(relative).name,
        "size": len(data),
        "content_type": "image/png",
        "md5_base64": md5_base64(data),
        "sha256": sha256,
    }


def build_command(
    cli: Path,
    config: dict[str, Any],
    execute: bool,
    private_root: Path,
) -> tuple[list[str], dict[str, Any]]:
    validate_config_shape(config)
    listing = config.get("listing")
    product = config.get("product")
    visuals = config.get("visuals")
    if not isinstance(listing, dict) or not isinstance(product, dict) or not isinstance(visuals, list):
        raise ValidationError("config_sections_missing")

    title = read_utf8(listing["name_path"], listing["name_sha256"])
    description_source = read_utf8(listing["description_path"], listing["description_sha256"])
    if listing.get("description_encoding") != "html_from_markdown_like":
        raise ValidationError("unsupported_description_encoding")
    rendered_description = description_html(description_source)
    tags = [
        line.strip()
        for line in read_utf8(listing["tags_path"], listing["tags_sha256"]).splitlines()
        if line.strip()
    ]
    if not 5 <= len(tags) <= 10 or len(tags) != len(set(tags)):
        raise ValidationError("invalid_tags")
    refund_fine_print = read_utf8(
        listing["refund_fine_print_path"], listing["refund_fine_print_sha256"]
    )
    if listing.get("refund_period") != "7" or not refund_fine_print:
        raise ValidationError("seven_day_refund_policy_required")
    if listing.get("price") != "12.00" or listing.get("currency") != "usd" or listing.get("type") != "digital":
        raise ValidationError("listing_price_currency_type_contract")
    custom_permalink = listing.get("custom_permalink")
    if custom_permalink != "non-repetitive-ai-trivia-shorts-kit":
        raise ValidationError("canonical_custom_permalink_required")
    custom_summary = listing.get("custom_summary")
    if not isinstance(custom_summary, str) or not custom_summary:
        raise ValidationError("custom_summary_required")

    product_source, product_data = repo_bytes(
        product["path"], product["sha256"], product["bytes"]
    )
    if product_source.suffix.lower() != ".zip":
        raise ValidationError("product_must_be_zip")
    product_path = stage_verified_bytes(
        private_root,
        "product",
        0,
        product_source.name,
        product_data,
        product["sha256"],
    )
    expected_flags = ["cover-image", "preview-image", "preview-image", "thumbnail"]
    actual_flags = [item.get("flag") for item in visuals if isinstance(item, dict)]
    if len(visuals) != 4 or actual_flags != expected_flags:
        raise ValidationError(f"visual_flag_contract:{actual_flags}")
    media: list[dict[str, Any]] = []
    for index, item in enumerate(visuals):
        if not isinstance(item, dict):
            raise ValidationError("visual_not_object")
        source_path, source_data = repo_bytes(item["path"], item["sha256"])
        if source_path.suffix.lower() != ".png":
            raise ValidationError(f"visual_must_be_png:{item['path']}")
        staged_path = stage_verified_bytes(
            private_root,
            "media",
            index,
            source_path.name,
            source_data,
            item["sha256"],
        )
        media.append(
            media_expectation(
                item["flag"], staged_path, item["path"], item["sha256"], source_data
            )
        )

    command = [
        str(cli),
        "--json",
        "--no-color",
        "--no-image",
        "--no-input",
        "--non-interactive",
        "--yes",
    ]
    if not execute:
        command.append("--dry-run")
    command.extend([
        "products",
        "create",
        "--name",
        title,
        "--description",
        rendered_description,
        "--custom-summary",
        custom_summary,
        "--custom-permalink",
        custom_permalink,
        "--price",
        listing["price"],
        "--currency",
        listing["currency"],
        "--type",
        listing["type"],
        "--refund-period",
        listing["refund_period"],
        "--refund-fine-print",
        refund_fine_print,
        "--file",
        str(product_path),
        "--file-name",
        product["display_name"],
    ])
    for tag in tags:
        command.extend(["--tag", tag])
    for item in media:
        command.extend([f"--{item['flag']}", item["absolute_path"]])

    products_index = command.index("products")
    if command[products_index : products_index + 2] != ["products", "create"]:
        raise ValidationError("command_safety_check_failed")
    forbidden_flags = {"--publish", "--unpublish", "--delete", "--update"}
    if any(token in forbidden_flags for token in command):
        raise ValidationError("forbidden_mutation_in_command")
    if execute and "--dry-run" in command:
        raise ValidationError("execute_command_contains_dry_run")
    if not execute and "--dry-run" not in command:
        raise ValidationError("default_command_missing_dry_run")

    semantic_plan = {
        "listing": {
            "title": title,
            "description_html_sha256": sha256_bytes(rendered_description.encode("utf-8")),
            "custom_summary": custom_summary,
            "custom_permalink": custom_permalink,
            "tags": tags,
            "price_minor_units": 1200,
            "currency": listing["currency"],
            "type": listing["type"],
            "refund_period": listing["refund_period"],
            "refund_fine_print_sha256": sha256_bytes(refund_fine_print.encode("utf-8")),
        },
        "product": {
            "relative_path": product["path"],
            "display_name": product["display_name"],
            "bytes": product["bytes"],
            "sha256": product["sha256"],
        },
        "media": [
            {
                "flag": item["flag"],
                "kind": item["kind"],
                "relative_path": item["relative_path"],
                "filename": item["filename"],
                "size": item["size"],
                "content_type": item["content_type"],
                "md5_base64": item["md5_base64"],
                "sha256": item["sha256"],
            }
            for item in media
        ],
    }
    semantic_plan_sha256 = sha256_bytes(
        json.dumps(semantic_plan, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    )
    expectation = {
        "title": title,
        "description_source": description_source,
        "description_html": rendered_description,
        "custom_summary": custom_summary,
        "custom_permalink": custom_permalink,
        "tags": tags,
        "price": listing["price"],
        "price_minor_units": 1200,
        "currency": listing["currency"],
        "type": listing["type"],
        "refund_period": listing["refund_period"],
        "refund_fine_print": refund_fine_print,
        "product": {
            "relative_path": product["path"],
            "absolute_path": str(product_path),
            "display_name": product["display_name"],
            "bytes": product["bytes"],
            "sha256": product["sha256"],
        },
        "media": media,
        "semantic_plan_sha256": semantic_plan_sha256,
    }
    return command, expectation


def expected_product_upload(expectation: dict[str, Any]) -> dict[str, Any]:
    product = expectation["product"]
    return {
        "action": "upload",
        "path": product["absolute_path"],
        "filename": product["display_name"],
        "size": product["bytes"],
        "part_size": 100 * 1024 * 1024,
        "part_count": 1,
    }


def expected_media_upload(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "action": "direct_upload",
        "kind": item["kind"],
        "path": item["absolute_path"],
        "filename": item["filename"],
        "size": item["size"],
        "part_size": item["size"],
        "part_count": 1,
        "content_type": item["content_type"],
        "checksum": item["md5_base64"],
    }


def expected_follow_ups(expectation: dict[str, Any]) -> list[dict[str, Any]]:
    follow_ups: list[dict[str, Any]] = []
    for index, item in enumerate(expectation["media"]):
        follow_ups.append({
            "method": "POST",
            "path": "/direct_uploads",
            "body": {
                "blob": {
                    "byte_size": item["size"],
                    "checksum": item["md5_base64"],
                    "content_type": item["content_type"],
                    "filename": item["filename"],
                }
            },
        })
        endpoint = "thumbnail" if item["kind"] == "thumbnail" else "covers"
        follow_ups.append({
            "method": "POST",
            "path": f"/products/created-product-id/{endpoint}",
            "body": {"signed_blob_id": f"<signed_blob:{item['kind']}:{index}>"},
        })
    return follow_ups


def parse_json_output(result: ProcessResult, label: str) -> dict[str, Any]:
    if result.timed_out or result.returncode != 0:
        raise ValidationError(f"{label}_process_failed:{diagnostics(result)}")
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValidationError(f"{label}_output_not_json") from exc
    if not isinstance(value, dict):
        raise ValidationError(f"{label}_output_not_object")
    return value


def validate_dry_run_output(result: ProcessResult, expectation: dict[str, Any]) -> dict[str, Any]:
    payload = parse_json_output(result, "dry_run")
    if result.stderr.strip():
        raise ValidationError(f"dry_run_unexpected_stderr:{redact_and_limit(result.stderr.strip())}")
    if set(payload) != {"dry_run", "uploads", "request", "follow_up_requests"}:
        raise ValidationError(f"dry_run_top_level_keys:{sorted(payload)}")
    if payload.get("dry_run") is not True:
        raise ValidationError("dry_run_not_confirmed")
    expected_uploads = [expected_product_upload(expectation)] + [
        expected_media_upload(item) for item in expectation["media"]
    ]
    if payload.get("uploads") != expected_uploads:
        raise ValidationError("dry_run_upload_plan_mismatch")

    request = payload.get("request")
    if not isinstance(request, dict) or set(request) != {"method", "path", "body"}:
        raise ValidationError("dry_run_request_shape")
    if request.get("method") != "POST" or request.get("path") != "/products":
        raise ValidationError("dry_run_create_request")
    body = request.get("body")
    expected_body_keys = {
        "custom_permalink",
        "custom_summary",
        "description",
        "files",
        "name",
        "native_type",
        "price",
        "price_currency_type",
        "refund_fine_print",
        "refund_period",
        "rich_content",
        "tags",
    }
    if not isinstance(body, dict) or set(body) != expected_body_keys:
        raise ValidationError(f"dry_run_body_keys:{sorted(body) if isinstance(body, dict) else 'not_object'}")
    exact_body = {
        "custom_permalink": expectation["custom_permalink"],
        "custom_summary": expectation["custom_summary"],
        "description": expectation["description_html"],
        "name": expectation["title"],
        "native_type": expectation["type"],
        "price": str(expectation["price_minor_units"]),
        "price_currency_type": expectation["currency"],
        "refund_fine_print": expectation["refund_fine_print"],
        "refund_period": expectation["refund_period"],
        "tags": expectation["tags"],
    }
    for key, expected in exact_body.items():
        if body.get(key) != expected:
            raise ValidationError(f"dry_run_body_value:{key}")
    files = body.get("files")
    if not isinstance(files, list) or len(files) != 1 or not isinstance(files[0], dict):
        raise ValidationError("dry_run_files_shape")
    file_item = files[0]
    if set(file_item) != {"display_name", "id", "url"}:
        raise ValidationError("dry_run_file_keys")
    file_id = file_item.get("id")
    if (
        file_item.get("display_name") != expectation["product"]["display_name"]
        or file_item.get("url") != "<uploaded:file:0>"
        or not isinstance(file_id, str)
        or not file_id.startswith("cli-upload-")
        or not UUID_RE.fullmatch(file_id.removeprefix("cli-upload-"))
    ):
        raise ValidationError("dry_run_file_reference")
    rich_content = body.get("rich_content")
    if not isinstance(rich_content, list) or len(rich_content) != 1:
        raise ValidationError("dry_run_rich_content_shape")
    page = rich_content[0]
    if not isinstance(page, dict) or set(page) != {"description", "title"} or page.get("title") != "Page 1":
        raise ValidationError("dry_run_rich_content_page")
    description = page.get("description")
    if not isinstance(description, dict) or set(description) != {"content", "type"} or description.get("type") != "doc":
        raise ValidationError("dry_run_rich_content_document")
    content = description.get("content")
    if not isinstance(content, list) or len(content) != 2:
        raise ValidationError("dry_run_rich_content_nodes")
    embed, paragraph = content
    if paragraph != {"type": "paragraph"} or not isinstance(embed, dict) or set(embed) != {"attrs", "type"}:
        raise ValidationError("dry_run_rich_content_nodes")
    attrs = embed.get("attrs")
    if embed.get("type") != "fileEmbed" or not isinstance(attrs, dict) or set(attrs) != {"collapsed", "id", "uid"}:
        raise ValidationError("dry_run_file_embed")
    if attrs.get("collapsed") is not False or attrs.get("id") != file_id:
        raise ValidationError("dry_run_file_embed_relation")
    uid = attrs.get("uid")
    if not isinstance(uid, str) or not UUID_RE.fullmatch(uid):
        raise ValidationError("dry_run_file_embed_uid")
    expected_follows = expected_follow_ups(expectation)
    if payload.get("follow_up_requests") != expected_follows:
        raise ValidationError("dry_run_follow_up_plan_mismatch")

    return {
        "dry_run": True,
        "request_method": "POST",
        "request_path": "/products",
        "publication_request_present": False,
        "exact_request_body_validated": True,
        "rich_content_file_id_relation_validated": True,
        "product_file": expected_uploads[0],
        "media": expected_uploads[1:],
        "follow_up_requests": expected_follows,
    }


def global_read_flags(cli: Path) -> list[str]:
    return [
        str(cli),
        "--json",
        "--no-color",
        "--no-image",
        "--no-input",
        "--non-interactive",
    ]


def list_command(cli: Path) -> list[str]:
    return global_read_flags(cli) + ["products", "list", "--all"]


def view_command(cli: Path, product_id: str) -> list[str]:
    if not PRODUCT_ID_RE.fullmatch(product_id):
        raise ValidationError("unsafe_product_id")
    return global_read_flags(cli) + ["products", "view", product_id]


def find_potential_products(
    payload: dict[str, Any], permalink: str, title: str
) -> list[dict[str, Any]]:
    if "success" in payload and payload.get("success") is not True:
        raise ValidationError("products_list_success_false_or_invalid")
    products = payload.get("products")
    if not isinstance(products, list):
        raise ValidationError("products_list_missing_products")
    matches: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for product in products:
        if not isinstance(product, dict):
            raise ValidationError("products_list_item_not_object")
        reasons: list[str] = []
        if product.get("custom_permalink") == permalink:
            reasons.append("canonical_permalink")
        if product.get("name") == title:
            reasons.append("exact_product_name")
        if reasons:
            product_id = product.get("id")
            if not isinstance(product_id, str) or not PRODUCT_ID_RE.fullmatch(product_id):
                raise ValidationError("products_list_unsafe_product_id")
            if product_id not in seen_ids:
                candidate = dict(product)
                candidate["_match_reasons"] = reasons
                matches.append(candidate)
                seen_ids.add(product_id)
    return matches


def validate_create_response(payload: dict[str, Any], expectation: dict[str, Any]) -> str:
    if "success" in payload and payload.get("success") is not True:
        raise ValidationError("create_response_success_false_or_invalid")
    product = payload.get("product")
    if not isinstance(product, dict):
        raise ValidationError("create_response_product_missing")
    product_id = product.get("id")
    if not isinstance(product_id, str) or not PRODUCT_ID_RE.fullmatch(product_id):
        raise ValidationError("create_response_product_id")
    if product.get("name") != expectation["title"]:
        raise ValidationError("create_response_name")
    if product.get("published") is not False:
        raise ValidationError("create_response_published_not_false")
    return product_id


def validate_product_view(payload: dict[str, Any], product_id: str, expectation: dict[str, Any]) -> dict[str, Any]:
    if "success" in payload and payload.get("success") is not True:
        raise ValidationError("product_view_success_false_or_invalid")
    product = payload.get("product")
    if not isinstance(product, dict):
        raise ValidationError("product_view_product_missing")
    errors: list[str] = []

    def require(condition: bool, label: str) -> None:
        if not condition:
            errors.append(label)

    require(product.get("id") == product_id, "id")
    require(product.get("name") == expectation["title"], "name")
    require(product.get("published") is False, "published_false")
    require(product.get("description") == expectation["description_html"], "description")
    require(product.get("custom_summary") == expectation["custom_summary"], "custom_summary")
    require(product.get("custom_permalink") == expectation["custom_permalink"], "custom_permalink")
    require(product.get("is_tiered_membership") is False, "not_tiered_membership")
    require(type(product.get("price")) is int and product.get("price") == 1200, "price_1200")
    require(product.get("currency") == "usd", "currency_usd")
    remote_tags = product.get("tags")
    require(
        isinstance(remote_tags, list)
        and len(remote_tags) == len(expectation["tags"])
        and all(isinstance(tag, str) for tag in remote_tags)
        and set(remote_tags) == set(expectation["tags"]),
        "tags_exact_set_and_count",
    )
    files = product.get("files")
    require(isinstance(files, list) and len(files) == 1, "files_count")
    if isinstance(files, list) and len(files) == 1 and isinstance(files[0], dict):
        require(files[0].get("name") == expectation["product"]["display_name"], "file_name")
        require(type(files[0].get("size")) is int and files[0].get("size") == expectation["product"]["bytes"], "file_size")
    else:
        errors.extend(["file_name", "file_size"])
    refund = product.get("refund_policy")
    require(isinstance(refund, dict), "refund_policy")
    if isinstance(refund, dict):
        require(refund.get("refund_period") == "7", "refund_period_7")
        require(refund.get("fine_print") == expectation["refund_fine_print"], "refund_fine_print")
        require(refund.get("inherited") is False, "refund_not_inherited")
    covers = product.get("covers")
    require(isinstance(covers, list) and len(covers) == 3, "covers_exactly_3")
    require(isinstance(product.get("thumbnail_url"), str) and bool(product.get("thumbnail_url")), "thumbnail_present")
    if errors:
        raise ValidationError("product_view_mismatch:" + ",".join(errors))
    return {
        "product_id": product_id,
        "name": product["name"],
        "published": False,
        "description_html_chars": len(product["description"]),
        "custom_summary": product["custom_summary"],
        "custom_permalink": product["custom_permalink"],
        "is_tiered_membership": False,
        "price": product["price"],
        "currency": product["currency"],
        "tags": product["tags"],
        "files": [{"name": files[0]["name"], "size": files[0]["size"]}],
        "refund_policy": {
            "refund_period": refund["refund_period"],
            "fine_print": refund["fine_print"],
            "inherited": refund["inherited"],
        },
        "cover_count": len(covers),
        "thumbnail_present": True,
    }


def read_product_view(
    cli: Path,
    product_id: str,
    environment: dict[str, str],
    expectation: dict[str, Any],
    runner: Runner,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    result = invoke_runner(
        runner, view_command(cli, product_id), environment, PROCESS_TIMEOUT_SECONDS
    )
    try:
        payload = parse_json_output(result, "products_view")
        return validate_product_view(payload, product_id, expectation), None
    except ValidationError as exc:
        return None, {"error": str(exc), "diagnostics": diagnostics(result)}


def list_potential_matches(
    cli: Path,
    environment: dict[str, str],
    expectation: dict[str, Any],
    runner: Runner,
) -> tuple[list[dict[str, Any]] | None, dict[str, Any] | None]:
    result = invoke_runner(
        runner, list_command(cli), environment, PROCESS_TIMEOUT_SECONDS
    )
    try:
        payload = parse_json_output(result, "products_list")
        matches = find_potential_products(
            payload, expectation["custom_permalink"], expectation["title"]
        )
        return matches, None
    except (ValidationError, OSError) as exc:
        return None, {"error": str(exc), "diagnostics": diagnostics(result)}


def execute_with_reconciliation(
    cli: Path,
    create_command: list[str],
    environment: dict[str, str],
    expectation: dict[str, Any],
    runner: Runner = run_process,
    *,
    lock_path: Path | None = None,
    journal_path: Path | None = None,
) -> dict[str, Any]:
    selected_journal_path = ATTEMPT_JOURNAL_PATH if journal_path is None else journal_path
    base: dict[str, Any] = {
        "ok": False,
        "needs_manual_review": False,
        "official_cli_auth_used": False,
        "authenticated_api_request_used": False,
        "authenticated_api_request_succeeded": False,
        "authenticated_cli_command_attempted": False,
        "authentication_flow_started": False,
        "credential_source": "official_cli_saved_config_via_HOME_XDG_if_request_succeeds",
        "official_cli_may_read_own_auth_config": True,
        "wrapper_parses_credentials": False,
        "create_attempted": False,
        "automatic_create_retries": 0,
        "publication_attempted": False,
        "authenticated_write_performed": False,
        "authenticated_write_attempted": False,
        "cross_invocation_lock_used": False,
        "durable_pre_create_journal_used": False,
    }

    try:
        with exclusive_execution_lock(lock_path):
            base["cross_invocation_lock_used"] = True
            return _execute_with_reconciliation_locked(
                cli,
                create_command,
                environment,
                expectation,
                runner,
                selected_journal_path,
                base,
            )
    except ExecutionLockBusy:
        base.update({
            "status": "execute_lock_busy_no_api_request_no_create",
            "needs_manual_review": True,
            "duplicate_create_prevented": True,
        })
        return base
    except (ValidationError, OSError, subprocess.SubprocessError, UnicodeError) as exc:
        create_attempted = base["create_attempted"]
        base.update({
            "status": (
                "execute_safety_failure_after_create_attempt_manual_review"
                if create_attempted
                else "execute_safety_state_invalid_no_create"
            ),
            "needs_manual_review": True,
            "safety_error": redact_and_limit(str(exc)),
        })
        return base


def _set_authenticated_read_success(base: dict[str, Any]) -> None:
    base["official_cli_auth_used"] = True
    base["authenticated_api_request_used"] = True
    base["authenticated_api_request_succeeded"] = True
    base["credential_source"] = "official_cli_saved_config_via_HOME_XDG"


def _journal_summary(journal: dict[str, Any]) -> dict[str, Any]:
    return {
        "attempt_id": journal["attempt_id"],
        "resolved": journal["resolved"],
        "status": journal["status"],
        "semantic_plan_sha256": journal["semantic_plan_sha256"],
        "custom_permalink": journal["custom_permalink"],
        "product_id": journal.get("product_id"),
    }


def _record_journal_outcome(
    base: dict[str, Any],
    path: Path,
    journal: dict[str, Any],
    *,
    status_value: str,
    resolved: bool,
    product_id: str | None = None,
) -> dict[str, Any] | None:
    try:
        updated = update_attempt_journal(
            path,
            journal,
            status_value=status_value,
            resolved=resolved,
            product_id=product_id,
        )
    except (ValidationError, OSError, subprocess.SubprocessError, UnicodeError) as exc:
        base["attempt_journal_update_error"] = redact_and_limit(str(exc))
        return None
    base["attempt_journal"] = _journal_summary(updated)
    return updated


def _manual_candidate_outcome(
    base: dict[str, Any],
    candidates: list[dict[str, Any]],
    cli: Path,
    environment: dict[str, str],
    expectation: dict[str, Any],
    runner: Runner,
    *,
    status_prefix: str,
) -> dict[str, Any]:
    base.update({
        "ok": False,
        "needs_manual_review": True,
        "duplicate_create_prevented": True,
        "candidate_products": [
            {"product_id": item["id"], "match_reasons": item["_match_reasons"]}
            for item in candidates
        ],
    })
    if len(candidates) != 1:
        base["status"] = f"{status_prefix}_multiple_candidates_require_manual_review"
        base["candidate_verifications"] = []
        for candidate in candidates:
            product_id = candidate["id"]
            verified, view_error = read_product_view(
                cli, product_id, environment, expectation, runner
            )
            base["candidate_verifications"].append({
                "product_id": product_id,
                "verification": verified,
                "error": view_error,
            })
        return base
    candidate = candidates[0]
    product_id = candidate["id"]
    verified, view_error = read_product_view(cli, product_id, environment, expectation, runner)
    base["product_id"] = product_id
    if view_error:
        base.update({
            "status": f"{status_prefix}_view_requires_manual_review",
            "verification": view_error,
        })
        return base
    base.update({
        "status": f"{status_prefix}_metadata_matches_but_remote_artifact_hashes_unverifiable",
        "verification": verified,
        "unverified_remote_facts": [
            "downloadable_file_sha256",
            "cover_image_sha256_values",
            "thumbnail_sha256",
        ],
    })
    return base


def _execute_with_reconciliation_locked(
    cli: Path,
    create_command: list[str],
    environment: dict[str, str],
    expectation: dict[str, Any],
    runner: Runner,
    journal_path: Path,
    base: dict[str, Any],
) -> dict[str, Any]:
    prior_journal = read_attempt_journal(journal_path)
    base["authenticated_cli_command_attempted"] = True
    base["official_cli_auth_used"] = None
    base["authenticated_api_request_used"] = None
    base["authenticated_api_request_succeeded"] = None
    base["credential_source"] = "unknown_official_cli_saved_config_may_have_been_read"
    candidates, list_error = list_potential_matches(cli, environment, expectation, runner)
    if list_error:
        base.update({"status": "preflight_list_failed_no_create", "preflight": list_error})
        return base
    _set_authenticated_read_success(base)
    assert candidates is not None

    if prior_journal is not None:
        # A durable journal is proof that some earlier invocation reached the
        # pre-POST boundary. Even a resolved journal must block another create:
        # list results can be stale, filtered by a different account, or empty
        # after deletion. Only explicit human clearance may remove this guard.
        base["prior_create_attempt_journal"] = _journal_summary(prior_journal)
        if candidates:
            return _manual_candidate_outcome(
                base,
                candidates,
                cli,
                environment,
                expectation,
                runner,
                status_prefix="prior_create_attempt",
            )
        journal_product_id = prior_journal.get("product_id")
        if isinstance(journal_product_id, str):
            verified, view_error = read_product_view(
                cli, journal_product_id, environment, expectation, runner
            )
            base.update({
                "ok": False,
                "needs_manual_review": True,
                "duplicate_create_prevented": True,
                "product_id": journal_product_id,
            })
            if view_error:
                base.update({
                    "status": "prior_create_attempt_product_id_view_requires_manual_review_no_create",
                    "verification": view_error,
                })
            else:
                base.update({
                    "status": "prior_create_attempt_product_id_metadata_matches_no_create",
                    "verification": verified,
                    "unverified_remote_facts": [
                        "downloadable_file_sha256",
                        "cover_image_sha256_values",
                        "thumbnail_sha256",
                    ],
                })
            return base
        base.update({
            "status": "prior_create_attempt_no_candidate_no_product_id_no_create",
            "needs_manual_review": True,
            "duplicate_create_prevented": True,
            "reconciliation": {
                "potential_product_observed": False,
                "create_retried": False,
            },
        })
        return base

    if candidates:
        return _manual_candidate_outcome(
            base,
            candidates,
            cli,
            environment,
            expectation,
            runner,
            status_prefix="existing_potential_duplicate",
        )

    journal = new_attempt_journal(expectation)
    write_attempt_journal(journal_path, journal)
    base["durable_pre_create_journal_used"] = True
    base["attempt_journal"] = _journal_summary(journal)

    base["create_attempted"] = True
    base["authenticated_write_attempted"] = True
    base["authenticated_write_performed"] = None
    create_result = invoke_runner(
        runner, create_command, environment, PROCESS_TIMEOUT_SECONDS
    )
    if create_result.timed_out or create_result.returncode != 0:
        base.update({
            "status": "create_failed_or_timed_out_reconciliation_required",
            "authenticated_write_state": "unknown",
            "create": diagnostics(create_result),
        })
        candidates, reconcile_error = list_potential_matches(
            cli, environment, expectation, runner
        )
        if reconcile_error:
            base.update({"needs_manual_review": True, "reconciliation": reconcile_error})
            _record_journal_outcome(
                base,
                journal_path,
                journal,
                status_value="create_failed_reconciliation_failed_manual_review",
                resolved=False,
            )
            return base
        assert candidates is not None
        if not candidates:
            base.update({
                "needs_manual_review": True,
                "reconciliation": {"potential_product_observed": False, "create_retried": False},
            })
            _record_journal_outcome(
                base,
                journal_path,
                journal,
                status_value="create_failed_no_candidate_manual_review",
                resolved=False,
            )
            return base
        _manual_candidate_outcome(
            base,
            candidates,
            cli,
            environment,
            expectation,
            runner,
            status_prefix="create_failed_reconciliation",
        )
        _record_journal_outcome(
            base,
            journal_path,
            journal,
            status_value="create_failed_candidate_observed_remote_hashes_unverifiable",
            resolved=False,
            product_id=base.get("product_id"),
        )
        return base

    try:
        create_payload = parse_json_output(create_result, "products_create")
        product_id = validate_create_response(create_payload, expectation)
    except ValidationError as exc:
        base.update({
            "status": "create_response_contract_failed",
            "needs_manual_review": True,
            "authenticated_write_state": "product_may_have_been_created",
            "create": {"error": str(exc), "diagnostics": diagnostics(create_result)},
        })
        candidates, reconcile_error = list_potential_matches(
            cli, environment, expectation, runner
        )
        if reconcile_error:
            base["reconciliation"] = reconcile_error
        elif candidates:
            _manual_candidate_outcome(
                base,
                candidates,
                cli,
                environment,
                expectation,
                runner,
                status_prefix="create_response_contract_failed_reconciliation",
            )
        else:
            base["reconciliation"] = {"potential_product_observed": False, "create_retried": False}
        _record_journal_outcome(
            base,
            journal_path,
            journal,
            status_value="create_response_invalid_manual_review",
            resolved=False,
            product_id=base.get("product_id"),
        )
        return base

    # A valid create response proves the product exists. Persist its ID before
    # spawning the read-only view so a crash or local spawn/resource failure can
    # always reconcile that specific product on the next invocation.
    base.update({
        "authenticated_write_performed": True,
        "authenticated_write_state": "confirmed_by_valid_create_response",
        "product_id": product_id,
        "create_response": {
            "product_id_and_name_validated": True,
            "published_false_validated": True,
        },
    })
    persisted_journal = _record_journal_outcome(
        base,
        journal_path,
        journal,
        status_value="create_response_valid_pending_post_create_view",
        resolved=False,
        product_id=product_id,
    )
    if persisted_journal is None:
        base.update({
            "ok": False,
            "needs_manual_review": True,
            "status": "created_product_id_journal_persist_failed_manual_review",
        })
        return base
    journal = persisted_journal

    verified, view_error = read_product_view(cli, product_id, environment, expectation, runner)
    if view_error:
        base.update({
            "status": "created_product_requires_manual_review",
            "needs_manual_review": True,
            "authenticated_write_performed": True,
            "product_id": product_id,
            "verification": view_error,
        })
        _record_journal_outcome(
            base,
            journal_path,
            journal,
            status_value="post_create_view_failed_manual_review",
            resolved=False,
            product_id=product_id,
        )
        return base
    resolved_journal = _record_journal_outcome(
        base,
        journal_path,
        journal,
        status_value="verified_unpublished_draft_created",
        resolved=True,
        product_id=product_id,
    )
    if resolved_journal is None:
        base.update({
            "ok": False,
            "needs_manual_review": True,
            "status": "created_and_verified_but_attempt_journal_resolution_failed",
            "authenticated_write_performed": True,
            "product_id": product_id,
            "verification": verified,
        })
        return base
    base.update({
        "ok": True,
        "status": "created_and_verified_exact_unpublished_draft",
        "authenticated_write_performed": True,
        "product_id": product_id,
        "draft_confirmation_source": "read_only_products_view",
        "verification": verified,
    })
    return base


def dry_run_flow(
    create_command: list[str],
    environment: dict[str, str],
    expectation: dict[str, Any],
    runner: Runner = run_process,
) -> dict[str, Any]:
    result = invoke_runner(
        runner, create_command, environment, PROCESS_TIMEOUT_SECONDS
    )
    validated = validate_dry_run_output(result, expectation)
    return {
        "ok": True,
        "needs_manual_review": False,
        "status": "full_exact_dry_run_passed",
        "official_cli_auth_used": False,
        "authenticated_api_request_used": False,
        "authenticated_api_request_succeeded": False,
        "authenticated_cli_command_attempted": False,
        "authentication_flow_started": False,
        "credential_source": "none_isolated_HOME_XDG",
        "official_cli_may_read_own_auth_config": False,
        "wrapper_parses_credentials": False,
        "publication_attempted": False,
        "authenticated_write_performed": False,
        "authenticated_write_attempted": False,
        "cli_exit_code": result.returncode,
        "cli_output": validated,
    }


def write_report(path: Path, report: dict[str, Any]) -> None:
    if path != REPORT_PATH:
        raise ValidationError("report_path_not_fixed")
    atomic_write_json(REPORT_PATH, report, 0o644)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate or create one exact unpublished Gumroad draft; dry-run is the default."
    )
    parser.add_argument("--config", default=str(CANONICAL_CONFIG))
    parser.add_argument("--gumroad-bin", default="gumroad")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Use authenticated read-only reconciliation, then create and verify one draft if absent; never publish.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    report: dict[str, Any] = {
        "ok": False,
        "needs_manual_review": False,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "classification": "assistant_operational_validation_not_permanent_directive",
        "mode": "execute_reconcile_or_create_draft" if args.execute else "dry_run",
        "draft_only": True,
        "publication_attempted": False,
        "authentication_flow_started": False,
        "wrapper_parses_credentials": False,
        "official_cli_may_read_own_auth_config": bool(args.execute),
        "official_cli_auth_used": False,
        "cost_yen": 0,
        "errors": [],
    }
    try:
        config_path = Path(args.config)
        config, config_sha256 = load_config_once(config_path, args.execute)
        validate_config_shape(config)

        with pinned_cli_copy(args.gumroad_bin) as (cli, private_root):
            isolated_environment = make_isolated_environment(private_root)
            version = validate_version(cli, isolated_environment)
            command, expectation = build_command(cli, config, args.execute, private_root)
            report.update({
                "cli_version": version,
                "cli_binary_sha256": OFFICIAL_CLI_SHA256,
                "pinned_private_cli_copy": True,
                "pinned_cli_copy_mode": "0700",
                "canonical_config_sha256": CANONICAL_CONFIG_SHA256,
                "loaded_config_sha256": config_sha256,
                "command": "gumroad products create",
                "dry_run_flag_present": "--dry-run" in command,
                "inputs": {
                    "title": expectation["title"],
                    "description_source_chars": len(expectation["description_source"]),
                    "description_html_chars": len(expectation["description_html"]),
                    "custom_summary": expectation["custom_summary"],
                    "custom_permalink": expectation["custom_permalink"],
                    "tag_count": len(expectation["tags"]),
                    "price": expectation["price"],
                    "currency": expectation["currency"],
                    "refund_period_days": 7,
                    "refund_fine_print_chars": len(expectation["refund_fine_print"]),
                    "product": expectation["product"],
                    "media": expectation["media"],
                    "semantic_plan_sha256": expectation["semantic_plan_sha256"],
                },
            })
            if args.execute:
                outcome = execute_with_reconciliation(
                    cli, command, make_execute_environment(), expectation
                )
            else:
                outcome = dry_run_flow(command, isolated_environment, expectation)
            report.update(outcome)
    except (KeyError, TypeError, ValidationError, OSError, subprocess.SubprocessError) as exc:
        report["errors"].append(redact_and_limit(str(exc)))

    write_report(REPORT_PATH, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
