#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/main_validation_evidence.yml"


def fail(message: str) -> None:
    raise SystemExit(message)


workflow = WORKFLOW.read_text(encoding="utf-8")
required = (
    'workflows: ["Validate and analyze"]',
    "types: [completed]",
    "issues: write",
    "github.event.workflow_run.head_branch == 'main'",
    "github.event.workflow_run.event == 'push'",
    "actions/github-script@60a0d83039c74a4aee543508d2ffcb1c3799cdea",
    "<!-- main-validate-evidence:v1 -->",
    "run.name !== 'Validate and analyze'",
    "run.head_branch !== 'main'",
    "run.event !== 'push'",
    "workflow_conclusion",
    "run.html_url",
    "comment.user?.login === 'github-actions[bot]'",
    "github.rest.issues.updateComment",
    "github.rest.issues.createComment",
    "linked run page is authoritative",
)
for fragment in required:
    if fragment not in workflow:
        fail(f"main_validation_evidence_contract_missing:{fragment}")

for forbidden in (
    "pull_request:",
    "actions/checkout@",
    "contents: write",
    "actions: write",
    "secrets.",
):
    if forbidden in workflow:
        fail(f"main_validation_evidence_forbidden:{forbidden}")

marker = "          script: |\n"
if workflow.count(marker) != 1:
    fail("main_validation_evidence_script_count")
source = workflow.split(marker, 1)[1]
javascript_lines: list[str] = []
for line in source.splitlines():
    if line.startswith("            "):
        javascript_lines.append(line[12:])
    elif line.strip():
        break
javascript = "async function githubScript() {\n" + "\n".join(
    f"  {line}" for line in javascript_lines
) + "\n}\n"
with tempfile.TemporaryDirectory(prefix="main-validation-evidence-js-") as tmp:
    script = Path(tmp) / "evidence.js"
    script.write_text(javascript, encoding="utf-8")
    result = subprocess.run(
        ["node", "--check", str(script)],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode:
        fail(f"main_validation_evidence_javascript:{result.stderr.strip()}")

print("main_validation_evidence_workflow_ok")
