# Mandatory bootstrap for every AI agent

Before planning, editing, asking the user to act, or ending a work unit in this repository:

1. Read `OPERATIONS/CORE_DIRECTIVE.md` as the canonical permanent directive.
2. Read `OPERATIONS/DIRECTIVE_MANIFEST.json` and verify the directive version/hash through `python scripts/check_directive_integrity.py`.
3. Read `state/current.json` and `state/user_action_requests.json`.
4. Follow `OPERATIONS/AUTOMATION_BEFORE_USER_GATE.md` before requesting any user operation.
5. Do not use memory or prior-chat summaries as the sole source of truth when these files are available.
6. If the integrity check fails and cannot be repaired from the redundant copies, do not make revenue-affecting writes. Open or update the integrity incident and report the exact failure.
7. Do not modify any existing repository other than `bachikoljunior-blip/note` without explicit repository-specific permission.

The permanent directive is versioned and intentionally updateable, but an update must change the canonical copy, mirror, encoded backup, manifest version/hash, and validation evidence together.
