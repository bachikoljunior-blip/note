#!/usr/bin/env python3
from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORMAT_MAP_PATH = ROOT / "config" / "english_topic_format_map.json"
PARTS_DIR = ROOT / "artifacts" / "product_en_v1_0"
BASE_OUTPUT = ROOT / "dist" / "Non_Repetitive_AI_Trivia_Shorts_Kit_EN_v1.0.zip"
OUTPUT = ROOT / "dist" / "Non_Repetitive_AI_Trivia_Shorts_Kit_EN_v1.1.zip"
REPORT = ROOT / "reports" / "english_product.json"
BASE_EXPECTED_BYTES = 20577
BASE_EXPECTED_SHA256 = "73d1009517456d50578f702c836d4da004e1cee4fe17a410e40df84a1559ffc8"
EXPECTED_MEMBERS = 15
FIXED_ZIP_TIME = (2026, 8, 7, 0, 0, 0)
JAPANESE = re.compile(r"[\u3040-\u30ff\u4e00-\u9fff]")

HOOK_TEMPLATES = {
    "F01": "Open from a future curator's viewpoint with the subject unnamed. Show two clues connected to “{q}”, reveal the subject only after clue two, then end on one overlooked implication.",
    "F02": "Show the visible effect in “{q}” without explaining it. Ask what is happening out of sight, travel through two hidden layers, then return to the same effect with one limitation.",
    "F03": "State the obvious alternative implied by “{q}”. Give that alternative one fair advantage, expose the hidden constraint, then show where the alternative still works.",
    "F04": "Withhold the answer to “{q}”. Present one visual clue, one numeric or historical clue, and one mechanism clue; invite a prediction after clue two, then reveal the answer and a condition where it changes.",
    "F05": "Place the start and end states behind “{q}” side by side. Run a fast clock through three transitions, freeze at the turning point, then name what the compression leaves out.",
    "F06": "Start with one small rule, dimension, or constraint behind “{q}”. Follow it across three consequences at increasing scale, show what fails without coordination, then name an exception.",
    "F07": "Show a baseline case for “{q}”, change exactly one condition, and ask viewers to predict the result. Compare outcomes, explain the mechanism, then state why the one-variable demonstration is not universal.",
    "F08": "Begin at the familiar scale in “{q}”, jump to a much smaller, larger, or longer time scale, reveal what becomes visible there, then return to the starting scale with the consequence.",
    "F09": "Open with the most tempting mistaken explanation for “{q}”, explicitly label it as a hypothesis, show the contradiction, then replace it with a narrower model.",
    "F10": "Choose the object, word, signal, payment, or information at the center of “{q}”. Follow it through three handoffs, pause at the hidden decision, then end at the user-visible result.",
    "F11": "Turn “{q}” into an A/B prediction. Show two outcomes, give viewers two seconds to choose, reveal the supported result, then identify whether the evidence is a measurement, demonstration, or simulation.",
    "F12": "Remove the mechanism, convention, or condition behind “{q}”. Show the first failure and one second-order effect, then introduce the workaround and explain why the original persists.",
}

VISUAL_TEMPLATES = {
    "Everyday Science": [
        "Macro view of the everyday object → transparent cutaway → return to the same object with cause arrows",
        "Side-by-side A/B setup → change one physical condition → compare the visible outcomes",
        "Slow-motion or time-compressed sequence → three labeled states → limitation card",
        "Tabletop demonstration → force, heat, or pressure arrows → real-world use",
        "Human-scale view → molecular or structural zoom → zoom back to the observed effect",
    ],
    "Brain & Perception": [
        "Two-panel perception test → viewer prediction → reveal the boundary condition",
        "First-person point of view → moving attention cue → simple input-processing-output diagram",
        "Timed choice demonstration → pause before the answer → alternate-explanation card",
        "Split sensory inputs → processing stages → subjective report versus measurable observation",
        "Memory or decision timeline → missing-information branch → uncertainty and individual-difference note",
    ],
    "AI & Technology": [
        "Screen-recorded symptom → simplified data-flow diagram → failure versus recovery",
        "Two inputs and two outputs → hidden transformation stages → capability-and-limitation card",
        "Device or sensor close-up → signal route map → user-visible consequence",
        "Before-and-after processing comparison → change one setting → speed-quality-privacy tradeoff",
        "System boundary diagram → what the feature does versus does not protect → practical takeaway",
    ],
    "History & Standards": [
        "Then-and-now objects → three-date timeline → surviving legacy",
        "Two-region adoption map → coordination constraint → modern difference",
        "Dimension or symbol overlay → interoperability chain → named exception",
        "Competing-option fork → lock-in turning point → present-day path dependence",
        "Everyday interface close-up → origin artifact → current use and failure mode",
    ],
    "Systems & Society": [
        "Customer or data journey map → three hidden handoffs → delay or risk point",
        "Two-country or two-provider comparison → rule branch → different user outcome",
        "Request-to-result timeline → bottleneck close-up → exception or reversal",
        "Stakeholder map → incentive and constraint arrows → consumer-visible result",
        "Normal operation versus disruption → first failure → workaround and remaining limit",
    ],
}

