#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import stat
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
FORMAT_MAP_PATH = ROOT / "config" / "english_topic_format_map.json"
PRODUCT = ROOT / "dist" / "Non_Repetitive_AI_Trivia_Shorts_Kit_EN_v1.1.zip"
REPORT = ROOT / "reports" / "english_product_quality.json"
TITLE = "Non-Repetitive AI Trivia Shorts Kit: 100 Topic Prompts + 12 Formats"
JAPANESE = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")
ALLOWED_SUFFIXES = {".csv", ".json", ".md", ".txt"}
FIXED_ZIP_TIME = (2026, 8, 7, 0, 0, 0)
MAX_ZIP_BYTES = 2_000_000
EXPECTED_PRODUCT_BYTES = 97319
EXPECTED_PRODUCT_SHA256 = "3adb147dc55b671d99141281cc9849e3530a8865def543d341c326a54bcf0113"
MAX_MEMBER_BYTES = 1_000_000
MAX_TOTAL_UNCOMPRESSED_BYTES = 2_000_000
EXPECTED_MEMBERS = [
    "100_topics.csv",
    "12_formats.md",
    "30_day_calendar.csv",
    "CHANGELOG.md",
    "LICENSE.txt",
    "README_PRODUCT.md",
    "REFERENCES.md",
    "WORKED_EXAMPLE_ice_floats.md",
    "analytics_decision_rules.md",
    "analytics_tracker.csv",
    "manifest.json",
    "originality_audit.md",
    "preview_10_topics.csv",
    "prompt_library.md",
    "source_log.csv",
]
EXPECTED_TOPIC_FIELDS = [
    "id", "category", "core_question", "recommended_format", "hook_direction",
    "visual_direction", "source_priority", "verification_risk",
]
EXPECTED_CALENDAR_FIELDS = [
    "day", "topic_id", "category", "format_id", "experiment_variable", "cta",
    "review_48h", "review_7d",
]
EXPECTED_SOURCE_LOG_FIELDS = [
    "topic_id", "video_id", "claim_id", "claim_text", "source_title", "publisher",
    "source_url", "source_type", "publication_or_update_date", "accessed_at",
    "support_summary", "conflicts_or_limits", "confidence", "publish_decision",
]
EXPECTED_CATEGORIES = {
    "Everyday Science", "Brain & Perception", "AI & Technology",
    "History & Standards", "Systems & Society",
}
EXPECTED_REFERENCE_URLS = {
    "https://support.google.com/youtube/answer/1311392",
    "https://support.google.com/youtube/answer/72851",
    "https://support.google.com/youtube/answer/13429240",
    "https://support.google.com/youtube/answer/14328491",
    "https://developers.google.com/youtube/analytics/metrics",
    "https://developers.google.com/youtube/analytics/revision_history",
}
EXPECTED_EXAMPLE_URLS = {
    "https://www.pmel.noaa.gov/arctic-zone/essay_wadhams.html",
    "https://www.usgs.gov/water-science-school/science/water-density",
}
EXPECTED_ANALYTICS_FIELDS = [
    "video_id", "publish_date", "topic_id", "format_id", "duration_sec",
    "hook_variant", "visual_variant", "cta_variant", "views", "engaged_views",
    "average_view_duration_sec", "average_view_percentage", "likes", "comments",
    "shares", "subscribers_gained", "subscribers_lost",
    "youtube_estimated_revenue", "youtube_revenue_currency_code", "link_clicks",
    "product_sales", "attributed_product_revenue", "product_revenue_currency_code",
    "reporting_currency_code", "youtube_to_reporting_fx_rate",
    "product_to_reporting_fx_rate", "fx_rate_date", "fx_rate_source",
    "youtube_revenue_reporting_currency", "product_revenue_reporting_currency",
    "youtube_revenue_per_1000_engaged_views_reporting_currency",
    "product_revenue_per_1000_engaged_views_reporting_currency",
    "engaged_view_rate", "share_rate", "comment_rate", "net_subscriber_rate",
    "decision", "next_action",
]


