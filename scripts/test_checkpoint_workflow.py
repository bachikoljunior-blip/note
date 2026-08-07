#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/checkpoints.yml"
STATE = ROOT / "state/current.json"


def fail(message: str) -> None:
    raise SystemExit(message)


workflow = WORKFLOW.read_text(encoding="utf-8")
state = json.loads(STATE.read_text(encoding="utf-8"))

for key in ("after_48h_utc", "after_7d_utc"):
    due = datetime.fromisoformat(state["checkpoints"][key].replace("Z", "+00:00"))
    if (due.hour, due.minute) != (11, 33):
        fail(f"unexpected_checkpoint_time:{key}:{due.isoformat()}")

required_fragments = (
    "push:",
    'branches: [main]',
    '".github/workflows/checkpoints.yml"',
    '"scripts/check_checkpoints.py"',
    '"scripts/test_checkpoint_workflow.py"',
    'cron: "34 11 * * *"',
    'cron: "17 0,6,12,18 * * *"',
    "group: revenue-checkpoints-${{ github.repository }}",
    "cancel-in-progress: false",
    "actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683",
    "persist-credentials: false",
    "actions/github-script@60a0d83039c74a4aee543508d2ffcb1c3799cdea",
    "python3 scripts/check_checkpoints.py",
    "<!-- revenue-checkpoints-heartbeat:v1 -->",
    "observed_phase: running_before_checkout",
    "checkpoint_steps_status_before_heartbeat_update",
    "heartbeat_update_attempted_at_utc",
    "CHECKED_AT_UTC: ${{ steps.due.outputs.checked_at_utc }}",
    "linked run page is authoritative for the final job conclusion",
    "if: always()",
    "github.rest.issues.listComments",
    "github.rest.issues.updateComment",
    "github.rest.issues.createComment",
    "comment.user?.login === 'github-actions[bot]'",
    "!issue.pull_request",
    "revenue-checkpoint:${item.checkpoint}:${publicationKey}",
    "does not claim that note dashboard metrics were read",
)
for fragment in required_fragments:
    if fragment not in workflow:
        fail(f"checkpoint_workflow_contract_missing:{fragment}")

if "pull_request:" in workflow:
    fail("checkpoint_workflow_must_not_run_per_pull_request")
if "actions/setup-python" in workflow:
    fail("checkpoint_workflow_must_use_runner_python3_without_setup_action")
if workflow.index("id: heartbeat_start") > workflow.index("actions/checkout@"):
    fail("checkpoint_heartbeat_must_start_before_checkout")
if "'- status:" in workflow or "`- status:" in workflow:
    fail("checkpoint_comment_must_not_claim_unqualified_final_status")
if "finished_at_utc" in workflow:
    fail("checkpoint_comment_must_not_claim_final_completion_time")
if "reports/checkpoints.json" in workflow:
    fail("checkpoint_final_heartbeat_must_not_read_stale_report")
if "checked_at_utc={payload['checked_at_utc']}" not in (
    ROOT / "scripts/check_checkpoints.py"
).read_text(encoding="utf-8"):
    fail("checkpoint_evaluator_must_export_checked_at_output")
if workflow.count("<!-- revenue-checkpoints-heartbeat:v1 -->") != 2:
    fail("heartbeat_marker_must_exist_in_start_and_completion_steps")

marker = "          script: |\n"
if workflow.count(marker) != 3:
    fail(f"unexpected_github_script_blocks:{workflow.count(marker)}")
sources = workflow.split(marker)[1:]
with tempfile.TemporaryDirectory(prefix="checkpoint-js-") as tmp:
    for index, source in enumerate(sources, start=1):
        javascript_lines: list[str] = []
        for line in source.splitlines():
            if line.startswith("            "):
                javascript_lines.append(line[12:])
            elif line.strip():
                break
        javascript = "async function githubScript() {\n" + "\n".join(
            f"  {line}" for line in javascript_lines
        ) + "\n}\n"
        if not javascript.strip():
            fail(f"github_script_missing:{index}")
        script = Path(tmp) / f"github-script-{index}.js"
        script.write_text(javascript, encoding="utf-8")
        result = subprocess.run(
            ["node", "--check", str(script)],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            fail(f"github_script_syntax:{index}:{result.stderr.strip()}")

print(
    json.dumps(
        {
            "ok": True,
            "exact_due_plus_one_minute_cron": "34 11 * * *",
            "heartbeat_and_backup_cron": "17 0,6,12,18 * * *",
            "heartbeat_marker_count": 2,
            "github_script_blocks": 3,
            "github_script_syntax": "passed",
            "immediate_main_push_trigger": True,
            "marker_based_due_issue_deduplication": True,
        },
        ensure_ascii=False,
    )
)
