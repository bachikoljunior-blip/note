#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORT = ROOT / "reports" / "inline_javascript.json"
JAVASCRIPT_TYPES = {"", "text/javascript", "application/javascript", "module"}


class InlineScriptCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.blocks: list[str] = []
        self._inside_script = False
        self._current: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "script":
            return
        values = {key.lower(): value for key, value in attrs}
        script_type = (values.get("type") or "").strip().lower()
        self._inside_script = True
        self._current = [] if not values.get("src") and script_type in JAVASCRIPT_TYPES else None

    def handle_data(self, data: str) -> None:
        if self._inside_script and self._current is not None:
            self._current.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "script" or not self._inside_script:
            return
        if self._current is not None:
            self.blocks.append("".join(self._current))
        self._inside_script = False
        self._current = None


def main() -> int:
    node = shutil.which("node")
    errors: list[str] = []
    checked: list[dict[str, object]] = []
    html_paths = sorted(DIST.rglob("*.html"))
    if not html_paths:
        errors.append("no_generated_html_found")
    if node is None:
        errors.append("node_not_found")

    for html_path in html_paths:
        parser = InlineScriptCollector()
        try:
            parser.feed(html_path.read_text(encoding="utf-8"))
            parser.close()
        except Exception as exc:  # HTMLParser errors are evidence, not a reason to abort the report.
            errors.append(f"html_parse_failed:{html_path.relative_to(ROOT)}:{exc}")
            continue

        item: dict[str, object] = {
            "path": str(html_path.relative_to(ROOT)),
            "inline_javascript_blocks": len(parser.blocks),
        }
        checked.append(item)
        if node is None:
            continue
        for index, source in enumerate(parser.blocks):
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", suffix=".mjs", delete=True
            ) as script_file:
                script_file.write(source)
                script_file.flush()
                result = subprocess.run(
                    [node, "--check", script_file.name],
                    capture_output=True,
                    text=True,
                    check=False,
                )
            if result.returncode != 0:
                detail = (result.stderr or result.stdout).strip().replace("\n", " | ")
                errors.append(
                    f"javascript_syntax_error:{html_path.relative_to(ROOT)}:{index}:{detail}"
                )

    payload = {
        "ok": not errors,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "html_files": len(html_paths),
        "inline_javascript_blocks": sum(
            int(item["inline_javascript_blocks"]) for item in checked
        ),
        "checked": checked,
        "errors": errors,
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