def csv_bytes(rows: list[dict[str, str]], fieldnames: list[str]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return b"\xef\xbb\xbf" + stream.getvalue().encode("utf-8")


def add_if(condition: bool, error: str, errors: list[str]) -> None:
    if condition:
        errors.append(error)


def main() -> int:
    errors: list[str] = []
    details: dict[str, object] = {}
    names: list[str] = []
    require_visual_report = "--require-visual-report" in sys.argv[1:]
    format_contract = json.loads(FORMAT_MAP_PATH.read_text(encoding="utf-8"))
    add_if(format_contract.get("schema_version") != "1.0", "format_map_schema_version", errors)
    add_if(
        format_contract.get("classification")
        != "assistant_curated_product_configuration_not_permanent_directive",
        "format_map_classification",
        errors,
    )
    curated_formats = format_contract.get("topic_formats", {})
    add_if(not isinstance(curated_formats, dict), "format_map_topic_formats", errors)
    if not isinstance(curated_formats, dict):
        curated_formats = {}
    expected_anchors = ["T004:F04", "T066:F06", "T093:F09"]
    add_if(
        format_contract.get("review", {}).get("required_visual_anchors") != expected_anchors,
        "format_map_visual_anchors",
        errors,
    )
    if not PRODUCT.is_file():
        errors.append("v1_1_product_missing")
        data = b""
    elif PRODUCT.stat().st_size > MAX_ZIP_BYTES:
        errors.append(f"zip_size_cap:{PRODUCT.stat().st_size}>{MAX_ZIP_BYTES}")
        data = b""
    else:
        data = PRODUCT.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    add_if(len(data) != EXPECTED_PRODUCT_BYTES, f"release_bytes:{len(data)}", errors)
    add_if(digest != EXPECTED_PRODUCT_SHA256, f"release_sha256:{digest}", errors)

    members: dict[str, bytes] = {}
    if data:
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                infos = archive.infolist()
                names = [info.filename for info in infos]
                metadata_safe = True
                if names != EXPECTED_MEMBERS:
                    errors.append(f"zip_member_contract:{names}")
                    metadata_safe = False
                if len(names) != len(set(names)):
                    errors.append("duplicate_zip_member")
                    metadata_safe = False
                if names != sorted(names):
                    errors.append("zip_members_not_sorted")
                    metadata_safe = False
                total_uncompressed = sum(info.file_size for info in infos)
                if total_uncompressed > MAX_TOTAL_UNCOMPRESSED_BYTES:
                    errors.append(
                        f"zip_total_uncompressed_cap:{total_uncompressed}>{MAX_TOTAL_UNCOMPRESSED_BYTES}"
                    )
                    metadata_safe = False
                for info in infos:
                    path = PurePosixPath(info.filename)
                    if path.is_absolute() or ".." in path.parts or "\\" in info.filename:
                        errors.append(f"unsafe_zip_member:{info.filename}")
                        metadata_safe = False
                    if info.flag_bits & 0x1:
                        errors.append(f"encrypted_zip_member:{info.filename}")
                        metadata_safe = False
                    if info.compress_type != zipfile.ZIP_STORED:
                        errors.append(f"non_portable_zip_compression:{info.filename}")
                        metadata_safe = False
                    if info.file_size > MAX_MEMBER_BYTES:
                        errors.append(f"zip_member_size_cap:{info.filename}:{info.file_size}")
                        metadata_safe = False
                    if info.compress_size != info.file_size:
                        errors.append(f"zip_member_size_ratio:{info.filename}")
                        metadata_safe = False
                    mode = info.external_attr >> 16
                    if info.create_system != 3 or stat.S_IFMT(mode) != stat.S_IFREG:
                        errors.append(f"non_regular_zip_member:{info.filename}")
                        metadata_safe = False
                    if stat.S_IMODE(mode) != 0o644:
                        errors.append(f"zip_member_permissions:{info.filename}:{oct(stat.S_IMODE(mode))}")
                        metadata_safe = False
                    if info.date_time != FIXED_ZIP_TIME:
                        errors.append(f"zip_member_timestamp:{info.filename}:{info.date_time}")
                        metadata_safe = False
                    if path.suffix.lower() not in ALLOWED_SUFFIXES:
                        errors.append(f"unsupported_zip_member:{info.filename}")
                        metadata_safe = False
                if metadata_safe:
                    bad_member = archive.testzip()
                    if bad_member is not None:
                        errors.append(f"corrupt_zip_member:{bad_member}")
                    else:
                        members = {name: archive.read(name) for name in names}
        except Exception as exc:  # noqa: BLE001
            errors.append(f"zip_open:{type(exc).__name__}:{exc}")

    if members:
        manifest = json.loads(members["manifest.json"].decode("utf-8"))
        add_if(
            set(manifest)
            != {"product_name", "version", "release_date", "language", "content_summary", "files", "disclaimer"},
            f"manifest_top_level_keys:{sorted(manifest)}",
            errors,
        )
        add_if(
            manifest.get("product_name") != "Non-Repetitive AI Trivia Shorts Kit",
            "manifest_product_name",
            errors,
        )
        add_if(manifest.get("version") != "1.1", "manifest_version", errors)
        add_if(manifest.get("release_date") != "2026-08-07", "manifest_release_date", errors)
        add_if(manifest.get("language") != "English", "manifest_language", errors)
        add_if(
            manifest.get("disclaimer")
            != "Topic rows are research prompts, not pre-verified factual claims.",
            "manifest_disclaimer",
            errors,
        )
        expected_names = sorted(name for name in names if name != "manifest.json")
        manifest_items = manifest.get("files", [])
        manifest_names = [item.get("name") for item in manifest_items]
        add_if(manifest_names != expected_names, "manifest_member_names", errors)
        manifest_by_name = {item.get("name"): item for item in manifest_items}
        for name in expected_names:
            item = manifest_by_name.get(name, {})
            add_if(item.get("bytes") != len(members[name]), f"manifest_bytes:{name}", errors)
            add_if(
                item.get("sha256") != hashlib.sha256(members[name]).hexdigest(),
                f"manifest_sha256:{name}",
                errors,
            )
        summary = manifest.get("content_summary", {})
        expected_summary = {
            "topic_prompts": 100,
            "story_formats": 12,
            "workflow_prompts": 9,
            "visual_planning_patterns": 25,
            "fully_worked_script_examples": 1,
        }
        add_if(summary != expected_summary, f"manifest_summary:{summary}", errors)

        formats_text = members["12_formats.md"].decode("utf-8")
        format_headings = re.findall(r"^## (F\d{2})\b", formats_text, flags=re.MULTILINE)
        add_if(
            format_headings != [f"F{index:02d}" for index in range(1, 13)],
            f"format_heading_contract:{format_headings}",
            errors,
        )
        prompt_text = members["prompt_library.md"].decode("utf-8")
        prompt_headings = re.findall(r"^## (P\d{2})\b", prompt_text, flags=re.MULTILINE)
        add_if(
            prompt_headings != [f"P{index:02d}" for index in range(1, 10)],
            f"prompt_heading_contract:{prompt_headings}",
            errors,
        )
        worked_example = members["WORKED_EXAMPLE_ice_floats.md"].decode("utf-8")
        add_if(len(worked_example) < 3500, "worked_example_too_short", errors)
        for heading in (
            "## 1. Research decision",
            "## 2. 55-second script",
            "## 3. Six connected clips",
            "## 4. Originality additions",
            "## 5. 48-hour review",
        ):
            add_if(heading not in worked_example, f"worked_example_missing:{heading}", errors)
        example_urls = set(re.findall(r"https://[^\s)]+", worked_example))
        add_if(example_urls != EXPECTED_EXAMPLE_URLS, f"worked_example_urls:{sorted(example_urls)}", errors)
        references = members["REFERENCES.md"].decode("utf-8")
        reference_urls = set(re.findall(r"https://[^\s)]+", references))
        add_if(reference_urls != EXPECTED_REFERENCE_URLS, f"reference_urls:{sorted(reference_urls)}", errors)
        license_text = members["LICENSE.txt"].decode("utf-8")
        for phrase in (
            "The purchaser may use this kit to create commercial",
            "Redistributing, reselling, sharing, or publicly uploading",
            "does not guarantee revenue, views",
            "responsible for final fact-checking, rights clearance, disclosure, and publication decisions",
        ):
            add_if(phrase not in license_text, f"license_contract_missing:{phrase}", errors)
        for name, member in members.items():
            add_if(len(member) == 0, f"empty_required_member:{name}", errors)

        topic_reader = csv.DictReader(
            io.StringIO(members["100_topics.csv"].decode("utf-8-sig"))
        )
        topic_fields = list(topic_reader.fieldnames or [])
        topics = list(topic_reader)
        ids = [row.get("id", "") for row in topics]
        questions = [row.get("core_question", "") for row in topics]
        category_counts = Counter(row.get("category", "") for row in topics)
        format_counts = Counter(row.get("recommended_format", "") for row in topics)
        add_if(topic_fields != EXPECTED_TOPIC_FIELDS, f"topic_header:{topic_fields}", errors)
        add_if(len(topics) != 100, f"topics:{len(topics)}!=100", errors)
        add_if(ids != [f"T{index:03d}" for index in range(1, 101)], "topic_id_sequence", errors)
        add_if(len(set(ids)) != 100, "topic_ids_not_unique", errors)
        add_if(len(set(questions)) != 100, "topic_questions_not_unique", errors)
        add_if(set(curated_formats) != set(ids), "format_map_topic_ids", errors)
        add_if(set(category_counts) != EXPECTED_CATEGORIES, "topic_categories", errors)
        for row in topics:
            for field in EXPECTED_TOPIC_FIELDS:
                add_if(not row.get(field, "").strip(), f"topic_empty:{row.get('id')}:{field}", errors)
            add_if(
                row.get("recommended_format") != curated_formats.get(row.get("id", "")),
                f"topic_format_contract:{row.get('id')}",
                errors,
            )
        add_if(
            sorted(category_counts.values()) != [20, 20, 20, 20, 20],
            f"category_distribution:{dict(category_counts)}",
            errors,
        )
        add_if(
            set(format_counts) != {f"F{index:02d}" for index in range(1, 13)},
            "format_ids",
            errors,
        )
        add_if(min(format_counts.values(), default=0) < 2, f"format_underused:{dict(format_counts)}", errors)
        add_if(max(format_counts.values(), default=0) > 15, f"format_overconcentrated:{dict(format_counts)}", errors)

        signature_counts: Counter[str] = Counter()
        format_to_signatures: dict[str, set[str]] = defaultdict(set)
        signature_to_formats: dict[str, set[str]] = defaultdict(set)
        visual_counts: Counter[str] = Counter()
        category_visuals: dict[str, set[str]] = defaultdict(set)
        format_visual_pairs: set[tuple[str, str]] = set()
        for row in topics:
            question = row.get("core_question", "")
            hook = row.get("hook_direction", "")
            format_id = row.get("recommended_format", "")
            visual = row.get("visual_direction", "")
            add_if(hook.count(question) != 1, f"hook_question_count:{row.get('id')}", errors)
            signature = re.sub(r"\s+", " ", hook.replace(question, "<QUESTION>")).strip()
            signature_counts[signature] += 1
            format_to_signatures[format_id].add(signature)
            signature_to_formats[signature].add(format_id)
            visual_counts[visual] += 1
            category_visuals[row.get("category", "")].add(visual)
            format_visual_pairs.add((format_id, visual))
        add_if(len(signature_counts) != 12, f"hook_signatures:{len(signature_counts)}!=12", errors)
        add_if(max(signature_counts.values(), default=0) > 15, f"hook_signature_overconcentrated:{dict(signature_counts)}", errors)
        add_if(
            any(len(values) != 1 for values in format_to_signatures.values()),
            "format_to_hook_signature_not_one_to_one",
            errors,
        )
        add_if(
            any(len(values) != 1 for values in signature_to_formats.values()),
            "hook_signature_to_format_not_one_to_one",
            errors,
        )
        add_if(len(visual_counts) != 25, f"visual_patterns:{len(visual_counts)}!=25", errors)
        add_if(
            any(count != 4 for count in visual_counts.values()),
            f"visual_pattern_distribution:{dict(visual_counts)}",
            errors,
        )
        add_if(
            any(len(values) != 5 for values in category_visuals.values()),
            "category_visual_count_not_five",
            errors,
        )
        visual_owners: dict[str, set[str]] = defaultdict(set)
        for category, visuals in category_visuals.items():
            for visual in visuals:
                visual_owners[visual].add(category)
        add_if(
            any(len(owners) != 1 for owners in visual_owners.values()),
            "visual_pattern_shared_between_categories",
            errors,
        )

        expected_preview = csv_bytes(topics[:10], topic_fields)
        add_if(
            members["preview_10_topics.csv"] != expected_preview,
            "preview_does_not_equal_first_ten_topics",
            errors,
        )

        calendar_reader = csv.DictReader(
            io.StringIO(members["30_day_calendar.csv"].decode("utf-8-sig"))
        )
        calendar_fields = list(calendar_reader.fieldnames or [])
        calendar = list(calendar_reader)
        by_id = {row["id"]: row for row in topics}
        add_if(calendar_fields != EXPECTED_CALENDAR_FIELDS, f"calendar_header:{calendar_fields}", errors)
        add_if(len(calendar) != 30, f"calendar_rows:{len(calendar)}!=30", errors)
        add_if(
            [row.get("day") for row in calendar] != [str(day) for day in range(1, 31)],
            "calendar_day_sequence",
            errors,
        )
        add_if(len({row.get("topic_id") for row in calendar}) != 30, "calendar_topic_ids", errors)
        for row in calendar:
            topic = by_id.get(row.get("topic_id", ""))
            if topic is None or row.get("format_id") != topic.get("recommended_format"):
                errors.append(f"calendar_format_mismatch:{row.get('day')}")
            if topic is None or row.get("category") != topic.get("category"):
                errors.append(f"calendar_category_mismatch:{row.get('day')}")
            for field in ("experiment_variable", "cta", "review_48h", "review_7d"):
                add_if(not row.get(field, "").strip(), f"calendar_empty:{row.get('day')}:{field}", errors)
            try:
                day = int(row.get("day", ""))
            except ValueError:
                continue
            add_if(row.get("review_48h") != f"Day {day + 2}", f"calendar_review_48h:{day}", errors)
            add_if(row.get("review_7d") != f"Day {day + 7}", f"calendar_review_7d:{day}", errors)
        add_if(
            any(row.get("cta") == "point to the free preview" for row in calendar),
            "unavailable_free_preview_cta",
            errors,
        )

        readme = members["README_PRODUCT.md"].decode("utf-8")
        for required in (
            "Use P03 to draft the script, then optionally use P04",
            "not 100 finished scripts",
            "one fully worked 55-second script example",
            "youtube_estimated_revenue",
            "attributed_product_revenue",
            "youtube_revenue_currency_code",
            "product_revenue_currency_code",
            "reporting_currency_code",
            "youtube_to_reporting_fx_rate",
            "product_to_reporting_fx_rate",
            "fx_rate_date",
            "fx_rate_source",
            "Never add or compare the two raw revenue values",
        ):
            add_if(required not in readme, f"readme_required:{required}", errors)
        add_if("Use P03 or P04" in readme, "readme_old_p03_p04", errors)

        source_reader = csv.DictReader(
            io.StringIO(members["source_log.csv"].decode("utf-8-sig"))
        )
        source_fields = list(source_reader.fieldnames or [])
        source_rows = list(source_reader)
        add_if(source_fields != EXPECTED_SOURCE_LOG_FIELDS, f"source_log_header:{source_fields}", errors)
        add_if(source_rows != [], "source_log_template_must_be_empty", errors)

        analytics_header = next(
            csv.reader(io.StringIO(members["analytics_tracker.csv"].decode("utf-8-sig")))
        )
        add_if(analytics_header != EXPECTED_ANALYTICS_FIELDS, "analytics_header", errors)
        add_if("estimated_revenue" in analytics_header, "old_estimated_revenue_column", errors)
        add_if("revenue" in analytics_header, "old_revenue_column", errors)

        prompt_library = members["prompt_library.md"].decode("utf-8")
        rules = members["analytics_decision_rules.md"].decode("utf-8")
        for required in (
            "youtube_estimated_revenue × youtube_to_reporting_fx_rate",
            "attributed_product_revenue × product_to_reporting_fx_rate",
            "youtube_revenue_reporting_currency / engaged_views × 1000",
            "product_revenue_reporting_currency / engaged_views × 1000",
            "both FX rates",
            "FX source",
        ):
            add_if(required not in prompt_library, f"prompt_required:{required}", errors)
        for old_name in (
            "engagedViews",
            "subscribersGained",
            "subscribersLost",
            "productSales",
            "linkClicks",
        ):
            add_if(old_name in prompt_library, f"prompt_old_column_name:{old_name}", errors)
        for required in (
            "youtube_revenue_reporting_currency / engaged_views * 1000",
            "product_revenue_reporting_currency / engaged_views * 1000",
            "youtube_revenue_currency_code",
            "product_revenue_currency_code",
            "reporting_currency_code",
            "fx_rate_date",
            "fx_rate_source",
        ):
            add_if(required not in rules, f"analytics_rules_required:{required}", errors)

        for name, member in members.items():
            text = member.decode("utf-8-sig")
            if JAPANESE.search(text):
                errors.append(f"japanese_character_found:{name}")
            lowered = text.lower()
            for placeholder in ("todo", "[confirm]", "insert here"):
                if placeholder in lowered:
                    errors.append(f"placeholder_found:{name}:{placeholder}")

        details.update({
            "topics": len(topics),
            "categories": dict(sorted(category_counts.items())),
            "formats": dict(sorted(format_counts.items())),
            "hook_signatures": len(signature_counts),
            "visual_patterns": len(visual_counts),
            "format_visual_pairs": len(format_visual_pairs),
        })

    title = (ROOT / "content" / "gumroad" / "title.txt").read_text(encoding="utf-8").strip()
    description = (ROOT / "content" / "gumroad" / "description.md").read_text(encoding="utf-8").strip()
    tags = [
        line.strip()
        for line in (ROOT / "content" / "gumroad" / "tags.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    add_if(title != TITLE, "listing_title", errors)
    for required in (
        "100 topic prompts, each paired with one of 12 format-specific hook approaches and one of 25 visual-planning patterns",
        "One fully worked 55-second script example",
        "This is not a pack of 100 finished scripts.",
        "primary or near-primary sources",
        "does not guarantee views",
        "digital download",
        "Redistribution",
    ):
        add_if(required.lower() not in description.lower(), f"listing_required:{required}", errors)
    add_if("under 25 KB".lower() in description.lower(), "listing_under_25kb", errors)
    add_if(not 5 <= len(tags) <= 10 or len(tags) != len(set(tags)), "listing_tags", errors)
    add_if("video scripts" in {tag.lower() for tag in tags}, "misleading_video_scripts_tag", errors)
    add_if("script prompts" not in {tag.lower() for tag in tags}, "script_prompts_tag_missing", errors)

    listing_state = json.loads((ROOT / "state" / "gumroad_listing.json").read_text(encoding="utf-8"))
    current_state = json.loads((ROOT / "state" / "current.json").read_text(encoding="utf-8"))
    distribution = json.loads((ROOT / "config" / "gumroad_distribution.json").read_text(encoding="utf-8"))
    listing_product = listing_state.get("product", {})
    current_product = current_state.get("product_artifacts", {}).get("english_product", {})
    for label, product_state in (("listing", listing_product), ("current", current_product)):
        add_if(product_state.get("version") != "1.1", f"state_version:{label}", errors)
        add_if(product_state.get("output") != str(PRODUCT.relative_to(ROOT)), f"state_output:{label}", errors)
        add_if(product_state.get("bytes") != len(data), f"state_bytes:{label}", errors)
        add_if(product_state.get("sha256") != digest, f"state_sha256:{label}", errors)
        add_if(product_state.get("zip_members") != 15, f"state_members:{label}", errors)
    for key, expected in {
        "artifact_id": "product_en_v1_1",
        "topic_prompts": 100,
        "formats": 12,
        "hook_signatures": 12,
        "visual_planning_patterns": 25,
        "workflow_prompts": 9,
        "fully_worked_script_examples": 1,
    }.items():
        add_if(listing_product.get(key) != expected, f"listing_state_fact:{key}", errors)
    add_if(listing_state.get("language") != "English", "listing_state_language", errors)
    for key, expected in {
        "artifact_id": "product_en_v1_1",
        "topics": 100,
        "formats": 12,
        "hook_signatures": 12,
        "visual_planning_patterns": 25,
        "prompts": 9,
        "fully_worked_script_examples": 1,
        "language": "English",
    }.items():
        add_if(current_product.get(key) != expected, f"current_state_fact:{key}", errors)
    sales_channel = current_state.get("sales_channels", {}).get("gumroad", {})
    add_if(sales_channel.get("product_version") != "1.1", "sales_channel_product_version", errors)
    add_if(
        sales_channel.get("product_output") != str(PRODUCT.relative_to(ROOT)),
        "sales_channel_product_output",
        errors,
    )
    distribution_product = distribution.get("product", {})
    add_if(distribution_product.get("title") != TITLE, "distribution_title", errors)
    add_if(distribution_product.get("version") != "1.1", "distribution_version", errors)
    distribution_facts = distribution_product.get("facts", {})
    for key, expected in {
        "topics": 100,
        "formats": 12,
        "prompts": 9,
        "hook_signatures": 12,
        "visual_planning_patterns": 25,
        "fully_worked_script_examples": 1,
        "price_usd": 12.0,
    }.items():
        add_if(distribution_facts.get(key) != expected, f"distribution_fact:{key}", errors)

    if require_visual_report:
        visual_report_path = ROOT / "reports" / "gumroad_visual_pack.json"
        if visual_report_path.is_file():
            visual_report = json.loads(visual_report_path.read_text(encoding="utf-8"))
            sample_pairs = [
                (item.get("id"), item.get("format_id"))
                for item in visual_report.get("sample_topics", [])
            ]
            add_if(
                sample_pairs != [("T004", "F04"), ("T066", "F06"), ("T093", "F09")],
                f"visual_sample_topics:{sample_pairs}",
                errors,
            )
        else:
            errors.append("gumroad_visual_report_missing")

    payload = {
        "ok": not errors,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "output": str(PRODUCT.relative_to(ROOT)),
        "bytes": len(data),
        "sha256": digest,
        "zip_members": len(names),
        "visual_report_required": require_visual_report,
        **details,
        "cost_yen": 0,
        "credentials_used": False,
        "errors": errors,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


def entrypoint() -> int:
    try:
        return main()
    except Exception as exc:  # Fail closed and replace any stale success report.
        payload = {
            "ok": False,
            "checked_at_utc": datetime.now(timezone.utc).isoformat(),
            "output": str(PRODUCT.relative_to(ROOT)),
            "cost_yen": 0,
            "credentials_used": False,
            "errors": [f"validation_crash:{type(exc).__name__}:{exc}"],
        }
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        REPORT.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(entrypoint())
