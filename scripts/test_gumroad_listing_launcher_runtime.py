#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "dist" / "gumroad_listing_launcher.html"
JAVASCRIPT_TYPES = {"", "text/javascript", "application/javascript", "module"}


class LauncherParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.data_payload = ""
        self.javascript: list[str] = []
        self._target: str | None = None
        self._buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "script":
            return
        values = {key.lower(): value for key, value in attrs}
        script_type = (values.get("type") or "").strip().lower()
        if values.get("id") == "data" and script_type == "application/json":
            self._target = "data"
        elif not values.get("src") and script_type in JAVASCRIPT_TYPES:
            self._target = "javascript"
        else:
            self._target = None
        self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._target is not None:
            self._buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "script" or self._target is None:
            return
        source = "".join(self._buffer)
        if self._target == "data":
            self.data_payload = source
        else:
            self.javascript.append(source)
        self._target = None
        self._buffer = []


def main() -> int:
    node = shutil.which("node")
    if node is None:
        print("node_not_found", file=sys.stderr)
        return 1
    if not LAUNCHER.is_file():
        print("gumroad_listing_launcher_missing", file=sys.stderr)
        return 1

    parser = LauncherParser()
    parser.feed(LAUNCHER.read_text(encoding="utf-8"))
    parser.close()
    if not parser.data_payload or len(parser.javascript) != 1:
        print(
            f"unexpected_launcher_scripts:data={bool(parser.data_payload)} js={len(parser.javascript)}",
            file=sys.stderr,
        )
        return 1

    payload = json.loads(parser.data_payload)
    node_program = f'''import assert from "node:assert/strict";
import vm from "node:vm";

const source = {json.dumps(parser.javascript[0])};
const dataText = {json.dumps(parser.data_payload)};
const payload = JSON.parse(dataText);
const elements = Object.fromEntries(
  ["title", "description", "tags", "status", "copy"].map((id) => [id, {{value: "", textContent: "", onclick: null}}]),
);
elements.data = {{textContent: dataText}};
let copied = null;
globalThis.document = {{
  getElementById(id) {{
    assert.ok(elements[id], `missing DOM stub: ${{id}}`);
    return elements[id];
  }},
}};
Object.defineProperty(globalThis, "navigator", {{
  configurable: true,
  value: {{clipboard: {{async writeText(value) {{copied = value;}}}}}},
}});

vm.runInThisContext(source, {{filename: "gumroad_listing_launcher.inline.js"}});
assert.equal(elements.title.value, payload.title, "title was not prefilled");
assert.equal(elements.description.value, payload.description, "description was not prefilled");
assert.equal(elements.tags.value, payload.tags.join("\\n"), "tags were not newline-separated");
assert.equal(typeof elements.copy.onclick, "function", "copy handler was not installed");

await elements.copy.onclick();
const expected = `Title\n${{payload.title}}\n\nPrice\nUSD ${{payload.price}}\n\nDescription\n${{payload.description}}\n\nTags\n${{payload.tags.join("\\n")}}\n\nZIP\n${{payload.product}}`;
assert.equal(copied, expected, "clipboard payload differs from visible listing data");
assert.equal(elements.status.textContent, "Copied.", "copy success status was not rendered");
console.log(JSON.stringify({{
  ok: true,
  title_chars: payload.title.length,
  description_chars: payload.description.length,
  tag_count: payload.tags.length,
  clipboard_chars: copied.length,
}}));
'''

    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", suffix=".mjs", delete=True
    ) as harness:
        harness.write(node_program)
        harness.flush()
        result = subprocess.run(
            [node, harness.name], capture_output=True, text=True, check=False
        )
    if result.stdout:
        print(result.stdout.strip())
    if result.returncode != 0:
        print(result.stderr.strip(), file=sys.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
