# Repository bootstrap

At the start of every autonomous round, resumed session, or long-session resynchronization:

1. Read `AGENTS.md`.
2. Read `OPERATIONS/CORE_DIRECTIVE.md` as the exact user permanent directive.
3. Read `OPERATIONS/DIRECTIVE_BOUNDARY.md`.
4. Read `OPERATIONS/ASSISTANT_OPERATING_POLICY.md` as mutable AI policy, not user instruction.
5. Run `python scripts/check_directive_integrity.py` before planning, spending, publishing, ending, or asking the user to act.
6. Read `state/current.json`, `state/budget_ledger.json`, and `state/user_action_requests.json`.
7. Automate, semi-automate, batch, prefill, and verify before requesting user operations.

Never merge assistant-created interpretation into `OPERATIONS/CORE_DIRECTIVE.md`. Only an explicit user redefinition of permanent instructions may change it, and every redundant copy plus the manifest must be updated together.

Treat `bachikoljunior-blip/note` as the only existing repository authorized for autonomous modification unless the user gives repository-specific permission. Do not silently proceed when directive integrity or separation fails.