ANALYTICS_FIELDS = [
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


def replace_exact(text: str, old: str, new: str, label: str, errors: list[str]) -> str:
    count = text.count(old)
    if count != 1:
        errors.append(f"replace_count:{label}:{count}!=1")
        return text
    return text.replace(old, new)


def load_format_map(errors: list[str]) -> dict[str, str]:
    try:
        contract = json.loads(FORMAT_MAP_PATH.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"format_map:{type(exc).__name__}:{exc}")
        return {}
    if contract.get("schema_version") != "1.0":
        errors.append("format_map_schema_version")
    if contract.get("classification") != "assistant_curated_product_configuration_not_permanent_directive":
        errors.append("format_map_classification")
    mapping = contract.get("topic_formats")
    if not isinstance(mapping, dict):
        errors.append("format_map_topic_formats")
        return {}
    return {str(key): str(value) for key, value in mapping.items()}


def load_base(errors: list[str]) -> tuple[bytes, str]:
    parts = sorted(PARTS_DIR.glob("part-*.b64"))
    source = "base64_parts"
    if len(parts) == 7:
        try:
            encoded = "".join(
                "".join(path.read_text(encoding="ascii").split()) for path in parts
            )
            data = base64.b64decode(encoded, validate=True)
        except Exception as exc:  # noqa: BLE001
            data = b""
            errors.append(f"decode:{type(exc).__name__}:{exc}")
    elif not parts and BASE_OUTPUT.is_file():
        data = BASE_OUTPUT.read_bytes()
        source = "validated_existing_base_zip"
    else:
        data = b""
        errors.append(f"part_count:{len(parts)}!=7")

    digest = hashlib.sha256(data).hexdigest()
    valid = True
    if len(data) != BASE_EXPECTED_BYTES:
        errors.append(f"base_bytes:{len(data)}!={BASE_EXPECTED_BYTES}")
        valid = False
    if digest != BASE_EXPECTED_SHA256:
        errors.append(f"base_sha256:{digest}!={BASE_EXPECTED_SHA256}")
        valid = False
    if valid:
        BASE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        BASE_OUTPUT.write_bytes(data)
        return data, source
    return b"", source


def transform(base_data: bytes, errors: list[str]) -> tuple[bytes, dict[str, object]]:
    try:
        with zipfile.ZipFile(io.BytesIO(base_data)) as archive:
            names = archive.namelist()
            if len(names) != EXPECTED_MEMBERS:
                errors.append(f"base_zip_members:{len(names)}!={EXPECTED_MEMBERS}")
            if len(names) != len(set(names)):
                errors.append("base_duplicate_member")
            if archive.testzip() is not None:
                errors.append("base_corrupt_member")
            members = {name: archive.read(name) for name in names}
    except Exception as exc:  # noqa: BLE001
        errors.append(f"base_zip:{type(exc).__name__}:{exc}")
        return b"", {}

    topic_text = members["100_topics.csv"].decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(topic_text))
    topic_fields = list(reader.fieldnames or [])
    topics = list(reader)
    format_map = load_format_map(errors)
    topic_ids = {row.get("id", "") for row in topics}
    if set(format_map) != topic_ids:
        errors.append("format_map_topic_ids")
    category_indices: Counter[str] = Counter()
    for row in topics:
        format_id = format_map.get(row.get("id", ""), "")
        row["recommended_format"] = format_id
        category = row.get("category", "")
        question = row.get("core_question", "")
        if format_id not in HOOK_TEMPLATES:
            errors.append(f"unknown_format:{row.get('id')}:{format_id}")
            continue
        if category not in VISUAL_TEMPLATES:
            errors.append(f"unknown_category:{row.get('id')}:{category}")
            continue
        row["hook_direction"] = HOOK_TEMPLATES[format_id].format(q=question)
        row["visual_direction"] = VISUAL_TEMPLATES[category][category_indices[category] % 5]
        category_indices[category] += 1
    members["100_topics.csv"] = csv_bytes(topics, topic_fields)
    members["preview_10_topics.csv"] = csv_bytes(topics[:10], topic_fields)

    readme = members["README_PRODUCT.md"].decode("utf-8")
    readme = replace_exact(
        readme,
        "5. Use P03 or P04 to create the script.",
        "5. Use P03 to draft the script, then optionally use P04 to divide the finished script into six connected clips.",
        "readme_p03_p04",
        errors,
    )
    readme += """
## What the 100 rows are
The 100 CSV rows are topic and production prompts for research. They are not 100 finished scripts and they are not pre-verified factual claims. The kit includes one fully worked 55-second script example.

## Opening the files
- CSV files open in Numbers, Google Sheets, Excel, or another spreadsheet app. Keep the header row when importing.
- Markdown files are plain text and open in any text editor or Markdown viewer.
- On iPhone, save the ZIP to Files, decompress it, then open a CSV in Numbers or a Markdown file in a text editor.

## Revenue column definitions
- `youtube_estimated_revenue`: the revenue estimate reported by YouTube for the video.
- `attributed_product_revenue`: product revenue attributed to that video or its tracked link.
- `youtube_revenue_currency_code`: the ISO currency code of the YouTube-reported estimate.
- `product_revenue_currency_code`: the ISO currency code of the attributed product revenue.
- `reporting_currency_code`: the one ISO currency used for normalized comparison on that row.
- `youtube_to_reporting_fx_rate` and `product_to_reporting_fx_rate`: reporting-currency units per one source-currency unit; use `1` when source and reporting currencies match.
- `fx_rate_date` and `fx_rate_source`: the date and source used for both recorded rates.
- `youtube_revenue_reporting_currency` and `product_revenue_reporting_currency`: each raw revenue value multiplied by its recorded FX rate.
- If a denominator or required FX rate is zero or missing, leave the related normalized field blank or mark it `NA`.
- Never add or compare the two raw revenue values when their source currencies differ.
"""
    members["README_PRODUCT.md"] = readme.encode("utf-8")

    calendar_reader = csv.DictReader(
        io.StringIO(members["30_day_calendar.csv"].decode("utf-8-sig"))
    )
    calendar_fields = list(calendar_reader.fieldnames or [])
    calendar = list(calendar_reader)
    replaced_ctas = 0
    formats_by_topic = {row["id"]: row["recommended_format"] for row in topics}
    for row in calendar:
        topic_id = row.get("topic_id", "")
        if topic_id in formats_by_topic:
            row["format_id"] = formats_by_topic[topic_id]
        else:
            errors.append(f"calendar_unknown_topic:{topic_id}")
        if row.get("cta") == "point to the free preview":
            row["cta"] = "mention the kit only when directly relevant"
            replaced_ctas += 1
    if replaced_ctas != 5:
        errors.append(f"calendar_free_preview_replacements:{replaced_ctas}!=5")
    members["30_day_calendar.csv"] = csv_bytes(calendar, calendar_fields)
    members["analytics_tracker.csv"] = csv_bytes([], ANALYTICS_FIELDS)

    prompt_library = members["prompt_library.md"].decode("utf-8")
    for old, new, label in (
        (
            "- Shorts `views` can include starts and replays, so use `engagedViews` when comparing quality.",
            "- Shorts `views` can include starts and replays, so use `engaged_views` when comparing quality.",
            "prompt_p07_engaged_views_name",
        ),
        ("- engaged-view rate = engagedViews / views", "- engaged-view rate = engaged_views / views", "prompt_p07_engaged_rate"),
        ("- share rate = shares / engagedViews", "- share rate = shares / engaged_views", "prompt_p07_share_rate"),
        ("- comment rate = comments / engagedViews", "- comment rate = comments / engaged_views", "prompt_p07_comment_rate"),
        (
            "- net subscriber rate = (subscribersGained - subscribersLost) / engagedViews",
            "- net subscriber rate = (subscribers_gained - subscribers_lost) / engaged_views",
            "prompt_p07_subscriber_rate",
        ),
        ("- product conversion = productSales / linkClicks", "- product conversion = product_sales / link_clicks", "prompt_p07_product_conversion"),
    ):
        prompt_library = replace_exact(prompt_library, old, new, label, errors)
    prompt_library = replace_exact(
        prompt_library,
        "- revenue per 1,000 engaged views = revenue / engagedViews × 1000",
        "- YouTube revenue in reporting currency = youtube_estimated_revenue × youtube_to_reporting_fx_rate\n- Product revenue in reporting currency = attributed_product_revenue × product_to_reporting_fx_rate\n- YouTube revenue per 1,000 engaged views in reporting currency = youtube_revenue_reporting_currency / engaged_views × 1000\n- Product revenue per 1,000 engaged views in reporting currency = product_revenue_reporting_currency / engaged_views × 1000",
        "prompt_p07_revenue",
        errors,
    )
    prompt_library = replace_exact(
        prompt_library,
        "- Change one experimental variable at a time.",
        "- Change one experimental variable at a time.\n- If a denominator or required FX rate is zero or missing, return blank or NA.\n- Keep YouTube and product revenue in their separate source currencies. To compare or add them, fill the reporting currency, both FX rates, FX date, and FX source.",
        "prompt_p07_safeguards",
        errors,
    )
    members["prompt_library.md"] = prompt_library.encode("utf-8")

    rules = members["analytics_decision_rules.md"].decode("utf-8")
    rules = replace_exact(
        rules,
        "6. `revenue / engaged_views * 1000`: revenue normalized for engaged-view scale.",
        "6. `youtube_revenue_reporting_currency / engaged_views * 1000`: FX-audited YouTube revenue normalized for engaged-view scale.\n7. `product_revenue_reporting_currency / engaged_views * 1000`: FX-audited product revenue normalized for engaged-view scale.",
        "analytics_rule_revenue",
        errors,
    )
    rules = replace_exact(
        rules,
        "7. `product_sales / link_clicks`: sales-page conversion when link tracking exists.",
        "8. `product_sales / link_clicks`: sales-page conversion when link tracking exists.",
        "analytics_rule_renumber",
        errors,
    )
    rules += """
## Revenue normalization safeguards
- Keep `youtube_estimated_revenue` and `attributed_product_revenue` in their separate source currencies; record their ISO codes in `youtube_revenue_currency_code` and `product_revenue_currency_code`.
- Select one `reporting_currency_code`. Record each FX rate as reporting-currency units per one source-currency unit, plus `fx_rate_date` and `fx_rate_source`. Use `1` when a source currency already matches the reporting currency.
- Calculate the two reporting-currency values separately, then calculate revenue per 1,000 engaged views from those normalized values.
- Leave a normalized value blank or mark it `NA` when its denominator or required FX rate is zero or missing.
- Never add or compare unlike raw currencies.
"""
    members["analytics_decision_rules.md"] = rules.encode("utf-8")

    changelog = members["CHANGELOG.md"].decode("utf-8")
    changelog = replace_exact(
        changelog,
        "# Changelog\n",
        """# Changelog

## v1.1 — 2026-08-07
- Replaced one repeated hook direction with 12 format-specific hook approaches.
- Expanded five repeated visual directions into 25 category-specific planning patterns.
- Clarified that the kit contains 100 research prompts and one fully worked script, not 100 finished scripts.
- Separated YouTube and product revenue currencies and added auditable reporting-currency FX fields.
- Removed calendar references to an unavailable free preview.
""",
        "changelog_heading",
        errors,
    )
    members["CHANGELOG.md"] = changelog.encode("utf-8")

    manifest_files = [
        {
            "name": name,
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        }
        for name, data in sorted(members.items())
        if name != "manifest.json"
    ]
    manifest = {
        "product_name": "Non-Repetitive AI Trivia Shorts Kit",
        "version": "1.1",
        "release_date": "2026-08-07",
        "language": "English",
        "content_summary": {
            "topic_prompts": 100,
            "story_formats": 12,
            "workflow_prompts": 9,
            "visual_planning_patterns": 25,
            "fully_worked_script_examples": 1,
        },
        "files": manifest_files,
        "disclaimer": "Topic rows are research prompts, not pre-verified factual claims.",
    }
    members["manifest.json"] = (
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
    ).encode("utf-8")

    output_stream = io.BytesIO()
    with zipfile.ZipFile(output_stream, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in sorted(members):
            info = zipfile.ZipInfo(name, date_time=FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_STORED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, members[name], compress_type=zipfile.ZIP_STORED)

    hook_signatures = {
        row["hook_direction"].replace(row["core_question"], "<QUESTION>")
        for row in topics
    }
    visual_counts = Counter(row["visual_direction"] for row in topics)
    format_counts = Counter(row["recommended_format"] for row in topics)
    summary: dict[str, object] = {
        "topics": len(topics),
        "unique_topic_ids": len({row.get("id", "") for row in topics}),
        "hook_signatures": len(hook_signatures),
        "format_counts": dict(sorted(format_counts.items())),
        "visual_patterns": len(visual_counts),
        "visual_pattern_counts": dict(sorted(visual_counts.items())),
        "calendar_free_preview_replacements": replaced_ctas,
    }
    return output_stream.getvalue(), summary


def main() -> int:
    errors: list[str] = []
    base_data, base_source = load_base(errors)
    data, summary = transform(base_data, errors) if base_data and not errors else (b"", {})
    digest = hashlib.sha256(data).hexdigest()

    member_count = 0
    format_count = 0
    prompt_count = 0
    if data:
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                names = archive.namelist()
                member_count = len(names)
                if archive.testzip() is not None:
                    errors.append("output_corrupt_member")
                if member_count != EXPECTED_MEMBERS:
                    errors.append(f"output_zip_members:{member_count}!={EXPECTED_MEMBERS}")
                formats = archive.read("12_formats.md").decode("utf-8")
                prompts = archive.read("prompt_library.md").decode("utf-8")
                format_count = len(re.findall(r"^## F\d{2}\b", formats, flags=re.MULTILINE))
                prompt_count = len(re.findall(r"^## P\d{2}\b", prompts, flags=re.MULTILINE))
                for name in names:
                    if Path(name).suffix.lower() not in {".md", ".txt", ".csv", ".json"}:
                        continue
                    text = archive.read(name).decode("utf-8-sig")
                    if JAPANESE.search(text):
                        errors.append(f"japanese_character_found:{name}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"output_zip_validation:{type(exc).__name__}:{exc}")

    if summary.get("topics") != 100:
        errors.append(f"topics:{summary.get('topics')}!=100")
    if summary.get("unique_topic_ids") != 100:
        errors.append(f"unique_topic_ids:{summary.get('unique_topic_ids')}!=100")
    if summary.get("hook_signatures") != 12:
        errors.append(f"hook_signatures:{summary.get('hook_signatures')}!=12")
    if summary.get("visual_patterns") != 25:
        errors.append(f"visual_patterns:{summary.get('visual_patterns')}!=25")
    if format_count != 12:
        errors.append(f"formats:{format_count}!=12")
    if prompt_count != 9:
        errors.append(f"prompts:{prompt_count}!=9")

    output_written = False
    if not errors:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(data)
        output_written = True
    elif OUTPUT.is_file():
        OUTPUT.unlink()

    payload = {
        "ok": not errors,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "base": {
            "source": base_source,
            "bytes": len(base_data),
            "sha256": hashlib.sha256(base_data).hexdigest(),
        },
        "version": "1.1",
        "output": str(OUTPUT.relative_to(ROOT)),
        "output_written": output_written,
        "bytes": len(data),
        "sha256": digest,
        "zip_members": member_count,
        "formats": format_count,
        "prompts": prompt_count,
        **summary,
        "japanese_character_scan": "passed" if not any("japanese_character" in e for e in errors) else "failed",
        "cost_yen": 0,
        "credentials_used": False,
        "errors": errors,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
