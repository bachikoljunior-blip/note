Always bootstrap from the repository, not from conversational memory alone.

Before making or proposing changes:

1. Read `AGENTS.md`.
2. Read `OPERATIONS/CORE_DIRECTIVE.md` as the verbatim user permanent directive.
3. Read `OPERATIONS/DIRECTIVE_BOUNDARY.md`.
4. Read `OPERATIONS/ASSISTANT_OPERATING_POLICY.md` as mutable AI policy.
5. Run `python scripts/check_directive_integrity.py`.
6. Read `state/current.json`, `state/budget_ledger.json`, and `state/user_action_requests.json`.
7. Apply the automation-before-user-request gate.

Never insert assistant-created interpretation, safety language, workflow rules, or stopping criteria into `OPERATIONS/CORE_DIRECTIVE.md`. Only an explicit user redefinition of permanent instructions may change it.

Do not request manual user actions until direct execution, official APIs, GitHub Actions, browser sharing, shortcuts, batching, prefilling, verification, and logging have been evaluated and implemented where worthwhile.

Only `bachikoljunior-blip/note` is authorized for autonomous modification among existing repositories.
