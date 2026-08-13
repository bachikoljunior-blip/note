#!/usr/bin/env python3
"""Fail-closed validation for the Assistants Migration Checker Product Hunt draft."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import parse_qs, urlparse


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def svg_dimension(value: str | None) -> int | None:
    if value is None:
        return None
    match = re.fullmatch(r"([0-9]+)(?:px)?", value.strip())
    return int(match.group(1)) if match else None


def png_dimensions(path: Path) -> tuple[int, int] | None:
    """Return PNG IHDR dimensions without third-party image dependencies."""
    data = path.read_bytes()[:24]
    if len(data) != 24 or data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR":
        return None
    return struct.unpack(">II", data[16:24])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/product_hunt_assistants_migration.json"),
    )
    args = parser.parse_args()
    root = args.root.resolve()
    config_path = args.config if args.config.is_absolute() else root / args.config
    errors: list[str] = []

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "failed", "errors": [str(exc)]}))
        return 1

    def require(condition: bool, message: str) -> None:
        if not condition:
            errors.append(message)

    require(config.get("schema_version") == "1.0", "unsupported schema_version")
    fields = config.get("fields", {})
    required = ("product_name", "direct_url", "tagline", "description", "pricing", "topics", "status", "first_comment")
    for key in required:
        require(bool(fields.get(key)), f"missing field: {key}")

    tagline = fields.get("tagline", "")
    description = fields.get("description", "")
    require(len(tagline) == config.get("limits", {}).get("tagline_expected_characters"), "tagline length changed")
    require(len(description) <= config.get("limits", {}).get("description_max_characters", 0), "description exceeds limit")
    require(len(description) == config.get("limits", {}).get("description_expected_characters"), "description length changed")
    require(str(fields.get("pricing", "")).lower() == "free", "pricing must remain Free")
    require(str(fields.get("status", "")).lower() == "live", "status must remain Live")
    topics = fields.get("topics", [])
    require(isinstance(topics, list) and 1 <= len(topics) <= 3, "topics must contain one to three items")
    require(len(topics) == len(set(topics)), "topics must be unique")

    parsed = urlparse(fields.get("direct_url", ""))
    require(parsed.scheme == "https" and bool(parsed.netloc), "direct_url must be an absolute HTTPS URL")
    query = parse_qs(parsed.query)
    for key, expected in config.get("required_utm", {}).items():
        require(query.get(key) == [expected], f"missing or changed UTM field: {key}")

    first_comment = fields.get("first_comment", "")
    for phrase in config.get("required_first_comment_phrases", []):
        require(phrase in first_comment, f"first comment missing disclosure: {phrase}")
    publishable_text = "\n".join(
        str(fields.get(key, "")) for key in ("product_name", "tagline", "description", "first_comment")
    )
    for pattern in config.get("forbidden_claim_patterns", []):
        require(re.search(pattern, publishable_text, flags=re.IGNORECASE) is None, f"forbidden claim pattern matched: {pattern}")

    launch_state = config.get("launch_state", {})
    for key in ("submitted", "scheduled", "published"):
        require(launch_state.get(key) is False, f"{key} must remain false in preflight")

    draft_path = root / config.get("draft_path", "")
    try:
        draft = draft_path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"draft unavailable: {exc}")
        draft = ""
    draft_needles = [
        fields.get("product_name", ""),
        fields.get("direct_url", ""),
        fields.get("tagline", ""),
        fields.get("description", ""),
        f"- Pricing: {fields.get('pricing', '')}",
        f"- Topics: {'; '.join(topics)}",
        f"- Status: {fields.get('status', '')}",
        fields.get("first_comment", ""),
        "prepared, not submitted, not scheduled",
    ]
    for needle in draft_needles:
        require(bool(needle) and needle in draft, f"draft/config drift: {needle[:80]}")

    assets = config.get("gallery_assets", [])
    require(len(assets) >= 2, "at least two gallery assets are required")
    seen_paths: set[str] = set()
    for asset in assets:
        rel = asset.get("path", "")
        require(rel not in seen_paths, f"duplicate asset path: {rel}")
        seen_paths.add(rel)
        path = root / rel
        if not path.is_file():
            errors.append(f"asset unavailable: {rel}")
            continue
        require(sha256(path) == asset.get("sha256"), f"asset SHA-256 mismatch: {rel}")
        try:
            svg = ET.parse(path).getroot()
            width = svg_dimension(svg.get("width"))
            height = svg_dimension(svg.get("height"))
        except (ET.ParseError, OSError) as exc:
            errors.append(f"invalid SVG {rel}: {exc}")
            continue
        require((width, height) == (asset.get("width"), asset.get("height")), f"asset dimensions changed: {rel}")

    upload_assets = config.get("upload_assets", [])
    require(len(upload_assets) == 3, "exactly one thumbnail and two upload-ready gallery PNGs are required")
    roles = [asset.get("role") for asset in upload_assets]
    require(roles.count("thumbnail") == 1, "exactly one upload-ready thumbnail is required")
    require(roles.count("gallery") == 2, "exactly two upload-ready gallery images are required")
    upload_paths: set[str] = set()
    for asset in upload_assets:
        rel = asset.get("path", "")
        require(bool(rel) and rel not in upload_paths, f"duplicate upload asset path: {rel}")
        upload_paths.add(rel)
        path = root / rel
        if not path.is_file():
            errors.append(f"upload asset unavailable: {rel}")
            continue
        require(path.suffix.lower() == ".png", f"upload asset must be PNG: {rel}")
        require(sha256(path) == asset.get("sha256"), f"upload asset SHA-256 mismatch: {rel}")
        try:
            dimensions = png_dimensions(path)
        except OSError as exc:
            errors.append(f"upload asset unreadable: {rel}: {exc}")
            continue
        require(dimensions is not None, f"invalid PNG: {rel}")
        require(dimensions == (asset.get("width"), asset.get("height")), f"upload asset dimensions changed: {rel}")

    for source in config.get("primary_sources", []):
        parsed_source = urlparse(source)
        require(parsed_source.scheme == "https" and bool(parsed_source.netloc), f"invalid source URL: {source}")

    result = {
        "status": "passed" if not errors else "failed",
        "product_name": fields.get("product_name"),
        "tagline_characters": len(tagline),
        "description_characters": len(description),
        "gallery_asset_count": len(assets),
        "upload_asset_count": len(upload_assets),
        "launch_state": launch_state,
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
