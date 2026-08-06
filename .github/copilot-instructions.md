Always bootstrap from the repository, not from conversational memory alone.

Before making or proposing changes:

1. Read `AGENTS.md`.
2. Read `OPERATIONS/CORE_DIRECTIVE.md`.
3. Run `python scripts/check_directive_integrity.py`.
4. Read `state/current.json` and `state/user_action_requests.json`.
5. Apply the automation-before-user-request gate.

Do not request manual user actions until direct execution, official APIs, GitHub Actions, browser sharing, shortcuts, batching, prefilling, verification, and logging have been evaluated and implemented where worthwhile.

Only `bachikoljunior-blip/note` is authorized for autonomous modification among existing repositories.
