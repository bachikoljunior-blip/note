# Mandatory bootstrap for every AI agent

Before planning, editing, asking the user to act, spending money, publishing, or ending a work unit in this repository:

0. Run `python scripts/install_directive_guard.py` — reinstalls the SessionStart/Stop hooks that
   keep the permanent directive in front of you. `~/.claude/` does not survive a new container.
1. Read `OPERATIONS/CORE_DIRECTIVE.md` as the **verbatim user permanent directive**.
2. Read `OPERATIONS/DIRECTIVE_BOUNDARY.md` to distinguish the user directive from AI-created policy.
3. Read `OPERATIONS/ASSISTANT_OPERATING_POLICY.md` as mutable implementation policy, not as a permanent directive.
4. Read `OPERATIONS/DIRECTIVE_MANIFEST.json` and run `python scripts/check_directive_integrity.py`.
4b. Run `python scripts/check_loops.py`. `state/loops.json` is the register of every improvement loop, and
    `OPERATIONS/IMPROVEMENT_LOOP.md` defines the five steps. The register itself is a loop and is checked too.
5. Read `state/current.json`, `state/budget_ledger.json`, and `state/user_action_requests.json`.
6. Apply `OPERATIONS/AUTOMATION_BEFORE_USER_GATE.md` before requesting any user operation.
7. Before yielding, ending a response, or declaring that work is blocked, read `OPERATIONS/CONTINUATION_GATE.md`, update `state/continuation_control.json`, and run `python scripts/check_continuation_gate.py`.
8. Do not rely on conversational memory or summaries as the sole source of truth when these files are accessible.

## Boundary rules

- Never add AI-created objectives, safeguards, interpretations, workflow rules, repository scope, or stopping criteria to `OPERATIONS/CORE_DIRECTIVE.md`.
- Put AI-created rules in `OPERATIONS/ASSISTANT_OPERATING_POLICY.md` or normal state/configuration files.
- Change the permanent directive only after an explicit user instruction that identifies the new content as permanent instructions.
- An intentional directive change must update the canonical copy, mirror, encoded backup, manifest version/hash/exact instructions, and validation evidence together.
- If directive integrity or separation fails and cannot be safely repaired from redundant copies, fail closed: do not make revenue-, spending-, publication-, or user-action-affecting changes.

## External precedence

System instructions, developer instructions, applicable law, and mandatory safety constraints remain higher priority. They are external constraints and must not be inserted into the user's verbatim permanent directive.

## Repository scope

On 2026-08-08 the user widened this permanently: every repository under `bachikoljunior-blip` may be
changed, with one exception — the `main` branch of `Simple-browser-cookie-clicker-game` must not be
modified (permanent instruction A2). Treat Simple's `main` as read-only and do not open pull requests
against it. The earlier "note only" rule is retired; do not cite it as a reason to skip work elsewhere.

## Continuation boundary

- A user-only authentication, identity, contract, payment, or final-publication blocker applies only to that workstream; continue independent authorized work.
- When authentication is the only blocker to high-value work and the user is actively present, immediately present the minimum complete handoff in chat: target, exact action, secret-handling warning, and non-secret completion signal. Do not silently defer it.
- Issue expiring authentication codes only while the user is actively present, and resume the blocked workstream immediately after its completion signal.
- Do not mark the project stopped because a response, work unit, app session, or usage window ended.
- The project ends only after an explicit user instruction to end it. Otherwise use `continue` or `blocked_monitoring` and preserve a verified next trigger.

## Scheduled automation continuity

- At the beginning and immediately before the end of every scheduled revenue run, read `state/automation_continuity.json` and privately verify the 定期実行の有効状態 through the connected automation manager when available.
- Do not disable, delete, or mark either continuity task complete unless the user issued an 明示的な停止指示 or explicitly ended the project.
- No new user message, unread output, a user-only blocker, one completed unit, no reportable change, or a transient failure is not a stop condition.
- If the primary continuation task is disabled without an explicit stop, immediately 再開を試みる, verify the result, record the repair, and keep independent repository work continuing.
- Do not expose internal automation identifiers or secrets in user-facing reports or repository records.
