# Repository bootstrap

This repository uses a versioned permanent directive. At the start of every autonomous round or resumed session:

- Read `AGENTS.md`.
- Read `OPERATIONS/CORE_DIRECTIVE.md`.
- Run `python scripts/check_directive_integrity.py` before planning or asking the user to act.
- Read `state/current.json` and `state/user_action_requests.json`.
- Automate, semi-automate, batch, prefill, and verify before requesting user operations.
- Treat `bachikoljunior-blip/note` as the only existing repository authorized for autonomous modification unless the user gives repository-specific permission.

Do not silently proceed when the directive integrity check fails.
