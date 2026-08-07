# Mandatory bootstrap for every AI agent

Before planning, editing, asking the user to act, spending money, publishing, or ending a work unit in this repository:

1. Read `OPERATIONS/CORE_DIRECTIVE.md` as the **verbatim user permanent directive**.
2. Read `OPERATIONS/DIRECTIVE_BOUNDARY.md` to distinguish the user directive from AI-created policy.
3. Read `OPERATIONS/ASSISTANT_OPERATING_POLICY.md` as mutable implementation policy, not as a permanent directive.
4. Read `OPERATIONS/DIRECTIVE_MANIFEST.json` and run `python scripts/check_directive_integrity.py`.
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

`bachikoljunior-blip/note` is authorized for this work. Do not modify another existing repository without explicit repository-specific permission.

## Continuation boundary

- A user-only authentication, identity, contract, payment, or final-publication blocker applies only to that workstream; continue independent authorized work.
- Do not mark the project stopped because a response, work unit, app session, or usage window ended.
- The project ends only after an explicit user instruction to end it. Otherwise use `continue` or `blocked_monitoring` and preserve a verified next trigger.
